"""
意图路由 (Intent Router)
─────────────────────────
将 Agent 的决策映射到特定的工具集或工作流上。

对应五层模型中的"意图对齐与路由":
    认知层输出 (Intent + Plan) → 路由到具体工具集 / Agent

路由策略:
- 精确匹配: 工具名精确对应
- 语义路由: 基于意图→工具映射表
- 级联路由: 一个意图触发多个工具链
- 降级路由: 目标不可用时使用替代工具
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from src.interaction.nlu import Intent

logger = logging.getLogger(__name__)


class RouteTarget(str, Enum):
    """路由目标类型"""
    TOOL = "tool"               # 单个工具
    TOOL_CHAIN = "tool_chain"   # 工具链 (顺序)
    AGENT = "agent"             # 专业子 Agent
    SKILL = "skill"             # 技能模块
    HUMAN = "human"             # 人工审批
    NOOP = "noop"               # 无需操作


@dataclass
class Route:
    """路由条目"""
    target: str                            # 目标名称
    target_type: RouteTarget
    params_template: dict = field(default_factory=dict)  # 参数模板
    requires_approval: bool = False
    fallback: Optional[str] = None         # 降级目标
    description: str = ""


@dataclass
class RouteResult:
    """路由结果"""
    routes: list[Route]
    confidence: float
    rationale: str = ""


# ── 路由表 ────────────────────────────────────────────────

class IntentRouter:
    """
    意图路由器 — 将意图映射到工具/Agent

    用法:
        router = IntentRouter()
        result = router.route(intent=Intent.LITERATURE_SEARCH, entities=[...])
        for route in result.routes:
            if route.target_type == RouteTarget.TOOL:
                tools.call(route.target, **route.params_template)
    """

    def __init__(self):
        # 意图 → 路由映射表
        self.routes: dict[Intent, list[Route]] = self._build_route_table()
        logger.info(f"IntentRouter initialized ({len(self.routes)} intents mapped)")

    def _build_route_table(self) -> dict[Intent, list[Route]]:
        """构建意图路由表"""
        return {
            Intent.LITERATURE_SEARCH: [
                Route(
                    target="search_literature",
                    target_type=RouteTarget.TOOL,
                    params_template={"source": "semantic_scholar", "limit": 20},
                    fallback="web_search",
                    description="搜索学术文献",
                ),
            ],
            Intent.LITERATURE_REVIEW: [
                Route(
                    target="literature_agent",
                    target_type=RouteTarget.AGENT,
                    description="启动文献分析 Agent 进行综述",
                ),
            ],
            Intent.ACOUSTIC_ANALYSIS: [
                Route(
                    target="load_acoustic_file",
                    target_type=RouteTarget.TOOL,
                    description="加载声学文件",
                ),
                Route(
                    target="detect_clicks",
                    target_type=RouteTarget.TOOL,
                    description="检测 NBHF click 脉冲",
                ),
            ],
            Intent.CLICK_DETECTION: [
                Route(
                    target="detect_clicks",
                    target_type=RouteTarget.TOOL,
                    params_template={"threshold_db": -134.0},
                    description="NBHF click 检测",
                ),
            ],
            Intent.ABUNDANCE_ESTIMATE: [
                Route(
                    target="estimate_abundance",
                    target_type=RouteTarget.TOOL,
                    params_template={"method": "cue_counting"},
                    fallback="distance_sampling",
                    description="种群丰度估计",
                ),
            ],
            Intent.HABITAT_MODEL: [
                Route(
                    target="model_habitat",
                    target_type=RouteTarget.SKILL,
                    description="栖息地建模 (SDM/MaxEnt)",
                ),
            ],
            Intent.FIELD_SURVEY: [
                Route(
                    target="plan_survey",
                    target_type=RouteTarget.SKILL,
                    requires_approval=True,
                    description="野外调查规划 (需人工审批)",
                ),
            ],
            Intent.CONSERVATION_ASSESS: [
                Route(
                    target="conservation_agent",
                    target_type=RouteTarget.AGENT,
                    description="保护评估 Agent",
                ),
            ],
            Intent.THREAT_ASSESS: [
                Route(
                    target="assess_threats",
                    target_type=RouteTarget.SKILL,
                    description="威胁因子评估",
                ),
            ],
            Intent.GENETIC_ANALYSIS: [
                Route(
                    target="analyze_genetics",
                    target_type=RouteTarget.SKILL,
                    description="遗传/基因组分析",
                ),
            ],
            Intent.REPORT_GENERATE: [
                Route(
                    target="generate_report",
                    target_type=RouteTarget.SKILL,
                    description="研究报告生成",
                ),
            ],
            Intent.QUESTION_ANSWER: [
                Route(
                    target="llm_direct",
                    target_type=RouteTarget.TOOL,
                    description="LLM 直接回答",
                ),
            ],
            Intent.CLARIFY: [
                Route(
                    target="human",
                    target_type=RouteTarget.HUMAN,
                    description="需要用户澄清",
                ),
            ],
            Intent.UNKNOWN: [
                Route(
                    target="llm_direct",
                    target_type=RouteTarget.TOOL,
                    fallback="human",
                    description="意图未知，LLM fallback",
                ),
            ],
        }

    def route(
        self,
        intent: Intent,
        entities: Optional[list] = None,
        sub_intents: Optional[list[Intent]] = None,
    ) -> RouteResult:
        """
        路由: 意图 → 工具/Agent 映射

        Args:
            intent: 主要意图
            entities: 实体列表 (用于参数填充)
            sub_intents: 子意图 (级联路由)

        Returns:
            RouteResult: 路由结果
        """
        entities = entities or []
        sub_intents = sub_intents or []

        # 主路由
        primary_routes = self.routes.get(intent, self.routes[Intent.UNKNOWN])

        # 用实体填充参数模板
        filled_routes = []
        for route in primary_routes:
            filled = Route(
                target=route.target,
                target_type=route.target_type,
                params_template=self._fill_params(route.params_template, entities),
                requires_approval=route.requires_approval,
                fallback=route.fallback,
                description=route.description,
            )
            filled_routes.append(filled)

        # 子意图路由 (级联)
        for sub in sub_intents:
            sub_routes = self.routes.get(sub, [])
            for route in sub_routes:
                filled_routes.append(Route(
                    target=route.target,
                    target_type=route.target_type,
                    params_template=self._fill_params(route.params_template, entities),
                    requires_approval=route.requires_approval,
                    fallback=route.fallback,
                    description=f"[Sub-intent: {sub.value}] {route.description}",
                ))

        # 置信度
        confidence = 1.0 if intent != Intent.UNKNOWN else 0.3
        if filled_routes:
            confidence = min(confidence + 0.1 * len(filled_routes), 1.0)

        return RouteResult(
            routes=filled_routes,
            confidence=confidence,
            rationale=f"Intent={intent.value}, sub_intents={[s.value for s in sub_intents]}",
        )

    def _fill_params(self, template: dict, entities: list) -> dict:
        """用实体填充参数模板"""
        params = dict(template) if template else {}

        for entity in entities:
            if entity.type == "species":
                params.setdefault("species", entity.normalized)
            elif entity.type == "location":
                params.setdefault("location", entity.normalized)
            elif entity.type == "time_range":
                params.setdefault("time_range", entity.normalized)
            elif entity.type == "device":
                params.setdefault("device", entity.normalized)
            elif entity.type == "method":
                params.setdefault("method", entity.normalized)

        return params

    def resolve_fallback(self, route: Route) -> Optional[Route]:
        """获取降级路由"""
        if route.fallback:
            # 查找 fallback 目标
            for intent_routes in self.routes.values():
                for r in intent_routes:
                    if r.target == route.fallback:
                        return r
            # 如果 fallback 是 tool 名称
            return Route(
                target=route.fallback,
                target_type=RouteTarget.TOOL,
                description=f"Fallback: {route.fallback}",
            )
        return None

    def add_custom_route(self, intent: Intent, route: Route):
        """添加自定义路由 (扩展用)"""
        if intent not in self.routes:
            self.routes[intent] = []
        self.routes[intent].append(route)
        logger.info(f"Custom route added: {intent.value} → {route.target}")
