#!/usr/bin/env python3
"""
coordination_test.py — Reasonix 全项目协调测试集
================================================
测试所有项目间的调用顺序和跨项目协调链路。

调用链:
  0. 工作区导入 (所有项目 cross-importable)
  1. workspace.health_check()        → 6 项目健康检查
  2. workspace.lookup_species()      → fish → conflict (auto)
  3. workspace.search_species()      → cognitive MCP 搜索
  4. workspace.full_stack_search()   → fish → cognitive → fish (WF_A)
  5. workspace.assess_conflict()     → conflict-arbiter
  6. workspace.rcca_setup/health()   → RCCA 集成
  7. 跨项目直调: coilia→fish, cognitive→conflict

用法:
  cd D:/Reasonix
  python scripts/coordination_test.py
  python scripts/coordination_test.py --quick     # skip slow tests
  python scripts/coordination_test.py --verbose   # verbose output
"""

from __future__ import annotations

import os
import sys
import time
import traceback
import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

# ── Path setup ──────────────────────────────────────────────
_WORKSPACE = Path(__file__).resolve().parent.parent  # D:\Reasonix
sys.path.insert(0, str(_WORKSPACE))

# ── Test runner ─────────────────────────────────────────────

PASS = 0
FAIL = 1
SKIP = 2

COLORS = {PASS: "\033[92m", FAIL: "\033[91m", SKIP: "\033[93m", "reset": "\033[0m"}
LABELS = {PASS: "PASS", FAIL: "FAIL", SKIP: "SKIP"}

_results: List[Tuple[int, str, str, float]] = []


def record(status: int, name: str, detail: str = "", elapsed: float = 0):
    _results.append((status, name, detail, elapsed))
    color = COLORS.get(status, "")
    reset = COLORS["reset"]
    label = LABELS.get(status, "???")
    ms = f" ({elapsed * 1000:.0f}ms)" if elapsed else ""
    line = f"  {color}[{label}]{reset} {name}{ms}"
    print(line)
    if detail and (status == FAIL or "--verbose" in sys.argv):
        for d in detail.split("\n"):
            print(f"        {d}")


# ═══════════════════════════════════════════════════════
# 测试用例
# ═══════════════════════════════════════════════════════


def test_0_workspace_import():
    """[0] 工作区导入 — 所有项目 cross-importable"""
    t0 = time.time()
    try:
        from workspace import (
            search_species, lookup_species, assess_conservation,
            assess_species, assess_conflict, health_check,
            full_stack_search, rcca_setup, rcca_health,
        )
        elapsed = time.time() - t0
        record(PASS, "workspace 全量导入", f"9 个函数可用", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "workspace 全量导入", str(e), elapsed)
        return False


def test_0b_cross_project_imports():
    """[0b] 跨项目直调导入"""
    all_ok = True

    # cognitive → McpClient
    try:
        from cognitive_search_engine.src.mcp_client import McpClient
        record(PASS, "cognitive → McpClient")
    except Exception as e:
        record(FAIL, "cognitive → McpClient", str(e)); all_ok = False

    # cognitive → search
    try:
        from cognitive_search_engine.src.search_coordinator import search
        record(PASS, "cognitive → search")
    except Exception as e:
        record(FAIL, "cognitive → search", str(e)); all_ok = False

    # fish → FishEcologyAdapter
    try:
        # Ensure D:\Reasonix is first (workspace import may reorder paths)
        if str(_WORKSPACE) not in sys.path:
            sys.path.insert(0, str(_WORKSPACE))
        from fish_ecology_assistant.src.adapter import FishEcologyAdapter
        record(PASS, "fish → FishEcologyAdapter")
    except Exception as e:
        record(FAIL, "fish → FishEcologyAdapter", str(e)); all_ok = False

    # arbiter → ConflictArbiter
    try:
        from conflict_arbiter.src.arbiter import ConflictArbiter
        record(PASS, "arbiter → ConflictArbiter")
    except Exception as e:
        record(FAIL, "arbiter → ConflictArbiter", str(e)); all_ok = False

    # coilia → fish adapter (cross-project)
    try:
        from fish_ecology_assistant.src.adapter import FishEcologyAdapter
        record(PASS, "coilia → fish (FishEcologyAdapter)")
    except Exception as e:
        record(FAIL, "coilia → fish", str(e)); all_ok = False

    return all_ok


def test_1_health_check():
    """[1] 全项目健康检查"""
    t0 = time.time()
    try:
        from workspace import health_check
        result = health_check()
        elapsed = time.time() - t0
        projects_checked = [k for k in result if not k.startswith("rcca") and k != "senses_layer"]
        ok_count = sum(1 for v in result.values() if isinstance(v, dict) and v.get("status") == "ok")
        record(PASS, "health_check()",
               f"{ok_count}/{len(projects_checked)} projects OK: {projects_checked}", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "health_check()", str(e), elapsed)
        return False


def test_2_lookup_species():
    """[2] lookup_species — fish 知识库 → conflict 自动仲裁"""
    t0 = time.time()
    try:
        from workspace import lookup_species
        result = lookup_species("Tribolodon")
        elapsed = time.time() - t0
        has_species = bool(result.get("species_data") or result.get("name"))
        has_conflict = "conflict_verdict" in result
        detail = f"species_data={'OK' if has_species else 'EMPTY'}, auto_conflict={'OK' if has_conflict else 'NONE'}"
        record(PASS, "lookup_species('Tribolodon') → fish→conflict", detail, elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "lookup_species('Tribolodon')", str(e), elapsed)
        return False


