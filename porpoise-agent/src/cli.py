"""
Porpoise Agent CLI — Command-line Interface v2.0
─────────────────────────────────────────────────
基于五层标准智能体架构 (Five-Layer Cybernetic Agent Model)

Usage:
    porpoise chat       Interactive chat mode (ReAct loop)
    porpoise run TASK   Run a single research task via Orchestrator
    porpoise topology   Show current MAS topology
    porpoise doctor     Health check
"""

import argparse
import asyncio
import logging
import sys


def setup_parser() -> argparse.ArgumentParser:
    """Setup CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog="porpoise",
        description="Porpoise Agent — 江豚研究智能体 (五层闭环反馈架构)",
        epilog="服务于无锡渔业学院/淡水渔业研究中心 刘凯研究员课题组",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # chat command — 交互式对话 (ReAct 循环)
    chat_parser = subparsers.add_parser("chat", help="Interactive chat mode (ReAct loop)")
    chat_parser.add_argument(
        "--model", "-m",
        type=str,
        default="deepseek-chat",
        help="Model to use (deepseek-chat or deepseek-reasoner)",
    )
    chat_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show reasoning traces",
    )

    # run command — 单次任务 (Orchestrator + MAS)
    run_parser = subparsers.add_parser("run", help="Run a single research task via Orchestrator")
    run_parser.add_argument(
        "task",
        type=str,
        help="Research task description",
    )
    run_parser.add_argument(
        "--model", "-m",
        type=str,
        default="deepseek-chat",
        help="Model to use",
    )
    run_parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "json", "table"],
        default="markdown",
        help="Output format",
    )
    run_parser.add_argument(
        "--topology", "-t",
        type=str,
        choices=["sequential", "debate", "auto"],
        default="auto",
        help="MAS topology (auto = determined by intent)",
    )

    # topology command — 查看拓扑
    subparsers.add_parser("topology", help="Show current MAS topology")

    # doctor command — 健康检查
    doctor_parser = subparsers.add_parser("doctor", help="Health check")
    doctor_parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Run full verification (includes network checks)",
    )

    return parser


# ── Chat Mode ───────────────────────────────────────────────

async def run_chat(model: str, verbose: bool = False):
    """Run interactive chat mode with ReAct loop"""
    from src.cognitive.react_loop import ReActLoop

    print("=" * 60)
    print("  🐬 Porpoise Agent — 江豚研究智能体")
    print("  架构: 五层闭环反馈系统 (v2.0)")
    print("  服务: 无锡渔业学院/淡水渔业研究中心")
    print("  课题组: 刘凯研究员课题组")
    print("=" * 60)
    print(f"  Model: {model}")
    print(f"  Verbose: {verbose}")
    print("  Type 'quit' to exit, 'help' for commands")
    print("-" * 60)

    loop = ReActLoop(model=model)

    while True:
        try:
            user_input = input("\n[You] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye! 🐬")
                break
            if user_input.lower() == "help":
                print("Commands: quit/exit/q, help, clear, stats")
                continue
            if user_input.lower() == "clear":
                loop.steps.clear()
                print("[Session cleared]")
                continue
            if user_input.lower() == "stats":
                stats = {
                    "steps": len(loop.steps),
                    "status": loop.status.value,
                }
                if loop.bdi:
                    stats["bdi"] = loop.bdi.get_state_snapshot()
                print(f"Stats: {stats}")
                continue

            result = await loop.run(user_input)

            # Render result
            if result.get("response"):
                print(f"\n[Agent]\n{result['response']}")
            else:
                print(f"\n[Agent] Status: {result.get('status', 'unknown')}")
                if result.get("papers"):
                    print(f"  📚 Found {len(result['papers'])} papers")
                if result.get("acoustic"):
                    ac = result["acoustic"]
                    print(f"  🔊 {ac.get('n_clicks', 0)} clicks, {ac.get('n_buzzes', 0)} buzzes")

            if verbose and result.get("reasoning_traces"):
                print("\n[Reasoning]")
                for t in result["reasoning_traces"][-3:]:
                    print(f"  Step {t['step']}: {t.get('thought', '')[:100]}")

        except KeyboardInterrupt:
            print("\nGoodbye! 🐬")
            break
        except Exception as e:
            print(f"Error: {e}")


# ── Task Mode ───────────────────────────────────────────────

async def run_task(task: str, model: str, format: str, topology: str):
    """Run a single research task via Orchestrator + MAS"""
    from src.agents.orchestrator import OrchestratorAgent
    from src.agents.literature import LiteratureAgent
    from src.agents.acoustic import AcousticAgent
    from src.agents.ecology import EcologyAgent
    from src.agents.conservation import ConservationAgent
    from src.agents.critic import CriticAgent
    from src.interaction.renderer import ResponseRenderer, OutputFormat

    print(f"Task: {task}")
    print(f"Model: {model}")
    print(f"Topology: {topology}")
    print("-" * 60)

    # Setup orchestrator with agents
    orch = OrchestratorAgent(model=model)

    # Register agents (lazy init — only what's needed)
    orch.register_agent(LiteratureAgent(model=model))
    orch.register_agent(AcousticAgent(model=model))
    orch.register_agent(EcologyAgent(model="deepseek-reasoner"))
    orch.register_agent(ConservationAgent(model="deepseek-reasoner"))
    orch.register_critic(CriticAgent(model="deepseek-reasoner"))

    result = await orch.run(task)

    # Render
    fmt = {
        "markdown": OutputFormat.MARKDOWN,
        "json": OutputFormat.JSON,
        "table": OutputFormat.TABLE,
    }.get(format, OutputFormat.MARKDOWN)

    renderer = ResponseRenderer(default_format=fmt)
    output = renderer.render(result, format=fmt, verbose=True)
    print(f"\n{output.content}")

    # Show topology
    print(f"\n[Topology] {orch.get_topology_diagram()}")

    return result


# ── Topology Mode ───────────────────────────────────────────

async def run_topology():
    """Show MAS topology"""
    from src.agents.topology import TopologyBuilder
    from src.agents.literature import LiteratureAgent
    from src.agents.acoustic import AcousticAgent
    from src.agents.conservation import ConservationAgent
    from src.agents.critic import CriticAgent

    builder = TopologyBuilder()

    # Register agents for topology visualization
    builder._agents["literature"] = LiteratureAgent()
    builder._agents["acoustic"] = AcousticAgent()
    builder._agents["ecology"] = "ecology"
    builder._agents["conservation"] = ConservationAgent()
    builder._agents["critic"] = CriticAgent()

    print("=" * 60)
    print("  Porpoise Agent — MAS Topology")
    print("=" * 60)
    print()

    # SOP workflow
    print("## SOP Workflow (Standard)")
    topo_sop = builder.sequential([
        "literature", "acoustic", "conservation"
    ])
    print(topo_sop.visualize())
    print()

    # Debate mode
    print("## Debate Mode (Generator ↔ Critic)")
    topo_debate = builder.debate("literature", "critic", rounds=3)
    for nid in ["literature", "critic"]:
        if nid not in topo_debate.agents and nid in builder._agents:
            topo_debate.add_agent(nid, builder._agents[nid])
    print(topo_debate.visualize())


# ── Doctor Mode ─────────────────────────────────────────────

async def run_doctor(full: bool = False):
    """Health check — verifies all five layers"""
    from src.utils.config import config

    print("Porpoise Agent Health Check v2.0")
    print("=" * 40)
    print()

    # Python
    py_version = sys.version_info
    print(f"[{'OK' if py_version >= (3, 11) else 'WARN'}] "
          f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")

    # API key
    api_key = config.deepseek_api_key
    if api_key and api_key != "sk-your-deepseek-api-key":
        print("[OK] DeepSeek API key configured")
    else:
        print("[WARN] DeepSeek API key not set. Edit .env file.")

    # Data directory
    data_dir = config.data_dir
    if data_dir.exists():
        print(f"[OK] Data directory: {data_dir}")
    else:
        print(f"[WARN] Data directory not found: {data_dir}")

    # Five-layer verification
    print()
    print("--- Five-Layer Architecture ---")

    # Layer 1: Interaction
    try:
        from src.interaction.nlu import NLUProcessor
        nlu = NLUProcessor()
        result = nlu.parse("test")
        print(f"[OK] Layer 1 - Interaction (NLU: {result.intent.value})")
    except Exception as e:
        print(f"[FAIL] Layer 1 - Interaction: {e}")

    # Layer 2: Cognitive
    try:
        from src.cognitive.bdi import BDICoordinator
        bdi = BDICoordinator()
        print(f"[OK] Layer 2 - Cognitive (BDI: {bdi.status.value})")
    except Exception as e:
        print(f"[FAIL] Layer 2 - Cognitive: {e}")

    # Layer 3: Memory
    try:
        from src.memory.manager import MemoryManager
        mm = MemoryManager()
        print(f"[OK] Layer 3 - Memory (STM: {mm.stm.max_tokens}t)")
    except Exception as e:
        print(f"[FAIL] Layer 3 - Memory: {e}")

    # Layer 4: Mapping
    try:
        from src.mapping.serializer import EngineeringSerializer
        ser = EngineeringSerializer()
        print(f"[OK] Layer 4 - Mapping (Serializer ready)")
    except Exception as e:
        print(f"[FAIL] Layer 4 - Mapping: {e}")

    # Layer 5: Execution
    try:
        from src.execution.sandbox import SandboxExecutor
        sb = SandboxExecutor()
        print(f"[OK] Layer 5 - Execution (Sandbox ready)")
    except Exception as e:
        print(f"[FAIL] Layer 5 - Execution: {e}")

    # MAS
    try:
        from src.agents.orchestrator import OrchestratorAgent
        orch = OrchestratorAgent()
        print(f"[OK] MAS - OrchestratorAgent ready")
    except Exception as e:
        print(f"[FAIL] MAS: {e}")

    # Dependencies
    print()
    print("--- Dependencies ---")
    deps = ["numpy", "scipy", "pandas", "librosa", "sklearn", "yaml"]
    for dep in deps:
        try:
            __import__(dep.replace("sklearn", "sklearn"))
            print(f"[OK] {dep}")
        except ImportError:
            print(f"[MISS] {dep}")

    # Full check (network)
    if full:
        print()
        print("--- Network ---")
        try:
            import httpx
            print("[OK] httpx available")
        except ImportError:
            print("[MISS] httpx (install for API calls)")

        try:
            import chromadb
            print("[OK] chromadb available")
        except ImportError:
            print("[INFO] chromadb not installed (long-term memory fallback active)")


# ── Main ────────────────────────────────────────────────────

def main():
    """Main CLI entry point"""
    parser = setup_parser()
    args = parser.parse_args()

    if args.command == "chat":
        asyncio.run(run_chat(
            args.model,
            verbose=getattr(args, 'verbose', False),
        ))
    elif args.command == "run":
        asyncio.run(run_task(
            args.task,
            args.model,
            getattr(args, 'format', 'markdown'),
            getattr(args, 'topology', 'auto'),
        ))
    elif args.command == "topology":
        asyncio.run(run_topology())
    elif args.command == "doctor":
        asyncio.run(run_doctor(full=getattr(args, 'full', False)))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
