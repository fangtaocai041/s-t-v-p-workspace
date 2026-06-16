"""
认知与决策层 (Cognitive & Decision Layer)
──────────────────────────────────────────
整个 Agent 的大脑，负责推理、规划和常识判断。

组件:
- BDI: Belief-Desire-Intention 状态机
- ReActLoop: Reasoning and Acting 闭环反馈系统
- Decomposer: 任务分解 (CoT / ToT / GoT)
- Reflexion: 自我反思 Critic + 信用分配
- Search: 思维树/图搜索 (BFS/DFS/Beam/MCTS)
"""

from src.cognitive.bdi import (
    BDICoordinator,
    BDIStatus,
    Belief,
    Desire,
    Intention,
    PlanStep,
    StepStatus,
)
from src.cognitive.react_loop import (
    ReActLoop,
    ReActContext,
    ReActStep,
    LoopStatus,
)
from src.cognitive.decomposer import (
    TaskDecomposer,
    DecompositionPlan,
    DecompositionStrategy,
)
from src.cognitive.reflexion import (
    Critic,
    CreditAssigner,
    FeedbackLoop,
    Reflection,
    ReflectionType,
    Severity,
    CreditNode,
)
from src.cognitive.search import (
    ThoughtTreeSearch,
    GraphThoughtSearch,
    ThoughtNode,
    GraphThoughtNode,
    SearchConfig,
    SearchStrategy,
    SearchResult,
)

__all__ = [
    # BDI
    "BDICoordinator",
    "BDIStatus",
    "Belief",
    "Desire",
    "Intention",
    "PlanStep",
    "StepStatus",
    # ReAct
    "ReActLoop",
    "ReActContext",
    "ReActStep",
    "LoopStatus",
    # Decomposer
    "TaskDecomposer",
    "DecompositionPlan",
    "DecompositionStrategy",
    # Reflexion
    "Critic",
    "CreditAssigner",
    "FeedbackLoop",
    "Reflection",
    "ReflectionType",
    "Severity",
    "CreditNode",
    # Search
    "ThoughtTreeSearch",
    "GraphThoughtSearch",
    "ThoughtNode",
    "GraphThoughtNode",
    "SearchConfig",
    "SearchStrategy",
    "SearchResult",
]
