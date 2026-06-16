"""Tests for ProjectHub — 多项目协调中枢测试。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.project_hub import ProjectHub, get_hub, reset_hub, TriangleMember, DerivedMember, TRIANGLE, DERIVED


def setup_method():
    reset_hub()


def test_triangle_members():
    """三角核心应有 3 个成员。"""
    assert len(TRIANGLE) == 3
    keys = [m.key for m in TRIANGLE]
    assert "fish" in keys
    assert "cognitive" in keys
    assert "eon" in keys


def test_derived_members():
    """衍生项目应有已知成员。"""
    assert len(DERIVED) >= 3
    keys = [m.key for m in DERIVED]
    for k in ("porpoise", "coilia", "conflict"):
        assert k in keys, f"缺少衍生成员: {k}"


def test_get_hub():
    """get_hub 应返回 ProjectHub 实例。"""
    hub = get_hub()
    assert isinstance(hub, ProjectHub)


def test_hub_health_all():
    """health_all 应返回完整健康结构。"""
    hub = get_hub()
    health = hub.health_all()
    assert "philosophy" in health
    assert "one" in health
    assert "two" in health
    assert "three" in health
    assert "myriad" in health
    assert "triangle_complete" in health


def test_hub_capabilities():
    """capabilities 应返回三角+万物信息。"""
    hub = get_hub()
    caps = hub.capabilities()
    assert "triangle" in caps
    assert "myriad" in caps
    # fish 应始终可用（本项目自身）
    assert caps["triangle"]["fish"]["available"] is True


def test_hub_triangle_status():
    """triangle_status 应包含所有三角成员。"""
    hub = get_hub()
    status = hub.triangle_status()
    for key in ("fish", "cognitive", "eon"):
        assert key in status
        assert "symbol" in status[key]
        assert "pole" in status[key]


def test_hub_singleton():
    """get_hub 应返回同一实例。"""
    h1 = get_hub()
    h2 = get_hub()
    assert h1 is h2


def test_relationship_map():
    """relationship_map 应返回 ASCII 图。"""
    result = ProjectHub.relationship_map()
    assert isinstance(result, str)
    assert len(result) > 100
    assert "道" in result or "Dao" in result
