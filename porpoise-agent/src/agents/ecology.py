"""
生态分析 Agent (Ecology Agent)
───────────────────────────────
负责栖息地建模、种群丰度估计、分布预测。

能力:
- 栖息地适宜性建模 (SDM/MaxEnt)
- 种群丰度估计 (Cue Counting / Distance Sampling / SECR)
- 环境协变量分析
- 空间分布预测
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.cognitive.bdi import Desire

logger = logging.getLogger(__name__)


class EcologyAgent(BaseAgent):
    """生态分析 Agent — 种群与栖息地分析专家"""

    def __init__(self, model: str = "deepseek-reasoner", memory: Any = None):
        super().__init__(name="ecology", model=model, memory=memory)

    def _init_desire(self):
        self.bdi.desire = Desire(
            primary_goal="精确估计江豚种群丰度并建模栖息地适宜性",
            constraints=[
                "方法需注明参数和假设",
                "不确定性需量化 (置信区间)",
                "结果需可复现",
            ],
            quality_thresholds={
                "min_sample_size": 30,
                "min_cv": 0.30,  # 变异系数上限
            },
        )

    def _init_tools(self):
        self.tools.register(
            name="estimate_abundance",
            description="Estimate porpoise abundance from detection data",
            parameters={
                "detections": {"type": "array"},
                "method": {"type": "string"},
            },
            fn=self._estimate_abundance,
            category="ecology",
        )
        self.tools.register(
            name="model_habitat",
            description="Model habitat suitability (MaxEnt/SDM)",
            parameters={
                "species": {"type": "string"},
                "environmental_layers": {"type": "array"},
            },
            fn=self._model_habitat,
            category="ecology",
        )

    async def handle_message(self, message: Any) -> dict:
        self._call_count += 1

        content = message.content if hasattr(message, 'content') else message
        if isinstance(content, str):
            content = {"query": content}

        action = content.get("action", "estimate_abundance")
        logger.info(f"EcologyAgent[{self.node_id}]: {action}")

        try:
            if action == "estimate_abundance":
                result = self._estimate_abundance(
                    detections=content.get("detections", []),
                    method=content.get("method", "cue_counting"),
                )
            elif action == "model_habitat":
                result = self._model_habitat(
                    species=content.get("species", "Neophocaena asiaeorientalis"),
                    environmental_layers=content.get("environmental_layers", []),
                )
            else:
                result = {"error": f"Unknown action: {action}"}

            return {"agent": "ecology", "action": action, **result}

        except Exception as e:
            self._error_count += 1
            return {"agent": "ecology", "error": str(e)}

    def _estimate_abundance(
        self, detections: list, method: str = "cue_counting"
    ) -> dict:
        """种群丰度估计"""
        n = len(detections)

        if method == "cue_counting":
            # 简化的 Cue Counting
            detection_prob = 0.5  # 检测概率 (需实地校准)
            cue_rate = 10.0       # click train/hour (需实地校准)
            survey_hours = 24.0   # 调查时长

            abundance = n / (detection_prob * cue_rate * survey_hours)

            return {
                "method": "cue_counting",
                "n_detections": n,
                "detection_probability": detection_prob,
                "cue_rate_per_hour": cue_rate,
                "survey_hours": survey_hours,
                "estimated_abundance": round(abundance, 1),
                "confidence_interval": [
                    round(abundance * 0.7, 1),
                    round(abundance * 1.3, 1),
                ],
                "note": "Simplified estimate; real calibration needed",
            }

        elif method == "distance_sampling":
            return {
                "method": "distance_sampling",
                "n_detections": n,
                "status": "requires_field_calibration",
                "estimated_abundance": None,
            }

        return {"method": method, "n_detections": n, "status": "not_implemented"}

    def _model_habitat(
        self, species: str, environmental_layers: list
    ) -> dict:
        """栖息地建模"""
        return {
            "species": species,
            "method": "MaxEnt",
            "n_layers": len(environmental_layers),
            "status": "requires_occurrence_data",
        }

    def can_handle(self, intent: str) -> bool:
        return intent in ("abundance_estimate", "habitat_model")
