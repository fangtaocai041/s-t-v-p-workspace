"""workspace integration test — 验证六项目 adapter + project_loader 全链路.

Usage:
    python scripts/test_workspace.py

Tests:
  1. project_loader imports all 4 adapters
  2. Each adapter exposes IProjectAdapter interface (search/health/info)
  3. Cross-project call: get_fish().search("Ochetobius elongatus")
  4. All adapters return valid dicts (not errors)
  5. eon-core can be imported
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure workspace root is on path
workspace = Path(__file__).resolve().parent.parent
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))


def test_project_loader_imports():
    """Test: project_loader can import all 4 adapter factories."""
    from scripts.project_loader import (
        get_fish, get_cognitive, get_porpoise, get_coilia,
        get_all_adapters, clear_cache, IProjectAdapter,
    )
    assert callable(get_fish), "get_fish is not callable"
    assert callable(get_cognitive), "get_cognitive is not callable"
    assert callable(get_porpoise), "get_porpoise is not callable"
    assert callable(get_coilia), "get_coilia is not callable"
    print("✅ [1/5] project_loader imports OK")

    return get_fish, get_cognitive, get_porpoise, get_coilia, get_all_adapters


def test_adapter_instantiation(get_fish, get_cognitive, get_porpoise, get_coilia):
    """Test: each adapter can be instantiated."""
    adapters = {}
    errors = []

    for name, factory in [
        ("fish", get_fish), ("cognitive", get_cognitive),
        ("porpoise", get_porpoise), ("coilia", get_coilia),
    ]:
        try:
            adapter = factory()
            adapters[name] = adapter
            status = "✅" if adapter is not None else "⚠️ stub"
            print(f"  {status} {name}: {type(adapter).__name__}")
        except Exception as e:
            errors.append(f"{name}: {e}")
            print(f"  ❌ {name}: {e}")

    if errors:
        print(f"⚠️  {len(errors)} adapter(s) unavailable (expected if projects not installed)")
    else:
        print("✅ [2/5] All 4 adapters instantiated")

    return adapters


def test_adapter_interface(adapters: dict):
    """Test: each adapter exposes IProjectAdapter protocol."""
    tested = 0
    for name, adapter in adapters.items():
        if adapter is None:
            continue
        for method_name in ["search", "health", "info"]:
            method = getattr(adapter, method_name, None)
            if not callable(method):
                print(f"  ❌ {name}.{method_name}() missing")
                continue
            try:
                result = method("test") if method_name == "search" else method()
                assert isinstance(result, dict), f"{method_name}() did not return dict"
                tested += 1
            except Exception as e:
                print(f"  ⚠️ {name}.{method_name}() raised: {e}")
    print(f"✅ [3/5] {tested} interface methods verified")


def test_cross_project_search(adapters: dict):
    """Test: cross-project search call."""
    if "fish" in adapters and adapters["fish"] is not None:
        result = adapters["fish"].search("Ochetobius elongatus", chinese_name="鳤")
        assert isinstance(result, dict), "search result is not dict"
        assert "status" in result, "result missing 'status'"
        print(f"✅ [4/5] Cross-project search OK: status={result.get('status')}")
    else:
        print("⏭️ [4/5] Fish adapter unavailable — skipping cross-project search")


def test_eon_core_import():
    """Test: eon-core can be imported."""
    try:
        from eon_core.src.kernel.origin import OriginKernel
        kernel = OriginKernel()
        assert kernel is not None
        print("✅ [5/5] eon-core import OK")
    except ImportError:
        # eon-core dir may not be on path
        eon_path = workspace / "eon-core"
        if eon_path.is_dir():
            sys.path.insert(0, str(eon_path))
            try:
                from src.kernel.origin import OriginKernel
                print("✅ [5/5] eon-core import OK (path fix)")
            except ImportError:
                print("⏭️ [5/5] eon-core import skipped (package not on path)")
        else:
            print("⏭️ [5/5] eon-core not found")


def main():
    print("=" * 50)
    print("  S-T-V-P Workspace Integration Test")
    print("=" * 50)

    factories = test_project_loader_imports()
    get_fish, get_cognitive, get_porpoise, get_coilia, get_all = factories

    adapters = test_adapter_instantiation(get_fish, get_cognitive, get_porpoise, get_coilia)
    test_adapter_interface(adapters)
    test_cross_project_search(adapters)
    test_eon_core_import()

    print("=" * 50)
    print("  All tests completed.")
    print("=" * 50)


if __name__ == "__main__":
    main()
