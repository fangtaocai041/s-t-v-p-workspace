#!/usr/bin/env python3
"""Coilia Agent CLI — 刀鲚专研入口 (P₂).

三角闭环架构:
  fish ── cognitive ── eon-core
                │
          P₂ 刀鲚专研 (本 Agent)

搜索协议: cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md
本 Agent 只做物种约束 + 领域专研分析。
"""

import sys
from pathlib import Path

# 1. Add D:\Reasonix to sys.path for shared protocols
_reasonix_root = str(Path(__file__).resolve().parent.parent.parent)  # D:\Reasonix
if _reasonix_root not in sys.path:
    sys.path.insert(0, _reasonix_root)

# 2. Add project root for local imports
_proj_root = str(Path(__file__).resolve().parent.parent)
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from src.agent.orchestrator import CoiliaOrchestrator


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="coilia",
        description="Coilia Agent — 刀鲚专研 (P₂) · 三角闭环衍生项目"
    )
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="执行刀鲚研究查询")
    p_run.add_argument("--query", "-q", required=True)

    args = parser.parse_args()
    if args.command == "run":
        orch = CoiliaOrchestrator()
        result = orch.run(args.query)

        print(f"\n{'='*60}")
        print(f"  {result['agent_name']} ({result['agent_id']})")
        print(f"  Species: {result['species_scientific']}")
        print(f"  Theme:   {result['theme']}")
        print(f"  Phase:   {result['phase']}")
        print(f"{'='*60}\n")

        print("🔍 搜索请求 (遵循 Unified Search Protocol):")
        print(f"   物种: {result['species_scientific']}")
        print(f"   变体: {', '.join(result['species_variants'])}")
        print(f"   查询: {result['query']}")
        print(f"   方向: {result['theme']}")
        print()
        print("   由 cognitive-search-engine 执行多引擎并行搜索")
        print("   (参见 cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md)")
        print()
        print("💡 搜索完成后可调用 analyze() 做刀鲚专研分析")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
