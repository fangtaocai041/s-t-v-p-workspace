"""Tests for src/api_clients.py — IUCN/CITES API 客户端测试。

测试策略:
  - 离线模式 (无 API key): 验证客户端不崩溃, 优雅返回 None
  - 缓存命中/过期逻辑
  - 速率限制器行为
  - from_live_data 集成 (arbiter 端)
  - batch_arbitrate 集成
"""

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 确保 src/ 在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# ═══════════════════════════════════════════════════════════════════
# CacheStore 测试
# ═══════════════════════════════════════════════════════════════════

class TestCacheStore:
    def test_get_missing_key(self, tmp_path):
        from src.api_clients import CacheStore
        store = CacheStore(ttl_seconds=3600)
        store._dir = tmp_path  # 覆盖缓存目录
        assert store.get("nonexistent_key") is None

    def test_set_and_get(self, tmp_path):
        from src.api_clients import CacheStore
        store = CacheStore(ttl_seconds=3600)
        store._dir = tmp_path
        payload = {"category": "EN", "name": "Endangered"}
        store.set("test_key", payload)
        result = store.get("test_key")
        assert result == payload

    def test_cache_expiry(self, tmp_path):
        from src.api_clients import CacheStore
        store = CacheStore(ttl_seconds=0)  # 立即过期
        store._dir = tmp_path
        store.set("expire_key", {"data": 1})
        time.sleep(0.01)
        assert store.get("expire_key") is None

    def test_cache_override(self, tmp_path):
        from src.api_clients import CacheStore
        store = CacheStore(ttl_seconds=3600)
        store._dir = tmp_path
        store.set("key", {"v": 1})
        store.set("key", {"v": 2})
        assert store.get("key") == {"v": 2}

    def test_clear(self, tmp_path):
        from src.api_clients import CacheStore
        store = CacheStore(ttl_seconds=3600)
        store._dir = tmp_path
        store.set("a", {"x": 1})
        store.set("b", {"y": 2})
        assert store.clear() == 2
        assert store.get("a") is None


# ═══════════════════════════════════════════════════════════════════
# RateLimiter 测试
# ═══════════════════════════════════════════════════════════════════

class TestRateLimiter:
    def test_basic_wait(self):
        from src.api_clients import RateLimiter
        rl = RateLimiter(calls_per_second=100)  # 高频率, 基本不等待
        start = time.time()
        rl.wait()
        rl.wait()
        elapsed = time.time() - start
        assert elapsed < 0.5  # 应在极短时间内完成

    def test_slow_rate(self):
        from src.api_clients import RateLimiter
        rl = RateLimiter(calls_per_second=2)
        start = time.time()
        rl.wait()
        rl.wait()
        elapsed = time.time() - start
        # 至少等待 0.5s (两次调用间隔)
        assert elapsed >= 0.4


# ═══════════════════════════════════════════════════════════════════
# IUCNClient 离线测试 (无 API key)
# ═══════════════════════════════════════════════════════════════════

class TestIUCNClientOffline:
    """无 API key 时 IUCNClient 应优雅降级, 返回 None 而不崩溃。"""

    def test_init_no_key(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="")
        assert client._api_key == ""
        assert client.health()["api_key_configured"] is False

    def test_get_assessment_no_key(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="")
        result = client.get_assessment("Coilia nasus")
        assert result is None

    def test_get_habitat_no_key(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="")
        result = client.get_habitat("Coilia nasus")
        assert result is None

    def test_get_threats_no_key(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="")
        result = client.get_threats("Coilia nasus")
        assert result is None

    def test_get_full_profile_no_key(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="")
        result = client.get_full_profile("Coilia nasus")
        assert result is None

    def test_health(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="test_key")
        h = client.health()
        assert h["api"] == "IUCN Red List v4"
        assert h["api_key_configured"] is True
        assert "httpx_available" in h

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("IUCN_API_KEY", "env_test_key")
        from src.api_clients import IUCNClient
        client = IUCNClient()
        assert client._api_key == "env_test_key"

    def test_cache_hit_offline(self, tmp_path, monkeypatch):
        """缓存命中时, 即使无 API key 也应返回数据。"""
        monkeypatch.setenv("IUCN_API_KEY", "")
        from src.api_clients import IUCNClient, CacheStore
        client = IUCNClient(api_key="")
        # 预填充缓存 — 注意 key 需与 _cache_key 输出一致 (含 .json 后缀)
        store = CacheStore(ttl_seconds=86400)
        store._dir = tmp_path
        store.set("iucn_assess_coilia_nasus.json", {"category": "EN", "category_name": "濒危"})
        client._cache = store
        result = client.get_assessment("Coilia nasus")
        assert result is not None
        assert result["category"] == "EN"


