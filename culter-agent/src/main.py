#!/usr/bin/env python3
"""Culter Agent CLI — 鲌类专研入口"""

import sys
from pathlib import Path

# Add project root to path (parent of src/)
_proj_root = str(Path(__file__).resolve().parent.parent)
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from src.agent.orchestrator import CulterOrchestrator


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="culter", description="Culter Agent — 鲌类专研 (P₃)")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="执行鲌类研究查询")
    p_run.add_argument("--query", "-q", required=True)

    args = parser.parse_args()
    if args.command == "run":
        orch = CulterOrchestrator()
        result = orch.run(args.query)
        mode = result.get("mode", "standalone")
        print(f"\n{'='*60}")
        print(f"  {result.get('agent', 'Culter Agent (P₃)')}")
        print(f"  Species: {result.get('species', 'Culter alburnus')}")
        print(f"  Mode:    {mode}")
        # Phase/skill: present only in integrated mode
        if mode == "integrated":
            print(f"  Phase:   {result.get('phase', 'N/A')}")
            print(f"  Skill:   {result.get('skill', 'N/A')}")
            print(f"  Status:  {result.get('status', 'N/A')}")
        else:
            phases = result.get("phases_executed", [])
            print(f"  Phases:  {', '.join(phases) if phases else 'N/A'}")
            print(f"  Papers:  {result.get('total_papers', 0)}")
        print(f"{'='*60}\n")
        if mode == "integrated":
            print(result.get("delegate_message", ""))
        else:
            print(result.get("synthesis", ""))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
