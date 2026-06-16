"""
保护评估 Agent (Conservation Agent)
────────────────────────────────────
负责 IUCN 标准评估、威胁分析、保护优先级排序。

能力:
- IUCN 红色名录标准评估
- 威胁因子排序与归因
- 保护行动优先级 (成本效益)
- 管理建议生成
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.cognitive.bdi import Desire

logger = logging.getLogger(__name__)


class ConservationAgent(BaseAgent):
    """保护评估 Agent — IUCN 标准评估与保护建议"""

    def __init__(self, model: str = "deepseek-reasoner", memory: Any = None):
        super().__init__(name="conservation", model=model, memory=memory)

    def _init_desire(self):
        self.bdi.desire = Desire(
            primary_goal="基于 IUCN 标准评估江豚保护状况并生成管理建议",
            constraints=[
                "所有建议需基于数据或文献证据",
                "管理建议需注明可行性和政策对齐度",
                "关键建议需人工审批",
            ],
            forbidden_actions=[
                "conservation_recommendation_without_approval",
            ],
        )

    async def handle_message(self, message: Any) -> dict:
        self._call_count += 1

        content = message.content if hasattr(message, 'content') else message
        if isinstance(content, str):
            content = {"query": content}

        action = content.get("action", "assess")
        logger.info(f"ConservationAgent[{self.node_id}]: {action}")

        try:
            if action == "assess":
                result = self._assess_iucn(content)
            elif action == "threats":
                result = self._assess_threats(content)
            elif action == "recommend":
                result = self._generate_recommendations(content)
            else:
                result = {"error": f"Unknown action: {action}"}

            return {"agent": "conservation", "action": action, **result}

        except Exception as e:
            self._error_count += 1
            return {"agent": "conservation", "error": str(e)}

    def _assess_iucn(self, content: dict) -> dict:
        """IUCN 标准评估"""
        species = content.get("species", "Neophocaena asiaeorientalis asiaeorientalis")

        # 基于已知信息评估
        return {
            "species": species,
            "iucn_category": "CR (Critically Endangered)",
            "criteria": [
                "A2b: 种群在过去三代减少 ≥80%",
                "C2a(i): 成熟个体 <250 + 持续下降",
                "D: 种群极小 (<50 成熟个体，部分亚群)",
            ],
            "population_trend": "Decreasing",
            "estimated_population": "1,000-1,200",
            "generation_length_years": 9,
            "threats": [
                "Habitat degradation (shipping, sand mining)",
                "Water infrastructure (dams, barriers)",
                "Bycatch in fishing gear",
                "Underwater noise pollution",
                "Prey depletion (10-year fishing ban impact TBD)",
            ],
            "confidence": "high",
            "requires_approval": False,
        }

    def _assess_threats(self, content: dict) -> dict:
        """威胁因子评估与排序"""
        threats = [
            {
                "threat": "栖息地退化",
                "severity": "极高",
                "trend": "加剧",
                "reversibility": "中等",
                "affected_fraction": ">80% 分布区",
            },
            {
                "threat": "航运干扰",
                "severity": "高",
                "trend": "加剧",
                "reversibility": "高 (限速禁航)",
                "affected_fraction": "长江干流全线",
            },
            {
                "threat": "水下噪声",
                "severity": "高",
                "trend": "加剧",
                "reversibility": "中等",
                "affected_fraction": "航运水道",
            },
            {
                "threat": "渔业误捕",
                "severity": "中等",
                "trend": "下降 (禁渔)",
                "reversibility": "高",
                "affected_fraction": "局部",
            },
            {
                "threat": "饵料资源下降",
                "severity": "中等",
                "trend": "禁渔后可能改善",
                "reversibility": "高",
                "affected_fraction": "全域",
            },
        ]

        return {
            "threats": threats,
            "n_threats": len(threats),
            "top_threat": threats[0]["threat"],
            "confidence": "high",
        }

    def _generate_recommendations(self, content: dict) -> dict:
        """生成保护管理建议"""
        return {
            "recommendations": [
                {
                    "action": "扩大自然保护区网络",
                    "priority": 1,
                    "feasibility": "中等",
                    "estimated_cost": "高",
                    "evidence_level": "强",
                    "requires_approval": True,
                },
                {
                    "action": "航运限速禁航区优化",
                    "priority": 2,
                    "feasibility": "高",
                    "estimated_cost": "中等",
                    "evidence_level": "强",
                    "requires_approval": True,
                },
                {
                    "action": "迁地保护种群扩容",
                    "priority": 3,
                    "feasibility": "高",
                    "estimated_cost": "中等",
                    "evidence_level": "中等",
                    "requires_approval": True,
                },
            ],
            "requires_approval": True,
            "approval_message": (
                "保护管理建议需课题组审核后方可实施。"
                "以上建议均基于文献证据，但具体实施方案需结合实地条件调整。"
            ),
        }

    def can_handle(self, intent: str) -> bool:
        return intent in ("conservation_assess", "threat_assess")
