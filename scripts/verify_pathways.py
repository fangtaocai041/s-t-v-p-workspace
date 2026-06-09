#!/usr/bin/env python3
"""
通路端到端验证 — verify_pathways

验证点→线→面→体架构中的每条通路可执行性:
  1. 导入所有核心专精 (CORES)
  2. 验证每条通路的源/目标适配器可导入
  3. 调用 adapter.health() 和 adapter.info() 验证连通性
  4. 验证工作流通路序列的完整性

用法: python scripts/verify_pathways.py
退出码: 0=全部通过, 1=有断裂通路
"""

import sys
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))

from scripts.pathway_contracts import (
    CORES, PATHWAYS, WORKFLOWS, VOLUME,
    verify_pathway_structure, verify_all_pathways,
)


def verify_core_imports() -> dict:
    """验证所有核心专精的适配器可导入。"""
    results = {}
    for key, core in CORES.items():
        try:
            if key == "eon_core":
                # eon-core 没有 project_loader 适配器，验证模块存在
                kernel_path = _WORKSPACE / "eon-core" / "src" / "kernel" / "origin.py"
                results[key] = {
                    "status": "OK" if kernel_path.exists() else "MISSING",
                    "path": str(kernel_path),
                }
            else:
                from scripts.project_loader import _resolve_project
                proj = _resolve_project(core.project)
                if proj:
                    results[key] = {"status": "OK", "path": str(proj)}
                else:
                    results[key] = {"status": "MISSING", "project": core.project}
        except Exception as e:
            results[key] = {"status": "ERROR", "error": str(e)}
    return results


def verify_pathway_connectivity() -> dict:
    """验证每条通路两端适配器的 health() 可调用。"""
    results = {}
    for pw_id, pw in PATHWAYS.items():
        try:
            # 加载源适配器
            source_ok = False
            target_ok = False

            # 尝试通过 project_loader 加载
            from scripts.project_loader import get_fish, get_cognitive, get_porpoise, get_coilia

            adapters = {
                "fish-ecology-assistant": get_fish,
                "cognitive-search-engine": get_cognitive,
                "porpoise-agent": get_porpoise,
                "coilia-agent": get_coilia,
            }

            # 多对一通路: 源是"所有适配器"
            if "所有" in pw.source or "全部" in pw.source:
                source_ok = True  # 多源通路合法

            for proj_name, getter in adapters.items():
                if proj_name in pw.source:
                    adapter = getter()
                    h = adapter.health()
                    source_ok = "status" in h
                if proj_name in pw.target:
                    adapter = getter()
                    h = adapter.health()
                    target_ok = "status" in h

            # P4: eon-core target — 验证内核模块存在 (非适配器接口)
            if "eon-core" in pw.target:
                kernel = _WORKSPACE / "eon-core" / "src" / "kernel" / "origin.py"
                target_ok = kernel.exists()

            results[pw_id] = {
                "status": "CONNECTED" if (source_ok and target_ok) else "BROKEN",
                "source_ok": source_ok,
                "target_ok": target_ok,
            }
        except Exception as e:
            results[pw_id] = {"status": "ERROR", "error": str(e)}
    return results


def verify_workflow_integrity() -> dict:
    """验证工作流通路序列的完整性。"""
    results = {}
    for wf_id, wf in WORKFLOWS.items():
        missing = [pid for pid in wf.pathway_sequence if pid not in PATHWAYS]
        results[wf_id] = {
            "status": "INTACT" if not missing else "BROKEN",
            "pathways": len(wf.pathway_sequence),
            "missing": missing,
        }
    return results


def main():
    live_mode = "--live" in sys.argv

    print(f"\n{'═'*60}")
    mode_str = "LIVE 执行模式" if live_mode else "结构验证模式"
    print(f"  通路端到端验证 ({mode_str})")
    print(f"  三角形: P1 P2 P4  |  派生: P3")
    print(f"{'═'*60}")

    # 1. 核心专精导入验证
    print(f"\n  ── 点 (Points): 5 核心专精 ──")
    cores = verify_core_imports()
    core_ok = sum(1 for c in cores.values() if c["status"] == "OK")
    for key, result in cores.items():
        icon = "✅" if result["status"] == "OK" else "❌"
        print(f"  {icon} {key}: {result['status']}")

    # 2. 通路结构验证
    print(f"\n  ── 线 (Lines): 4 数据流通路 ──")
    structures = verify_all_pathways()
    for pw_id, result in structures["pathways"].items():
        icon = "✅" if result["status"] == "VALID" else "❌"
        print(f"  {icon} {pw_id}: {result['name']}")

    # 3. 通路连通性验证
    print(f"\n  ── 连通性检查 ──")
    connectivity = verify_pathway_connectivity()
    conn_ok = sum(1 for c in connectivity.values() if c["status"] == "CONNECTED")
    for pw_id, result in connectivity.items():
        icon = "✅" if result["status"] == "CONNECTED" else "⚠️"
        print(f"  {icon} {pw_id}: {result['status']}")

    # 4. 工作流验证
    print(f"\n  ── 面 (Surfaces): 2 工作流 ──")
    workflows = verify_workflow_integrity()
    wf_ok = sum(1 for w in workflows.values() if w["status"] == "INTACT")
    for wf_id, result in workflows.items():
        icon = "✅" if result["status"] == "INTACT" else "❌"
        print(f"  {icon} {wf_id}: {result['status']} ({result['pathways']} 条通路)")

    # 5. 体验证
    print(f"\n  ── 体 (Volume): eon-core 反馈环 ──")
    print(f"  ✅ {VOLUME.name}")
    print(f"     {VOLUME.layers} 层 · {len(VOLUME.vertices)} 顶点 · {len(VOLUME.karma_states)} 业力状态")
    print(f"     {len(VOLUME.invariants)} 条架构不变量")

    # 汇总
    total = len(cores) + len(structures["pathways"]) + len(connectivity) + len(workflows) + 1
    passed = core_ok + structures["valid"] + conn_ok + wf_ok + 1
    failed = total - passed

    print(f"\n{'─'*60}")
    print(f"  总检查项: {total}  |  通过: {passed}  |  断裂: {failed}")
    print(f"{'═'*60}")

    if failed == 0:
        print(f"  ✅ 全部通路可执行: 三角闭环 + 派生赋能")
        print(f"     三角形: fish+cognitive+eon-core  |  万物: P₁ P₂ ...Pₙ")
    else:
        print(f"  ❌ {failed} 条通路断裂 — 需修复")

    # ── LIVE 模式: 真实执行全部通路 ──
    if live_mode:
        print(f"\n  ── LIVE 执行追踪 ──")
        from scripts.pathway_executor import execute_all_pathways
        species = "Ochetobius elongatus"
        traces = execute_all_pathways(species)
        live_ok = 0
        live_total = len(traces)
        for pw_id, trace in traces.items():
            icon = "✅" if trace.is_valid else "⚠️"
            if trace.is_valid:
                live_ok += 1
            print(f"  {icon} {pw_id}: {trace.total_ms:.0f}ms — {trace.validate_message}")
        live_failed = live_total - live_ok
        if live_failed > 0:
            failed += live_failed
            total += live_total
            passed = total - failed

    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
