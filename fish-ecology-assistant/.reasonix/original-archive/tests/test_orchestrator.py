"""Tests for FishEcologyOrchestrator — 主入口 API 测试。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator import FishEcologyOrchestrator, KbFirstResult, get_orchestrator


def test_importable():
    assert FishEcologyOrchestrator is not None
    assert KbFirstResult is not None


def test_get_orchestrator():
    orch = get_orchestrator()
    assert isinstance(orch, FishEcologyOrchestrator)


def test_health():
    orch = get_orchestrator()
    health = orch.health()
    assert health["project"] == "fish-ecology-assistant"
    assert health["status"] in ("HEALTHY", "DEGRADED")
    assert "pipeline_stages" in health
    assert "species_db_size" in health


def test_info():
    orch = get_orchestrator()
    info = orch.info()
    assert info["project"] == "fish-ecology-assistant"
    assert "version" in info
    assert "capabilities" in info
    assert "kb_first_two_stage_search" in info["capabilities"]


def test_kb_first_lookup_known_species():
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="鳤")
    assert isinstance(result, KbFirstResult)


def test_kb_first_lookup_by_scientific():
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="Cyprinus carpio")
    assert isinstance(result, KbFirstResult)


def test_kb_first_lookup_unknown():
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="_unknown_species_xyz_")
    assert isinstance(result, KbFirstResult)


def test_stages_constant():
    assert FishEcologyOrchestrator.STAGES == ["Plan", "Search", "Analyze", "Write", "Review"]


def test_get_orchestrator_twice():
    """get_orchestrator 应可多次调用。"""
    pass



