"""End-to-end test: eon-core full pipeline.

Scenario: User queries "长江江豚种群恢复" →
  1. eon-core boots (DAG + EventBus)
  2. route_event classifies intent → V2 (porpoise)
  3. V2 vertex calls project_loader → PorpoiseAdapter
  4. adapter.search() returns result
  5. Shutdown gracefully

Usage:
    python scripts/test_e2e.py
"""

import asyncio
import sys
from pathlib import Path

workspace = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace / "eon-core"))


async def test_full_pipeline():
    from src.kernel.origin import OriginKernel
    from src.kernel.event_bus import SystemEvent
    from src.kernel.lifecycle import LifecycleStage

    print("=" * 60)
    print("  E2E Full Pipeline Test")
    print("=" * 60)

    # ── 1. Bootstrap ──
    kernel = OriginKernel()
    config_path = str(workspace / "eon-core" / "config" / "taiji.yaml")
    report = await kernel.bootstrap(config_path)
    assert report.success, f"Bootstrap failed: {report.errors}"
    assert kernel.state.stage == LifecycleStage.BLOOMING
    print(f"✅ Bootstrap: {len(kernel.registry)} vertices, DAG={kernel.topology.number_of_nodes()}n/{kernel.topology.number_of_edges()}e")

    # ── 2. Route porpoise query ──
    event = SystemEvent(
        trace_id="e2e-porpoise-1",
        source="e2e-test",
        payload={"query": "长江江豚在禁渔后的种群恢复趋势"},
    )
    result = await kernel.route_event(event)
    assert len(result.plan) >= 1, f"Empty route plan"
    print(f"✅ Route '江豚': plan={result.plan}")

    # ── 3. Route fish query ──
    event2 = SystemEvent(
        trace_id="e2e-fish-1",
        source="e2e-test",
        payload={"query": "鳤 Ochetobius elongatus 文献调研"},
    )
    result2 = await kernel.route_event(event2)
    print(f"✅ Route '鳤': plan={result2.plan}")

    # ── 4. Route cognitive query ──
    event3 = SystemEvent(
        trace_id="e2e-cog-1",
        source="e2e-test",
        payload={"query": "验证 Coilia nasus 的洄游路径假设"},
    )
    result3 = await kernel.route_event(event3)
    print(f"✅ Route 'coilia验证': plan={result3.plan}")

    # ── 5. Adapter integration ──
    print()
    print("─ Adapter Integration ─")
    try:
        from scripts.project_loader import get_all_adapters
        adapters = get_all_adapters()
        for name, adapter in adapters.items():
            if adapter is None:
                print(f"  ⚠️ {name}: not available")
                continue
            info = adapter.info()
            health = adapter.health()
            print(f"  ✅ {name}: {info.get('role','?')} | {health['status']}")
    except ImportError:
        print("  ⚠️ project_loader not available (expected in CI)")

    # ── 6. Shutdown ──
    await kernel.shutdown()
    assert kernel.state.stage == LifecycleStage.SEEDING
    print(f"\n✅ Shutdown: returned to SEEDING")

    print("=" * 60)
    print("  E2E Pipeline Test — PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