# ═══════════════════════════════════════════════════════════════════
# CITESClient 离线测试 (无 API key)
# ═══════════════════════════════════════════════════════════════════

class TestCITESClientOffline:
    """无 API key 时 CITESClient 应优雅降级。"""

    def test_init_no_key(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="")
        assert client._api_key == ""
        assert client.health()["api_key_configured"] is False

    def test_get_listing_no_key(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="")
        result = client.get_listing("Anguilla japonica")
        assert result is None

    def test_get_distribution_no_key(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="")
        result = client.get_distribution("Anguilla japonica")
        assert result is None

    def test_get_full_profile_no_key(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="")
        result = client.get_full_profile("Anguilla japonica")
        assert result is None

    def test_health(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="test_key")
        h = client.health()
        assert h["api"] == "CITES Species+ v1"
        assert h["api_key_configured"] is True

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("CITES_API_KEY", "env_cites_key")
        from src.api_clients import CITESClient
        client = CITESClient()
        assert client._api_key == "env_cites_key"


# ═══════════════════════════════════════════════════════════════════
# from_live_data 集成测试 (无真实 API)
# ═══════════════════════════════════════════════════════════════════

class TestFromLiveData:
    """测试 ConflictArbiter.from_live_data 在无 API 环境下的行为。"""

    def test_falls_back_to_builtin(self):
        """无 API key 时应回退到内置数据和本地规则。"""
        from src.arbiter import ConflictArbiter
        result = ConflictArbiter.from_live_data(
            species_name="Coilia nasus",
            region="china",
            iucn_api_key="",
            cites_api_key="",
        )
        assert isinstance(result, dict)
        assert result["species_name"] == "Coilia nasus"
        assert "conflict_level" in result
        assert "verdict" in result
        # API 元信息应存在
        assert "api_sources" in result
        assert result["api_sources"]["local_data_used"] is True

    def test_unknown_species_no_api(self):
        """未知物种且无 API 时返回合理结果。"""
        from src.arbiter import ConflictArbiter
        result = ConflictArbiter.from_live_data(
            species_name="Unknownus maximus",
            region="global",
            iucn_api_key="",
            cites_api_key="",
        )
        assert result["species_name"] == "Unknownus maximus"
        # 无数据源时应返回 conflict_level=0
        assert result["conflict_level"] == 0

    def test_china_region_policy_applied(self):
        """中国区域策略应标记在结果中。"""
        from src.arbiter import ConflictArbiter
        result = ConflictArbiter.from_live_data(
            species_name="Acipenser sinensis",
            region="china",
            iucn_api_key="",
            cites_api_key="",
        )
        assert result["region_policy"] == "china"
        # 中国来源为权威
        assert "按中国保护等级执行" in result["verdict"] or "中国分类为准" in result.get(
            "consensus", {}
        ).get("level", "")


# ═══════════════════════════════════════════════════════════════════
# batch_arbitrate 测试
# ═══════════════════════════════════════════════════════════════════

