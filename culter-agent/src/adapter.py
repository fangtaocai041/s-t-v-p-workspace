"""CulterAdapter — culter-agent (P₃ 万物衍生·鲌类).

核心专精: assess_culter_species(species: str, context: str) → SpeciesAssessment
    年龄与生长建模 + 资源评估 + 栖息地适宜性 (领域专精知识)
    通路: P3(cognitive→culter) P5(culter→conflict)

Wraps CulterOrchestrator for cross-project consumption.
Provides age-growth analysis + resource assessment as standard interface.

P₁(porpoise) / P₂(coilia) / P₃(culter) 为同级平行项目，均由三角核心派生。
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Import shared adapter protocol (workspace root on sys.path)
try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object  # fallback for standalone usage


class CulterAdapter(IProjectAdapter):
    """Adapter for culter-agent (P₃ — 鲌类领域, 衍生自三角)."""

    project_name = "culter-agent"

    def __init__(self) -> None:
        self._orchestrator: Any = None
        self._init_orchestrator()

    def _init_orchestrator(self) -> None:
        base = Path(__file__).resolve().parent.parent
        orch_file = base / "src" / "agent" / "orchestrator.py"
        if not orch_file.is_file():
            logger.warning(f"Culter orchestrator not found at {orch_file}")
            return
        proj_str = str(base)
        if proj_str not in sys.path:
            sys.path.insert(0, proj_str)
        try:
            import importlib, importlib.util
            # Clear cached 'src' to avoid cross-project conflict
            for key in list(sys.modules.keys()):
                if key == "src" or key.startswith("src."):
                    del sys.modules[key]
            module_name = f"culter.orchestrator.{id(self)}"
            spec = importlib.util.spec_from_file_location(
                module_name, str(orch_file))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod  # 必须注册，否则 @dataclass 崩溃
                spec.loader.exec_module(mod)
                cls = getattr(mod, "CulterOrchestrator", None)
                if cls:
                    self._orchestrator = cls()
        except Exception as exc:
            logger.warning(f"Culter orchestrator init failed: {exc}")

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        if self._orchestrator:
            try:
                result = self._orchestrator.run(query)
                return {"status": "ok", "result": result}
            except Exception as exc:
                return {"status": "error", "error": str(exc)}
        return {"status": "unavailable", "query": query,
                "note": "Culter orchestrator not loaded"}

    def health(self) -> Dict[str, Any]:
        return {"project": self.project_name,
                "status": "HEALTHY" if self._orchestrator else "DEGRADED"}

    def info(self) -> Dict[str, Any]:
        return {
            "project": self.project_name,
            "role": "P₃ 万物衍生·鲌类",
            "capabilities": [
                "genome_assembly_and_comparative_genomics",
                "phylogeography_and_population_genetics",
                "age_growth_modeling_von_Bertalanffy",
                "stable_isotope_ecology_d13C_d15N",
                "trophic_niche_and_MixSIAR_mixing_models",
                "sympatric_coexistence_niche_partitioning",
                "resource_assessment_CPUE_MSY_YPR",
                "habitat_suitability_HSI_spawning_grounds",
            ],
        }


def get_adapter() -> CulterAdapter:
    return CulterAdapter()
