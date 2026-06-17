"""CognitiveAnalyzer — BDI-inspired domain analysis engine for coilia-agent.

Cross-pollination from porpoise-agent's cognitive architecture:
  - BDI state machine (Belief → Desire → Intention)
  - Self-reflection loop (analyze → reflect → improve)
  - Cross-project knowledge supply from fish-ecology-assistant (V0)
  - Search delegation to cognitive-search-engine (V1)

Architecture:
  Belief  = Species KB + fish-ecology KB lookup + prior research
  Desire  = Research question + domain constraints
  Intention = Analysis plan → Execute → Reflect → Refine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CognitiveState(str, Enum):
    """BDI cognitive states — from porpoise-agent BDI pattern."""
    IDLE = "idle"
    PERCEIVING = "perceiving"      # Gathering beliefs
    DELIBERATING = "deliberating"  # Forming intentions
    EXECUTING = "executing"        # Running analysis
    REFLECTING = "reflecting"      # Self-critique
    DONE = "done"


@dataclass
class Belief:
    """What the agent knows about a domain question."""
    species_data: Dict[str, Any] = field(default_factory=dict)
    prior_knowledge: List[str] = field(default_factory=list)
    search_results: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1


@dataclass
class Desire:
    """What the agent wants to achieve."""
    question: str
    theme_id: str = ""
    depth: str = "standard"  # quick / standard / deep
    expected_outputs: List[str] = field(default_factory=list)


@dataclass
class Intention:
    """Concrete analysis plan."""
    steps: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    data_requirements: List[str] = field(default_factory=list)
    fallback_plan: str = ""


@dataclass
class Reflection:
    """Self-critique after analysis — from porpoise-agent Reflexion pattern."""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)
    confidence_adjustment: float = 0.0
    needs_reanalysis: bool = False
    suggested_improvements: List[str] = field(default_factory=list)


@dataclass
class CognitiveResult:
    """Complete cognitive cycle output."""
    question: str
    theme_id: str
    state: CognitiveState = CognitiveState.IDLE
    belief: Belief = field(default_factory=Belief)
    desire: Desire = field(default_factory=Desire)
    intention: Intention = field(default_factory=Intention)
    findings: List[str] = field(default_factory=list)
    reflection: Optional[Reflection] = None
    sources_used: List[str] = field(default_factory=list)
    triangles_engaged: List[str] = field(default_factory=list)


class CognitiveAnalyzer:
    """BDI-inspired cognitive analysis engine.

    Cross-pollination sources:
      - porpoise-agent: BDI state machine + Reflexion pattern
      - fish-ecology-assistant (V0): Knowledge supply for species data
      - cognitive-search-engine (V1): Multi-source search verification
      - eon-core (Coord): Triangle coordination protocol
    """

    def __init__(self, species_config: Dict[str, Any]):
        self.species_config = species_config
        self.state = CognitiveState.IDLE
        self._iteration = 0
        self._max_iterations = 3

    # ── Public API ──

    def analyze(self, question: str, theme_id: str = "",
                search_results: Optional[Dict[str, Any]] = None,
                depth: str = "standard") -> CognitiveResult:
        """Execute a full BDI cognitive cycle.

        Pipeline: PERCEIVE → DELIBERATE → EXECUTE → REFLECT → (repeat or DONE)
        """
        self.state = CognitiveState.PERCEIVING

        # Phase 1: PERCEIVE — gather beliefs
        belief = self._perceive(question, theme_id, search_results)

        # Phase 2: DELIBERATE — form intentions
        desire = Desire(question=question, theme_id=theme_id, depth=depth)
        intention = self._deliberate(belief, desire)

        # Phase 3: EXECUTE — run analysis
        self.state = CognitiveState.EXECUTING
        findings = self._execute(belief, desire, intention)

        # Phase 4: REFLECT — self-critique (from porpoise-agent Reflexion)
        self.state = CognitiveState.REFLECTING
        reflection = self._reflect(findings, belief, desire)

        # Iterative refinement loop
        while (reflection.needs_reanalysis and
               self._iteration < self._max_iterations):
            self._iteration += 1
            logger.info(f"Cognitive refinement iteration {self._iteration}")
            intention = self._deliberate(belief, desire, reflection)
            new_findings = self._execute(belief, desire, intention)
            findings.extend(new_findings)
            reflection = self._reflect(findings, belief, desire)

        self.state = CognitiveState.DONE
        return CognitiveResult(
            question=question,
            theme_id=theme_id,
            state=self.state,
            belief=belief,
            desire=desire,
            intention=intention,
            findings=findings,
            reflection=reflection,
            sources_used=self._list_sources(),
            triangles_engaged=self._list_triangles(),
        )

    # ── BDI Phases ──

    def _perceive(self, question: str, theme_id: str,
                  search_results: Optional[Dict]) -> Belief:
        """Gather all available knowledge (Belief formation).

        Sources:
          1. Local species config (always available)
          2. fish-ecology-assistant KB (V0 cross-project)
          3. cognitive-search-engine results (V1 cross-project)
        """
        belief = Belief()

        # Source 1: Local species knowledge
        belief.species_data = {
            "scientific": self.species_config.get("species_scientific", ""),
            "chinese": self.species_config.get("species_chinese", []),
            "profile": self.species_config.get("profile", {}),
            "research_themes": self.species_config.get("research_themes", {}),
        }
        belief.prior_knowledge = self._extract_prior_knowledge(theme_id)

        # Source 2: Cross-project — fish-ecology KB (V0)
        try:
            from fish_ecology_assistant.src.adapter import FishEcologyAdapter
            adapter = FishEcologyAdapter()
            kb_result = adapter.search_species(
                self.species_config.get("species_scientific", ""),
                self.species_config.get("species_chinese", [""])[0],
            )
            if kb_result.get("known_species"):
                belief.species_data["kb_data"] = kb_result.get("species_data", {})
                belief.confidence += 0.3
        except (ImportError, Exception) as e:
            logger.debug(f"V0 KB unavailable: {e}")

        # Source 3: Cross-project — cognitive-search-engine results (V1)
        if search_results:
            belief.search_results = search_results
            papers = search_results.get("papers", search_results.get("items", []))
            belief.prior_knowledge.extend(
                [f"Search: {p.get('title', '')}" for p in papers[:5]]
            )
            belief.confidence += min(0.4, len(papers) * 0.05)
        else:
            belief.constraints.append("no_search_results")

        # Baseline confidence from local KB
        if belief.prior_knowledge:
            belief.confidence = max(belief.confidence, 0.3)

        return belief

    def _deliberate(self, belief: Belief, desire: Desire,
                    prev_reflection: Optional[Reflection] = None) -> Intention:
        """Form analysis intentions based on beliefs and desires.

        Incorporates feedback from previous reflection cycle.
        """
        theme = self.species_config.get("research_theimes", {}).get(
            desire.theme_id, {}
        )

        methods = []
        if desire.theme_id == "migration":
            methods = ["Sr/Ca ratio analysis", "LA-ICP-MS line scan",
                      "migration pattern modeling", "habitat connectivity assessment"]
        elif desire.theme_id == "genetics":
            methods = ["microsatellite (SSR) analysis", "mitochondrial COI/D-loop",
                      "SNP genotyping", "effective population size (Ne) estimation"]
        elif desire.theme_id == "stock":
            methods = ["CPUE standardization", "Schaefer surplus production model",
                      "MSY estimation", "fishery-dependent data analysis"]
        elif desire.theme_id == "feeding":
            methods = ["stable isotope analysis (δ¹³C/δ¹⁵N)",
                      "stomach content analysis", "DNA metabarcoding",
                      "trophic niche breadth calculation"]
        elif desire.theme_id == "early_life":
            methods = ["spawning ground survey", "larval fish resource assessment",
                      "recruitment dynamics modeling", "hydrological correlation"]
        else:
            methods = ["literature synthesis", "knowledge gap identification",
                      "cross-study comparison"]

        steps = [f"Review {len(belief.prior_knowledge)} knowledge items",
                 f"Apply {', '.join(methods[:2])}",
                 "Synthesize findings",
                 "Identify gaps and uncertainties"]

        if prev_reflection and prev_reflection.suggested_improvements:
            steps.extend(prev_reflection.suggested_improvements)

        return Intention(
            steps=steps,
            methods=methods,
            data_requirements=self._derive_data_requirements(desire.theme_id),
            fallback_plan="Return best-available synthesis with confidence caveats",
        )

    def _execute(self, belief: Belief, desire: Desire,
                 intention: Intention) -> List[str]:
        """Execute the analysis intention.

        Integrates: local KB findings + search results + cross-project data.
        """
        findings = []

        # Species identification
        sci = belief.species_data.get("scientific", "")
        cn = ", ".join(belief.species_data.get("chinese", []))
        findings.append(f"## 物种识别: {sci} ({cn})")

        # Domain-specific analysis
        theme_label = self.species_config.get("research_themes", {}).get(
            desire.theme_id, {}).get("label", "文献综述")
        findings.append(f"## 研究方向: {theme_label}")

        # Extract from prior knowledge
        if belief.prior_knowledge:
            findings.append(f"### 已有知识 ({len(belief.prior_knowledge)} 条)")
            for item in belief.prior_knowledge[:10]:
                findings.append(f"  - {item}")

        # Extract from search results
        if belief.search_results:
            papers = belief.search_results.get("papers",
                        belief.search_results.get("items", []))
            if papers:
                findings.append(f"### 文献证据 ({len(papers)} 篇)")
                for p in papers[:5]:
                    title = p.get("title", p.get("name", "Unknown"))
                    year = p.get("year", p.get("date", ""))
                    findings.append(f"  - {title} ({year})")

        # Method application note
        findings.append(f"### 分析方法: {', '.join(intention.methods[:3])}")

        # Cross-project KB enrichment
        kb = belief.species_data.get("kb_data", {})
        if kb:
            conservation = kb.get("conservation", "")
            ecology = kb.get("ecology", "")
            if conservation:
                findings.append(f"### 保护等级 (V0 KB): {conservation}")
            if ecology:
                findings.append(f"### 生态特征 (V0 KB): {ecology}")

        # Gap identification
        gaps = self._identify_gaps(belief, desire)
        if gaps:
            findings.append(f"### 知识空白: {', '.join(gaps)}")

        # Confidence statement
        findings.append(f"### 置信度: {belief.confidence:.0%} "
                       f"({'多源验证' if belief.confidence > 0.6 else '需进一步搜索'})")

        return findings

    def _reflect(self, findings: List[str], belief: Belief,
                 desire: Desire) -> Reflection:
        """Self-critique — from porpoise-agent Reflexion pattern.

        Evaluates: completeness, consistency, confidence, actionability.
        """
        refl = Reflection()

        # Strengths
        if belief.confidence > 0.5:
            refl.strengths.append("Multi-source evidence available")
        if len(findings) > 5:
            refl.strengths.append("Comprehensive analysis across multiple dimensions")
        if belief.species_data.get("kb_data"):
            refl.strengths.append("Cross-project V0 knowledge enrichment")

        # Weaknesses
        if belief.confidence < 0.4:
            refl.weaknesses.append("Low confidence — limited evidence base")
            refl.needs_reanalysis = True
        if "no_search_results" in belief.constraints:
            refl.weaknesses.append("No search results available — analysis is KB-only")
        if len(belief.prior_knowledge) < 3:
            refl.weaknesses.append("Insufficient prior knowledge items")

        # Missing evidence
        refl.missing_evidence = self._identify_gaps(belief, desire)

        # Confidence adjustment
        if refl.missing_evidence:
            refl.confidence_adjustment = -0.2
        if refl.strengths and not refl.weaknesses:
            refl.confidence_adjustment = 0.1

        # Suggestions
        if refl.needs_reanalysis:
            refl.suggested_improvements = [
                "Expand search to include Chinese databases (CNKI, 万方)",
                "Cross-reference with V0 species knowledge base",
                "Include grey literature and agency reports",
            ]

        return refl

    # ── Helpers ──

    def _extract_prior_knowledge(self, theme_id: str) -> List[str]:
        """Extract prior knowledge from species config for a theme."""
        knowledge = []
        profile = self.species_config.get("profile", {})

        if profile.get("family"):
            knowledge.append(f"分类: {profile['family']}")
        if profile.get("migration_type"):
            knowledge.append(f"洄游类型: {profile['migration_type']}")
        if profile.get("historical_peak"):
            knowledge.append(f"历史峰值: {profile['historical_peak']}")
        if profile.get("current_status"):
            knowledge.append(f"资源现状: {profile['current_status']}")
        if profile.get("research_group"):
            knowledge.append(f"课题组: {profile['research_group']}")

        # Theme-specific knowledge
        theme_knowledge = {
            "migration": [
                "耳石微化学 Sr/Ca 比值可区分淡水/半咸水/海水生境",
                "LA-ICP-MS 线扫描分辨率通常为 10μm/点",
                "长江口崇明段和靖江段为关键栖息地",
            ],
            "genetics": [
                "微卫星(SSR)标记用于群体遗传结构分析",
                "线粒体 COI 和 D-loop 为常用分子标记",
                "SNP 标记可提供全基因组水平的遗传多样性评估",
            ],
            "stock": [
                "CPUE 标准化常用 GLM/GAM 方法",
                "Schaefer 和 Fox 模型为常用剩余产量模型",
                "MSY 估算需考虑环境容纳量 K 和内禀增长率 r",
            ],
            "feeding": [
                "δ¹³C 指示食物来源 (碳源)",
                "δ¹⁵N 指示营养级位置 (每级富集约3.4‰)",
                "胃含物分析与稳定同位素互补使用",
            ],
            "early_life": [
                "产卵期 4-6月，水温 18-25°C",
                "仔鱼资源量年际波动与水文条件密切相关",
                "长江中下游干流和鄱阳湖为主要产卵场",
            ],
        }
        knowledge.extend(theme_knowledge.get(theme_id, []))

        return knowledge

    def _derive_data_requirements(self, theme_id: str) -> List[str]:
        """Derive data needs for a research theme."""
        requirements = {
            "migration": ["耳石样品", "Sr/Ca 比值数据", "盐度梯度数据"],
            "genetics": ["组织样品 (鳍条/肌肉)", "DNA 提取", "PCR 扩增数据"],
            "stock": ["渔获量时间序列", "捕捞努力量数据", "环境变量数据"],
            "feeding": ["胃含物样品", "稳定同位素数据", "潜在食源同位素基线"],
            "early_life": ["仔鱼密度数据", "水温/流量时间序列", "产卵场分布数据"],
        }
        return requirements.get(theme_id, ["文献全文", "研究数据"])

    def _identify_gaps(self, belief: Belief, desire: Desire) -> List[str]:
        """Identify knowledge gaps for a theme."""
        gaps = []
        theme_gaps = {
            "migration": ["不同江段洄游路线的精确时空分布",
                         "气候变化对洄游物候的影响"],
            "genetics": ["全基因组水平的适应性进化研究",
                        "不同群体间的基因流定量评估"],
            "stock": ["长时间序列 (30年+) 资源量重建",
                     "气候变化情景下的MSY预测"],
            "feeding": ["不同生活史阶段的食性转变定量分析",
                       "种间食物竞争强度评估"],
            "early_life": ["产卵场微生境特征定量描述",
                          "早期补充过程的环境驱动机制"],
        }
        gaps.extend(theme_gaps.get(desire.theme_id, []))
        if "no_search_results" in belief.constraints:
            gaps.append("缺少最新文献搜索数据")
        return gaps

    def _list_sources(self) -> List[str]:
        return ["species_config (local)", "fish-ecology KB (V0)",
                "cognitive-search-engine (V1)", "prior_knowledge"]

    def _list_triangles(self) -> List[str]:
        return ["S(fish-ecology V0)", "V(cognitive-search V1)"]

    @property
    def iteration_count(self) -> int:
        return self._iteration

    def reset(self) -> None:
        self.state = CognitiveState.IDLE
        self._iteration = 0
