"""
向后兼容导出 — 旧模块已迁移到五层架构。

映射:
  Orchestrator   → src/agents/orchestrator.py
  PorpoiseLoop   → src/cognitive/react_loop.py
  ToolRegistry   → src/execution/tool_registry.py
  MemoryStore    → src/memory/manager.py
"""

from src.agents.orchestrator import OrchestratorAgent as Orchestrator
from src.cognitive.react_loop import ReActLoop as PorpoiseLoop
from src.execution.tool_registry import ToolRegistry, tools
from src.memory.manager import MemoryManager as MemoryStore

__all__ = [
    "Orchestrator",
    "PorpoiseLoop",
    "ToolRegistry",
    "tools",
    "MemoryStore",
]
