"""CoiliaAdapter — P₂ 刀鲚专研 · 三角闭环适配器.

实现 scripts/adapter_protocol.py::IProjectAdapter 标准接口 (D:/Reasonix 层)。
被 scripts/project_loader.py 发现和加载。

P₂ 在三角闭环中的位置:
  S(fish-ecology-assistant) → T(porpoise-agent) → V(cognitive-search-engine)
                                    ↑
                               P₂ 刀鲚专研 (本 Adapter)

搜索由 cognitive-search-engine 统一提供 (Unified Search Protocol),
P₂ 负责物种约束 (Coilia nasus) + 领域专研分析。
参见: cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Add D:/Reasonix to sys.path for shared protocols
_reasonix = str(Path(__file__).resolve().parent.parent.parent)  # D:\Reasonix
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

from scripts.adapter_protocol import IProjectAdapter

from src.agent.orchestrator import CoiliaOrchestrator


class CoiliaAdapter(IProjectAdapter):
    """P₂ 刀鲚专研 — 标准 IProjectAdapter 实现."""

    project_name = "coilia-agent"

    def __init__(self) -> None:
        self._orchestrator = CoiliaOrchestrator()

    # ── IProjectAdapter 标准接口 ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行刀鲚搜索 + 领域分析。

        此方法：
        1. 返回搜索参数 (物种约束 + 研究方向)
        2. 实际搜索由调用方 (cognitive-search-engine / Reasonix) 完成
        3. 搜索完成后调 analyze() 做 P₂ 专研分析
        """
        return self._orchestrator.run(query)

    def health(self) -> Dict[str, Any]:
        return {
            "project": self.project_name,
            "role": "P₂ · 刀鲚专研",
            "status": "HEALTHY",
            "species": "Coilia nasus",
        }

    def info(self) -> Dict[str, Any]:
        return {
            "project": self.project_name,
            "role": "P₂ · 刀鲚专研",
            "species": ["Coilia nasus (刀鲚/长江刀鱼)"],
            "related_species": [
                "Coilia brachygnathus (短颌鲚)",
                "Coilia mystus (凤鲚)",
            ],
            "research_themes": [
                "洄游生态与耳石微化学",
                "群体遗传与种群结构",
                "资源评估与管理",
                "食性与营养生态",
                "早期资源与繁殖",
            ],
            "capabilities": [
                "otolith_microchemistry",
                "migration_path_reconstruction",
                "population_genetics",
                "stock_assessment",
                "conservation_recommendations",
            ],
            "search_protocol": "Unified Search Protocol v1.0 "
                "(cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md)",
        }

    # ── P₂ 特有方法 ──

    def analyze(self, phase: str, search_result: dict) -> Dict[str, Any]:
        """搜索结果 → P₂ 领域专研分析."""
        return self._orchestrator.analyze(phase, search_result)


def get_adapter() -> CoiliaAdapter:
    """Factory — 被 scripts/project_loader.py 调用 (D:/Reasonix 层)."""
    return CoiliaAdapter()
