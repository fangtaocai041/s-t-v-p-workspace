"""CoiliaAdapter — P₂ 鲚属专研 · 三角闭环适配器.

实现 scripts/adapter_protocol.py::IProjectAdapter 标准接口 (D:/Reasonix 层)。
被 scripts/project_loader.py 发现和加载。

P₂ 在三角闭环中的位置:
  S(fish-ecology-assistant) → T(porpoise-agent) → V(cognitive-search-engine)
                                    ↑
                               P₂ 鲚属专研 (本 Adapter)

搜索由 cognitive-search-engine 统一提供 (Unified Search Protocol),
P₂ 负责物种约束 (Coilia spp.) + 领域专研分析。
多物种支持由 config/species/*.yaml + SpeciesRegistry 提供。
参见: cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add D:/Reasonix to sys.path for shared protocols
_reasonix = str(Path(__file__).resolve().parent.parent.parent)  # D:\Reasonix
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

from scripts.adapter_protocol import IProjectAdapter

from src.agent.orchestrator import CoiliaOrchestrator
from src.agent.species_registry import get_registry


class CoiliaAdapter(IProjectAdapter):
    """P₂ 鲚属专研 — 标准 IProjectAdapter 实现.

    支持多物种: 通过 species_id 指定 (默认 coilia_nasus)。
    """

    project_name = "coilia-agent"

    def __init__(self, species_id: Optional[str] = None) -> None:
        self._registry = get_registry()
        if species_id is None:
            species_id = self._registry.default_id()
        self.species_id = species_id
        self._orchestrator = CoiliaOrchestrator(species_id=species_id)

    # ── IProjectAdapter 标准接口 ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行鲚属搜索 + 领域分析。

        此方法：
        1. 返回搜索参数 (物种约束 + 研究方向)
        2. 实际搜索由调用方 (cognitive-search-engine / Reasonix) 完成
        3. 搜索完成后调 analyze() 做 P₂ 专研分析
        """
        return self._orchestrator.run(query)

    def health(self) -> Dict[str, Any]:
        cfg = self._orchestrator.config
        return {
            "project": self.project_name,
            "role": "P2 · 鲚属专研",
            "status": "HEALTHY",
            "species": cfg.get("species_scientific", "Coilia nasus"),
        }

    def info(self) -> Dict[str, Any]:
        """动态返回当前物种信息."""
        cfg = self._orchestrator.config
        all_species = self._registry.list_species()
        related = [
            self._fmt_species(sid) for sid in all_species
            if sid != self.species_id
        ]

        return {
            "project": self.project_name,
            "role": "P2 · 鲚属专研",
            "current_species": self._fmt_species(self.species_id),
            "species": [self._fmt_species(self.species_id)],
            "related_species": related,
            "available_species": [
                self._fmt_species(sid) for sid in all_species
            ],
            "research_themes": [
                theme.get("label", tid)
                for tid, theme in cfg.get("research_themes", {}).items()
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

    def switch_species(self, species_id: str) -> bool:
        """切换当前物种.

        Returns:
            True 如果切换成功, False 如果物种 ID 不存在。
        """
        cfg = self._registry.get(species_id)
        if cfg is None:
            return False
        self.species_id = species_id
        self._orchestrator = CoiliaOrchestrator(species_id=species_id)
        return True

    def list_available_species(self) -> List[str]:
        """列出所有可用物种 ID."""
        return self._registry.list_species()

    # ── 内部辅助 ──

    def _fmt_species(self, species_id: str) -> str:
        """格式化物种描述: 'coilia_nasus → 刀鲚 (Coilia nasus)'."""
        cfg = self._registry.get(species_id)
        if cfg:
            cn = cfg.get("species_chinese", [species_id])[0]
            sci = cfg.get("species_scientific", species_id)
            return f"{cn} ({sci})"
        return species_id


def get_adapter(species_id: Optional[str] = None) -> CoiliaAdapter:
    """Factory — 被 scripts/project_loader.py 调用 (D:/Reasonix 层).

    Args:
        species_id: 可选物种 ID (默认 coilia_nasus)
    """
    return CoiliaAdapter(species_id=species_id)
