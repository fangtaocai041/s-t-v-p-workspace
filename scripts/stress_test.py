#!/usr/bin/env python3
"""
极限测试 — 全系统压力验证

测试项目:
  1. 独立验证 (5项目自举)
  2. 通路结构 (16项)
  3. 通路LIVE (4条真实执行)
  4. 规则覆盖 (18条)
  5. 演化演示 (道→一→二→三→万物)
  6. Pₙ 生成+验证+清理
  7. 全部通路连续执行

用法: python scripts/stress_test.py
"""

import sys
import time
import subprocess
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))


def run(name: str, cmd: list, timeout: int = 30) -> tuple[bool, str, float]:
    t0 = time.perf_counter()
    try:
        r = subprocess.run(
            [sys.executable] + cmd,
            capture_output=True, text=True, timeout=timeout,
            cwd=str(_WORKSPACE),
        )
        elapsed = (time.perf_counter() - t0) * 1000
        ok = r.returncode == 0
        msg = r.stdout.split("\n")[-3:] if r.stdout else r.stderr[:200]
        return ok, "\n".join(msg), elapsed
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT ({timeout}s)", timeout * 1000
    except Exception as e:
        return False, str(e), (time.perf_counter() - t0) * 1000


def main():
    print(f"\n{'═'*70}")
    print(f"  🏋️ 极限测试 — 全系统压力验证")
    print(f"{'═'*70}")

    tests = []
    passed = 0
    failed = 0
    total_ms = 0

    # ═══ 1. 独立验证 ═══
    print(f"\n  ── 1. 独立验证 (道生一) ──")
    for name, cmd in [
        ("fish (S/V0)",       ["scripts/verify_standalone.py"]),
        ("pathways (struct)",  ["scripts/verify_pathways.py"]),
        ("philosophy (rules)", ["scripts/verify_philosophy_rules.py"]),
        ("run_all_tests",      ["scripts/run_all_tests.py", "--level", "low"]),
    ]:
        ok, msg, ms = run(f"standalone/{name}", cmd)
        status = "✅" if ok else "❌"
        if ok: passed += 1
        else: failed += 1
        total_ms += ms
        print(f"  {status} {name}: {ms:.0f}ms")
        tests.append((name, ok, ms))

    # ═══ 2. 通路 LIVE + 演化 ═══
    print(f"\n  ── 2. 通路LIVE + 演化演示 ──")
    for name, cmd in [
        ("pathways LIVE", ["scripts/verify_pathways.py", "--live"]),
        ("demo evolution", ["scripts/demo_evolution.py"]),
    ]:
        ok, msg, ms = run(name, cmd)
        status = "✅" if ok else "❌"
        if ok: passed += 1
        else: failed += 1
        total_ms += ms
        print(f"  {status} {name}: {ms:.0f}ms")
        tests.append((name, ok, ms))

    # ═══ 3. 全部通路连续执行 ═══
    print(f"\n  ── 3. 全部通路连续执行 ──")
    for species, pw_id in [
        ("鳤", "P1"),
        ("Neophocaena asiaeorientalis", "P1"),
        ("Coilia nasus", "P1"),
    ]:
        ok, msg, ms = run(
            f"pathway {pw_id} '{species}'",
            ["scripts/run_pathway.py", pw_id, species],
            timeout=15,
        )
        status = "✅" if ok else "❌"
        if ok: passed += 1
        else: failed += 1
        total_ms += ms
        print(f"  {status} {pw_id}('{species}'): {ms:.0f}ms")
        tests.append((f"{pw_id}/{species}", ok, ms))

    # P2/P3/P4
    for pw_id in ["P2", "P3", "P4"]:
        ok, msg, ms = run(f"pathway {pw_id}", ["scripts/run_pathway.py", pw_id], timeout=15)
        status = "✅" if ok else "❌"
        if ok: passed += 1
        else: failed += 1
        total_ms += ms
        print(f"  {status} {pw_id}: {ms:.0f}ms")
        tests.append((pw_id, ok, ms))

    # ═══ 4. Pₙ 生成+验证+清理 ═══
    print(f"\n  ── 4. Pₙ 万物生成+验证 ──")
    # 生成
    ok, msg, ms = run(
        "spawn P3",
        ["scripts/spawn_agent.py", "Acipenser sinensis", "中华鲟", "洄游|保护", "--create"],
    )
    status = "✅" if ok else "❌"
    if ok: passed += 1
    else: failed += 1
    total_ms += ms
    print(f"  {status} spawn P3 (中华鲟): {ms:.0f}ms")

    # 验证自动发现
    ok, msg, ms = run("verify with P3", ["scripts/verify_standalone.py"])
    status = "✅" if ok else "❌"
    if ok: passed += 1
    else: failed += 1
    total_ms += ms
    print(f"  {status} verify (含P3自动发现): {ms:.0f}ms")

    # 清理
    import shutil
    p3_dir = _WORKSPACE / "acipenser-agent"
    if p3_dir.exists():
        shutil.rmtree(p3_dir)
        print(f"  ✅ cleanup: acipenser-agent removed")

    # ═══ 汇总 ═══
    total_tests = passed + failed
    print(f"\n{'═'*70}")
    print(f"  极限测试结果")
    print(f"{'─'*70}")
    for name, ok, ms in tests:
        print(f"  {'✅' if ok else '❌'} {name}: {ms:.0f}ms")
    print(f"{'─'*70}")
    print(f"  通过: {passed}/{total_tests}  |  失败: {failed}")
    print(f"  总耗时: {total_ms:.0f}ms  |  平均: {total_ms/total_tests:.0f}ms/项")
    print(f"{'═'*70}")

    if failed == 0:
        print(f"  ✅ 极限测试全部通过 — 系统健壮")
    else:
        print(f"  ❌ {failed} 项失败 — 需修复")

    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
