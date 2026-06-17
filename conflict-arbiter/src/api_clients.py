"""IUCN / CITES API 实时数据接入客户端 (火 🟥)

提供 IUCN Red List API v4 和 CITES Species+ Checklist API 的 Python 客户端。
支持: API key 环境变量、本地 JSON 缓存 (24h TTL)、速率限制、优雅降级。

环境变量:
    IUCN_API_KEY    — IUCN Red List API v4 token
    CITES_API_KEY   — CITES Species+ API token

缓存目录: $HOME/.conflict_arbiter_cache/ 或项目根下的 .cache/
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 尝试导入 httpx (可选依赖, 优雅降级)
try:
    import httpx

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False
    logger.warning("httpx 未安装, API 客户端将以离线模式运行 (仅缓存)")


# ── 缓存工具 ──

def _cache_dir() -> Path:
    """获取缓存目录, 确保存在。"""
    env_dir = os.environ.get("CONFLICT_ARBITER_CACHE_DIR", "")
    if env_dir:
        d = Path(env_dir)
    else:
        d = Path.home() / ".conflict_arbiter_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_key(prefix: str, name: str) -> str:
    """生成缓存文件名 (去除特殊字符)."""
    safe = name.lower().replace(" ", "_").replace("/", "_")
    return f"{prefix}_{safe}.json"


class CacheStore:
    """简单的 JSON 文件缓存, 带 TTL 过期。"""

    def __init__(self, ttl_seconds: int = 86400) -> None:
        self._dir = _cache_dir()
        self._ttl = ttl_seconds  # 默认 24 小时

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """读取缓存, 过期返回 None。"""
        fpath = self._dir / key
        if not fpath.is_file():
            return None
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            return None
        age = time.time() - data.get("_cached_at", 0)
        if age > self._ttl:
            logger.debug(f"缓存过期: {key} (age={age:.0f}s)")
            return None
        logger.debug(f"缓存命中: {key} (age={age:.0f}s)")
        return data.get("payload")

    def set(self, key: str, payload: Dict[str, Any]) -> None:
        """写入缓存。"""
        fpath = self._dir / key
        data = {"_cached_at": time.time(), "payload": payload}
        fpath.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")

    def clear(self) -> int:
        """清空所有缓存, 返回删除文件数。"""
        count = 0
        for f in self._dir.glob("*"):
            if f.is_file():
                f.unlink()
                count += 1
        return count


# ── 速率限制器 ──

class RateLimiter:
    """简单的令牌桶速率限制器 (线程不安全, 单线程够用)。"""

    def __init__(self, calls_per_second: float = 2.0) -> None:
        self._rate = calls_per_second
        self._min_interval = 1.0 / calls_per_second
        self._last_call = 0.0

    def wait(self) -> None:
        """必要时等待以遵守速率限制。"""
        now = time.time()
        elapsed = now - self._last_call
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_call = time.time()


# ═══════════════════════════════════════════════════════════════════
# IUCN Red List API v4 客户端
# ═══════════════════════════════════════════════════════════════════

class IUCNClient:
    """IUCN Red List API v4 客户端。

    文档: https://api.iucnredlist.org/api/v4/docs
    需要 API key (注册免费): https://api.iucnredlist.org/
    """

    BASE = "https://api.iucnredlist.org/api/v4"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl: int = 86400,
        rate_limit: float = 2.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("IUCN_API_KEY", "")
        self._cache = CacheStore(ttl_seconds=cache_ttl)
        self._limiter = RateLimiter(calls_per_second=rate_limit)
        if not self._api_key:
            logger.warning(
                "IUCN_API_KEY 未设置 — IUCN API 调用将不可用。"
                " 请设置环境变量 IUCN_API_KEY 或传入 api_key 参数。"
            )

    # ── 公共 API ──

    def get_assessment(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取 IUCN 红色名录评估信息。

        Returns:
            {
                "category": "EN",           # IUCN 分类代码
                "category_name": "濒危",
                "assessment_date": "2023-01-15",
                "criteria": "A2bcd",
                "population_trend": "decreasing",
                "threats": [...],           # 威胁列表
                "habitats": [...],          # 栖息地列表
                "url": "https://www.iucnredlist.org/species/..."
            }
            失败返回 None。
        """
        ckey = _cache_key("iucn_assess", scientific_name)
        cached = self._cache.get(ckey)
        if cached is not None:
            return cached

        result = self._fetch_assessment(scientific_name)
        if result is not None:
            self._cache.set(ckey, result)
        return result

    def get_habitat(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取物种栖息地信息。

        Returns:
            {"suitable": [...], "major": [...], "marginal": [...]}
        """
        ckey = _cache_key("iucn_habitat", scientific_name)
        cached = self._cache.get(ckey)
        if cached is not None:
            return cached

        result = self._fetch_habitat(scientific_name)
        if result is not None:
            self._cache.set(ckey, result)
        return result

    def get_threats(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取物种威胁信息。

        Returns:
            {"threats": [{"code": "5.4.1", "title": "...", "timing": "...",
                          "scope": "...", "severity": "...", "score": "..."}]}
        """
        ckey = _cache_key("iucn_threats", scientific_name)
        cached = self._cache.get(ckey)
        if cached is not None:
            return cached

        result = self._fetch_threats(scientific_name)
        if result is not None:
            self._cache.set(ckey, result)
        return result

    def get_full_profile(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取 IUCN 完整信息 (评估 + 栖息地 + 威胁)。

        Returns:
            合并后的完整 profile dict, 或 None (全部获取失败时)。
        """
        assessment = self.get_assessment(scientific_name)
        habitat = self.get_habitat(scientific_name)
        threats = self.get_threats(scientific_name)

        if assessment is None and habitat is None and threats is None:
            return None

        return {
            "scientific_name": scientific_name,
            "source": "iucn",
            "assessment": assessment or {},
            "habitat": habitat or {},
            "threats": threats or {},
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # ── 内部 HTTP 方法 ──

    def _fetch_assessment(self, name: str) -> Optional[Dict[str, Any]]:
        """通过 /assessment/species/name/{name} 端点获取评估。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/assessment/species/name/{name}"
        data = self._get(url)
        if data is None:
            return None

        try:
            # API v4 返回格式: {"assessments": [...]}
            assessments = data.get("assessments", [])
            if not assessments:
                logger.info(f"IUCN: 未找到 {name} 的评估记录")
                return None
            # 取最新一条
            latest = assessments[0]
            return {
                "category": latest.get("redlistCategory", {}).get("code", ""),
                "category_name": latest.get("redlistCategory", {}).get("title", ""),
                "assessment_date": latest.get("year_published", ""),
                "criteria": latest.get("criteria", ""),
                "population_trend": latest.get("population_trend", ""),
                "url": latest.get("url", ""),
            }
        except Exception as exc:
            logger.warning(f"IUCN 解析评估数据失败: {exc}")
            return None

    def _fetch_habitat(self, name: str) -> Optional[Dict[str, Any]]:
        """通过 /habitats/species/name/{name} 端点获取栖息地。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/habitats/species/name/{name}"
        data = self._get(url)
        if data is None:
            return None

        try:
            habitats = data.get("result", [])
            suitable = [h["habitat"] for h in habitats if h.get("suitability") == "Suitable"]
            major = [h["habitat"] for h in habitats if h.get("majorimportance")]
            marginal = [h["habitat"] for h in habitats if h.get("suitability") == "Marginal"]
            return {
                "suitable": suitable,
                "major": major,
                "marginal": marginal,
                "all": habitats,
            }
        except Exception as exc:
            logger.warning(f"IUCN 解析栖息地数据失败: {exc}")
            return None

    def _fetch_threats(self, name: str) -> Optional[Dict[str, Any]]:
        """通过 /threats/species/name/{name} 端点获取威胁。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/threats/species/name/{name}"
        data = self._get(url)
        if data is None:
            return None

        try:
            raw_threats = data.get("result", [])
            threats = []
            for t in raw_threats:
                threats.append({
                    "code": t.get("code", ""),
                    "title": t.get("title", ""),
                    "timing": t.get("timing", ""),
                    "scope": t.get("scope", ""),
                    "severity": t.get("severity", ""),
                    "score": t.get("score", ""),
                })
            return {"threats": threats}
        except Exception as exc:
            logger.warning(f"IUCN 解析威胁数据失败: {exc}")
            return None

    def _get(self, url: str) -> Optional[Dict[str, Any]]:
        """发送带认证的 GET 请求 (含速率限制 + 优雅降级)。"""
        if not _HTTPX_AVAILABLE:
            logger.debug("httpx 不可用, 跳过 HTTP 请求")
            return None
        self._limiter.wait()
        headers = {
            "accept": "application/json",
            "Authorization": self._api_key,
        }
        try:
            response = httpx.get(url, headers=headers, timeout=30.0)
            if response.status_code == 404:
                logger.debug(f"IUCN 404: {url}")
                return None
            if response.status_code == 429:
                logger.warning(f"IUCN 速率限制触发 (429), 等待 5s 后重试...")
                time.sleep(5)
                response = httpx.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(f"IUCN HTTP {exc.response.status_code}: {url}")
            return None
        except httpx.RequestError as exc:
            logger.warning(f"IUCN 请求失败: {exc}")
            return None
        except Exception as exc:
            logger.warning(f"IUCN 未知错误: {exc}")
            return None

    def health(self) -> Dict[str, Any]:
        """健康检查。"""
        return {
            "api": "IUCN Red List v4",
            "base_url": self.BASE,
            "api_key_configured": bool(self._api_key),
            "httpx_available": _HTTPX_AVAILABLE,
        }


# ═══════════════════════════════════════════════════════════════════
# CITES Species+ Checklist API 客户端
# ═══════════════════════════════════════════════════════════════════

class CITESClient:
    """CITES Species+ / Checklist API 客户端。

    API 文档: https://api.speciesplus.net/documentation
    需要 API token (注册免费): https://api.speciesplus.net/
    """

    BASE = "https://api.speciesplus.net/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl: int = 86400,
        rate_limit: float = 2.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("CITES_API_KEY", "")
        self._cache = CacheStore(ttl_seconds=cache_ttl)
        self._limiter = RateLimiter(calls_per_second=rate_limit)
        if not self._api_key:
            logger.warning(
                "CITES_API_KEY 未设置 — CITES API 调用将不可用。"
                " 请设置环境变量 CITES_API_KEY 或传入 api_key 参数。"
            )

    # ── 公共 API ──

    def get_listing(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取 CITES 附录列名信息。

        Returns:
            {
                "appendix": "II",          # I / II / III
                "appendix_name": "附录Ⅱ",
                "listed_since": "1975-07-01",
                "annotation": "...",       # 注释/限制说明
                "url": "https://speciesplus.net/..."
            }
            失败返回 None。
        """
        ckey = _cache_key("cites_list", scientific_name)
        cached = self._cache.get(ckey)
        if cached is not None:
            return cached

        taxon_id = self._resolve_taxon_id(scientific_name)
        if taxon_id is None:
            return None

        result = self._fetch_listing(taxon_id)
        if result is not None:
            self._cache.set(ckey, result)
        return result

    def get_distribution(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取 CITES 记录的物种分布信息。

        Returns:
            {"countries": [...], "regions": [...]}
        """
        ckey = _cache_key("cites_dist", scientific_name)
        cached = self._cache.get(ckey)
        if cached is not None:
            return cached

        taxon_id = self._resolve_taxon_id(scientific_name)
        if taxon_id is None:
            return None

        result = self._fetch_distribution(taxon_id)
        if result is not None:
            self._cache.set(ckey, result)
        return result

    def get_full_profile(self, scientific_name: str) -> Optional[Dict[str, Any]]:
        """获取 CITES 完整信息 (列名 + 分布)。"""
        listing = self.get_listing(scientific_name)
        distribution = self.get_distribution(scientific_name)

        if listing is None and distribution is None:
            return None

        return {
            "scientific_name": scientific_name,
            "source": "cites",
            "listing": listing or {},
            "distribution": distribution or {},
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # ── 内部方法 ──

    def _resolve_taxon_id(self, name: str) -> Optional[int]:
        """通过名称解析 CITES taxon_concept_id。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/taxon_concepts?name={name}"
        data = self._get(url)
        if data is None:
            return None

        try:
            concepts = data.get("taxon_concepts", [])
            if not concepts:
                logger.info(f"CITES: 未找到 '{name}' 的分类概念")
                return None
            # 取第一个 (通常最匹配)
            return concepts[0]["id"]
        except Exception as exc:
            logger.warning(f"CITES 解析分类 ID 失败: {exc}")
            return None

    def _fetch_listing(self, taxon_id: int) -> Optional[Dict[str, Any]]:
        """通过 taxon_concept_id 获取 CITES 附录列名。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/taxon_concepts/{taxon_id}/listings"
        data = self._get(url)
        if data is None:
            return None

        try:
            listings = data.get("cites_listings", [])
            if not listings:
                return None

            # 取当前有效的列名
            current = None
            for lst in listings:
                if lst.get("is_current", False):
                    current = lst
                    break
            if current is None:
                current = listings[0]

            appendix_map = {"I": "附录Ⅰ", "II": "附录Ⅱ", "III": "附录Ⅲ"}
            appendix = current.get("appendix", "")
            return {
                "appendix": appendix,
                "appendix_name": appendix_map.get(appendix, appendix),
                "listed_since": current.get("effective_at", ""),
                "annotation": current.get("annotation", ""),
            }
        except Exception as exc:
            logger.warning(f"CITES 解析列名数据失败: {exc}")
            return None

    def _fetch_distribution(self, taxon_id: int) -> Optional[Dict[str, Any]]:
        """获取 CITES 分布数据。"""
        if not self._api_key:
            return None
        url = f"{self.BASE}/taxon_concepts/{taxon_id}/distributions"
        data = self._get(url)
        if data is None:
            return None

        try:
            distributions = data.get("distributions", [])
            countries = []
            regions = []
            for d in distributions:
                country = d.get("country", d.get("name", ""))
                if country:
                    countries.append(country)
                region = d.get("region", "")
                if region:
                    regions.append(region)
            return {
                "countries": list(set(countries)),
                "regions": list(set(regions)),
                "raw": distributions,
            }
        except Exception as exc:
            logger.warning(f"CITES 解析分布数据失败: {exc}")
            return None

    def _get(self, url: str) -> Optional[Dict[str, Any]]:
        """发送带认证的 GET 请求。"""
        if not _HTTPX_AVAILABLE:
            logger.debug("httpx 不可用, 跳过 HTTP 请求")
            return None
        self._limiter.wait()
        headers = {
            "accept": "application/json",
            "X-Authentication-Token": self._api_key,
        }
        try:
            response = httpx.get(url, headers=headers, timeout=30.0)
            if response.status_code == 404:
                logger.debug(f"CITES 404: {url}")
                return None
            if response.status_code == 429:
                logger.warning(f"CITES 速率限制触发 (429), 等待 5s 后重试...")
                time.sleep(5)
                response = httpx.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(f"CITES HTTP {exc.response.status_code}: {url}")
            return None
        except httpx.RequestError as exc:
            logger.warning(f"CITES 请求失败: {exc}")
            return None
        except Exception as exc:
            logger.warning(f"CITES 未知错误: {exc}")
            return None

    def health(self) -> Dict[str, Any]:
        """健康检查。"""
        return {
            "api": "CITES Species+ v1",
            "base_url": self.BASE,
            "api_key_configured": bool(self._api_key),
            "httpx_available": _HTTPX_AVAILABLE,
        }


# ── 便捷工厂 ──

def get_iucn_client(api_key: Optional[str] = None) -> IUCNClient:
    """工厂: 创建 IUCN 客户端实例。"""
    return IUCNClient(api_key=api_key)


def get_cites_client(api_key: Optional[str] = None) -> CITESClient:
    """工厂: 创建 CITES 客户端实例。"""
    return CITESClient(api_key=api_key)