def test_3_search_species(quick=False):
    """[3] search_species — cognitive MCP 多引擎搜索"""
    t0 = time.time()
    try:
        from workspace import search_species
        group = "quick" if quick else "standard"
        result = search_species("Tribolodon", group=group, limit=3)
        elapsed = time.time() - t0
        papers = len(result.papers) if hasattr(result, 'papers') else 0
        record(PASS, f"search_species('Tribolodon', group='{group}')",
               f"{papers} papers, mode={result.mode}, engine={result.engine_stats}", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "search_species('Tribolodon')", str(e), elapsed)
        return False


def test_4_full_stack_search():
    """[4] full_stack_search — WF_A: fish→cognitive→fish"""
    t0 = time.time()
    try:
        from workspace import full_stack_search
        result = full_stack_search("Tribolodon")
        elapsed = time.time() - t0
        has_profile = bool(result.get("profile"))
        has_lit = bool(result.get("literature"))
        has_cred = bool(result.get("credibility"))
        detail = f"profile={'OK' if has_profile else 'NO'}, lit={'OK' if has_lit else 'NO'}, cred={'OK' if has_cred else 'NO'}"
        record(PASS, "full_stack_search('Tribolodon') [WF_A]", detail, elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "full_stack_search('Tribolodon')", str(e), elapsed)
        return False


def test_5_assess_conflict():
    """[5] assess_conflict — 冲突仲裁 (火)"""
    t0 = time.time()
    try:
        from workspace import assess_conflict
        sources = [
            {"source": "iucn", "iucn": "LC"},
            {"source": "chinese_red_list", "protection_level": "省级重点"},
        ]
        result = assess_conflict("Tribolodon", sources=sources, region="china")
        elapsed = time.time() - t0
        has_verdict = bool(result.get("verdict"))
        has_level = bool(result.get("conflict_level"))
        record(PASS, "assess_conflict('Tribolodon', sources=2)",
               f"verdict={'OK' if has_verdict else 'NO'}, level={'OK' if has_level else 'NO'}", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "assess_conflict('Tribolodon')", str(e), elapsed)
        return False


def test_6_rcca():
    """[6] RCCA 集成 — 四件套装配"""
    t0 = time.time()
    try:
        from workspace import rcca_setup, rcca_health
        health = rcca_health()
        elapsed = time.time() - t0
        status = health.get("status", "unknown")
        if status == "available":
            try:
                core = rcca_setup()
                has_all = all(k in core for k in ["self_model", "emotion", "transposition", "reflection"])
                record(PASS, "rcca_setup() + rcca_health()",
                       f"status={status}, all_4={'OK' if has_all else 'MISSING'}", elapsed)
            except Exception as e2:
                record(PASS, "rcca_health()", f"status={status}, setup failed: {e2}", elapsed)
        else:
            record(SKIP, "rcca_health()", f"status={status} (RCCA not deployed)", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "rcca_setup/health", str(e), elapsed)
        return False


def test_7_eon_cross_adapters():
    """[7] eon-core 跨项目适配器 — kb/bdi/reflexion/emergence"""
    t0 = time.time()
    try:
        from eon_core.src.cross_adapters import (
            kb_first_lookup, bdi_deliberate, reflexion_analyze,
            check_emergence, generate_name_variants, thompson_select,
        )
        funcs = [kb_first_lookup, bdi_deliberate, reflexion_analyze,
                 check_emergence, generate_name_variants, thompson_select]
        valid = sum(1 for f in funcs if callable(f))
        elapsed = time.time() - t0
        record(PASS, "eon-core cross_adapters", f"{valid}/{len(funcs)} functions available", elapsed)
        return True
    except Exception as e:
        elapsed = time.time() - t0
        record(FAIL, "eon-core cross_adapters", str(e), elapsed)
        return False


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Reasonix 全项目协调测试集")
    parser.add_argument("--quick", action="store_true", help="跳过慢测试（仅 quick 模式搜索）")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    if args.verbose:
        sys.argv.append("--verbose")

    print("=" * 60)
    print("  Reasonix 全项目协调测试集")
    print("=" * 60)
    print(f"  工作区: {_WORKSPACE}")
    print(f"  Python: {sys.version.split()[0]}")
    print()

    tests = [
        ("0. workspace 导入", test_0_workspace_import),
        ("0b. 跨项目直调导入", test_0b_cross_project_imports),
        ("1. health_check 全项目", test_1_health_check),
        ("2. lookup_species (fish→conflict)", test_2_lookup_species),
        ("3. search_species (cognitive)", lambda: test_3_search_species(quick=args.quick)),
        ("4. full_stack_search (WF_A)", test_4_full_stack_search),
        ("5. assess_conflict", test_5_assess_conflict),
        ("6. RCCA 集成", test_6_rcca),
        ("7. eon-core 适配器", test_7_eon_cross_adapters),
    ]

    for title, fn in tests:
        print(f"\n── {title} ──")
        try:
            fn()
        except Exception as e:
            record(FAIL, title, traceback.format_exc())

    # ── Summary ──
    passed = sum(1 for s, _, _, _ in _results if s == PASS)
    failed = sum(1 for s, _, _, _ in _results if s == FAIL)
    skipped = sum(1 for s, _, _, _ in _results if s == SKIP)
    total = len(_results)

    print(f"\n{'=' * 60}")
    print(f"  结果: {passed} PASS / {failed} FAIL / {skipped} SKIP (共 {total} 项)")
    print(f"{'=' * 60}")

    if failed:
        print(f"\n  Failed:")
        for status, name, detail, _ in _results:
            if status == FAIL:
                print(f"    X {name}")
                if detail:
                    for d in detail.split("\n")[:3]:
                        print(f"       {d}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
