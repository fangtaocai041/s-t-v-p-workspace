"""
fishkb — 鱼类生态学知识库核心库

从 fish-ecology-assistant 提取的独立纯 Python 库，提供:
  - KnowledgeDB: SQLite 知识库层 (物种存储/搜索/写回)
  - FishSpeciesMatcher: KB-first 物种查找与模糊匹配
  - CredibilityScorer: 三角验证文献可信度评分
  - SpeciesVariants: 物种拼写变体注册表
  - 核心类型: ResearchContext, SourceEntry, AnalysisFinding 等

Usage:
    from fishkb import KnowledgeDB, FishSpeciesMatcher

    db = KnowledgeDB()
    matcher = FishSpeciesMatcher(db)
    result = matcher.kb_first_lookup(query="鳤")
    print(result.summary_text)
"""

from .types import (
    AnalysisFinding,
    ConfidenceLevel,
    EmergenceSignal,
    EvidenceQuality,
    PipelinePhase,
    PipelineStats,
    ResearchContext,
    ReviewReport,
    ReviewResult,
    SessionResult,
    SourceEntry,
)

from .db import KnowledgeDB, get_db

from .search import FishSpeciesMatcher, KbFirstResult, get_matcher

from .credibility import (
    detect_journal_tier,
    format_credibility,
    is_predatory,
    score_paper,
    score_papers,
)

# Convenience class alias for the credibility module functions
class CredibilityScorer:
    """文献可信度评分器 — 三角验证五维评分."""
    score_paper = staticmethod(score_paper)
    score_papers = staticmethod(score_papers)
    detect_journal_tier = staticmethod(detect_journal_tier)
    is_predatory = staticmethod(is_predatory)
    format_credibility = staticmethod(format_credibility)

from .shared import (
    JOURNAL_WHITELIST,
    build_search_queries,
    generate_ocr_variants,
)

from .variants import SpeciesVariants, get_variants

__all__ = [
    # types
    "AnalysisFinding",
    "ConfidenceLevel",
    "EmergenceSignal",
    "EvidenceQuality",
    "PipelinePhase",
    "PipelineStats",
    "ResearchContext",
    "ReviewReport",
    "ReviewResult",
    "SessionResult",
    "SourceEntry",
    # db
    "KnowledgeDB",
    "get_db",
    # search
    "FishSpeciesMatcher",
    "KbFirstResult",
    "get_matcher",
    # credibility
    "CredibilityScorer",
    "detect_journal_tier",
    "format_credibility",
    "is_predatory",
    "score_paper",
    "score_papers",
    # shared
    "JOURNAL_WHITELIST",
    "build_search_queries",
    "generate_ocr_variants",
    # variants
    "SpeciesVariants",
    "get_variants",
]

__version__ = "1.0.0"
