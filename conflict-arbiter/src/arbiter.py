"""ConflictArbiter — 冲突仲裁核心引擎 (火 🟥)

多源保护推荐冲突检测 + 可信度加权仲裁 + 熔断逻辑。

区域规则:
  - region="china": 中国保护等级为权威，IUCN/CITES 仅参考
    中国来源权重: chinese_red_list=100, provincial_protection=90
    国际来源权重: iucn=40, cites=40
    裁决: 以最高优先级中国来源为准

典型场景:
  - 中国物种: IUCN "极危(CR)" vs 中国红色名录 "濒危(EN)"
    → 冲突等级 1, 裁决以中国为准
  - 文献A "2010年长江中游种群下降30%" vs 文献B "2025年长江下游种群稳定"
    → 时空不一致, 不构成冲突 (不同年不同地区)
  - 文献A "2010年长江中游种群下降30%" vs 文献B "2010年长江中游种群稳定"
    → 时空一致, 三级冲突, 熔断
  - 省级保护 vs 国家保护 vs IUCN → 跨层级矛盾检测, 中国分类为准
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── 保护等级标准化映射 ──
# 将所有来源的保护等级映射到统一数值轴 [0-100], 0=无危, 100=灭绝

IUCN_MAP = {
    "灭绝(EX)": 100, "extinct": 100, "EX": 100,
    "野外灭绝(EW)": 95, "extinct in the wild": 95, "EW": 95,
    "极危(CR)": 85, "critically endangered": 85, "CR": 85,
    "濒危(EN)": 70, "endangered": 70, "EN": 70,
    "易危(VU)": 55, "vulnerable": 55, "VU": 55,
    "近危(NT)": 35, "near threatened": 35, "NT": 35,
    "无危(LC)": 10, "least concern": 10, "LC": 10,
    "数据缺乏(DD)": 5, "data deficient": 5, "DD": 5,
    "未评估(NE)": 0, "not evaluated": 0, "NE": 0,
}

CHINESE_RED_LIST_MAP = {
    "国家一级": 90, "一级": 90,
    "国家二级": 70, "二级": 70,
    "省级重点": 50,
    "三有保护": 30,
    "无": 0,
}

CITES_MAP = {
    "附录Ⅰ": 95, "Appendix Ⅰ": 95, "I": 95,
    "附录Ⅱ": 75, "Appendix Ⅱ": 75, "II": 75,
    "附录Ⅲ": 50, "Appendix Ⅲ": 50, "III": 50,
}


class ConflictArbiter:
    """冲突仲裁引擎 — 多源保护推荐一致性检测 + 加权仲裁 + 熔断。"""

    # 默认数据源权重
    DEFAULT_SOURCE_WEIGHTS: Dict[str, int] = {
        "iucn": 90,
        "cites": 90,
        "chinese_red_list": 80,
        "provincial_protection": 70,
        "peer_reviewed_literature": 75,
        "survey_report": 60,
        "news_media": 30,
        "citizen_science": 20,
    }

    # 熔断阈值
    CIRCUIT_BREAKER = {
        "max_conflict_level": 3,
        "min_sources_for_consensus": 3,
    }

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self._source_weights = dict(self.DEFAULT_SOURCE_WEIGHTS)
        self._cb = dict(self.CIRCUIT_BREAKER)
        if config_path and config_path.is_file():
            self._load_config(config_path)

    def _load_config(self, path: Path) -> None:
        """从 agent.yaml 加载仲裁配置。"""
        try:
            import yaml
            cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            arb = cfg.get("arbiter", {})
            if "source_weights" in arb:
                self._source_weights.update(arb["source_weights"])
            if "circuit_breaker" in arb:
                self._cb.update(arb["circuit_breaker"])
        except Exception as exc:
            logger.warning(f"Config load failed: {exc}")

    # ── 公共 API ──

    def detect_conflicts(
        self,
        species_name: str,
        sources: List[Dict[str, Any]],
        region: str = "china",
    ) -> Dict[str, Any]:
        """检测多源保护推荐冲突。

        Args:
            species_name: 物种名 (中文/学名)
            sources: 数据源列表, 每项 {source, protection_level, status, iucn, ...}
            region: 区域策略. "china"=中国保护等级为权威, "global"=常规加权

        Returns:
            {species_name, conflict_level, consensus, sources_analyzed, verdict, details}
        """
        if not sources:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": "无数据", "score": None},
                "sources_analyzed": 0,
                "verdict": "无数据来源, 无法仲裁",
                "details": [],
            }

        # Step 1: 标准化所有来源的保护等级到统一数值轴
        normalized: List[Dict[str, Any]] = []
        for s in sources:
            norm = self._normalize_source(s)
            if norm is not None:
                normalized.append(norm)

        if len(normalized) < 2:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": "仅单源", "score": normalized[0]["score"] if normalized else None},
                "sources_analyzed": len(normalized),
                "verdict": "仅单一数据源, 无需仲裁",
                "details": normalized,
            }

        # Step 1.5: 区域权重覆盖 — 中国物种以中国保护等级为准
        has_chinese_source = any(
            n["source"] in ("chinese_red_list", "provincial_protection")
            for n in normalized
        )
        china_authoritative = (region == "china" and has_chinese_source)

        if china_authoritative:
            for n in normalized:
                src = n["source"]
                if src == "chinese_red_list":
                    n["weight"] = 100
                    n["authority"] = "primary"
                elif src == "provincial_protection":
                    n["weight"] = 90
                    n["authority"] = "secondary"
                elif src in ("iucn", "cites"):
                    n["weight"] = 40
                    n["authority"] = "reference"
                else:
                    n["weight"] = self._source_weights.get(src, 50)
                    n["authority"] = "reference"
                n["weighted_score"] = n["score"] * n["weight"] / 100

        # Step 2: 计算冲突等级
        scores = [n["score"] for n in normalized]
        weights = [n["weight"] for n in normalized]
        conflict_level, max_gap = self._compute_conflict_level(scores)

        # Step 3: 加权仲裁
        consensus = self._weighted_arbitration(scores, weights, conflict_level)

        # Step 3.5: 中国物种 — 以中国来源数值覆盖仲裁结果
        if china_authoritative:
            chinese_primary = None
            for src_priority in ("chinese_red_list", "provincial_protection"):
                chinese_primary = next(
                    (n for n in normalized if n["source"] == src_priority), None
                )
                if chinese_primary:
                    break
            if chinese_primary:
                authoritative_score = chinese_primary["score"]
                authoritative_level = self._score_to_level(authoritative_score)
                consensus["score"] = authoritative_score
                consensus["mapped_level"] = authoritative_level
                consensus["authority"] = "chinese_classification"
                consensus["authoritative_source"] = chinese_primary["source"]
                consensus["level"] = (
                    "中国分类为准"
                    if conflict_level <= 1
                    else f"⚠️ 冲突等级 {conflict_level}，但按中国分类执行"
                )

        # Step 4: 熔断判断
        verdict = self._circuit_judgment(
            conflict_level, consensus, len(normalized), china_authoritative
        )

        return {
            "species_name": species_name,
            "conflict_level": conflict_level,
            "max_gap": max_gap,
            "consensus": consensus,
            "sources_analyzed": len(normalized),
            "region_policy": region if china_authoritative else "global",
            "verdict": verdict,
            "details": normalized,
        }

    def arbitrate(
        self,
        species_name: str,
        claims: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """通用声明仲裁 — 对任意带权声明做一致性检测。

        时空一致性规则: 只有同一时间+同一地区的声明才构成冲突。
        不同年份/不同地区的声明 -> "不同时空数据，不构成冲突"。

        Args:
            species_name: 物种名
            claims: [{claim, source, weight, confidence, value,
                       time_period: {start, end}, region}]

        Returns:
            {conflict_level, consensus, verdict, details, spatiotemporal}
        """
        if not claims:
            return {"conflict_level": 0, "consensus": None, "verdict": "无声明"}

        # Step 1: 检查声明是否时空可比
        comparable, st_result = self._check_spatiotemporal_comparability(claims)

        if not comparable:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": st_result["reason"],
                              "score": None},
                "claims_analyzed": len(claims),
                "spatiotemporal": st_result,
                "verdict": (
                    f"🟢 不同时空数据，不构成冲突。"
                    f" {st_result['detail']}"
                ),
                "details": claims,
            }

        # Step 2: 时空可比 → 正常仲裁
        values = [c.get("value", 0) for c in claims]
        weights = [c.get("weight", 50) for c in claims]
        conflict_level, _ = self._compute_conflict_level(values)
        consensus = self._weighted_arbitration(values, weights, conflict_level)

        return {
            "species_name": species_name,
            "conflict_level": conflict_level,
            "consensus": consensus,
            "claims_analyzed": len(claims),
            "spatiotemporal": st_result,
            "verdict": self._circuit_judgment(conflict_level, consensus, len(claims)),
            "details": claims,
        }

    @staticmethod
    def _check_spatiotemporal_comparability(
        claims: List[Dict[str, Any]],
    ) -> tuple[bool, dict]:
        """检查声明集是否时空一致才比较。

        返回:
            (True, {"status": "comparable"|"info_incomplete",
                     "time_periods": [...], "regions": [...]})
            或
            (False, {"status": "incomparable", "reason": "...", "detail": "..."})
        """
        time_periods = [c.get("time_period") for c in claims]
        regions = [c.get("region") for c in claims]

        all_have_time = all(t is not None for t in time_periods)
        all_have_region = all(r is not None for r in regions)

        if all_have_time and all_have_region:
            # 检查时间是否重叠
            time_overlap = True
            for i in range(len(claims)):
                for j in range(i + 1, len(claims)):
                    if not ConflictArbiter._times_overlap(
                        time_periods[i], time_periods[j]
                    ):
                        time_overlap = False
                        break
                if not time_overlap:
                    break

            # 检查区域是否相同
            same_region = len(set(regions)) == 1

            if not time_overlap and not same_region:
                return False, {
                    "status": "incomparable",
                    "reason": "时空均不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"时间: {time_periods}, 地区: {regions}",
                }
            if not time_overlap:
                return False, {
                    "status": "incomparable",
                    "reason": "时间不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"时间不重叠: {time_periods}",
                }
            if not same_region:
                return False, {
                    "status": "incomparable",
                    "reason": "地区不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"地区不同: {regions}",
                }
            return True, {
                "status": "comparable",
                "time_periods": time_periods,
                "regions": regions,
            }

        # 部分声明缺时空信息 → 仍比较，但标记信息不全
        return True, {
            "status": "info_incomplete",
            "time_periods": time_periods,
            "regions": regions,
        }

    @staticmethod
    def _times_overlap(t1: dict, t2: dict) -> bool:
        """检查两个时间段是否重叠。{start, end} 年份。"""
        s1 = t1.get("start", 0)
        e1 = t1.get("end", 9999)
        s2 = t2.get("start", 0)
        e2 = t2.get("end", 9999)
        return max(s1, s2) <= min(e1, e2)

    # ── 内部方法 ──

    def _normalize_source(self, source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """将单个数据源的保护等级标准化到数值轴 [0-100]。"""
        src_name = source.get("source", "unknown")
        weight = self._source_weights.get(src_name, 50)

        # 尝试各映射表
        score = None

        # IUCN 状态
        iucn_val = source.get("iucn", "")
        if iucn_val:
            for key, val in IUCN_MAP.items():
                if key.lower() in iucn_val.lower():
                    score = val
                    break

        # 中国保护等级
        if score is None:
            prot = source.get("protection_level", "")
            for key, val in CHINESE_RED_LIST_MAP.items():
                if key in prot:
                    score = val
                    break

        # CITES
        if score is None:
            cites = source.get("cites", "")
            for key, val in CITES_MAP.items():
                if key in cites:
                    score = val
                    break

        # 数值直给
        if score is None:
            score = source.get("score", source.get("value", None))

        if score is None:
            return None

        return {
            "source": src_name,
            "original": source.get("protection_level", source.get("iucn", str(source))),
            "score": score,
            "weight": weight,
            "weighted_score": score * weight / 100,
        }

    @staticmethod
    def _compute_conflict_level(scores: List[float]) -> Tuple[int, float]:
        """计算冲突等级 [0-3] 和最大分差。

        0 = 完全一致 (max_gap ≤ 5)
        1 = 轻微差异 (max_gap ≤ 15)
        2 = 显著差异 (max_gap ≤ 35)
        3 = 严重对立 (max_gap > 35)
        """
        if not scores:
            return 0, 0.0
        max_gap = max(scores) - min(scores)
        if max_gap <= 5:
            return 0, max_gap
        elif max_gap <= 15:
            return 1, max_gap
        elif max_gap <= 35:
            return 2, max_gap
        else:
            return 3, max_gap

    def _weighted_arbitration(
        self, scores: List[float], weights: List[float], conflict_level: int
    ) -> Dict[str, Any]:
        """加权仲裁 — 计算加权均值和可信区间。"""
        total_weight = sum(weights)
        if total_weight == 0:
            return {"agreed": False, "level": "无法计算", "score": None, "ci": None}

        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / total_weight

        # 置信区间: 按权重计算标准差
        variance = sum(w * (s - weighted_avg) ** 2 for s, w in zip(scores, weights)) / total_weight
        std_dev = variance ** 0.5

        # 判定
        if conflict_level == 0:
            agreed = True
            level = "完全一致"
        elif conflict_level == 1:
            agreed = True
            level = "基本一致"
        elif conflict_level == 2:
            agreed = False
            level = "显著差异 — 加权仲裁"
        else:
            agreed = False
            level = "严重对立 — 触发熔断"

        # 数值映射回文字等级
        mapped_level = self._score_to_level(weighted_avg)

        return {
            "agreed": agreed,
            "level": level,
            "score": round(weighted_avg, 1),
            "mapped_level": mapped_level,
            "std_dev": round(std_dev, 1),
            "ci_95": (
                round(max(0, weighted_avg - 1.96 * std_dev), 1),
                round(min(100, weighted_avg + 1.96 * std_dev), 1),
            ),
        }

    def _circuit_judgment(
        self, conflict_level: int, consensus: Dict[str, Any],
        n_sources: int, china_authoritative: bool = False,
    ) -> str:
        """熔断判断 + 生成裁决文本。"""
        max_level = self._cb.get("max_conflict_level", 3)
        min_consensus = self._cb.get("min_sources_for_consensus", 3)

        # 中国物种: 以中国保护等级为准，冲突仅做参考提示
        if china_authoritative:
            auth_src = consensus.get("authoritative_source", "chinese_red_list")
            mapped = consensus.get("mapped_level", "N/A")
            score = consensus.get("score", "N/A")
            if conflict_level <= 1:
                return (
                    f"🟢 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" 国际来源与之一致。"
                )
            elif conflict_level == 2:
                return (
                    f"🟡 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" ⚠️ 国际来源有显著差异 (冲突等级 {conflict_level}/3)，仅供参考。"
                )
            else:
                return (
                    f"🟠 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" 🔴 国际来源严重对立 (冲突等级 {conflict_level}/3)，建议人工复核差异原因。"
                )

        # 常规裁决逻辑 (region != "china" 或无中国来源)
        if conflict_level >= max_level:
            return (
                f"🔴 熔断! 冲突等级 {conflict_level}/{max_level}, "
                f"超过熔断阈值。建议人工复核。"
            )
        if n_sources < min_consensus:
            return (
                f"🟡 数据源不足 ({n_sources}/{min_consensus}), "
                f"仲裁结果仅供参考。共识: {consensus.get('mapped_level', 'N/A')}"
            )
        if consensus.get("agreed"):
            return (
                f"🟢 仲裁通过。共识: {consensus.get('mapped_level', 'N/A')} "
                f"(得分 {consensus.get('score', 'N/A')}/100)"
            )
        return (
            f"🟠 显著差异, 加权仲裁结果: {consensus.get('mapped_level', 'N/A')} "
            f"(得分 {consensus.get('score', 'N/A')}/100)。建议交叉验证。"
        )

    @staticmethod
    def _score_to_level(score: float) -> str:
        """将数值分数映射回保护等级文字。"""
        if score >= 95:
            return "灭绝/野外灭绝"
        elif score >= 80:
            return "极危"
        elif score >= 65:
            return "濒危"
        elif score >= 50:
            return "易危"
        elif score >= 30:
            return "近危"
        elif score >= 10:
            return "无危"
        else:
            return "未评估/数据缺乏"

    def health(self) -> Dict[str, Any]:
        return {
            "project": "conflict-arbiter",
            "status": "HEALTHY",
            "source_weights_loaded": len(self._source_weights),
            "circuit_breaker": self._cb,
        }

    def info(self) -> Dict[str, Any]:
        return {
            "project": "conflict-arbiter",
            "version": "1.0.0",
            "role": "V4_ArbitrateVertex (C-Conflict)",
            "element": "火 🟥",
            "capabilities": [
                "protection_level_conflict_detection",
                "weighted_arbitration",
                "circuit_breaker",
                "multi_source_normalization",
                "cross_project_consensus",
                "live_api_integration",
                "batch_arbitration",
                "local_caching",
            ],
        }

    # ── 实时 API 集成 ──

    @classmethod
    def from_live_data(
        cls,
        species_name: str,
        region: str = "china",
        config_path: Optional[Path] = None,
        iucn_api_key: Optional[str] = None,
        cites_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """从 IUCN/CITES 实时 API 获取数据并执行仲裁。

        本地数据优先 (config/arbitration_rules.yaml), API 数据作为补充。
        当 API 不可用时优雅降级。

        Args:
            species_name: 物种学名, 如 "Coilia nasus"
            region: 区域策略 ("china" | "global")
            config_path: arbiter 配置文件路径
            iucn_api_key: IUCN API key (也可通过环境变量 IUCN_API_KEY 设置)
            cites_api_key: CITES API key (也可通过环境变量 CITES_API_KEY 设置)

        Returns:
            完整的仲裁结果 dict, 含 api_sources 字段。
        """
        arbiter = cls(config_path=config_path)

        # 1. 尝试加载本地预置数据
        local_sources: List[Dict[str, Any]] = []
        local_data = cls._load_local_species_data(species_name)
        if local_data:
            local_sources.extend(local_data)
            logger.info(f"加载本地数据: {species_name} ({len(local_sources)} 条)")

        # 2. 尝试调用实时 API
        api_sources: List[Dict[str, Any]] = []
        api_errors: List[str] = []

        # IUCN
        try:
            from api_clients import IUCNClient
            iucn = IUCNClient(api_key=iucn_api_key)
            iucn_profile = iucn.get_full_profile(species_name)
            if iucn_profile and iucn_profile.get("assessment"):
                cat = iucn_profile["assessment"].get("category", "")
                cat_name = iucn_profile["assessment"].get("category_name", cat)
                trend = iucn_profile["assessment"].get("population_trend", "")
                api_sources.append({
                    "source": "iucn",
                    "iucn": cat or cat_name,
                    "status": cat or cat_name,
                    "population_trend": trend,
                    "raw": iucn_profile,
                    "origin": "api",
                })
                logger.info(f"IUCN API: {species_name} → {cat} ({cat_name})")
            else:
                api_errors.append("IUCN: 未找到评估数据")
        except Exception as exc:
            api_errors.append(f"IUCN: {exc}")

        # CITES
        try:
            from api_clients import CITESClient
            cites = CITESClient(api_key=cites_api_key)
            cites_profile = cites.get_full_profile(species_name)
            if cites_profile and cites_profile.get("listing"):
                listing = cites_profile["listing"]
                appendix = listing.get("appendix", "")
                api_sources.append({
                    "source": "cites",
                    "cites": appendix,
                    "status": listing.get("appendix_name", appendix),
                    "listed_since": listing.get("listed_since", ""),
                    "raw": cites_profile,
                    "origin": "api",
                })
                logger.info(f"CITES API: {species_name} → 附录{appendix}")
            else:
                api_errors.append("CITES: 未找到列名数据")
        except Exception as exc:
            api_errors.append(f"CITES: {exc}")

        # 3. 合并来源: 本地优先, API 补充 (去重同源)
        seen_sources = {s.get("source") for s in local_sources}
        combined = list(local_sources)
        for api_src in api_sources:
            if api_src.get("source") not in seen_sources:
                combined.append(api_src)
                seen_sources.add(api_src.get("source"))

        # 4. 执行仲裁
        result = arbiter.detect_conflicts(
            species_name=species_name,
            sources=combined if combined else api_sources,
            region=region,
        )

        # 5. 附加 API 元信息
        result["api_sources"] = {
            "iucn_available": any(s["source"] == "iucn" for s in api_sources),
            "cites_available": any(s["source"] == "cites" for s in api_sources),
            "api_errors": api_errors if api_errors else None,
            "local_data_used": len(local_sources) > 0,
        }
        result["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return result

    def batch_arbitrate(
        self,
        species_list: List[str],
        region: str = "china",
        use_api: bool = False,
        iucn_api_key: Optional[str] = None,
        cites_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """批量仲裁多个物种。

        Args:
            species_list: 物种学名列表
            region: 区域策略
            use_api: 是否尝试实时 API (建议批处理时关闭避免速率限制)
            iucn_api_key: IUCN API key
            cites_api_key: CITES API key

        Returns:
            {
                "total": 3,
                "results": [...],
                "summary": {"conflict_0": 1, "conflict_1": 1, ...},
                "batch_fetched_at": "..."
            }
        """
        results = []
        summary: Dict[str, int] = {}

        for name in species_list:
            if use_api:
                result = self.from_live_data(
                    species_name=name,
                    region=region,
                    iucn_api_key=iucn_api_key,
                    cites_api_key=cites_api_key,
                )
            else:
                # 纯本地数据模式
                local_sources = self._load_local_species_data(name)
                result = self.detect_conflicts(
                    species_name=name,
                    sources=local_sources,
                    region=region,
                )

            results.append(result)
            cl = f"conflict_{result.get('conflict_level', '?')}"
            summary[cl] = summary.get(cl, 0) + 1

        return {
            "total": len(species_list),
            "results": results,
            "summary": summary,
            "batch_fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # ── 本地缓存层 ──

    _species_cache: Dict[str, Dict[str, Any]] = {}
    _cache_file: Optional[Path] = None

    @classmethod
    def _load_local_species_data(cls, species_name: str) -> List[Dict[str, Any]]:
        """从本地配置文件加载物种预置数据。

        查找 config/arbitration_rules.yaml 中的 species_data 节,
        或使用内置的中文物种数据。
        """
        # 1. 内存缓存
        if species_name in ConflictArbiter._species_cache:
            return list(ConflictArbiter._species_cache[species_name].get("sources", []))

        # 2. 尝试从 YAML 配置文件加载
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "arbitration_rules.yaml"
        if cfg_path.is_file():
            try:
                import yaml
                cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
                species_data = cfg.get("species_data", {})
                entry = species_data.get(species_name.lower())
                if entry:
                    sources = entry.get("sources", [])
                    ConflictArbiter._species_cache[species_name] = {"sources": sources}
                    return list(sources)
            except Exception as exc:
                logger.debug(f"加载本地物种数据失败: {exc}")

        # 3. 内置硬编码数据 (常见中国保护物种快速参考)
        builtin = cls._get_builtin_species_data(species_name)
        if builtin:
            ConflictArbiter._species_cache[species_name] = {"sources": builtin}
            return list(builtin)

        return []

    @classmethod
    def _get_builtin_species_data(cls, name: str) -> List[Dict[str, Any]]:
        """内置常见鱼类保护数据 (快速参考, 避免 API 调用)。"""
        key = name.lower().strip()
        data: Dict[str, List[Dict[str, Any]]] = {
            "coilia nasus": [
                {"source": "chinese_red_list", "protection_level": "二级",
                 "status": "EN", "note": "长江流域重点保护"},
                {"source": "survey_report", "protection_level": "重点保护",
                 "status": "VU", "note": "2020年长江禁渔后种群恢复中"},
                {"source": "iucn", "iucn": "EN", "status": "濒危",
                 "note": "IUCN评估为濒危(EN)"},
            ],
            "anguilla japonica": [
                {"source": "chinese_red_list", "protection_level": "二级",
                 "status": "EN", "note": "国家重点保护水生野生动物"},
                {"source": "iucn", "iucn": "EN", "status": "濒危",
                 "note": "IUCN评估为濒危(EN)"},
                {"source": "cites", "cites": "附录Ⅱ", "status": "附录Ⅱ",
                 "note": "CITES附录Ⅱ管控国际贸易"},
            ],
            "acipenser sinensis": [
                {"source": "chinese_red_list", "protection_level": "一级",
                 "status": "CR", "note": "国家一级保护动物"},
                {"source": "iucn", "iucn": "CR", "status": "极危",
                 "note": "IUCN评估为极危(CR)"},
                {"source": "cites", "cites": "附录Ⅱ", "status": "附录Ⅱ",
                 "note": "CITES附录Ⅱ管控"},
            ],
            "myxocyprinus asiaticus": [
                {"source": "chinese_red_list", "protection_level": "二级",
                 "status": "VU", "note": "国家二级保护动物"},
                {"source": "iucn", "iucn": "VU", "status": "易危",
                 "note": "IUCN评估为易危(VU)"},
            ],
            "pecten albicans": [
                {"source": "chinese_red_list", "protection_level": "二级",
                 "status": "EN", "note": "国家重点保护水生野生动物"},
                {"source": "iucn", "iucn": "EN", "status": "濒危",
                 "note": "IUCN评估为濒危(EN)"},
            ],
        }
        return data.get(key, [])

    @classmethod
    def load_cache(cls, cache_path: Optional[Path] = None) -> int:
        """从 JSON 缓存文件加载仲裁结果。返回加载的记录数。"""
        if cache_path is None:
            cache_path = cls._cache_file or (
                Path.home() / ".conflict_arbiter_cache" / "arbitration_results.json"
            )
        if not cache_path.is_file():
            return 0
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cls._species_cache.update(data)
                return len(data)
            return 0
        except Exception as exc:
            logger.warning(f"缓存加载失败: {exc}")
            return 0

    @classmethod
    def save_cache(cls, cache_path: Optional[Path] = None) -> int:
        """将内存中的仲裁结果保存为 JSON 缓存文件。返回保存的记录数。"""
        if cache_path is None:
            cache_path = cls._cache_file or (
                Path.home() / ".conflict_arbiter_cache" / "arbitration_results.json"
            )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cls._cache_file = cache_path
        try:
            cache_path.write_text(
                json.dumps(cls._species_cache, ensure_ascii=False, default=str, indent=2),
                encoding="utf-8",
            )
            return len(cls._species_cache)
        except Exception as exc:
            logger.warning(f"缓存保存失败: {exc}")
            return -1


# ── 便捷工厂 ──

def get_arbiter(config_path: Optional[Path] = None) -> ConflictArbiter:
    return ConflictArbiter(config_path=config_path)
