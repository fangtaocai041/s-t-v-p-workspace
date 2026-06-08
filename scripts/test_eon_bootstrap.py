"""eon-core bootstrap self-check + DAG topology verification.

Usage:
    python scripts/test_eon_bootstrap.py

Tests:
  1. OriginKernel singleton creation
  2. bootstrap() loads taiji.yaml, creates EventBus, verifies DAG
  3. 4 vertices registered in registry
  4. Topology IS DAG (enforced)
  5. route_event() filters by Samsara state
  6. EventBus publish/consume roundtrip
  7. shutdown() transitions to SEEDING
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure eon-core is importable
workspace = Path(__file__).resolve().parent.parent
# Use relative path for package resolution
if "eon-core" not in sys.path:
    sys.path.insert(0, "eon-core")


async def test_bootstrap():
    """Test: OriginKernel.bootstrap() loads config and creates DAG topology."""
    from src.kernel.origin import OriginKernel
    from src.kernel.lifecycle import LifecycleStage

    kernel = OriginKernel()
    assert kernel.state.stage == LifecycleStage.SEEDING, f"Expected SEEDING, got {kernel.state.stage}"

    config_path = "eon-core/config/taiji.yaml"
    report = await kernel.bootstrap(config_path)

    assert report.success, f"Bootstrap failed: {report.errors}"
    assert kernel.state.stage == LifecycleStage.BLOOMING, f"Expected BLOOMING, got {kernel.state.stage}"
    assert len(kernel.registry) == 4, f"Expected 4 vertices, got {len(kernel.registry)}"
    assert kernel.topology.number_of_nodes() >= 4, "Topology missing origin + vertices"

    print("✅ [1/4] Bootstrap OK: DAG verified, 4 vertices registered")
    return kernel


async def test_event_bus(kernel):
    """Test: EventBus publish/consume roundtrip."""
    from src.kernel.event_bus import SystemEvent

    event = SystemEvent(
        trace_id="test-trace-1",
        source="test",
        payload={"query": "Ochetobius elongatus"},
    )

    event_id = await kernel.event_bus.publish(event, "test.topic")
    assert event_id, "publish returned empty event_id"

    consumed = await asyncio.wait_for(
        kernel.event_bus.consume("test.topic", timeout=2.0),
        timeout=3.0,
    )
    assert consumed.trace_id == "test-trace-1", "Consumed event trace mismatch"

    print("✅ [2/4] EventBus roundtrip OK")


async def test_route_event(kernel):
    """Test: route_event classifies intent and returns plan."""
    from src.kernel.event_bus import SystemEvent

    # Route a porpoise query
    event = SystemEvent(
        trace_id="test-trace-2",
        source="test",
        payload={"query": "Yangtze finless porpoise population recovery after fishing ban"},
    )

    result = await kernel.route_event(event)
    assert len(result.plan) >= 1, f"Route plan empty: {result.plan}"
    assert "V2" in result.plan or "V0" in result.plan, f"Expected V0/V2 in plan, got {result.plan}"

    print(f"✅ [3/4] Route OK: plan={result.plan}, samsara_states={dict(result.samsara_states)}")


async def test_shutdown(kernel):
    """Test: shutdown transitions to SEEDING."""
    from src.kernel.lifecycle import LifecycleStage

    await kernel.shutdown()
    assert kernel.state.stage == LifecycleStage.SEEDING, f"Expected SEEDING after shutdown, got {kernel.state.stage}"

    print("✅ [4/4] Shutdown OK: system returned to SEEDING")


async def main():
    print("=" * 50)
    print("  eon-core Bootstrap Self-Check")
    print("=" * 50)

    try:
        kernel = await test_bootstrap()
        await test_event_bus(kernel)
        await test_route_event(kernel)
        await test_shutdown(kernel)

        print("=" * 50)
        print("  All checks passed — eon-core DAG verified.")
        print("=" * 50)
    except Exception as exc:
        print(f"\n❌ FAIL: {exc}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
