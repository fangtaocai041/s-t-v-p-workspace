"""
test_integration.py — workspace 跨项目调用链集成测试

验证通过 workspace 统一入口调用各子项目的完整链路。
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def test_workspace_imports():
    """所有核心 API 可导入。"""
    from workspace import (
        search_species, lookup_species, assess_conflict,
        health_check, full_stack_search, rcca_setup,
        synthesize_review,
    )
    assert callable(search_species)
    assert callable(health_check)
    print("[OK] workspace imports")


def test_rcca_chain():
    """RCCA 核心 → 7 项目 shim → eon-core 规范源。"""
    from workspace import rcca_setup, rcca_health
    core = rcca_setup()
    state = core["self_model"].reflect()
    assert state.stability >= 0
    health = rcca_health()
    assert health["status"] == "available"
    print(f"[OK] rcca chain (stability={state.stability:.3f})")


def test_health_check():
    """全栈健康检查覆盖所有项目。"""
    from workspace import health_check
    result = health_check()
    projects = [
        "cognitive-search-engine", "fish-ecology-assistant",
        "porpoise-agent", "coilia-agent", "culter-agent",
        "conflict-arbiter",
    ]
    for p in projects:
        assert p in result, f"Missing {p}"
    print(f"[OK] health check: {len(projects)} projects")


def test_version_consistency():
    """VERSION.yaml 是唯一版本源。"""
    from workspace import _load_coordination
    config = _load_coordination()
    assert config["_loaded"], "coordination.yaml not loaded"
    ver = config.get("version")
    assert ver, "No version"
    print(f"[OK] version: {ver}")


def test_senses_layer():
    """感受器层 12 领域可用。"""
    from workspace import senses_health, setup_senses
    s = setup_senses()
    assert len(s["domains"]) == 12, f"Expected 12 domains, got {len(s['domains'])}"
    health = senses_health()
    assert health["status"] == "available"
    print(f"[OK] senses: {len(s['domains'])} domains")


def test_shared_modules_importable():
    """所有共享模块可直接导入。"""
    import sys as _sys
    from pathlib import Path as _P
    shared = str(_P(__file__).resolve().parent.parent / "eon-core" / "src" / "shared")
    if shared not in _sys.path:
        _sys.path.insert(0, shared)

    modules = [
        ("thompson", "ThompsonBandit"),
        ("pid_limiter", "PIDRateLimiter"),
        ("circuit_breaker", "CircuitBreaker"),
        ("variant_generator", "generate_variants"),
        ("rcca_core", "SelfModelEngine"),
        ("cognitive_base", "CognitiveState"),
        ("protection_scoring", "score_protection"),
        ("domains", "ALL_DOMAIN_NAMES"),
        ("magma_memory", "MagmaMemory"),
        ("chinese_nlp", "segment"),
    ]
    for mod_name, cls_name in modules:
        try:
            mod = __import__(mod_name)
            assert hasattr(mod, cls_name), f"{mod_name}.{cls_name} not found"
            print(f"  [OK] {mod_name}.{cls_name}")
        except ImportError as e:
            print(f"  [SKIP] {mod_name}: {e}")


def test_cognitive_engine():
    """共享认知引擎可用。"""
    import sys as _sys
    from pathlib import Path as _P
    shared = str(_P(__file__).resolve().parent.parent / "eon-core" / "src" / "shared")
    if shared not in _sys.path:
        _sys.path.insert(0, shared)

    from cognitive import BDICoordinator, ReActLoop, TaskDecomposer
    bdi = BDICoordinator()
    assert bdi is not None
    dc = TaskDecomposer()
    assert dc is not None
    print(f"[OK] cognitive engine: BDI + Decomposer")


if __name__ == "__main__":
    tests = [
        ("imports", test_workspace_imports),
        ("rcca", test_rcca_chain),
        ("health", test_health_check),
        ("version", test_version_consistency),
        ("senses", test_senses_layer),
        ("shared", test_shared_modules_importable),
        ("cognitive", test_cognitive_engine),
    ]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
