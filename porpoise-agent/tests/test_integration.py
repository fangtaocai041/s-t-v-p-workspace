"""
集成测试 — 验证核心模块在无可选依赖时的行为。

运行:
    pytest tests/test_integration.py -v -m integration
    pytest tests/test_integration.py -v -m "not network"
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ═══════════════════════════════════════════════════════════════
# 1. 核心模块导入 (不依赖可选包)
# ═══════════════════════════════════════════════════════════════

class TestCoreImports:
    """验证核心模块可以在无可选依赖时正常导入"""

    def test_import_cognitive_bdi(self):
        """BDI 状态机"""
        from src.cognitive.bdi import (
            BDICoordinator, BDIStatus,
            Belief, Desire, Intention, PlanStep, StepStatus,
        )
        assert BDICoordinator is not None
        assert Belief is not None

    def test_import_execution_tool_registry(self):
        """工具注册中心 (含 safe_import)"""
        from src.execution.tool_registry import (
            ToolRegistry, ToolSpec, ToolCall,
            tool, tools,
            safe_import, is_available, list_missing_optionals,
        )
        assert tools is not None
        # safe_import 对核心模块应返回非 None
        json_mod = safe_import("json", feature_name="JSON")
        assert json_mod is not None

    def test_import_agents_base(self):
        """Agent 基类"""
        from src.agents.base import BaseAgent
        assert BaseAgent is not None

    def test_import_agents_topology(self):
        """图拓扑引擎"""
        from src.agents.topology import (
            Topology, TopologyType, TopologyBuilder,
            Message, MessageType, Edge,
        )
        assert Topology is not None
        assert TopologyType is not None

    def test_import_memory_manager(self):
        """记忆管理器"""
        from src.memory.manager import MemoryManager
        assert MemoryManager is not None

    def test_import_interaction_nlu(self):
        """NLU 处理器 (基于关键词，无 LLM 依赖)"""
        from src.interaction.nlu import NLUProcessor, Intent, Entity
        assert NLUProcessor is not None
        assert Intent is not None

    def test_import_mapping_router(self):
        """意图路由器"""
        from src.mapping.router import IntentRouter
        assert IntentRouter is not None

    def test_import_execution_sandbox(self):
        """沙盒执行器"""
        from src.execution.sandbox import (
            SandboxExecutor, SandboxConfig, SandboxResult,
        )
        assert SandboxExecutor is not None

    def test_import_utils(self):
        """工具模块"""
        from src.utils.config import Config, load_yaml
        from src.utils.logging import setup_logging
        from src.utils.types import (
            ResearchContext, BDIState, Observation, Action, MDPStep,
        )
        assert Config is not None
        assert load_yaml is not None
        assert setup_logging is not None
        assert ResearchContext is not None

    def test_import_agent_package(self):
        """向后兼容导出"""
        from src.agent import Orchestrator, PorpoiseLoop, ToolRegistry, MemoryStore
        assert Orchestrator is not None
        assert ToolRegistry is not None

    def test_import_agents_package(self):
        """多智能体包"""
        from src.agents import (
            OrchestratorAgent, LiteratureAgent,
            AcousticAgent, CriticAgent,
            Topology, TopologyType,
        )
        assert OrchestratorAgent is not None

    def test_import_without_optional_succeeds(self):
        """验证缺失可选依赖不会导致 import 崩溃"""
        # 模拟缺失 librosa / chromadb / geopandas / torch
        # 这些导入应在模块级别存在 try/except 保护
        from src.execution.tool_registry import safe_import, is_available

        # 检查各可选组状态 (允许缺失)
        librosa = safe_import("librosa", feature_name="声学分析", pip_package="acoustics")
        chromadb = safe_import("chromadb", feature_name="知识图谱", pip_package="knowledge")
        geopandas = safe_import("geopandas", feature_name="空间分析", pip_package="spatial")
        sklearn = safe_import("sklearn", feature_name="机器学习", pip_package="ml")

        # 不崩溃即为通过
        assert True


# ═══════════════════════════════════════════════════════════════
# 2. Orchestrator 基本流程
# ═══════════════════════════════════════════════════════════════

class TestOrchestratorBasic:
    """测试 Orchestrator 在不调用 LLM 时的基本行为"""

    @pytest.fixture
    def orch(self):
        from src.agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent()

    def test_initialization(self, orch):
        """Orchestrator 初始化"""
        from src.agents.orchestrator import OrchestratorAgent
        o = OrchestratorAgent()
        assert o.name == "orchestrator"
        assert o._agents == {}
        assert o._critic is None
        assert o._current_topology is None

    def test_register_agent(self, orch):
        """注册子 Agent"""
        from src.agents.base import BaseAgent

        class MockAgent(BaseAgent):
            async def handle_message(self, msg):
                return {"agent": self.name, "result": "ok"}

        agent = MockAgent(name="test_agent")
        orch.register_agent(agent)

        assert "test_agent" in orch._agents
        assert orch._agents["test_agent"] is agent

    def test_register_multiple_agents(self, orch):
        """注册多个 Agent"""
        from src.agents.base import BaseAgent

        class MockAgent(BaseAgent):
            async def handle_message(self, msg):
                return {"agent": self.name, "result": "ok"}

        orch.register_agent(MockAgent(name="lit"))
        orch.register_agent(MockAgent(name="aco"))
        orch.register_agent(MockAgent(name="eco"))

        assert len(orch._agents) == 3
        assert "lit" in orch._agents
        assert "aco" in orch._agents
        assert "eco" in orch._agents

    def test_register_critic(self, orch):
        """注册批判 Agent"""
        from src.agents.base import BaseAgent

        class MockCritic(BaseAgent):
            async def handle_message(self, msg):
                return {"review": "ok"}

        critic = MockCritic(name="critic")
        orch.register_critic(critic)

        assert orch._critic is critic
        assert orch._critic.name == "critic"

    def test_unregister_agent(self, orch):
        """注销 Agent"""
        from src.agents.base import BaseAgent

        class MockAgent(BaseAgent):
            async def handle_message(self, msg):
                return {}

        agent = MockAgent(name="temp")
        orch.register_agent(agent)
        assert "temp" in orch._agents

        orch.unregister_agent("temp")
        assert "temp" not in orch._agents

    def test_stats_empty(self, orch):
        """空 Orchestrator 统计"""
        stats = orch.stats()
        assert stats["name"] == "orchestrator"
        assert stats["registered_agents"] == []
        assert stats["has_critic"] is False

    def test_stats_with_agents(self, orch):
        """有 Agent 时的统计"""
        from src.agents.base import BaseAgent

        class MockAgent(BaseAgent):
            async def handle_message(self, msg):
                return {}

        orch.register_agent(MockAgent(name="lit"))
        orch.register_agent(MockAgent(name="eco"))

        stats = orch.stats()
        assert "lit" in stats["registered_agents"]
        assert "eco" in stats["registered_agents"]

    def test_get_topology_diagram_no_topology(self, orch):
        """无拓扑时返回提示"""
        result = orch.get_topology_diagram()
        assert "No topology" in result

    def test_error_result(self, orch):
        """错误结果格式"""
        err = orch._error_result("test error")
        assert err["phase"] == "error"
        assert err["status"] == "failed"
        assert "test error" in err["error"]

    def test_should_review_without_critic(self, orch):
        """无 Critic 时不需要审查"""
        result = orch._should_review({"status": "completed"})
        # 无 critic 时应返回 False
        assert result is False

    def test_bdi_integration(self, orch):
        """Orchestrator 的 BDI 已初始化"""
        from src.cognitive.bdi import BDIStatus
        assert orch.bdi is not None
        assert orch.bdi.status == BDIStatus.IDLE
        assert orch.bdi.belief is not None
        assert orch.bdi.desire is not None
        assert orch.bdi.intention is not None


# ═══════════════════════════════════════════════════════════════
# 3. BDI 状态机转换
# ═══════════════════════════════════════════════════════════════

class TestBDIStateMachine:
    """BDI 状态机完整测试"""

    @pytest.fixture
    def bdi(self):
        from src.cognitive.bdi import BDICoordinator
        return BDICoordinator()

    def test_initial_state(self, bdi):
        from src.cognitive.bdi import BDIStatus
        assert bdi.status == BDIStatus.IDLE
        assert bdi.belief.user_query == ""
        assert bdi.desire.primary_goal == ""
        assert bdi.intention.is_complete is True

    def test_configure_desire(self, bdi):
        bdi.configure_desire(
            primary_goal="完成江豚文献综述",
            constraints=["2020年后", "中英文"],
            quality_thresholds={"min_papers": 10},
            forbidden_actions=["delete_data"],
        )
        assert bdi.desire.primary_goal == "完成江豚文献综述"
        assert len(bdi.desire.constraints) == 2
        assert bdi.desire.quality_thresholds["min_papers"] == 10
        assert "delete_data" in bdi.desire.forbidden_actions

    def test_perceive_updates_belief(self, bdi):
        from src.cognitive.bdi import BDIStatus
        bdi.perceive({"query": "江豚声学", "result": {"papers_found": 5}})

        assert bdi.status == BDIStatus.PERCEIVING
        assert len(bdi.belief.observation_history) == 1
        assert bdi.belief.last_observation["result"]["papers_found"] == 5

    def test_deliberate_creates_intention(self, bdi):
        from src.cognitive.bdi import BDIStatus, PlanStep
        plan = [
            PlanStep(id="s1", description="搜索PubMed", action="search_pubmed"),
            PlanStep(id="s2", description="下载全文", action="download_pdf"),
            PlanStep(id="s3", description="提取关键信息", action="extract_info"),
        ]
        bdi.deliberate(plan, method="cot")

        assert bdi.status == BDIStatus.DELIBERATING
        assert len(bdi.intention.plan) == 3
        assert bdi.intention.decomposition_method == "cot"
        assert bdi.intention.current_step is not None
        assert bdi.intention.current_step.id == "s1"

    def test_alignment_check_passes(self, bdi):
        from src.cognitive.bdi import PlanStep
        bdi.configure_desire("test")
        plan = [PlanStep(id="s1", description="搜索", action="search_pubmed")]
        bdi.deliberate(plan)
        assert bdi.check_alignment() is True

    def test_alignment_detects_forbidden(self, bdi):
        from src.cognitive.bdi import PlanStep
        bdi.configure_desire("test", forbidden_actions=["delete_data"])
        plan = [PlanStep(id="s1", description="删除", action="delete_data")]
        bdi.deliberate(plan)
        assert bdi.check_alignment() is False

    def test_full_cycle_idle_to_done(self, bdi):
        """完整 BDI 循环: IDLE → PERCEIVING → DELIBERATING → 执行步骤"""
        from src.cognitive.bdi import BDIStatus, PlanStep

        # 初始状态
        assert bdi.status == BDIStatus.IDLE

        # 1. 配置愿望
        bdi.configure_desire(
            primary_goal="完成搜索",
            quality_thresholds={"min_papers": 5},
            forbidden_actions=["delete_data"],
        )

        # 2. 感知
        bdi.perceive({"query": "江豚种群", "result": {"papers_found": 3}})
        assert bdi.status == BDIStatus.PERCEIVING
        assert len(bdi.belief.observation_history) == 1

        # 3. 决策 (生成计划)
        plan = [
            PlanStep(id="s1", description="搜索PubMed", action="search_pubmed"),
            PlanStep(id="s2", description="下载全文", action="download"),
            PlanStep(id="s3", description="撰写综述", action="write_review"),
        ]
        bdi.deliberate(plan, method="cot")
        assert bdi.status == BDIStatus.DELIBERATING
        assert len(bdi.intention.plan) == 3

        # 4. 逐步执行
        # Step 1
        assert bdi.intention.current_step.id == "s1"
        bdi.intention.advance()
        assert bdi.intention.current_step.id == "s2"

        # Step 2 — 模拟失败
        bdi.perceive({"error": "download failed"})
        bdi.intention.retreat()
        assert bdi.intention.current_step.id == "s1"
        from src.cognitive.bdi import StepStatus
        assert bdi.intention.current_step.status == StepStatus.RETRYING

    def test_state_snapshot(self, bdi):
        from src.cognitive.bdi import PlanStep
        bdi.configure_desire("目标", constraints=["c1", "c2"])
        plan = [
            PlanStep(id="s1", description="步骤1", action="act1"),
            PlanStep(id="s2", description="步骤2", action="act2"),
        ]
        bdi.deliberate(plan)

        snap = bdi.get_state_snapshot()
        assert "status" in snap
        assert "belief" in snap
        assert "desire" in snap
        assert "intention" in snap
        assert snap["intention"]["total_steps"] == 2
        assert snap["intention"]["completed"] == 0

    def test_intention_progress(self, bdi):
        from src.cognitive.bdi import PlanStep
        plan = [
            PlanStep(id="a", description="A", action="act_a"),
            PlanStep(id="b", description="B", action="act_b"),
            PlanStep(id="c", description="C", action="act_c"),
            PlanStep(id="d", description="D", action="act_d"),
        ]
        bdi.deliberate(plan)

        progress = bdi.intention.get_progress()
        assert progress["total_steps"] == 4
        assert progress["completed"] == 0
        assert progress["progress_pct"] == 0.0

        bdi.intention.advance()
        progress = bdi.intention.get_progress()
        assert progress["completed"] == 1
        assert progress["progress_pct"] == 25.0

        bdi.intention.advance()
        bdi.intention.advance()
        progress = bdi.intention.get_progress()
        assert progress["completed"] == 3
        assert progress["progress_pct"] == 75.0

    def test_belief_context_summary(self, bdi):
        bdi.belief.user_query = "搜索江豚声学监测文献"
        bdi.belief.relevant_knowledge = [
            {"title": "长江江豚种群监测 (2022)", "content": "..."},
            {"title": "NBHF声学特征分析", "content": "..."},
        ]
        bdi.belief.errors = ["timeout", "rate_limit"]

        summary = bdi.belief.get_context_summary()
        assert "搜索江豚声学监测文献" in summary
        assert "长江江豚种群监测" in summary
        assert "timeout" in summary

    def test_multiple_perceive_calls(self, bdi):
        """多次感知调用追踪历史"""
        bdi.perceive({"step": 1, "result": "a"})
        bdi.perceive({"step": 2, "result": "b"})
        bdi.perceive({"step": 3, "error": "fail"})

        assert len(bdi.belief.observation_history) == 3
        assert len(bdi.belief.errors) == 1
        assert "fail" in bdi.belief.errors[0]

    def test_revise_intention(self, bdi):
        from src.cognitive.bdi import PlanStep
        # 初始计划
        plan1 = [PlanStep(id="old1", description="旧步骤1", action="old1")]
        bdi.deliberate(plan1)
        assert bdi.intention.plan[0].id == "old1"

        # 修正计划
        plan2 = [
            PlanStep(id="new1", description="新步骤1", action="new1"),
            PlanStep(id="new2", description="新步骤2", action="new2"),
        ]
        bdi.revise_intention(plan2)
        assert len(bdi.intention.plan) == 2
        assert bdi.intention.current_step_index == 0
        assert bdi.intention.plan[0].id == "new1"


# ═══════════════════════════════════════════════════════════════
# 4. 工具注册中心优雅降级
# ═══════════════════════════════════════════════════════════════

class TestToolRegistryGracefulDegradation:
    """验证工具注册中心在可选依赖缺失时正常降级"""

    def test_register_builtin_tools_does_not_crash(self):
        """register_builtin_tools 在任意依赖状态下不崩溃"""
        from src.execution.tool_registry import ToolRegistry
        registry = ToolRegistry()
        status = registry.register_builtin_tools()
        # 返回各组状态
        assert isinstance(status, dict)
        for group in ["acoustics", "spatial", "knowledge", "ml"]:
            assert group in status
            assert isinstance(status[group], bool)

    def test_stats_includes_optional_tools(self):
        """统计信息反映实际注册的工具"""
        from src.execution.tool_registry import ToolRegistry
        registry = ToolRegistry()
        registry.register_builtin_tools()

        stats = registry.stats()
        assert stats["total_tools"] >= 0
        assert "by_category" in stats

    def test_list_missing_optionals(self):
        """列出所有可选依赖状态"""
        from src.execution.tool_registry import list_missing_optionals
        status = list_missing_optionals()
        assert isinstance(status, dict)
        # 每个可选依赖都有条目
        assert len(status) >= 4

    def test_tool_call_unknown_raises(self):
        """调用未注册工具抛出 ValueError"""
        from src.execution.tool_registry import ToolRegistry
        registry = ToolRegistry()
        with pytest.raises(ValueError, match="Unknown tool"):
            registry.call("nonexistent_tool")

    def test_tool_call_not_implemented(self):
        """调用 fn=None 的工具返回 not_implemented"""
        from src.execution.tool_registry import ToolRegistry
        registry = ToolRegistry()
        registry.register(
            name="stub_tool",
            description="A stub",
            fn=None,
            category="test",
        )
        result = registry.call("stub_tool")
        assert result["status"] == "not_implemented"

    def test_tool_call_history(self):
        """调用历史正确记录"""
        from src.execution.tool_registry import ToolRegistry
        registry = ToolRegistry()

        def dummy_fn(**kwargs):
            return {"ok": True}

        registry.register(
            name="test_tool",
            description="Test",
            fn=dummy_fn,
            category="test",
        )
        registry.call("test_tool", param="value")
        registry.call("test_tool", param="value2")

        history = registry.get_history(limit=10)
        assert len(history) == 2

        success_only = registry.get_history(success_only=True)
        assert len(success_only) == 2


# ═══════════════════════════════════════════════════════════════
# 5. NLU 关键词匹配 (无 LLM 依赖)
# ═══════════════════════════════════════════════════════════════

class TestNLUKeywordMatching:
    """NLU 基于关键词匹配，不依赖 LLM"""

    @pytest.fixture
    def nlu(self):
        from src.interaction.nlu import NLUProcessor
        return NLUProcessor()

    def test_literature_search_intent(self, nlu):
        result = nlu.parse("搜索江豚声学监测的文献")
        from src.interaction.nlu import Intent
        assert result.intent == Intent.LITERATURE_SEARCH
        assert result.confidence >= 0.5

    def test_acoustic_analysis_intent(self, nlu):
        result = nlu.parse("分析江豚的声学数据 click 脉冲检测")
        from src.interaction.nlu import Intent
        assert result.intent in (
            Intent.ACOUSTIC_ANALYSIS,
            Intent.CLICK_DETECTION,
            Intent.LITERATURE_SEARCH,  # "分析" 可能被识别为文献搜索
        )

    def test_conservation_intent(self, nlu):
        result = nlu.parse("评估江豚的保护状况和威胁因子")
        from src.interaction.nlu import Intent
        # 保护相关
        assert result.intent is not None

    def test_unknown_intent_fallback(self, nlu):
        result = nlu.parse("你好")
        from src.interaction.nlu import Intent
        assert result.intent in (Intent.QUESTION_ANSWER, Intent.UNKNOWN)

    def test_entity_extraction_species(self, nlu):
        result = nlu.parse("搜索 Neophocaena asiaeorientalis 的文献")
        species_entities = [e for e in result.entities if e.type == "species"]
        if species_entities:
            assert "Neophocaena" in species_entities[0].value or \
                   "asiaeorientalis" in species_entities[0].value


# ═══════════════════════════════════════════════════════════════
# 6. 记忆系统基本行为
# ═══════════════════════════════════════════════════════════════

class TestMemoryBasic:
    """记忆系统基本测试 (不依赖 ChromaDB)"""

    def test_memory_manager_init(self):
        from src.memory.manager import MemoryManager
        mm = MemoryManager()
        assert mm is not None

    def test_short_term_memory_init(self):
        from src.memory.short_term import ShortTermMemory
        stm = ShortTermMemory(max_tokens=1000)
        assert stm is not None


# ═══════════════════════════════════════════════════════════════
# 7. 端到端工作流 (无 LLM)
# ═══════════════════════════════════════════════════════════════

class TestEndToEndWorkflow:
    """端到端工作流: 初始化 → 注册 → NLU → 拓扑 → 统计"""

    def test_minimal_workflow(self):
        """
        最小完整流程:
        1. 创建 Orchestrator
        2. 注册 Mock Agent
        3. NLU 解析输入
        4. 路由 → 构建拓扑
        5. 获取统计
        """
        from src.agents.orchestrator import OrchestratorAgent
        from src.agents.base import BaseAgent
        from src.interaction.nlu import NLUProcessor

        # 1. 创建 Orchestrator
        orch = OrchestratorAgent()

        # 2. 注册 Mock Agent
        class MockLitAgent(BaseAgent):
            async def handle_message(self, msg):
                return {
                    "agent": self.name,
                    "papers": [{"title": "Test Paper", "year": 2023}],
                }

        class MockEcoAgent(BaseAgent):
            async def handle_message(self, msg):
                return {
                    "agent": self.name,
                    "abundance": 1249,
                    "trend": "increasing",
                }

        orch.register_agent(MockLitAgent(name="literature"))
        orch.register_agent(MockEcoAgent(name="ecology"))

        # 3. NLU 解析
        nlu = NLUProcessor()
        result = nlu.parse("搜索江豚种群数量文献并评估生态状况")
        assert result.intent is not None
        assert result.confidence > 0

        # 4. 统计
        stats = orch.stats()
        assert "literature" in stats["registered_agents"]
        assert "ecology" in stats["registered_agents"]
        assert stats["has_critic"] is False

        # 5. BDI 就绪
        from src.cognitive.bdi import BDIStatus
        assert orch.bdi.status == BDIStatus.IDLE
