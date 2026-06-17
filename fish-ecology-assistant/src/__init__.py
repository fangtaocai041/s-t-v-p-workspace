"""fish-ecology-assistant — 鱼类生态学知识供给引擎 (S/V0)

提供多流域鱼类物种知识库查询、两阶段文献搜索、三角验证评分能力。
是 Triangle Core 的 S/V0 知识供给层。

Usage:
    from src import get_orchestrator, get_hub

    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="鳤")
    print(result.summary_text)

    hub = get_hub()
    print(hub.is_triangle_complete())

    # 道→一→二→三→万物 执行引擎 (需显式导入)
    from src.dao_engine import DaoEngine, DaoQuery

    # 类型系统
    from src.types import PipelinePhase, ConfidenceLevel, ResearchContext
"""

__version__ = "6.5.3"

# ── 延迟导入以避免缺失可选依赖 (fishkb) 时崩溃 ──
# 核心类通过 get_* 工厂函数按需加载，而非模块级直接导入。

import logging as _logging
_logger = _logging.getLogger(__name__)


def get_orchestrator():
    """延迟获取 FishEcologyOrchestrator 单例."""
    from .orchestrator import get_orchestrator as _go
    return _go()


def get_hub():
    """延迟获取 ProjectHub 单例."""
    from .project_hub import get_hub as _gh
    return _gh()


# ── 安全导出 — 只在模块可以导入时暴露 ──
# 跨项目适配器 (优先保证可导入)
from .adapter import FishEcologyAdapter  # noqa: E402

# 类型系统 (纯 dataclass, 无外部依赖)
from .types import (  # noqa: E402
    PipelinePhase,
    ConfidenceLevel,
    EvidenceQuality,
    ReviewResult,
    ResearchContext,
    SourceEntry,
    AnalysisFinding,
    EmergenceSignal,
    ReviewReport,
    PipelineStats,
    SessionResult,
)

__all__ = [
    # Core orchestrator (lazy)
    "get_orchestrator",
    # Project hub (lazy)
    "get_hub",
    # Adapter
    "FishEcologyAdapter",
    # Types
    "PipelinePhase",
    "ConfidenceLevel",
    "EvidenceQuality",
    "ReviewResult",
    "ResearchContext",
    "SourceEntry",
    "AnalysisFinding",
    "EmergenceSignal",
    "ReviewReport",
    "PipelineStats",
    "SessionResult",
    # Version
    "__version__",
]
