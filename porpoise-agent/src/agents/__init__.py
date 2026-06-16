"""
多智能体系统 (Multi-Agent System)
───────────────────────────────────
基于图论的分布式 Agent 架构。

组件:
- Topology: 图拓扑引擎 (节点 + 边 + 消息路由)
- BaseAgent: Agent 基类 (BDI + 工具集 + 消息处理)
- LiteratureAgent: 文献分析
- AcousticAgent: 声学分析
- EcologyAgent: 生态分析
- ConservationAgent: 保护评估
- CriticAgent: 批判审查
- OrchestratorAgent: 中央编排
"""

from src.agents.topology import (
    Topology,
    TopologyType,
    TopologyBuilder,
    Message,
    MessageType,
    Edge,
)
from src.agents.base import BaseAgent
from src.agents.literature import LiteratureAgent
from src.agents.acoustic import AcousticAgent
from src.agents.ecology import EcologyAgent
from src.agents.conservation import ConservationAgent
from src.agents.critic import CriticAgent
from src.agents.orchestrator import OrchestratorAgent

__all__ = [
    # Topology
    "Topology",
    "TopologyType",
    "TopologyBuilder",
    "Message",
    "MessageType",
    "Edge",
    # Agents
    "BaseAgent",
    "LiteratureAgent",
    "AcousticAgent",
    "EcologyAgent",
    "ConservationAgent",
    "CriticAgent",
    "OrchestratorAgent",
]
