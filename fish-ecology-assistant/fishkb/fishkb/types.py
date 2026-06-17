"""
fishkb — Core Types

提供研究流水线各阶段的结构化数据类型，确保类型安全和接口一致。
从 fish-ecology-assistant/src/types.py 提取。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class PipelinePhase(str, Enum):
    """五阶段研究流水线阶段"""
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    REVIEWING = "reviewing"


class ConfidenceLevel(str, Enum):
    """校准置信度等级"""
    VERIFIED = "verified"       # ✅ — 多源一致，数据公开可查
    INFERRED = "inferred"       # ⚠️ — 逻辑延伸自已验证数据
    UNCERTAIN = "uncertain"     # ❓ — 单来源，未复现
    NO_SOURCE = "no_source"     # 🚫 — 不可溯源，禁止写入


class EvidenceQuality(str, Enum):
    """证据质量加权"""
    HIGH = "high"       # ★★★ — 数据+代码公开+可复现
    MEDIUM = "medium"   # ★★☆ — 可信但不可复现
    LOW = "low"         # ★☆☆ — 信息不足
    GREY = "grey"       # ★☆☆ — 灰色文献


class ReviewResult(str, Enum):
    """评审结果"""
    PASS = "pass"
    NEEDS_REVISION = "needs_revision"
    FAIL = "fail"


@dataclass
class ResearchContext:
    """研究上下文 — 贯穿整个流水线"""
    research_question: str
    phase: PipelinePhase = PipelinePhase.PLANNING
    target_species: str = ""
    study_area: str = ""
    time_range: tuple[str, str] = ("", "")
    keywords_en: list[str] = field(default_factory=list)
    keywords_cn: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceEntry:
    """文献来源条目"""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int = 0
    journal: str = ""
    doi: str = ""
    url: str = ""
    relevance: str = "medium"  # high / medium / low
    quality: EvidenceQuality = EvidenceQuality.MEDIUM
    key_findings: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class AnalysisFinding:
    """分析发现 — 含置信度标签"""
    statement: str
    confidence: ConfidenceLevel = ConfidenceLevel.UNCERTAIN
    supporting_sources: list[str] = field(default_factory=list)
    contradicting_sources: list[str] = field(default_factory=list)
    quality_score: int = 0  # 1-5 stars


@dataclass
class EmergenceSignal:
    """涌现信号 — ≥3 独立来源指向非预期模式"""
    pattern: str
    sources: list[str] = field(default_factory=list)
    source_count: int = 0
    potential_explanation: str = ""
    confidence: str = "medium"  # high / medium / low
    timestamp: str = ""

    def __post_init__(self):
        self.source_count = len(self.sources)


@dataclass
class ReviewReport:
    """评审报告"""
    result: ReviewResult = ReviewResult.PASS
    dimension_scores: dict[str, float] = field(default_factory=dict)
    revision_notes: list[str] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 3

    @property
    def passed(self) -> bool:
        return self.result == ReviewResult.PASS

    @property
    def can_retry(self) -> bool:
        return self.iteration < self.max_iterations


@dataclass
class PipelineStats:
    """流水线统计"""
    stage: PipelinePhase
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    search_query_count: int = 0
    source_count: int = 0
    finding_count: int = 0
    emergence_signal_count: int = 0

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()


@dataclass
class SessionResult:
    """会话结果 — 流水线完整输出"""
    research_question: str
    phases_completed: list[PipelinePhase] = field(default_factory=list)
    findings: list[AnalysisFinding] = field(default_factory=list)
    emergence_signals: list[EmergenceSignal] = field(default_factory=list)
    sources: list[SourceEntry] = field(default_factory=list)
    pipeline_stats: dict[str, PipelineStats] = field(default_factory=dict)
    final_report: str = ""
    review_result: Optional[ReviewReport] = None
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
