# Porpoise Agent Core Types

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AgentRole(str, Enum):
    LITERATURE = "literature"
    ACOUSTIC = "acoustic"
    ECOLOGY = "ecology"
    CONSERVATION = "conservation"
    GENETICS = "genetics"
    FIELD = "field"
    ORCHESTRATOR = "orchestrator"


class ResearchPhase(str, Enum):
    LITERATURE_REVIEW = "literature_review"
    DATA_ANALYSIS = "data_analysis"
    FIELD_SURVEY = "field_survey"
    CONSERVATION_ASSESSMENT = "conservation_assessment"
    REPORT_GENERATION = "report_generation"


class ClickType(str, Enum):
    REGULAR_CLICK = "regular_click"
    BUZZ = "buzz"
    BURST_PULSE = "burst_pulse"
    WHISTLE = "whistle"


@dataclass
class ClickEvent:
    timestamp: float
    peak_frequency: float
    center_frequency: float
    bandwidth_3db: float
    duration: float
    spl_peak: float
    click_type: ClickType = ClickType.REGULAR_CLICK


@dataclass
class ClickTrain:
    clicks: list = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    mean_ici: float = 0.0
    buzz_ratio: float = 0.0
    n_clicks: int = 0


@dataclass
class AcousticFeatures:
    ici_mean: float = 0.0
    ici_std: float = 0.0
    duration: float = 0.0
    buzz_check: float = 0.0
    peak_freq: float = 0.0
    center_freq: float = 0.0
    bandwidth_3db: float = 0.0
    spl_mean: float = 0.0
    spl_std: float = 0.0
    av_splr: float = 0.0
    sd_pi: float = 0.0
    start_freq: float = 0.0
    end_freq: float = 0.0


@dataclass
class PorpoiseObservation:
    timestamp: datetime
    latitude: float
    longitude: float
    group_size: int = 1
    calves: int = 0
    behavior: str = ""
    detection_method: str = ""
    confidence: float = 1.0
    notes: str = ""


@dataclass
class ResearchContext:
    research_question: str
    phase: ResearchPhase = ResearchPhase.LITERATURE_REVIEW
    target_species: str = "Neophocaena asiaeorientalis asiaeorientalis"
    study_area: str = ""
    time_range: tuple = ("", "")
    constraints: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ReasoningTrace:
    subgoals: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    uncertainties: list = field(default_factory=list)
    rejected_paths: list = field(default_factory=list)
    raw_reasoning: str = ""


# ── 新增: BDI 相关类型 ──────────────────────────────────────

@dataclass
class BDIState:
    """BDI 状态快照 (用于持久化和传输)"""
    belief_summary: str = ""
    desire_goal: str = ""
    intention_plan: list[str] = field(default_factory=list)
    intention_progress: float = 0.0
    status: str = "idle"


@dataclass
class Observation:
    """
    MDP 中的观察 O_t

    包含 Agent 从环境中感知到的一切信息。
    """
    action_name: str = ""
    params: dict = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    requires_approval: bool = False
    approval_message: str = ""
    timestamp: float = 0.0


@dataclass
class Action:
    """
    MDP 中的动作 A_t

    对应策略函数 π(A_t | O_t, M_t) 的输出。
    """
    name: str
    params: dict = field(default_factory=dict)
    thought: str = ""                   # 推理过程
    expected_output: str = ""           # 期望输出描述
    requires_approval: bool = False
    fallback: Optional[str] = None


@dataclass
class MDPStep:
    """
    MDP 单步记录

    S_t → A_t → O_{t+1} → S_{t+1}
    """
    step_id: int
    state_before: Optional["BDIState"] = None
    action: Optional[Action] = None
    observation: Optional[Observation] = None
    state_after: Optional["BDIState"] = None
    reward: float = 0.0                # 外部奖励信号
    timestamp: float = 0.0


# ── 新增: 推理节点 (用于 ToT/GoT) ──────────────────────────

@dataclass
class ReasoningNode:
    """思维树/图中的推理节点"""
    id: str
    content: str
    parent_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)
    score: float = 0.0
    depth: int = 0
    visits: int = 0
    value: float = 0.0


# ── 新增: MAS 拓扑类型 ─────────────────────────────────────

@dataclass
class AgentNode:
    """MAS 拓扑中的 Agent 节点"""
    agent_id: str
    agent_type: str
    capabilities: list[str] = field(default_factory=list)
    status: str = "idle"
    load: int = 0                      # 任务负载


@dataclass
class TopologyEdge:
    """MAS 拓扑中的通信边"""
    source: str
    target: str
    weight: float = 1.0
    condition: Optional[str] = None
    message_types: list[str] = field(default_factory=list)


# ── 新增: Reflexion 类型 ───────────────────────────────────

@dataclass
class ReflexionRecord:
    """反思记录"""
    step_id: int
    type: str = ""                     # error_correction / quality_improve / path_backtrack
    severity: str = "medium"           # critical / high / medium / low
    diagnosis: str = ""
    suggestion: str = ""
    verbal_feedback: str = ""          # 注入下一次迭代的反馈文本
    timestamp: float = 0.0
