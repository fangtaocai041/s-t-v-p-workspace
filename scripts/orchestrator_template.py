"""
%%CHINESE_NAME%% Orchestrator — %%CHINESE_NAME%%专研管线 (P%%N%%, V%%N%%)

从三角形 (fish+cognitive+eon-core) 派生的领域专精模板。
模板来源: coilia-agent/src/agent/orchestrator.py (P2)

双模式:
  独立模式: 通过 project_loader 调用 cognitive
  集成模式: 由 eon-core OriginKernel 调度

5 阶段管线:
  Literature -> %%DOMAIN1%% -> %%DOMAIN2%% -> %%DOMAIN3%% -> Report
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from eon_core.src.orchestrator_base import (
        VerificationStatus, ContradictionType,
        PhaseResult as BasePhaseResult,
        PipelineResult as BasePipelineResult,
    )
    _HAS_SHARED_BASE = True
except ImportError:
    VerificationStatus = None
    ContradictionType = None
    BasePhaseResult = object
    BasePipelineResult = object
    _HAS_SHARED_BASE = False


class ResearchPhase(str, Enum):
    LITERATURE = "literature_review"
    %%DOMAIN1_UPPER%% = "%%DOMAIN1%%"
    %%DOMAIN2_UPPER%% = "%%DOMAIN2%%"
    %%DOMAIN3_UPPER%% = "%%DOMAIN3%%"
    REPORT = "report_generation"


@dataclass
class PhaseResult:
    phase: ResearchPhase
    status: str = "ok"
    papers_found: int = 0
    data_points: int = 0
    tokens_used: int = 0
    findings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    question: str = ""
    phases_executed: List[str] = field(default_factory=list)
    phase_results: Dict[str, PhaseResult] = field(default_factory=dict)
    total_papers: int = 0
    total_tokens: int = 0
    synthesis: str = ""


SPECIES_PROFILE = dict(
    scientific_name="%%SCIENTIFIC_NAME%%",
    chinese_name="%%CHINESE_NAME%%",
    genus="%%GENUS%%",
    species="%%SPECIES%%",
    research_group="待填写",
    domains=[%%DOMAIN_LIST_PY%%],
)


class %%CLASS_NAME%%:
    """%%CHINESE_NAME%%专研管线协调器 (P%%N%% - 三角派生模板)。"""

    PHASE_KEYWORDS = {
        ResearchPhase.LITERATURE: ["文献", "论文", "搜索", "检索"],
        ResearchPhase.%%DOMAIN1_UPPER%%: %%DOMAIN1_KW%%,
        ResearchPhase.%%DOMAIN2_UPPER%%: %%DOMAIN2_KW%%,
        ResearchPhase.%%DOMAIN3_UPPER%%: %%DOMAIN3_KW%%,
    }

    def __init__(self):
        self.context = None

    def run(self, question: str, mode: str = "standalone") -> dict:
        phase = self._route_phase(question)
        lit = self._execute_literature(question)
        domain_result = self._execute_domain(phase, question, lit)
        synthesis = self._synthesize(question, lit, domain_result)
        return dict(
            agent="%%CLASS_NAME%% (P%%N%%)",
            species=SPECIES_PROFILE["scientific_name"],
            phase=phase.value,
            literature=lit.__dict__,
            domain=domain_result.__dict__,
            synthesis=synthesis,
        )

    def _route_phase(self, question: str) -> ResearchPhase:
        q = question.lower()
        for phase, keywords in self.PHASE_KEYWORDS.items():
            if any(kw in q for kw in keywords):
                return phase
        return ResearchPhase.LITERATURE

    def _execute_literature(self, question: str) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.LITERATURE)
        try:
            from scripts.project_loader import get_cognitive
            cog = get_cognitive()
            search_result = cog.search(
                SPECIES_PROFILE["genus"],
                SPECIES_PROFILE["species"],
                full_pipeline=False,
            )
            result.papers_found = search_result.get("papers_found", 0)
            result.status = "ok"
        except Exception as e:
            result.errors.append(str(e))
            result.status = "degraded"
        return result

    def _execute_domain(self, phase, question, lit) -> PhaseResult:
        result = PhaseResult(phase=phase)
        result.findings = [
            f"物种: {SPECIES_PROFILE['scientific_name']} ({SPECIES_PROFILE['chinese_name']})",
            f"阶段: {phase.value}",
        ]
        return result

    def _synthesize(self, question, lit, domain) -> str:
        return f"{SPECIES_PROFILE['chinese_name']}研究: 文献{lit.papers_found}篇, 领域分析完成"
