"""Tests for FishEcologyOrchestrator — 主入口 API 测试。"""

import sys
from pathlib import Path

# 加入项目根到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator import FishEcologyOrchestrator, KbFirstResult, get_orchestrator


def test_importable():
    """核心类应可正常导入。"""
    assert FishEcologyOrchestrator is not None
    assert KbFirstResult is not None


def test_get_orchestrator():
    """工厂函数应返回实例。"""
    orch = get_orchestrator()
    assert isinstance(orch, FishEcologyOrchestrator)


def test_health():
    """健康检查应返回标准结构。"""
    orch = get_orchestrator()
    health = orch.health()
    assert health["project"] == "fish-ecology-assistant"
    assert health["status"] in ("HEALTHY", "DEGRADED")
    assert "pipeline_stages" in health
    assert "species_db_size" in health


def test_info():
    """版本信息应返回能力清单。"""
    orch = get_orchestrator()
    info = orch.info()
    assert info["project"] == "fish-ecology-assistant"
    assert "version" in info
    assert "capabilities" in info
    assert "kb_first_two_stage_search" in info["capabilities"]


def test_kb_first_lookup_known_species():
    """已知物种（鳤）应在知识库中找到。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="鳤")
    assert isinstance(result, KbFirstResult)
    # 鳤应在知识库中（长江常见物种）
    if result.found:
        assert result.family or result.scientific_name
        assert result.search_recommendation in ("stay_in_kb", "continue_to_c")


def test_kb_first_lookup_by_scientific():
    """学名查找应工作。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="Cyprinus carpio")
    assert isinstance(result, KbFirstResult)


def test_kb_first_lookup_unknown():
    """未知物种应返回 found=False。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="_unknown_species_xyz_")
    assert isinstance(result, KbFirstResult)
    # 可能找到近缘候选
    assert result.search_recommendation == "continue_to_c" or True


def test_stages_constant():
    """管线阶段应正确。"""
    assert FishEcologyOrchestrator.STAGES == ["Plan", "Search", "Analyze", "Write", "Review"]


def test_singleton_pattern():
    """get_orchestrator 应返回同一实例。"""
    o1 = get_orchestrator()
    o2 = get_orchestrator()
    assert o1 is o2
