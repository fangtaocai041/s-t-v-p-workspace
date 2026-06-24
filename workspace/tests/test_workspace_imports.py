"""
test_workspace_imports.py — workspace 包导入冒烟测试

验证 workspace 统一入口的所有核心 API 可正常导入。
"""

import sys
from pathlib import Path

# Ensure workspace root is on path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def test_workspace_imports():
    """验证 workspace 包的基础导入。"""
    from workspace import (
        search_species,
        lookup_species,
        assess_conservation,
        assess_species,
        assess_conflict,
        health_check,
        full_stack_search,
        rcca_setup,
        rcca_health,
        synthesize_review,
        setup_senses,
        senses_health,
        search,
        lookup,
        assess,
        health,
        full,
        conflict,
    )
    # All imports succeeded
    assert callable(search_species), "search_species should be callable"
    assert callable(lookup_species), "lookup_species should be callable"
    assert callable(health_check), "health_check should be callable"
    print("[OK] workspace imports")


def test_rcca_setup():
    """验证 RCCA 核心可用。"""
    from workspace import rcca_setup, rcca_health
    core = rcca_setup()
    assert "self_model" in core, "Missing self_model"
    assert "emotion" in core, "Missing emotion"
    assert "transposition" in core, "Missing transposition"
    assert "reflection" in core, "Missing reflection"
    assert rcca_health()["status"] == "available"
    print("[OK] RCCA setup")


def test_senses_health():
    """验证感受器层可用。"""
    from workspace import senses_health, setup_senses
    health = senses_health()
    assert health["status"] == "available", f"Senses unavailable: {health}"
    assert len(health.get("domains", [])) > 0, "No domains registered"
    print(f"[OK] Senses ({len(health['domains'])} domains)")


def test_version_consistency():
    """验证版本号从 VERSION.yaml 正确加载。"""
    from workspace import _load_coordination
    config = _load_coordination()
    assert config.get("_loaded"), "coordination.yaml not loaded"
    assert config.get("version"), "No workspace version"
    print(f"[OK] Coordination v{config['version']}")


def test_health_check():
    """验证全栈健康检查。"""
    from workspace import health_check
    result = health_check()
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert "cognitive-search-engine" in result, "Missing cognitive"
    assert "fish-ecology-assistant" in result, "Missing fish"
    # Health check may return errors for some projects — that's OK
    statuses = {k: v.get("status", "?") for k, v in result.items()
                if isinstance(v, dict)}
    print(f"[OK] Health check: {len(statuses)} projects")


if __name__ == "__main__":
    tests = [
        ("imports", test_workspace_imports),
        ("rcca", test_rcca_setup),
        ("senses", test_senses_health),
        ("version", test_version_consistency),
        ("health", test_health_check),
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    print(f"\n---\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)
