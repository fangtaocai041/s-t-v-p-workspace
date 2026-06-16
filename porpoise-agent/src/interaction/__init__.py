"""
交互与感知层 (Interaction & Perception Layer)
─────────────────────────────────────────────
Agent 与外部世界（人类用户或其他系统）进行信息交换的接口。

组件:
- NLU (Natural Language Understanding): 意图识别 + 实体提取
- Renderer: 结果格式化渲染 (Markdown / JSON / Table / Visual)
- MultimodalInput: 多模态感知 (文本/语音/图像/结构化数据流)
"""

from src.interaction.nlu import NLUProcessor, Intent, Entity
from src.interaction.renderer import ResponseRenderer, OutputFormat

__all__ = [
    "NLUProcessor",
    "Intent",
    "Entity",
    "ResponseRenderer",
    "OutputFormat",
]
