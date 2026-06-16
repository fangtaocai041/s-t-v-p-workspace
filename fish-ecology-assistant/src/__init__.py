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
"""

__version__ = "6.5.0"

from .orchestrator import FishEcologyOrchestrator, KbFirstResult, get_orchestrator
from .project_hub import ProjectHub, get_hub, TriangleMember, DerivedMember
from .adapter import FishEcologyAdapter

__all__ = [
    "FishEcologyOrchestrator",
    "KbFirstResult",
    "ProjectHub",
    "FishEcologyAdapter",
    "TriangleMember",
    "DerivedMember",
    "get_orchestrator",
    "get_hub",
    "__version__",
]
