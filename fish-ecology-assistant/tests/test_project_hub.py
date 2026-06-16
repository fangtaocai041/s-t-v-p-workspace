"""Tests for ProjectHub — 多项目协调中枢测试。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.project_hub import ProjectHub, get_hub, reset_hub, TriangleMember, DerivedMember, TRIANGLE, DERIVED


def setup_method():
    reset_hub()


def test_triangle_members():
    assert len(TRIANGLE) == 3
    keys = [m.key for m in TRIANGLE]
    assert "fish" in keys
    assert "cognitive" in keys
    assert "eon" in keys


def test_derived_members():
    assert len(DERIVED) >= 3
    keys = [m.key for m in DERIVED]
    for k in ("porpoise", "coilia", "conflict"):
        assert k in keys, f"缺失: {k}"


def test_get_hub():
    hub = get_hub()
    assert isinstance(hub, ProjectHub)


def test_hub_health_all():
    hub = get_hub()
    health = hub.health_all()
    assert "philosophy" in health
    assert "one" in health
    assert "two" in health
    assert "three" in health
    assert "myriad" in health


def test_hub_capabilities():
    hub = get_hub()
    caps = hub.capabilities()
    assert "triangle" in caps
    assert "myriad" in caps
    assert caps["triangle"]["fish"]["available"] is True


def test_hub_triangle_status():
    hub = get_hub()
    status = hub.triangle_status()
    for key in ("fish", "cognitive", "eon"):
        assert key in status
        assert "symbol" in status[key]
        assert "pole" in status[key]


def test_hub_singleton():
    h1 = get_hub()
    h2 = get_hub()
    assert h1 is h2


def test_relationship_map():
    result = ProjectHub.relationship_map()
    assert isinstance(result, str)
    assert len(result) > 100
