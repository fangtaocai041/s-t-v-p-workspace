"""
编排 Agent (Orchestrator Agent)
─────────────────────────────────
中央调度器 — 基于图拓扑的多 Agent 编排。

职责:
- 接收用户请求
- 理解意图 → 构建拓扑
- 调度 Agent 执行
- 聚合结果
- 管理人工审批节点
"""

import asyncio
import logging
import time
from typing import Any, Optional

from src.agents.base import BaseAgent
from src.agents.topology import (
    Topology, TopologyType, Message, MessageType,
    TopologyBuilder,
)
from src.cognitive.bdi import BDICoordinator, Desire
from src.interaction.nlu import NLUProcessor
from src.mapping.router import IntentRouter

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    编排 Agent — 多 Agent 系统的中央调度器

    对应 BDI:
    - Belief: 所有子 Agent 的状态和结果
    - Desire: 用户目标
    - Intention: 当前拓扑执行计划

    用法:
        orch = OrchestratorAgent()
        orch.register_agent(LiteratureAgent())
        orch.register_agent(AcousticAgent())
        orch.register_agent(ConservationAgent())
        orch.register_agent(CriticAgent())

        result = await orch.run("搜索江豚声学监测文献并评估保护状况")
    """

    def __init__(self, model: str = "deepseek-chat", memory: Any = None):
        super().__init__(name="orchestrator", model=model, memory=memory)

        self.nlu = NLUProcessor()
        self.router = IntentRouter()
        self.builder = TopologyBuilder()

        # 注册的子 Agent
        self._agents: dict[str, BaseAgent] = {}
        self._critic: Optional[BaseAgent] = None

        # 拓扑
        self._current_topology: Optional[Topology] = None

        # 结果
        self._results: dict[str, Any] = {}
        self._session_start: float = 0.0

        logger.info("OrchestratorAgent initialized")

    def register_agent(self, agent: BaseAgent):
        """注册子 Agent"""
        self._agents[agent.name] = agent
        self.builder._agents[agent.name] = agent
        logger.info(f"Orchestrator: registered {agent.name} ({agent.__class__.__name__})")

    def register_critic(self, critic: BaseAgent):
        """注册批判 Agent"""
        self._critic = critic
        self.builder._agents["critic"] = critic

    def unregister_agent(self, name: str):
        """注销子 Agent"""
        self._agents.pop(name, None)
        self.builder._agents.pop(name, None)

    async def handle_message(self, message: Any) -> dict:
        """处理编排请求"""
        return await self.run(message)

    async def run(self, input_data: Any) -> dict:
        """
        主执行入口

        Args:
            input_data: 用户输入 (str / Message / dict)

        Returns:
            dict: {"results": {...}, "topology": "..."}
        """
        self._session_start = time.time()
        self._call_count += 1

        # 1. 解析输入
        if isinstance(input_data, str):
            query = input_data
        elif hasattr(input_data, 'content'):
            query = input_data.content
        else:
            query = str(input_data)

        if isinstance(query, dict):
            query = query.get("query", str(query))
        query = str(query)

        logger.info(f"Orchestrator: processing '{query[:100]}'")

        # 2. NLU 理解
        nlu_result = self.nlu.parse(query)
        logger.info(f"Orchestrator: intent={nlu_result.intent.value}, "
                    f"confidence={nlu_result.confidence:.2f}")

        # 3. 路由
        route_result = self.router.route(
            intent=nlu_result.intent,
            entities=nlu_result.entities,
            sub_intents=nlu_result.sub_intents,
        )

        # 4. 构建拓扑
        topology = self._build_topology(nlu_result, route_result)

        # 5. 执行拓扑
        try:
            initial_msg = Message(
                id="task_0",
                type=MessageType.TASK,
                source="orchestrator",
                target=self._first_node(topology),
                content=query,
                metadata={
                    "intent": nlu_result.intent.value,
                    "entities": [(e.type, e.value) for e in nlu_result.entities],
                    "query": query,
                },
                priority=5,
            )

            exec_result = await topology.execute(initial_msg, max_iterations=30)
            self._results = exec_result

        except Exception as e:
            logger.error(f"Topology execution failed: {e}")
            return self._error_result(str(e))

        # 6. 聚合结果
        final = self._aggregate_results(
            topology, nlu_result, exec_result
        )

        # 7. 可选: Critic 审查
        if self._critic and self._should_review(final):
            review = await self._run_review(final)
            final["review"] = review

        elapsed = time.time() - self._session_start
        final["elapsed_seconds"] = elapsed
        final["topology_used"] = topology.type.value

        return final

    def _build_topology(self, nlu_result, route_result) -> Topology:
        """根据意图构建拓扑"""

        # 确定需要哪些 Agent
        needed_agents: list[str] = []

        for route in route_result.routes:
            if route.target_type.value == "agent":
                needed_agents.append(route.target)
            elif route.target in self._agents:
                needed_agents.append(route.target)

        # 如果没有特定 Agent，使用默认线性链:
        #   literature → acoustic → ecology → conservation
        if not needed_agents:
            needed_agents = ["literature"]

            # 根据子意图添加
            sub_intents = nlu_result.sub_intents
            all_intents = [nlu_result.intent] + sub_intents

            for intent in all_intents:
                intent_val = intent.value if hasattr(intent, 'value') else str(intent)
                if "acoustic" in intent_val or "click" in intent_val:
                    if "acoustic" not in needed_agents:
                        needed_agents.append("acoustic")
                if "conservation" in intent_val or "threat" in intent_val:
                    if "conservation" not in needed_agents:
                        needed_agents.append("conservation")
                if "abundance" in intent_val or "habitat" in intent_val:
                    if "ecology" not in needed_agents:
                        needed_agents.append("ecology")

        # 过滤出已注册的 Agent
        available = [a for a in needed_agents if a in self._agents or a in self.builder._agents]

        if not available:
            # 降级: 只用 literature
            available = ["literature"] if "literature" in self._agents else []

        # 构建拓扑
        if len(available) == 1:
            # 单 Agent: 直接调用
            topo = Topology(type=TopologyType.SEQUENTIAL)
            for a in available:
                if a in self._agents:
                    topo.add_agent(a, self._agents[a])
                elif a in self.builder._agents:
                    topo.add_agent(a, self.builder._agents[a])

        elif len(available) >= 2:
            # 顺序流水线 (默认 SOP)
            topo = self.builder.sequential(available)

        else:
            topo = Topology(type=TopologyType.SEQUENTIAL)

        self._current_topology = topo
        logger.info(f"Orchestrator: topology {topo.type.value} with {available}")
        return topo

    def _first_node(self, topology: Topology) -> str:
        """获取拓扑中的第一个节点"""
        # 找到入度为 0 的节点
        targets = {e.target for e in topology.edges}
        for node_id in topology.agents:
            if node_id not in targets:
                return node_id
        # fallback
        if topology.agents:
            return list(topology.agents.keys())[0]
        return "literature"

    def _aggregate_results(
        self,
        topology: Topology,
        nlu_result,
        exec_result: dict,
    ) -> dict:
        """聚合各 Agent 的结果"""
        aggregated: dict[str, Any] = {
            "query": self.bdi.belief.user_query,
            "intent": nlu_result.intent.value,
            "phase": "completed",
            "status": "completed",
        }

        # 合并所有 Agent 的结果
        all_papers = []
        acoustic_data = None
        conservation_data = None
        ecology_data = None
        errors = []

        for agent_name, result in exec_result.get("results", {}).items():
            if isinstance(result, dict):
                if result.get("agent") == "literature":
                    all_papers.extend(result.get("papers", []))
                elif result.get("agent") == "acoustic":
                    acoustic_data = result
                elif result.get("agent") == "conservation":
                    conservation_data = result
                elif result.get("agent") == "ecology":
                    ecology_data = result

                if result.get("error"):
                    errors.append(f"[{agent_name}] {result['error']}")

        if all_papers:
            aggregated["papers"] = all_papers
            aggregated["n_papers"] = len(all_papers)
        if acoustic_data:
            aggregated["acoustic"] = acoustic_data
        if conservation_data:
            aggregated["conservation"] = conservation_data
        if ecology_data:
            aggregated["ecology"] = ecology_data
        if errors:
            aggregated["errors"] = errors

        # 生成响应消息
        aggregated["message"] = self._generate_response_message(aggregated)

        return aggregated

    def _generate_response_message(self, aggregated: dict) -> str:
        """生成人类可读的响应消息"""
        parts = []

        if aggregated.get("n_papers", 0) > 0:
            parts.append(
                f"📚 找到 {aggregated['n_papers']} 篇相关文献"
            )

        if aggregated.get("acoustic"):
            ac = aggregated["acoustic"]
            n_clicks = ac.get("n_clicks", 0)
            n_buzzes = ac.get("n_buzzes", 0)
            if n_clicks > 0:
                parts.append(
                    f"🔊 检测到 {n_clicks} 个 click 脉冲"
                    + (f", 含 {n_buzzes} 个 buzz 事件" if n_buzzes > 0 else "")
                )

        if aggregated.get("conservation"):
            cons = aggregated["conservation"]
            if cons.get("verdict"):
                parts.append(f"🛡️ 保护评估: {cons['verdict']}")

        if aggregated.get("errors"):
            parts.append(f"⚠️ {len(aggregated['errors'])} 个步骤出现问题")

        if not parts:
            parts.append("✅ 任务完成")

        return "\n".join(parts)

    async def _run_review(self, result: dict) -> dict:
        """运行 Critic 审查"""
        if not self._critic:
            return {}

        review_msg = Message(
            id="review_0",
            type=MessageType.FEEDBACK,
            source="orchestrator",
            target="critic",
            content=result,
            metadata={"source_agent": "orchestrator_aggregated"},
        )

        review_result = await self._critic.handle_message(review_msg)
        return review_result

    def _should_review(self, result: dict) -> bool:
        """是否需要 Critic 审查"""
        # 包含保护建议 → 需要审查
        if result.get("conservation", {}).get("requires_approval"):
            return True
        # 有错误 → 需要审查
        if result.get("errors"):
            return True
        return False

    def _error_result(self, error: str) -> dict:
        """错误结果"""
        return {
            "phase": "error",
            "status": "failed",
            "error": error,
            "message": f"❌ 执行失败: {error}",
        }

    def get_topology_diagram(self) -> str:
        """获取当前拓扑图"""
        if self._current_topology:
            return self._current_topology.visualize()
        return "No topology built yet"

    def stats(self) -> dict:
        base_stats = super().stats()
        base_stats["registered_agents"] = list(self._agents.keys())
        base_stats["has_critic"] = self._critic is not None
        if self._current_topology:
            base_stats["topology"] = self._current_topology.type.value
        return base_stats
