"""
多智能体拓扑 (Multi-Agent Topology)
─────────────────────────────────────
基于图论的 MAS 通信架构。

每个 Agent 视作节点 (Node)，通信通道视作边 (Edge)。
研究的重点在于设计有向网络结构，以确保上下文信息
在流转过程中熵增最小，避免关键信息衰减。

拓扑类型:
- SEQUENTIAL:    线性流水线 (A → B → C → D)
- HIERARCHICAL:  层级结构 (Orchestrator → Workers)
- STAR:          星型 (Hub → Spokes)
- DEBATE:        对抗博弈 (Generator ↔ Critic)
- DAG:           有向无环图 (灵活路由)
- DYNAMIC:       动态路由 (LLM 决策下一跳)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import asyncio

logger = logging.getLogger(__name__)


class TopologyType(str, Enum):
    """拓扑类型"""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    STAR = "star"
    DEBATE = "debate"
    DAG = "dag"
    DYNAMIC = "dynamic"


class MessageType(str, Enum):
    """消息类型"""
    TASK = "task"               # 任务分配
    RESULT = "result"           # 执行结果
    QUERY = "query"             # 查询请求
    FEEDBACK = "feedback"       # 反馈/批判
    APPROVAL = "approval"       # 审批请求
    INFO = "info"               # 信息传递
    ERROR = "error"             # 错误报告


@dataclass
class Message:
    """节点间通信消息"""
    id: str
    type: MessageType
    source: str                     # 发送者 node_id
    target: str                     # 接收者 node_id
    content: Any
    metadata: dict = field(default_factory=dict)
    priority: int = 0               # 0-10, 越高越优先
    requires_response: bool = False


@dataclass
class Edge:
    """图中的边 — Agent 间的通信通道"""
    source: str                     # 源节点 ID
    target: str                     # 目标节点 ID
    weight: float = 1.0             # 边权重 (影响消息优先级)
    condition: Optional[str] = None # 条件: "if result.confidence > 0.7"
    description: str = ""


@dataclass
class Topology:
    """
    多智能体拓扑

    用法:
        topo = Topology(type=TopologyType.SEQUENTIAL)
        topo.add_agent("literature", LiteratureAgent())
        topo.add_agent("acoustic", AcousticAgent())
        topo.add_edge("literature", "acoustic", description="文献结果→声学分析")
        topo.add_edge("acoustic", "conservation", condition="if result.n_clicks > 0")
        await topo.execute(initial_message)
    """
    type: TopologyType = TopologyType.DAG
    agents: dict[str, Any] = field(default_factory=dict)  # {node_id: Agent}
    edges: list[Edge] = field(default_factory=list)
    message_queue: list[Message] = field(default_factory=list)
    message_history: list[Message] = field(default_factory=list)

    def add_agent(self, node_id: str, agent: Any):
        """添加 Agent 节点"""
        self.agents[node_id] = agent
        agent.node_id = node_id
        logger.info(f"Topology: +Agent {node_id} ({agent.__class__.__name__})")

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float = 1.0,
        condition: Optional[str] = None,
        description: str = "",
    ):
        """添加边"""
        edge = Edge(
            source=source, target=target,
            weight=weight, condition=condition, description=description,
        )
        self.edges.append(edge)
        logger.debug(f"Topology: edge {source} → {target}")

    def remove_agent(self, node_id: str):
        """移除节点及关联的边"""
        self.agents.pop(node_id, None)
        self.edges = [
            e for e in self.edges
            if e.source != node_id and e.target != node_id
        ]

    def get_neighbors(self, node_id: str) -> list[str]:
        """获取下游邻居"""
        return [e.target for e in self.edges if e.source == node_id]

    def get_upstream(self, node_id: str) -> list[str]:
        """获取上游节点"""
        return [e.source for e in self.edges if e.target == node_id]

    def route(
        self,
        message: Message,
        current_node: str,
    ) -> list[Message]:
        """
        路由消息 — 从当前节点发送到下游

        考虑条件边 (condition edge):
            if condition evaluates to True → send to that target

        Returns:
            list[Message]: 生成的下一批消息
        """
        next_messages = []

        for edge in self.edges:
            if edge.source != current_node:
                continue

            # 检查条件
            if edge.condition:
                if not self._evaluate_condition(edge.condition, message):
                    continue

            next_msg = Message(
                id=f"msg_{len(self.message_history)}",
                type=MessageType.TASK,
                source=current_node,
                target=edge.target,
                content=message.content,
                metadata={
                    **message.metadata,
                    "route_weight": edge.weight,
                    "route_description": edge.description,
                },
                priority=int(message.priority * edge.weight),
            )
            next_messages.append(next_msg)

        return next_messages

    def _evaluate_condition(self, condition: str, message: Message) -> bool:
        """评估条件表达式"""
        try:
            # 简单条件解析
            import re

            # 匹配: result.field > value
            match = re.match(
                r'result\.(\w+)\s*(==|!=|>|<|>=|<=)\s*([\w.]+)',
                condition,
            )
            if match:
                field = match.group(1)
                op = match.group(2)
                value = match.group(3)

                # 从 message.content 中提取字段值
                content = message.content
                if isinstance(content, dict):
                    field_value = content.get(field)
                elif hasattr(content, field):
                    field_value = getattr(content, field)
                else:
                    return True  # 无法评估 → 通过

                # 类型转换
                try:
                    cmp_value = float(value)
                    field_value = float(field_value) if field_value is not None else 0
                except (ValueError, TypeError):
                    cmp_value = value

                # 执行比较
                ops = {
                    "==": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                    ">=": lambda a, b: a >= b,
                    "<=": lambda a, b: a <= b,
                }
                return ops.get(op, lambda a, b: True)(field_value, cmp_value)

            return True  # 无法解析条件 → 默认通过

        except Exception as e:
            logger.debug(f"Condition evaluation failed: {e}")
            return True

    async def execute(
        self,
        initial_message: Message,
        max_iterations: int = 20,
    ) -> dict[str, Any]:
        """
        执行拓扑 — 按图结构调度 Agent

        算法: BFS 消息传播
        1. 初始消息放入队列
        2. 取出消息 → 目标 Agent 执行
        3. Agent 返回结果 → 路由到下游
        4. 重复直到队列空或超限

        Returns:
            dict: {node_id: result, ...}
        """
        self.message_queue = [initial_message]
        results: dict[str, Any] = {}
        iteration = 0

        while self.message_queue and iteration < max_iterations:
            iteration += 1
            msg = self.message_queue.pop(0)
            self.message_history.append(msg)

            target_agent = self.agents.get(msg.target)
            if not target_agent:
                logger.warning(f"No agent at {msg.target}, skipping message")
                continue

            # Agent 执行
            try:
                if hasattr(target_agent, 'handle_message'):
                    result = await target_agent.handle_message(msg)
                elif hasattr(target_agent, 'run'):
                    result = await target_agent.run(msg.content)
                else:
                    result = f"Agent {msg.target} has no handler"

                results[msg.target] = result

                # 创建结果消息
                result_msg = Message(
                    id=f"result_{msg.id}",
                    type=MessageType.RESULT,
                    source=msg.target,
                    target="",  # 由路由决定
                    content=result,
                    metadata=msg.metadata,
                    priority=msg.priority,
                )

                # 路由到下游
                next_msgs = self.route(result_msg, msg.target)
                self.message_queue.extend(next_msgs)

            except Exception as e:
                logger.error(f"Agent {msg.target} failed: {e}")
                error_msg = Message(
                    id=f"error_{msg.id}",
                    type=MessageType.ERROR,
                    source=msg.target,
                    target=msg.source,  # 回传给上游
                    content={"error": str(e)},
                    metadata=msg.metadata,
                    priority=10,  # 高优先级
                )
                self.message_queue.append(error_msg)

        return {
            "results": results,
            "iterations": iteration,
            "messages_processed": len(self.message_history),
            "remaining_queue": len(self.message_queue),
        }

    def visualize(self) -> str:
        """生成拓扑可视化 (ASCII)"""
        lines = [f"Topology: {self.type.value}", ""]
        lines.append("Agents:")
        for node_id, agent in self.agents.items():
            lines.append(f"  [{node_id}] {agent.__class__.__name__}")
        lines.append("")
        lines.append("Edges:")
        for edge in self.edges:
            cond = f" [{edge.condition}]" if edge.condition else ""
            desc = f" # {edge.description}" if edge.description else ""
            lines.append(f"  {edge.source} → {edge.target}{cond}{desc}")
        return "\n".join(lines)


# ── 拓扑构建器 ──────────────────────────────────────────────

class TopologyBuilder:
    """
    拓扑构建器 — 提供常见拓扑的快速构建

    用法:
        builder = TopologyBuilder()
        topo = builder.sequential(["A", "B", "C"])
        topo = builder.hierarchical("orchestrator", ["worker1", "worker2"])
        topo = builder.debate("generator", "critic")
    """

    def __init__(self):
        self._agents: dict[str, Any] = {}

    def sequential(self, node_ids: list[str]) -> Topology:
        """线性流水线: A → B → C"""
        topo = Topology(type=TopologyType.SEQUENTIAL)
        for nid in node_ids:
            if nid in self._agents:
                topo.add_agent(nid, self._agents[nid])
        for i in range(len(node_ids) - 1):
            topo.add_edge(node_ids[i], node_ids[i + 1])
        return topo

    def hierarchical(self, root_id: str, worker_ids: list[str]) -> Topology:
        """层级结构: Root → Workers → Root"""
        topo = Topology(type=TopologyType.HIERARCHICAL)
        if root_id in self._agents:
            topo.add_agent(root_id, self._agents[root_id])
        for wid in worker_ids:
            if wid in self._agents:
                topo.add_agent(wid, self._agents[wid])
            topo.add_edge(root_id, wid, description="Task dispatch")
            topo.add_edge(wid, root_id, description="Result return")
        return topo

    def star(self, hub_id: str, spoke_ids: list[str]) -> Topology:
        """星型: Hub ↔ Spokes"""
        topo = Topology(type=TopologyType.STAR)
        if hub_id in self._agents:
            topo.add_agent(hub_id, self._agents[hub_id])
        for sid in spoke_ids:
            if sid in self._agents:
                topo.add_agent(sid, self._agents[sid])
            topo.add_edge(hub_id, sid)
            topo.add_edge(sid, hub_id)
        return topo

    def debate(self, agent_a: str, agent_b: str, rounds: int = 3) -> Topology:
        """对抗博弈: A ↔ B (多轮)"""
        topo = Topology(type=TopologyType.DEBATE)
        for nid in [agent_a, agent_b]:
            if nid in self._agents:
                topo.add_agent(nid, self._agents[nid])
        topo.add_edge(agent_a, agent_b, description="Generator output → Critic review")
        topo.add_edge(agent_b, agent_a, description="Critic feedback → Generator revision")
        return topo

    def dag(self, edges: list[tuple[str, str, Optional[str]]]) -> Topology:
        """
        有向无环图

        Args:
            edges: [(source, target, condition?), ...]
        """
        topo = Topology(type=TopologyType.DAG)
        node_ids = set()
        for src, tgt, *_ in edges:
            node_ids.add(src)
            node_ids.add(tgt)
        for nid in node_ids:
            if nid in self._agents:
                topo.add_agent(nid, self._agents[nid])

        for edge_spec in edges:
            src = edge_spec[0]
            tgt = edge_spec[1]
            cond = edge_spec[2] if len(edge_spec) > 2 else None
            topo.add_edge(src, tgt, condition=cond)
        return topo
