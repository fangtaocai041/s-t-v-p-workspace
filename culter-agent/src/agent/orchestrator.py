"""
Culter Agent Orchestrator — 鲌类专研管线协调器 (P₃, V4)

P₁(porpoise-agent), P₂(coilia-agent), P₃(culter-agent) 为同级平行项目，
分别对应 eon-core 四象顶点 V2, V3, V4。

共享基类: eon-core/src/orchestrator_base.py
  — VerificationStatus, ContradictionType, PhaseResult, PipelineResult
  — 可从 eon-core 导入以启用验证标记和矛盾分析

双模式:
  独立模式 (standalone): 作为独立 Agent，通过 project_loader 调用 cognitive
  集成模式 (integrated):  由 eon-core OriginKernel 调度，返回 DELEGATE 协议

9 阶段管线:
  Literature → Growth → Genomics → Genetics → Trophic → Coexistence → Resource → Habitat → Report
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── 共享类型 — from workspace-level shared_types
from scripts.shared_types import VerificationStatus, ContradictionType
try:
    from src.knowledge_base import get_knowledge_base
except ImportError:
    get_knowledge_base = None  # type: ignore
BasePhaseResult = object
BasePipelineResult = object


# ═══════════════════════════════════════════════════════════════
# Types (本地扩展 — 继承自 eon-core 共享基类)
# ═══════════════════════════════════════════════════════════════

class ResearchPhase(str, Enum):
    LITERATURE = "literature_review"
    GROWTH = "growth_analysis"
    GENOMICS = "genomics_analysis"
    GENETICS = "genetics_analysis"
    TROPHIC = "trophic_ecology"
    COEXISTENCE = "coexistence_modeling"
    RESOURCE = "resource_assessment"
    HABITAT = "habitat_modeling"
    REPORT = "report_generation"


class RunMode(str, Enum):
    STANDALONE = "standalone"
    INTEGRATED = "integrated"


@dataclass
class ResearchContext:
    question: str
    phase: ResearchPhase = ResearchPhase.LITERATURE
    mode: RunMode = RunMode.STANDALONE
    trace_id: str = ""


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
    errors: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Species Knowledge Base (内置 — 鲌类专研)
# ═══════════════════════════════════════════════════════════════

# ── 默认种配置 (知识库不可用时的回退) ──
_DEFAULT_PROFILE = {
    "primary_species": "Culter alburnus",
    "chinese_name": "翘嘴鲌 (白鱼/翘壳)",
    "family": "Cyprinidae (鲤科)",
    "subfamily": "Cultrinae (鲌亚科)",
    "feeding_type": "凶猛肉食性 (piscivorous)",
    "habitat": "湖泊/水库/河流缓流段中上层",
}


# ═══════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════

class CulterOrchestrator:
    """鲌类专研编排器 (P₃, 同级于 P₁ porpoise-agent / P₂ coilia-agent).

    9 阶段管线:
      Literature → Growth → Genomics → Genetics → Trophic → Coexistence → Resource → Habitat → Report
    """

    PHASE_ORDER = [
        ResearchPhase.LITERATURE,
        ResearchPhase.GROWTH,
        ResearchPhase.GENOMICS,
        ResearchPhase.GENETICS,
        ResearchPhase.TROPHIC,
        ResearchPhase.COEXISTENCE,
        ResearchPhase.RESOURCE,
        ResearchPhase.HABITAT,
        ResearchPhase.REPORT,
    ]

    PHASE_KEYWORDS: Dict[ResearchPhase, List[str]] = {
        ResearchPhase.GROWTH: [
            "年龄", "生长", "growth", "age", "vb", "von bertalanffy",
            "鳞片", "scale", "耳石", "otolith", "轮纹", "年轮",
        ],
        ResearchPhase.GENOMICS: [
            "基因组", "genome", "genomics", "测序", "sequencing", "组装",
            "assembly", "注释", "annotation", "rad-seq", "radseq",
            "gbs", "genotyping", "转录组", "transcriptome",
            "线粒体基因组", "mitogenome", "比较基因组", "comparative",
            "系统发育基因组", "phylogenomic", "全基因组", "whole genome",
            "简化基因组", "ddrad", "基因家族", "gene family",
        ],
        ResearchPhase.GENETICS: [
            "遗传", "genetic", "dna", "微卫星", "microsatellite", "ssr",
            "snp", "线粒体", "mitochondrial", "haplotype", "单倍型",
            "分化", "diversity", "遗传多样性", "基因流", "gene flow",
            "谱系地理", "phylogeography", "系统发育", "phylogenetic",
            "瓶颈", "bottleneck", "有效种群", "ne", "population structure",
            "种群历史", "demographic", "coi", "cytb", "d-loop",
        ],
        ResearchPhase.TROPHIC: [
            "同位素", "isotope", "δ13c", "δ15n", "δ34s", "稳定同位素",
            "stable isotope", "mixsiar", "siar", "siber", "混合模型",
            "营养级", "trophic position", "trophic level",
            "营养生态位", "trophic niche", "食性", "diet", "feeding",
            "胃含物", "gut content", "stomach content",
            "饵料", "prey", "食物组成", "food composition",
            "摄食", "foraging", "捕食", "predation",
        ],
        ResearchPhase.COEXISTENCE: [
            "共存", "coexistence", "同域", "sympatric", "生态位分化",
            "niche partitioning", "资源分割", "resource partitioning",
            "种间竞争", "interspecific competition", "生态位重叠",
            "niche overlap", "重叠", "重叠度", "pianka",
            "栖位", "空间生态位", "时间生态位", "营养生态位",
            "生态位宽度", "niche breadth", "levin",
        ],
        ResearchPhase.RESOURCE: [
            "资源", "stock", "cpue", "评估", "msy", "种群",
            "捕捞", "产量", "ypr", "补充", "recruitment",
            "增殖放流", "enhancement", "release",
        ],
        ResearchPhase.HABITAT: [
            "栖息地", "habitat", "生境", "hsi", "适宜性",
            "水位", "产卵场", "spawning ground", "环境",
            "环境因子", "environmental", "生态调度",
        ],
        ResearchPhase.REPORT: ["报告", "report", "综述", "总结"],
    }

    def __init__(self):
        self.context: Optional[ResearchContext] = None
        self._cognitive_adapter: Any = None
        self._kb: Any = None
        if get_knowledge_base is not None:
            try:
                self._kb = get_knowledge_base()
            except Exception:
                pass

    def _get_species_profile(self) -> Dict[str, Any]:
        """从知识库动态构建物种档案，不可用时回退到 _DEFAULT_PROFILE。"""
        if self._kb is None:
            return dict(_DEFAULT_PROFILE)
        data = self._kb.get_species("Culter_alburnus")
        if data is None:
            return dict(_DEFAULT_PROFILE)
        bio = data.get("biology", {})
        repro = data.get("reproduction", {})
        hab = data.get("habitat", {})
        return {
            "primary_species": data.get("scientific", _DEFAULT_PROFILE["primary_species"]),
            "chinese_name": data.get("chinese", _DEFAULT_PROFILE["chinese_name"]),
            "family": data.get("family", _DEFAULT_PROFILE["family"]),
            "subfamily": data.get("subfamily", _DEFAULT_PROFILE["subfamily"]),
            "max_length_cm": bio.get("max_length", ""),
            "max_weight_kg": bio.get("max_weight", ""),
            "lifespan_years": bio.get("lifespan", ""),
            "maturity_age": repro.get("maturity_age", ""),
            "spawning_season": repro.get("spawning_season", ""),
            "feeding_type": (bio.get("feeding") or {}).get("type", _DEFAULT_PROFILE["feeding_type"]),
            "habitat": hab.get("depth_preference", _DEFAULT_PROFILE["habitat"]),
            "key_research_themes": data.get("key_research_themes", []),
            "related_species": [
                f"{rs.get('chinese', '')} ({rs.get('scientific', '')})"
                for rs in data.get("related_species", [])
                if isinstance(rs, dict)
            ],
            "niche_axes": {
                ax.get("axis", ""): ax.get("description", "")
                for ax in (data.get("sympatric_coexistence", {})
                           .get("niche_partitioning_axes", []))
                if isinstance(ax, dict)
            },
            "isotope_baselines": {
                bl.split(":")[0].strip() if ":" in bl else bl: bl
                for bl in (data.get("stable_isotopes", {})
                           .get("baseline_organisms", []))
                if isinstance(bl, str)
            },
        }

    # ── Public API ──

    def run(self, question: str) -> dict:
        """入口: 问题 → 模式检测 → 阶段路由 → 执行。"""
        mode = self._detect_mode()
        phase = self._route_phase(question)
        self.context = ResearchContext(question=question, phase=phase, mode=mode)

        if mode == RunMode.INTEGRATED:
            return self._integrated_response(question, phase)

        return self._run_pipeline(question, phase)

    # ── Mode Detection ──

    def _detect_mode(self) -> RunMode:
        try:
            from scripts.project_loader import get_cognitive
            self._cognitive_adapter = get_cognitive()
            return RunMode.INTEGRATED
        except ImportError:
            return RunMode.STANDALONE

    # ── Phase Routing ──

    def _route_phase(self, question: str) -> ResearchPhase:
        """Route by keyword. DEFAULT: LITERATURE."""
        q_lower = question.lower()
        for phase, keywords in self.PHASE_KEYWORDS.items():
            if any(kw in q_lower for kw in keywords):
                return phase
        return ResearchPhase.LITERATURE

    # ── Pipeline Execution ──

    def _run_pipeline(self, question: str, phase: ResearchPhase) -> dict:
        result = PipelineResult(question=question)

        lit = self._execute_literature(question)
        result.phase_results["literature"] = lit
        result.phases_executed.append("literature")
        result.total_papers += lit.papers_found
        result.total_tokens += lit.tokens_used

        phase_methods = {
            ResearchPhase.GROWTH: self._execute_growth,
            ResearchPhase.GENOMICS: self._execute_genomics,
            ResearchPhase.GENETICS: self._execute_genetics,
            ResearchPhase.TROPHIC: self._execute_trophic,
            ResearchPhase.COEXISTENCE: self._execute_coexistence,
            ResearchPhase.RESOURCE: self._execute_resource,
            ResearchPhase.HABITAT: self._execute_habitat,
            ResearchPhase.REPORT: self._execute_report,
        }
        executor = phase_methods.get(phase)
        if executor:
            pr = executor(question, lit)
            result.phase_results[phase.value] = pr
            result.phases_executed.append(phase.value)
            result.total_papers += pr.papers_found
            result.total_tokens += pr.tokens_used

        result.synthesis = self._synthesize(result)
        return {
            "agent": "Culter Agent (P₃)",
            "species": self._get_species_profile()["primary_species"],
            "phase": phase.value,
            "skill": self._phase_to_skill(phase),
            "status": "completed",
            "mode": "standalone",
            "delegate_message": result.synthesis,
            **result.__dict__,
        }

    # ── Phase: Literature ──

    def _execute_literature(self, question: str) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.LITERATURE)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        if self._cognitive_adapter:
            try:
                resp = self._cognitive_adapter.search("Culter alburnus")
                papers = resp.get("items", resp.get("papers", []))
                result.papers_found = len(papers)
                result.data_points = len(papers)
                result.findings = [f"Found {len(papers)} papers on Culter alburnus"]
            except Exception as e:
                result.errors.append(f"Literature search failed: {e}")
        else:
            sci = (data or {}).get("scientific", "Culter alburnus")
            cn = (data or {}).get("chinese", "翘嘴鲌")
            family = (data or {}).get("family", "鲤科")
            subfam = (data or {}).get("subfamily", "鲌亚科")
            feed = ((data or {}).get("biology", {}).get("feeding", {}).get("type", "肉食性"))
            result.findings = [
                f"{sci} ({cn}): {family} > {subfam}, {feed}",
            ]
            # 相关物种 → 搜索建议
            related = (data or {}).get("related_species", [])
            if isinstance(related, list) and related:
                sci_names = [rs.get("scientific", "") for rs in related if isinstance(rs, dict)]
                if sci_names:
                    result.findings.append(
                        f"建议搜索: {sci} OR {' OR '.join(sci_names[:3])}"
                    )
            # 关键研究主题 → 搜索方向
            themes = (data or {}).get("key_research_themes", [])
            if themes:
                result.findings.append(f"研究主题: {'; '.join(themes[:3])}")
            # 分布
            native = (data or {}).get("habitat", {}).get("distribution_native", [])
            if native:
                result.findings.append(f"自然分布: {'; '.join(native[:3])}")
        return result

    # ── Phase: Growth Analysis ──

    def _execute_growth(self, question: str, lit: PhaseResult) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.GROWTH)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        bio = (data or {}).get("biology", {})
        repro = (data or {}).get("reproduction", {})

        result.findings = [
            "年龄鉴定材料: 鳞片 (常用)、矢耳石 (精度高)、脊椎骨 (辅助)",
            "von Bertalanffy 方程: Lt = L∞(1 - e^(-K(t-t0)))",
            f"体长上限: {bio.get('max_length', '105 cm')}, 常见: {bio.get('common_length', '30-60 cm')}",
            f"体重上限: {bio.get('max_weight', '15 kg')}, 常见: {bio.get('common_weight', '0.5-3 kg')}",
            f"寿命: {bio.get('lifespan', '15-20 年')}",
            f"生长速率: {bio.get('growth_rate', '中等偏快')}",
            f"性成熟: {repro.get('maturity_age', '♀ 3-4龄, ♂ 2-3龄')}",
            f"产卵季: {repro.get('spawning_season', '5-7月')}",
            f"繁殖力: {repro.get('fecundity', '5-60万粒')}",
            "文献参数范围: L∞ 60-120 cm, K 0.10-0.35 yr⁻¹, t0 -0.5~0 yr",
        ]
        return result

    # ── Phase: Genomics ──

    def _execute_genomics(self, question: str, lit: PhaseResult) -> PhaseResult:
        """Genomics analysis: whole genome, RAD-seq/GBS, mitogenome, comparative genomics."""
        result = PhaseResult(phase=ResearchPhase.GENOMICS)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        gen = (data or {}).get("genomics", {})
        mito = gen.get("mitogenome", {})
        result.findings = [
            f"基因组大小: {gen.get('genome_size', '~1.0-1.2 Gb (估算)')}",
            f"染色体数: {gen.get('chromosome_number', '2n = 48 (鲤科典型)')}",
            f"线粒体基因组: {mito.get('size', '~16.6 kb')}, {mito.get('genes', '13 PCGs + 22 tRNA + 2 rRNA + D-loop')}",
            f"可用物种: {mito.get('available_for', ['C. alburnus', 'C. mongolicus', 'Ch. erythropterus'])}",
            f"测序现状: {gen.get('sequencing_status', '已有简化基因组 (RAD-seq/GBS) 和线粒体全基因组数据')}",
            f"全基因组状态: {gen.get('whole_genome_status', '尚未公开组装')}",
        ]
        # 追加基因组资源和关键问题
        for res in gen.get("genomic_resources", []):
            result.findings.append(f"已有资源: {res}")
        for q in gen.get("key_questions", []):
            result.findings.append(f"待解决问题: {q}")
        return result

    # ── Phase: Genetics ──

    def _execute_genetics(self, question: str, lit: PhaseResult) -> PhaseResult:
        """Population genetics + phylogeography — 结合 KB 基因组资源。"""
        result = PhaseResult(phase=ResearchPhase.GENETICS)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        gen = (data or {}).get("genomics", {})
        cons = (data or {}).get("conservation", {})

        result.findings = [
            "遗传标记: 微卫星(SSR) + 线粒体 Cyt b/D-loop/COI + 核基因 SNP",
            "水系间遗传分化: 长江/珠江/黑龙江群体存在显著遗传结构",
            "谱系地理: 推测第四纪冰期避难所 + 冰后期扩散路径",
        ]
        # 从 KB 拉取基因组资源 (遗传分析相关)
        for res in gen.get("genomic_resources", []):
            if any(kw in res.lower() for kw in ["rad", "gbs", "ssr", "snp", "微卫星"]):
                result.findings.append(f"可用标记: {res}")
        # 关键遗传问题
        for q in gen.get("key_questions", []):
            if any(kw in q.lower() for kw in ["adapt", "分化", "群体", "遗传", "population", "gene flow"]):
                result.findings.append(f"待解问题: {q}")
        result.findings.extend([
            "有效种群大小 (Ne): 建议 LD 法 + PSMC/MSMC 历史动态重建",
            "建议: RAD-seq/GBS → 适应性分化扫描 (Fst outliers, pcadapt)",
            f"保护关注: {cons.get('concerns', '过度捕捞 + 栖息地破碎化')}",
        ])
        return result

    # ── Phase: Trophic Ecology (Isotopes + Diet) ──

    def _execute_trophic(self, question: str, lit: PhaseResult) -> PhaseResult:
        """Stable isotope ecology + trophic niche analysis — 优先从知识库拉取。"""
        result = PhaseResult(phase=ResearchPhase.TROPHIC)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        iso = (data or {}).get("stable_isotopes", {})
        troph = (data or {}).get("trophic_niche", {})

        # 同位素数据
        result.findings.append(
            f"稳定同位素: δ¹³C, δ¹⁵N (肌肉白肌), δ³⁴S — {iso.get('ontogenetic_shift', '体长 > 30 cm 后 δ¹⁵N 显著升高')}"
        )
        tv = iso.get("typical_values", {})
        if tv:
            result.findings.append(f"营养级: {tv.get('trophic_position', '3.5-4.5')}")
        for bl in iso.get("baseline_organisms", []):
            result.findings.append(f"基线生物: {bl}")
        for method in iso.get("analytical_methods", []):
            result.findings.append(f"分析方法: {method}")

        # 营养生态位
        result.findings.append(f"食性类型: {troph.get('feeding_guild', '顶级捕食者')}")
        ps = troph.get("prey_spectrum", {})
        prey_fish = ps.get("fish", [])
        if prey_fish:
            result.findings.append(f"鱼类饵料 ({len(prey_fish)} 种): {', '.join(prey_fish)}")
        prey_crust = ps.get("crustaceans", [])
        if prey_crust:
            result.findings.append(f"甲壳类饵料: {', '.join(prey_crust)}")

        # 食性转换阶段
        ds = troph.get("dietary_shift", {})
        for stage_key in ["stage_1", "stage_2", "stage_3", "stage_4"]:
            if stage_key in ds:
                result.findings.append(f"食性转换 {stage_key}: {ds[stage_key]}")

        # 生态位指标
        nm = troph.get("niche_metrics", {})
        if nm.get("levin_index"):
            result.findings.append(f"Levin 指数: {nm['levin_index']}")
        if nm.get("pianka_overlap"):
            result.findings.append(f"Pianka 重叠: {nm['pianka_overlap']}")
        if troph.get("seasonal_variation"):
            result.findings.append(f"季节性: {troph['seasonal_variation']}")
        return result

    # ── Phase: Sympatric Coexistence ──

    def _execute_coexistence(self, question: str, lit: PhaseResult) -> PhaseResult:
        """Niche partitioning + resource partitioning — 优先从知识库拉取。"""
        result = PhaseResult(phase=ResearchPhase.COEXISTENCE)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        coex = (data or {}).get("sympatric_coexistence", {})

        for pair in coex.get("co_occurring_culter_species", []):
            if not isinstance(pair, dict):
                continue
            pair_name = pair.get("pair", "")
            wb = pair.get("water_bodies", [])
            wb_str = ", ".join(wb) if isinstance(wb, list) else str(wb)
            result.findings.append(f"同域对: {pair_name} — 分布: {wb_str}")
            for mech in pair.get("coexistence_mechanisms", []):
                result.findings.append(f"  → {mech}")

        for axis in coex.get("niche_partitioning_axes", []):
            if isinstance(axis, dict):
                result.findings.append(
                    f"生态位轴 [{axis.get('axis', '?')}]: {axis.get('description', '')} "
                    f"(证据强度: {axis.get('evidence_strength', '?')})"
                )

        for gap in coex.get("research_gaps", []):
            result.findings.append(f"研究空白: {gap}")
        return result

    # ── Phase: Resource Assessment ──

    def _execute_resource(self, question: str, lit: PhaseResult) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.RESOURCE)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        fishery = (data or {}).get("fishery", {})
        cons = (data or {}).get("conservation", {})

        result.findings = [
            "评估方法: CPUE 标准化 + 剩余产量模型 (Schaefer/Fox) + YPR 分析",
            f"历史重要性: {fishery.get('historical_importance', '长江中下游重要经济鱼类')}",
            f"捕捞趋势: {fishery.get('catch_trend', '野生资源量显著下降')}",
            f"养殖现状: {fishery.get('aquaculture', '规模化人工养殖已成功')}",
            f"保护状态: {cons.get('china_status', '重要经济鱼类')} | IUCN: {cons.get('iucn', '未评估')}",
            f"禁捕: {cons.get('yangtze_fishing_ban', '2021年起长江全面禁捕')}",
        ]
        for mgmt in fishery.get("management", []):
            result.findings.append(f"管理措施: {mgmt}")
        return result

    # ── Phase: Habitat Modeling ──

    def _execute_habitat(self, question: str, lit: PhaseResult) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.HABITAT)
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        hab = (data or {}).get("habitat", {})
        repro = (data or {}).get("reproduction", {})

        wb_types = hab.get("water_body_types", [])
        wb_str = ", ".join(wb_types) if isinstance(wb_types, list) else str(wb_types)
        result.findings = [
            f"适宜水体: {wb_str}",
            f"水深偏好: {hab.get('depth_preference', '中上层 (0-5m)')}",
            f"温度范围: {hab.get('temperature_range', '4-32°C (最适 22-28°C)')}",
            f"产卵场: {repro.get('spawning_habitat', '静水或缓流、有水生植物的浅水区')}",
            f"产卵类型: {repro.get('spawning_type', '分批产卵')} — {repro.get('egg_type', '粘性卵')}",
            f"孵化期: {repro.get('incubation', '2-4天 (水温相关)')}",
            "HSI 模型关键因子: 水深、水温、透明度、水生植被覆盖度",
        ]
        native = hab.get("distribution_native", [])
        if native:
            result.findings.append(f"自然分布: {'; '.join(native)}")
        introduced = hab.get("introduced_areas", [])
        if introduced:
            result.findings.append(f"引入区域: {'; '.join(introduced)}")
        result.findings.append("建议: 生态调度 + 产卵场修复 + 环境流保障")
        return result

    # ── Phase: Report Generation ──

    def _execute_report(self, question: str, lit: PhaseResult) -> PhaseResult:
        result = PhaseResult(phase=ResearchPhase.REPORT)
        sp = self._get_species_profile()
        data = self._kb.get_species("Culter_alburnus") if self._kb else None
        gen = (data or {}).get("genomics", {})
        cons = (data or {}).get("conservation", {})
        coex = (data or {}).get("sympatric_coexistence", {})

        result.findings = [
            f"物种: {sp['primary_species']} ({sp['chinese_name']})",
            f"分类: {sp['family']} > {sp['subfamily']}",
            f"生态类型: {sp['feeding_type']} | 栖息: {sp['habitat']}",
            f"体长/体重上限: {sp['max_length_cm']} / {sp['max_weight_kg']}",
            f"寿命/性成熟: {sp['lifespan_years']} / {sp['maturity_age']}",
            f"全基因组状态: {gen.get('whole_genome_status', '尚未公开组装')}",
            f"IUCN/保护: {cons.get('iucn', '未评估')} | {cons.get('china_status', '')}",
        ]
        # 近缘种
        related = sp.get('related_species', [])
        if related:
            result.findings.append(f"近缘种 ({len(related)}): {'; '.join(related)}")
        # 关键空白
        gaps = coex.get("research_gaps", [])
        for gap in gaps[:2]:
            result.findings.append(f"研究空白: {gap}")
        result.findings.append(
            "核心建议: 全基因组组装为最高优先级，结合同位素与共存研究构建多维保护框架"
        )
        return result

    # ── Synthesis ──

    def _synthesize(self, result: PipelineResult) -> str:
        sp = self._get_species_profile()
        parts = [f"## {sp['primary_species']} ({sp['chinese_name']}) 研究综合报告\n"]
        parts.append(f"分类: {sp['family']} > {sp['subfamily']}")
        parts.append(f"问题: {result.question}")
        parts.append(f"执行阶段: {', '.join(result.phases_executed)}")
        parts.append(f"论文数: {result.total_papers}")
        parts.append(f"\n### 物种档案")
        parts.append(f"- 学名: {sp['primary_species']}")
        parts.append(f"- 中文名: {sp['chinese_name']}")
        parts.append(f"- 食性: {sp['feeding_type']}")
        parts.append(f"- 体长上限: {sp['max_length_cm']}")
        parts.append(f"- 体重上限: {sp['max_weight_kg']}")
        parts.append(f"- 寿命: {sp['lifespan_years']}")
        parts.append(f"- 性成熟: {sp['maturity_age']}")
        parts.append(f"- 产卵季: {sp['spawning_season']}")
        related = sp.get('related_species', [])
        if related:
            parts.append(f"- 近缘种: {', '.join(related[:5])}")
        parts.append(f"\n### 主要发现")
        for phase_name, pr in result.phase_results.items():
            for finding in pr.findings[:6]:
                parts.append(f"- {finding}")
        return "\n".join(parts)

    # ── Integrated Mode ──

    def _integrated_response(self, question: str, phase: ResearchPhase) -> dict:
        return {
            "agent": "Culter Agent (P₃)",
            "species": self._get_species_profile()["primary_species"],
            "phase": phase.value,
            "skill": self._phase_to_skill(phase),
            "mode": "integrated",
            "status": "delegated",
            "delegate_message": (
                f"DELEGATE to culter-agent (V4):\n"
                f"  species: Culter alburnus\n"
                f"  phase: {phase.value}\n"
                f"  question: {question}"
            ),
        }

    def _phase_to_skill(self, phase: ResearchPhase) -> str:
        return {
            ResearchPhase.LITERATURE: "search-literature",
            ResearchPhase.GROWTH: "analyze-growth",
            ResearchPhase.GENOMICS: "analyze-genomics",
            ResearchPhase.GENETICS: "analyze-genetics",
            ResearchPhase.TROPHIC: "analyze-trophic",
            ResearchPhase.COEXISTENCE: "model-coexistence",
            ResearchPhase.RESOURCE: "assess-resource",
            ResearchPhase.HABITAT: "model-habitat",
            ResearchPhase.REPORT: "report-generation",
        }.get(phase, "search-literature")
