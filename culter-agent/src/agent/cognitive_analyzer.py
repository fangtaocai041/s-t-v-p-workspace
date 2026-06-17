"""CognitiveAnalyzer — BDI-inspired domain analysis engine for culter-agent.

Cross-pollination from porpoise-agent's cognitive architecture:
  - BDI state machine (Belief → Desire → Intention)
  - Self-reflection loop (analyze → reflect → improve)
  - Cross-project knowledge supply from fish-ecology-assistant (V0)
  - Search delegation to cognitive-search-engine (V1)

Culter-specific: 9-phase pipeline covering genomics, stable isotopes,
sympatric coexistence, and habitat modeling for Culter species.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CognitiveState(str, Enum):
    IDLE = "idle"
    PERCEIVING = "perceiving"
    DELIBERATING = "deliberating"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    DONE = "done"


@dataclass
class Belief:
    species_data: Dict[str, Any] = field(default_factory=dict)
    prior_knowledge: List[str] = field(default_factory=list)
    search_results: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class Desire:
    question: str
    phase_id: str = "literature_review"
    depth: str = "standard"
    expected_outputs: List[str] = field(default_factory=list)


@dataclass
class Intention:
    steps: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    data_requirements: List[str] = field(default_factory=list)
    fallback_plan: str = ""


@dataclass
class Reflection:
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)
    confidence_adjustment: float = 0.0
    needs_reanalysis: bool = False
    suggested_improvements: List[str] = field(default_factory=list)


@dataclass
class CognitiveResult:
    question: str
    phase_id: str
    state: CognitiveState = CognitiveState.IDLE
    belief: Belief = field(default_factory=Belief)
    desire: Desire = field(default_factory=Desire)
    intention: Intention = field(default_factory=Intention)
    findings: List[str] = field(default_factory=list)
    reflection: Optional[Reflection] = None
    sources_used: List[str] = field(default_factory=list)
    triangles_engaged: List[str] = field(default_factory=list)


# Culter-specific domain knowledge (cross-pollination from culter KB)
CULTER_DOMAIN_KNOWLEDGE = {
    "growth_analysis": [
        "VBGF (von Bertalanffy Growth Function): L_t = L∞(1 - e^(-K(t-t₀)))",
        "翘嘴鲌 L∞ 约 80-120 cm, K 约 0.10-0.25 year⁻¹",
        "鳞片/耳石/脊椎骨用于年龄鉴定，耳石最可靠",
        "生长拐点年龄 t_op 用于确定最适捕捞规格",
    ],
    "genomics_analysis": [
        "翘嘴鲌基因组大小约 1.0-1.2 Gb, 染色体数 2n=48",
        "MITO 基因组: 13 PCGs + 22 tRNA + 2 rRNA + D-loop",
        "RAD-seq/GBS 简化基因组技术适用于种群基因组学",
        "比较基因组学可用于揭示鲌亚科适应性进化",
    ],
    "genetics_analysis": [
        "微卫星(SSR)标记揭示长江/珠江群体遗传分化",
        "线粒体 COI/Cytb/D-loop 用于谱系地理分析",
        "SNP 标记提供全基因组水平的遗传多样性评估",
        "有效群体大小(Ne)常用 LD法或 Coalescent 法估算",
    ],
    "trophic_ecology": [
        "δ¹³C 指示碳源 (沿岸带 vs 敞水带)",
        "δ¹⁵N 指示营养级位置 (每级富集约 3.4‰)",
        "MixSIAR 贝叶斯混合模型用于定量食源贡献",
        "SIBER 用于计算营养生态位宽度和重叠度",
        "Levin 指数: B = 1/Σ(p_i²), 标准化 B_A = (B-1)/(n-1)",
        "Pianka 重叠指数: O_jk = Σ(p_ij·p_ik)/√(Σp_ij²·Σp_ik²)",
    ],
    "coexistence_modeling": [
        "同域共存机制: 食性分化/空间分化/时间分化",
        "翘嘴鲌 vs 蒙古鲌: 食性转换时序差异 (鲌→鱼→虾)",
        "翘嘴鲌 vs 尖头鲌: 微生境选择差异",
        "翘嘴鲌 vs 达氏鲌: 产卵时间错峰 (春 vs 初夏)",
    ],
    "resource_assessment": [
        "CPUE 标准化: GLM/GAM/Delta-lognormal 方法",
        "剩余产量模型: Schaefer (对称) / Fox (不对称)",
        "YPR (Yield Per Recruit) 模型用于捕捞规制评估",
        "数据缺乏时可用 CMSY/LBB 等有限数据方法",
    ],
    "habitat_modeling": [
        "HSI (Habitat Suitability Index) 模型",
        "MaxEnt/Maxlike 物种分布模型",
        "关键环境因子: 水深/流速/水温/透明度/DO",
        "水文情势变化 (三峡调度) 对产卵场的影响评估",
    ],
}


class CognitiveAnalyzer:
    """BDI-inspired cognitive analysis for culter domain research.

    Cross-pollination:
      - porpoise-agent: BDI+ReAct+Reflexion architecture
      - coilia-agent: CognitiveAnalyzer pattern (sibling project)
      - fish-ecology-assistant (V0): Species KB enrichment
      - cognitive-search-engine (V1): Multi-source search
    """

    def __init__(self, species_profile: Dict[str, Any]):
        self.species_profile = species_profile
        self.state = CognitiveState.IDLE
        self._iteration = 0
        self._max_iterations = 3

    def analyze(self, question: str, phase_id: str = "",
                search_results: Optional[Dict[str, Any]] = None,
                depth: str = "standard") -> CognitiveResult:
        """Execute full BDI cognitive cycle for culter research."""
        self.state = CognitiveState.PERCEIVING

        belief = self._perceive(question, phase_id, search_results)
        desire = Desire(question=question, phase_id=phase_id, depth=depth)
        intention = self._deliberate(belief, desire)

        self.state = CognitiveState.EXECUTING
        findings = self._execute(belief, desire, intention)

        self.state = CognitiveState.REFLECTING
        reflection = self._reflect(findings, belief, desire)

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
            phase_id=phase_id,
            state=self.state,
            belief=belief,
            desire=desire,
            intention=intention,
            findings=findings,
            reflection=reflection,
            sources_used=self._list_sources(),
            triangles_engaged=self._list_triangles(),
        )

    def _perceive(self, question: str, phase_id: str,
                  search_results: Optional[Dict]) -> Belief:
        """Gather beliefs from species KB + cross-project sources."""
        belief = Belief()

        # Source 1: Local species profile
        belief.species_data = dict(self.species_profile)
        belief.prior_knowledge = CULTER_DOMAIN_KNOWLEDGE.get(phase_id, [])

        # Source 2: fish-ecology V0 cross-project
        try:
            from fish_ecology_assistant.src.adapter import FishEcologyAdapter
            adapter = FishEcologyAdapter()
            kb_result = adapter.search_species(
                self.species_profile.get("primary_species", "Culter alburnus"),
                self.species_profile.get("chinese_name", "翘嘴鲌"),
            )
            if kb_result.get("known_species"):
                belief.species_data["kb_data"] = kb_result.get("species_data", {})
                belief.confidence += 0.3
        except (ImportError, Exception) as e:
            logger.debug(f"V0 KB unavailable: {e}")

        # Source 3: search results from V1
        if search_results:
            belief.search_results = search_results
            papers = search_results.get("papers", search_results.get("items", []))
            belief.confidence += min(0.4, len(papers) * 0.05)
        else:
            belief.constraints.append("no_search_results")

        belief.confidence = max(belief.confidence,
                                0.2 if belief.prior_knowledge else 0.0)
        return belief

    def _deliberate(self, belief: Belief, desire: Desire,
                    prev_reflection: Optional[Reflection] = None) -> Intention:
        """Form analysis intentions."""
        methods_map = {
            "growth_analysis": ["VBGF fitting", "Age-length key", "Back-calculation"],
            "genomics_analysis": ["Genome assembly QC", "Gene family analysis",
                                  "Positive selection scan", "Synteny comparison"],
            "genetics_analysis": ["Genetic diversity indices", "F_ST pairwise",
                                  "AMOVA", "STRUCTURE/ADMIXTURE", "Ne estimation"],
            "trophic_ecology": ["δ¹³C/δ¹⁵N biplot", "MixSIAR mixing model",
                               "SIBER niche metrics", "Levin/Pianka indices"],
            "coexistence_modeling": ["Niche overlap quantification",
                                    "Resource partitioning axis analysis",
                                    "Temporal/spatial segregation test"],
            "resource_assessment": ["CPUE standardization", "Surplus production model",
                                   "MSY/MSY_range estimation", "Kobe plot"],
            "habitat_modeling": ["HSI modeling", "Environmental envelope",
                                "Spatial prediction", "Climate scenario projection"],
        }
        methods = methods_map.get(desire.phase_id, ["Literature synthesis"])

        steps = [
            f"Review domain knowledge ({len(belief.prior_knowledge)} items)",
            f"Apply {methods[0]}",
            "Cross-reference with related species",
            "Synthesize and identify gaps",
        ]
        if prev_reflection and prev_reflection.suggested_improvements:
            steps.extend(prev_reflection.suggested_improvements)

        return Intention(
            steps=steps,
            methods=methods,
            data_requirements=self._derive_data_requirements(desire.phase_id),
            fallback_plan="Return KB-based synthesis with caveats",
        )

    def _execute(self, belief: Belief, desire: Desire,
                 intention: Intention) -> List[str]:
        """Execute analysis intention."""
        findings = []

        # Header
        sp = belief.species_data
        sci = sp.get("primary_species", sp.get("scientific", "Culter spp."))
        cn = sp.get("chinese_name", sp.get("chinese", "鲌类"))
        findings.append(f"## 物种: {sci} ({cn})")

        phase_labels = {
            "growth_analysis": "年龄与生长",
            "genomics_analysis": "基因组学",
            "genetics_analysis": "群体遗传学",
            "trophic_ecology": "营养生态位与稳定同位素",
            "coexistence_modeling": "同域共存机制",
            "resource_assessment": "资源评估",
            "habitat_modeling": "栖息地建模",
        }
        label = phase_labels.get(desire.phase_id, desire.phase_id)
        findings.append(f"## 研究方向: {label}")

        # Domain knowledge
        if belief.prior_knowledge:
            findings.append(f"### 领域知识 ({len(belief.prior_knowledge)} 条)")
            for item in belief.prior_knowledge[:8]:
                findings.append(f"  - {item}")

        # Species-specific data
        if sp.get("max_length_cm"):
            findings.append(f"  - 最大体长: {sp['max_length_cm']}")
        if sp.get("lifespan_years"):
            findings.append(f"  - 寿命: {sp['lifespan_years']}")
        if sp.get("feeding_type"):
            findings.append(f"  - 食性: {sp['feeding_type']}")

        # Isotope baselines (unique to culter KB)
        baselines = sp.get("isotope_baselines", {})
        if baselines:
            findings.append("### 同位素基线")
            for org, desc in baselines.items():
                findings.append(f"  - {org}: {desc}")

        # Niche axes
        axes = sp.get("niche_axes", {})
        if axes:
            findings.append("### 生态位分化轴")
            for axis, desc in axes.items():
                findings.append(f"  - {axis}: {desc}")

        # Coexisting species
        related = sp.get("related_species", [])
        if related:
            findings.append(f"### 近缘/同域物种 ({len(related)} 种)")
            for rs in related[:5]:
                findings.append(f"  - {rs}")

        # Methods
        findings.append(f"### 分析方法: {', '.join(intention.methods[:3])}")

        # Gaps
        gaps = self._identify_gaps(belief, desire)
        if gaps:
            findings.append(f"### 知识空白: {', '.join(gaps)}")

        findings.append(f"### 置信度: {belief.confidence:.0%} "
                       f"({'多源验证' if belief.confidence > 0.5 else '基于KB，需搜索验证'})")

        return findings

    def _reflect(self, findings: List[str], belief: Belief,
                 desire: Desire) -> Reflection:
        """Self-critique from porpoise-agent Reflexion pattern."""
        refl = Reflection()

        if belief.confidence > 0.5:
            refl.strengths.append("Multi-source evidence integrated")
        if len(findings) > 8:
            refl.strengths.append("Comprehensive multi-dimensional analysis")
        if belief.species_data.get("kb_data"):
            refl.strengths.append("V0 cross-project species KB enrichment")
        if belief.species_data.get("isotope_baselines"):
            refl.strengths.append("Isotope baseline data available")

        if belief.confidence < 0.3:
            refl.weaknesses.append("Low confidence — insufficient evidence")
            refl.needs_reanalysis = True
        if "no_search_results" in belief.constraints:
            refl.weaknesses.append("No search results — KB-only analysis")
        if len(belief.prior_knowledge) < 3:
            refl.weaknesses.append("Limited domain knowledge items")

        refl.missing_evidence = self._identify_gaps(belief, desire)

        if refl.missing_evidence:
            refl.confidence_adjustment = -0.15
        refl.confidence_adjustment += 0.05 * len(refl.strengths)

        if refl.needs_reanalysis:
            refl.suggested_improvements = [
                "Expand to Chinese databases (CNKI, CSCD, 万方)",
                "Cross-reference with coilia-agent isotope methods",
                "Add porpoise-agent habitat modeling comparison",
                "Include grey literature from fishery agencies",
            ]

        return refl

    def _derive_data_requirements(self, phase_id: str) -> List[str]:
        reqs = {
            "growth_analysis": ["Age-length data", "Otolith/scale samples", "VBGF parameters"],
            "genomics_analysis": ["Genome assembly (FASTA)", "Annotation (GFF)", "RNA-seq data"],
            "genetics_analysis": ["Genotype data (VCF)", "Population labels", "Geographic coordinates"],
            "trophic_ecology": ["δ¹³C/δ¹⁵N measurements", "Prey isotope data", "Diet composition matrix"],
            "coexistence_modeling": ["Multi-species diet data", "Spatial occurrence records", "Environmental covariates"],
            "resource_assessment": ["Catch time series (10+ years)", "Fishing effort data", "Life history parameters"],
            "habitat_modeling": ["Species occurrence points", "Environmental raster layers", "Hydrographic data"],
        }
        return reqs.get(phase_id, ["Relevant literature", "Research data"])

    def _identify_gaps(self, belief: Belief, desire: Desire) -> List[str]:
        gaps_map = {
            "growth_analysis": ["长期 (20年+) 生长时间序列", "气候变暖对生长速率的影响"],
            "genomics_analysis": ["染色体水平参考基因组", "适应性进化功能验证"],
            "genetics_analysis": ["全流域尺度群体基因组学", "历史有效群体大小重建"],
            "trophic_ecology": ["年际同位素基线变化", "不同水文年的食性可塑性"],
            "coexistence_modeling": ["控制实验验证共存机制", "气候变化下的共存前景"],
            "resource_assessment": ["独立于渔业的丰度指数", "增殖放流效果定量评估"],
            "habitat_modeling": ["三峡调度对产卵场的影响量化", "生态调度优化方案"],
        }
        gaps = list(gaps_map.get(desire.phase_id, []))
        if "no_search_results" in belief.constraints:
            gaps.append("缺少最新文献搜索数据")
        return gaps

    def _list_sources(self) -> List[str]:
        return ["species_profile (local KB)", "fish-ecology KB (V0)",
                "cognitive-search-engine (V1)", "culter domain knowledge"]

    def _list_triangles(self) -> List[str]:
        return ["S(fish-ecology V0)", "V(cognitive-search V1)"]

    @property
    def iteration_count(self) -> int:
        return self._iteration

    def reset(self) -> None:
        self.state = CognitiveState.IDLE
        self._iteration = 0
