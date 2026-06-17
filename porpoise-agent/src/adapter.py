"""PorpoiseAdapter — porpoise-agent (P₁ 江豚专研 · 三角闭环适配器).

实现 scripts/adapter_protocol.py::IProjectAdapter 标准接口 (D:/Reasonix 层)。
被 scripts/project_loader.py 发现和加载。

P₁ 在三角闭环中的位置:
  S(fish-ecology-assistant) → T(porpoise-agent) → V(cognitive-search-engine)
                                    ↑
                               P₁ 江豚专研 (本 Adapter)

核心专精: acoustic monitoring + population abundance estimation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add D:/Reasonix to sys.path for shared protocols
_reasonix = str(Path(__file__).resolve().parent.parent.parent)  # D:\Reasonix
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object  # fallback for standalone usage

from src.agents.orchestrator import OrchestratorAgent


class PorpoiseAdapter(IProjectAdapter):
    """P₁ 江豚专研 — 标准 IProjectAdapter 实现.

    支持领域: acoustic (声学监测), population (种群丰度), conservation (保护评估).
    """

    project_name = "porpoise-agent"

    def __init__(self) -> None:
        self._orchestrator = OrchestratorAgent()

    # ── IProjectAdapter 标准接口 ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行江豚领域搜索 + 分析.

        路由到 OrchestratorAgent.run() 进行多轮 BDI 推理。
        """
        import asyncio
        domain = kwargs.get("domain", "")
        full_query = query
        if domain == "acoustic":
            full_query = f"analyze acoustic data for {query}"
        elif domain == "population":
            full_query = f"estimate population abundance for {query}"
        elif domain == "conservation":
            full_query = f"assess conservation status for {query}"

        try:
            # OrchestratorAgent.run is async
            if asyncio.iscoroutinefunction(self._orchestrator.run):
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create new loop in thread? No — just call sync wrapper
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, self._orchestrator.run(full_query)
                        )
                        result = future.result(timeout=60)
                else:
                    result = loop.run_until_complete(self._orchestrator.run(full_query))
            else:
                result = self._orchestrator.run(full_query)

            if isinstance(result, dict):
                return {"status": "ok", "result": result}
            return {"status": "ok", "result": str(result)}
        except Exception as exc:
            return {"status": "error", "error": str(exc), "query": query}

    def health(self) -> Dict[str, Any]:
        return {
            "project": self.project_name,
            "status": "HEALTHY",
            "role": "P1 · 江豚专研",
            "orchestrator": type(self._orchestrator).__name__,
        }

    def info(self) -> Dict[str, Any]:
        return {
            "project": self.project_name,
            "role": "P1 · 江豚专研",
            "species": "Neophocaena asiaeorientalis (长江江豚)",
            "capabilities": [
                "acoustic_monitoring",
                "population_abundance_estimation",
                "habitat_suitability_modeling",
                "conservation_priority_assessment",
                "multi_round_BDI_reasoning",
            ],
            "research_themes": [
                "passive_acoustic_monitoring",
                "line_transect_survey",
                "distribution_modeling",
                "threat_assessment",
            ],
        }

    # ── P₁ 特有方法 ──

    def analyze_acoustic(self, query: str) -> Dict[str, Any]:
        """声学数据分析."""
        return self.search(query, domain="acoustic")

    def estimate_population(self, query: str) -> Dict[str, Any]:
        """种群丰度估计."""
        return self.search(query, domain="population")

    def assess_conservation(self, query: str) -> Dict[str, Any]:
        """保护状态评估."""
        return self.search(query, domain="conservation")


def get_adapter() -> PorpoiseAdapter:
    """Factory — 被 scripts/project_loader.py 调用 (D:/Reasonix 层)."""
    return PorpoiseAdapter()