class TestBatchArbitrate:
    def test_batch_builtin_species(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        results = arbiter.batch_arbitrate(
            species_list=["Coilia nasus", "Acipenser sinensis"],
            region="china",
            use_api=False,
        )
        assert results["total"] == 2
        assert len(results["results"]) == 2
        assert "summary" in results
        assert "batch_fetched_at" in results
        # 每个结果应有 verdict
        for r in results["results"]:
            assert "verdict" in r

    def test_batch_empty_list(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        results = arbiter.batch_arbitrate(
            species_list=[],
            region="china",
        )
        assert results["total"] == 0
        assert results["results"] == []
        assert results["summary"] == {}


# ═══════════════════════════════════════════════════════════════════
# 缓存持久化测试
# ═══════════════════════════════════════════════════════════════════

class TestCachePersistence:
    def test_save_and_load_cache(self, tmp_path, monkeypatch):
        from src.arbiter import ConflictArbiter
        # 先触发数据加载以填充内存缓存
        ConflictArbiter._species_cache.clear()
        data = ConflictArbiter._load_local_species_data("Coilia nasus")
        assert len(data) > 0

        cache_file = tmp_path / "test_cache.json"
        saved = ConflictArbiter.save_cache(cache_file)
        assert saved > 0
        assert cache_file.is_file()

        # 清空, 再加载
        ConflictArbiter._species_cache.clear()
        loaded = ConflictArbiter.load_cache(cache_file)
        assert loaded > 0
        # 再次查询应命中缓存
        data2 = ConflictArbiter._load_local_species_data("Coilia nasus")
        assert len(data2) > 0

    def test_load_nonexistent_cache(self):
        from src.arbiter import ConflictArbiter
        loaded = ConflictArbiter.load_cache(Path("/nonexistent/path/cache.json"))
        assert loaded == 0


# ═══════════════════════════════════════════════════════════════════
# 工厂函数测试
# ═══════════════════════════════════════════════════════════════════

class TestFactories:
    def test_get_iucn_client(self):
        from src.api_clients import get_iucn_client
        client = get_iucn_client()
        assert client is not None

    def test_get_cites_client(self):
        from src.api_clients import get_cites_client
        client = get_cites_client()
        assert client is not None

    def test_get_arbiter(self):
        from src.arbiter import get_arbiter
        arbiter = get_arbiter()
        assert arbiter is not None
        assert arbiter.health()["status"] == "HEALTHY"


# ═══════════════════════════════════════════════════════════════════
# 模拟 HTTP 响应的集成测试
# ═══════════════════════════════════════════════════════════════════

class TestIUCNClientWithMockHTTP:
    """使用 mock httpx 模拟 IUCCN API 响应。"""

    def test_parse_assessment_response(self):
        """验证 IUCN 评估 JSON 解析逻辑。"""
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="fake_key")

        mock_response = {
            "assessments": [{
                "redlistCategory": {"code": "EN", "title": "Endangered"},
                "year_published": 2023,
                "criteria": "A2bcd",
                "population_trend": "decreasing",
                "url": "https://www.iucnredlist.org/species/123",
            }]
        }

        with patch.object(client, "_get", return_value=mock_response):
            result = client.get_assessment("Testus mockus")
            assert result is not None
            assert result["category"] == "EN"
            assert result["category_name"] == "Endangered"
            assert result["population_trend"] == "decreasing"

    def test_parse_empty_assessment(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="fake_key")

        with patch.object(client, "_get", return_value={"assessments": []}):
            result = client.get_assessment("Nobody home")
            assert result is None

    def test_parse_habitat_response(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="fake_key")

        mock = {
            "result": [
                {"habitat": "Wetlands", "suitability": "Suitable", "majorimportance": True},
                {"habitat": "Forest", "suitability": "Marginal", "majorimportance": False},
            ]
        }
        with patch.object(client, "_get", return_value=mock):
            result = client.get_habitat("Testus mockus")
            assert result is not None
            assert "Wetlands" in result["suitable"]
            assert "Forest" in result["marginal"]
            assert "Wetlands" in result["major"]

    def test_parse_threats_response(self):
        from src.api_clients import IUCNClient
        client = IUCNClient(api_key="fake_key")

        mock = {
            "result": [
                {"code": "5.4.1", "title": "Fishing & harvesting aquatic resources",
                 "timing": "Ongoing", "scope": "Majority", "severity": "Very Rapid Declines"}
            ]
        }
        with patch.object(client, "_get", return_value=mock):
            result = client.get_threats("Testus mockus")
            assert result is not None
            assert len(result["threats"]) == 1
            assert result["threats"][0]["code"] == "5.4.1"


class TestCITESClientWithMockHTTP:
    """使用 mock httpx 模拟 CITES API 响应。"""

    def test_parse_listing_response(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="fake_key")

        # Mock 两步调用: taxon_concepts 解析 ID + listings 获取列名
        mock_taxon = {"taxon_concepts": [{"id": 9999}]}
        mock_listing = {
            "cites_listings": [
                {"appendix": "II", "is_current": True,
                 "effective_at": "1975-07-01", "annotation": ""}
            ]
        }

        def mock_get(url):
            if "listings" in url:
                return mock_listing
            return mock_taxon

        with patch.object(client, "_get", side_effect=mock_get):
            result = client.get_listing("Testus mockus")
            assert result is not None
            assert result["appendix"] == "II"
            assert result["appendix_name"] == "附录Ⅱ"
            assert result["listed_since"] == "1975-07-01"

    def test_resolve_taxon_id_not_found(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="fake_key")

        with patch.object(client, "_get", return_value={"taxon_concepts": []}):
            result = client.get_listing("Imaginarus species")
            assert result is None

    def test_get_full_profile_mock(self):
        from src.api_clients import CITESClient
        client = CITESClient(api_key="fake_key")

        mock_taxon = {"taxon_concepts": [{"id": 42}]}
        mock_listing = {
            "cites_listings": [
                {"appendix": "I", "is_current": True,
                 "effective_at": "1987-10-22", "annotation": "Includes all subspecies"}
            ]
        }
        mock_dist = {"distributions": [{"country": "China", "region": "Asia"}]}

        def mock_get(url):
            if "listings" in url:
                return mock_listing
            elif "distributions" in url:
                return mock_dist
            return mock_taxon

        with patch.object(client, "_get", side_effect=mock_get):
            result = client.get_full_profile("Panthera tigris")
            assert result is not None
            assert result["source"] == "cites"
            assert result["listing"]["appendix"] == "I"
            assert "China" in result["distribution"]["countries"]
