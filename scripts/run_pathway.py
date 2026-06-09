#!/usr/bin/env python3
"""
通路命令行执行工具 — 点动成线

用法:
  python scripts/run_pathway.py P1 "鳤"          # 执行通路 P1
  python scripts/run_pathway.py P2                # 执行通路 P2 (使用缓存)
  python scripts/run_pathway.py --all "Ochetobius elongatus"  # 全部通路
  python scripts/run_pathway.py --list            # 列出所有通路
"""

import sys
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))

from scripts.pathway_executor import (
    execute_pathway,
    execute_all_pathways,
    get_executor,
)


def list_pathways():
    """列出所有已注册通路。"""
    print("\n已注册通路 (三角形 + 派生):\n")
    for pw_id in ["P1_fish_to_cognitive", "P2_cognitive_to_fish",
                   "P3_cognitive_to_domain", "P4_health_to_karma"]:
        ex = get_executor(pw_id)
        if ex:
            step_count = len(ex.steps)
            print(f"  {pw_id}")
            print(f"    名称: {ex.pathway_name}")
            print(f"    步骤: {step_count} 步")
            print()
        else:
            print(f"  {pw_id}: 未注册\n")


# 短ID到全ID的映射
_SHORT_TO_FULL = {
    "P1": "P1_fish_to_cognitive",
    "P2": "P2_cognitive_to_fish",
    "P3": "P3_cognitive_to_domain",
    "P4": "P4_health_to_karma",
}


def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    if "--list" in args:
        list_pathways()
        return 0

    if "--all" in args:
        species = args[args.index("--all") + 1] if len(args) > args.index("--all") + 1 else "Ochetobius elongatus"
        print(f"\n{'═'*60}")
        print(f"  执行全部通路 — 初始输入: {species}")
        print(f"{'═'*60}")
        traces = execute_all_pathways(species)
        all_valid = True
        for pw_id, trace in traces.items():
            print(f"\n{trace.summary()}")
            if not trace.is_valid:
                all_valid = False
        print(f"\n{'═'*60}")
        print(f"  总计: {len(traces)} 条通路, {'全部通过 ✅' if all_valid else '有断裂 ❌'}")
        print(f"{'═'*60}\n")
        return 0 if all_valid else 1

    # 单通路执行 — 支持短ID
    pathway_id = args[0]
    pathway_id = _SHORT_TO_FULL.get(pathway_id, pathway_id)
    initial_input = args[1] if len(args) > 1 else "Ochetobius elongatus"

    trace = execute_pathway(pathway_id, initial_input)
    print(f"\n{trace.summary()}\n")
    return 0 if trace.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
