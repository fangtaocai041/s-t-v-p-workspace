"""
自然语言理解 (NLU) — 意图识别与实体提取
────────────────────────────────────────
双层路由策略:
1. 关键词快速匹配 (确定性, 零延迟)
2. LLM 语义理解 (高精度, 作为 fallback)

输入: 用户原始自然语言文本
输出: Intent (意图分类) + Entities (命名实体列表) + Confidence (置信度)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)


# ── 意图枚举 ──────────────────────────────────────────────

class Intent(str, Enum):
    """用户意图分类"""
    # 研究任务
    LITERATURE_SEARCH = "literature_search"       # 文献检索
    LITERATURE_REVIEW = "literature_review"       # 文献综述
    ACOUSTIC_ANALYSIS = "acoustic_analysis"       # 声学数据分析
    CLICK_DETECTION = "click_detection"           # Click 脉冲检测
    ABUNDANCE_ESTIMATE = "abundance_estimate"     # 种群丰度估计
    HABITAT_MODEL = "habitat_model"               # 栖息地建模
    FIELD_SURVEY = "field_survey"                 # 野外调查规划
    CONSERVATION_ASSESS = "conservation_assess"   # 保护评估
    THREAT_ASSESS = "threat_assess"               # 威胁因子评估
    GENETIC_ANALYSIS = "genetic_analysis"         # 遗传分析
    REPORT_GENERATE = "report_generate"           # 报告生成
    # 元操作
    QUESTION_ANSWER = "question_answer"           # 一般问答
    TOOL_USE = "tool_use"                         # 工具调用
    CLARIFY = "clarify"                           # 澄清/追问
    UNKNOWN = "unknown"                           # 无法识别


# ── 实体类型 ──────────────────────────────────────────────

@dataclass
class Entity:
    """命名实体"""
    type: str           # species, location, method, device, time_range, metric
    value: str          # 实体原始文本
    normalized: str     # 规范化值
    start: int = -1     # 在原文中的起始位置
    end: int = -1       # 在原文中的结束位置


@dataclass
class NLUResult:
    """NLU 解析结果"""
    intent: Intent
    confidence: float           # 0.0 - 1.0
    entities: list[Entity] = field(default_factory=list)
    sub_intents: list[Intent] = field(default_factory=list)
    raw_input: str = ""
    routing_hint: str = ""      # 建议路由到的 Agent


# ── 关键词路由表 ──────────────────────────────────────────

INTENT_KEYWORDS: dict[Intent, list[str]] = {
    Intent.LITERATURE_SEARCH: [
        "搜索", "查找", "找文献", "找论文", "检索", "search",
        "find paper", "look up",
    ],
    Intent.LITERATURE_REVIEW: [
        "综述", "回顾", "进展", "研究现状", "文献综述", "review",
        "overview", "state of the art", "survey",
    ],
    Intent.ACOUSTIC_ANALYSIS: [
        "声学分析", "PAM", "passive acoustic", "声学监测",
        "声信号", "acoustic analysis", "sound analysis",
    ],
    Intent.CLICK_DETECTION: [
        "click", "脉冲", "回声定位", "echolocation", "NBHF",
        "窄带高频", "脉冲检测", "click detection",
    ],
    Intent.ABUNDANCE_ESTIMATE: [
        "丰度", "种群数量", "abundance", "population estimate",
        "密度", "density", "数量估算", "cue counting",
    ],
    Intent.HABITAT_MODEL: [
        "栖息地", "habitat", "分布", "distribution", "SDM",
        "MaxEnt", "生态位", "niche",
    ],
    Intent.FIELD_SURVEY: [
        "野外调查", "field survey", "样线", "transect",
        "调查规划", "路线", "部署",
    ],
    Intent.CONSERVATION_ASSESS: [
        "保护评估", "conservation assessment", "IUCN",
        "保护状况", "评估",
    ],
    Intent.THREAT_ASSESS: [
        "威胁", "threat", "风险", "risk", "干扰",
        "航运", "shipping", "噪声", "pollution",
    ],
    Intent.GENETIC_ANALYSIS: [
        "遗传", "genetic", "基因组", "genome", "DNA",
        "分子", "molecular",
    ],
    Intent.REPORT_GENERATE: [
        "生成报告", "写报告", "报告", "report", "草稿",
        "撰写", "draft", "manuscript",
    ],
}

# ── 物种实体列表 ──────────────────────────────────────────

KNOWN_SPECIES: dict[str, str] = {
    # 江豚
    "长江江豚": "Neophocaena asiaeorientalis asiaeorientalis",
    "江豚": "Neophocaena asiaeorientalis",
    "窄脊江豚": "Neophocaena asiaeorientalis",
    "东亚江豚": "Neophocaena asiaeorientalis",
    "宽脊江豚": "Neophocaena phocaenoides",
    "印太江豚": "Neophocaena phocaenoides",
    "finless porpoise": "Neophocaena",
    "yangtze finless porpoise": "Neophocaena asiaeorientalis asiaeorientalis",
    # 近缘种
    "中华白海豚": "Sousa chinensis",
    "白鱀豚": "Lipotes vexillifer",
    "长江白鲟": "Psephurus gladius",
    "鼠海豚": "Phocoenidae",
    "窄脊江豚长江亚种": "Neophocaena asiaeorientalis asiaeorientalis",
}

# ── 已知水域/地点 ─────────────────────────────────────────

KNOWN_LOCATIONS: dict[str, str] = {
    "长江": "Yangtze River",
    "鄱阳湖": "Poyang Lake",
    "洞庭湖": "Dongting Lake",
    "安庆": "Anqing",
    "芜湖": "Wuhu",
    "南京": "Nanjing",
    "镇江": "Zhenjiang",
    "天鹅洲": "Tian'ezhou",
    "天鹅洲故道": "Tian'ezhou Oxbow",
    "何王庙": "Hewangmiao",
}


class NLUProcessor:
    """
    自然语言理解处理器

    策略: 关键词快速匹配 (O(1)) → 置信度不足时 fallback 到 LLM

    用法:
        nlu = NLUProcessor()
        result = nlu.parse("搜索2020年以来关于江豚被动声学监测的文献")
        # result.intent -> Intent.LITERATURE_SEARCH
        # result.entities -> [Entity(type="species", ...), Entity(type="time_range", ...)]
    """

    def __init__(self, llm_fallback: bool = True):
        self.llm_fallback = llm_fallback
        self._intent_patterns = self._compile_patterns()
        logger.info("NLUProcessor initialized (keywords + LLM fallback)")

    def _compile_patterns(self) -> dict[Intent, list[re.Pattern]]:
        """预编译关键词正则"""
        patterns: dict[Intent, list[re.Pattern]] = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            patterns[intent] = [
                re.compile(re.escape(kw), re.IGNORECASE)
                for kw in keywords
            ]
        return patterns

    def parse(self, text: str) -> NLUResult:
        """
        解析用户输入 → 意图 + 实体

        Args:
            text: 用户原始自然语言输入

        Returns:
            NLUResult: 意图分类 + 实体列表 + 置信度
        """
        if not text.strip():
            return NLUResult(intent=Intent.UNKNOWN, confidence=0.0, raw_input=text)

        # 1. 关键词意图匹配
        intent, confidence = self._match_intent(text)

        # 2. 实体提取
        entities = self._extract_entities(text)

        # 3. 子意图检测 (复合查询)
        sub_intents = self._detect_sub_intents(text, intent)

        # 4. 路由提示
        routing_hint = self._compute_routing(intent, entities)

        return NLUResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            sub_intents=sub_intents,
            raw_input=text,
            routing_hint=routing_hint,
        )

    def _match_intent(self, text: str) -> tuple[Intent, float]:
        """关键词匹配意图"""
        scores: dict[Intent, int] = {}

        for intent, patterns in self._intent_patterns.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > 0:
                scores[intent] = score

        if not scores:
            return Intent.UNKNOWN, 0.0

        # 返回得分最高的意图
        best_intent = max(scores, key=scores.get)  # type: ignore
        max_score = scores[best_intent]
        total_score = sum(scores.values())
        confidence = min(max_score / max(total_score, 1), 1.0)

        return best_intent, confidence

    def _extract_entities(self, text: str) -> list[Entity]:
        """提取命名实体: 物种 / 地点 / 时间段 / 方法 / 设备"""
        entities: list[Entity] = []

        # 物种
        for name, normalized in KNOWN_SPECIES.items():
            if name.lower() in text.lower():
                pos = text.lower().find(name.lower())
                entities.append(Entity(
                    type="species",
                    value=text[pos:pos + len(name)],
                    normalized=normalized,
                    start=pos,
                    end=pos + len(name),
                ))

        # 地点
        for name, normalized in KNOWN_LOCATIONS.items():
            if name in text:
                pos = text.find(name)
                # 避免重复 (如"安庆江段"中已匹配"安庆")
                if not any(e.start <= pos < e.end for e in entities):
                    entities.append(Entity(
                        type="location",
                        value=text[pos:pos + len(name)],
                        normalized=normalized,
                        start=pos,
                        end=pos + len(name),
                    ))

        # 时间段 (年份范围 / 相对时间)
        time_entity = self._extract_time_range(text)
        if time_entity:
            entities.append(time_entity)

        # 设备
        device_entity = self._extract_device(text)
        if device_entity:
            entities.append(device_entity)

        # 方法
        method_entity = self._extract_method(text)
        if method_entity:
            entities.append(method_entity)

        return entities

    def _extract_time_range(self, text: str) -> Optional[Entity]:
        """提取时间段实体"""
        # 年份范围: "2020年以来", "2020-2024", "近五年"
        year_range = re.search(r'(\d{4})\s*年?\s*以[来后]', text)
        if year_range:
            return Entity(
                type="time_range",
                value=year_range.group(),
                normalized=f"{year_range.group(1)}-present",
            )

        year_span = re.search(r'(\d{4})\s*年?\s*[-–—至到和]\s*(\d{4})', text)
        if year_span:
            return Entity(
                type="time_range",
                value=year_span.group(),
                normalized=f"{year_span.group(1)}-{year_span.group(2)}",
            )

        relative = re.search(r'近\s*(\d+)\s*年', text)
        if relative:
            return Entity(
                type="time_range",
                value=relative.group(),
                normalized=f"last_{relative.group(1)}_years",
            )

        return None

    def _extract_device(self, text: str) -> Optional[Entity]:
        """提取设备实体"""
        devices = {
            "SoundTrap": "SoundTrap",
            "soundtrap": "SoundTrap",
            "A-tag": "A-tag",
            "a-tag": "A-tag",
            "C-POD": "C-POD",
            "c-pod": "C-POD",
            "F-POD": "F-POD",
            "RPCD": "RPCD-II",
            "RPCD-II": "RPCD-II",
        }
        for name, normalized in devices.items():
            if name in text:
                return Entity(type="device", value=name, normalized=normalized)
        return None

    def _extract_method(self, text: str) -> Optional[Entity]:
        """提取方法实体"""
        methods = {
            "cue counting": "cue_counting",
            "Cue Counting": "cue_counting",
            "distance sampling": "distance_sampling",
            "Distance Sampling": "distance_sampling",
            "SECR": "secr",
            "MaxEnt": "maxent",
            "最大熵": "maxent",
            "随机森林": "random_forest",
            "Random Forest": "random_forest",
        }
        for name, normalized in methods.items():
            if name in text:
                return Entity(type="method", value=name, normalized=normalized)
        return None

    def _detect_sub_intents(self, text: str, primary: Intent) -> list[Intent]:
        """检测子意图 (复合查询)"""
        sub = []
        for intent, patterns in self._intent_patterns.items():
            if intent != primary and any(p.search(text) for p in patterns):
                sub.append(intent)
        return sub

    def _compute_routing(self, intent: Intent, entities: list[Entity]) -> str:
        """根据意图 + 实体计算路由目标"""
        routing_map = {
            Intent.LITERATURE_SEARCH: "literature_agent",
            Intent.LITERATURE_REVIEW: "literature_agent",
            Intent.ACOUSTIC_ANALYSIS: "acoustic_agent",
            Intent.CLICK_DETECTION: "acoustic_agent",
            Intent.ABUNDANCE_ESTIMATE: "ecology_agent",
            Intent.HABITAT_MODEL: "ecology_agent",
            Intent.FIELD_SURVEY: "field_agent",
            Intent.CONSERVATION_ASSESS: "conservation_agent",
            Intent.THREAT_ASSESS: "conservation_agent",
            Intent.GENETIC_ANALYSIS: "genetics_agent",
            Intent.REPORT_GENERATE: "orchestrator",
            Intent.QUESTION_ANSWER: "orchestrator",
        }
        return routing_map.get(intent, "orchestrator")
