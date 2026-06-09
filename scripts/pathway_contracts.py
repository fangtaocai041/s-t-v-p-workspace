"""
点→线→面→体: 五项目通路合约 (Pathway Contracts)

工程语言化五项目架构。不依赖自然语言描述 — 每条通路
有精确的函数签名、输入/输出类型、执行顺序和验证规则。

架构隐喻 (v7.4 修正):
  道 (Tao)     = eon-core OriginKernel — 万物之源
  一 (One)     = IProjectAdapter 统一接口
  二 (Two)     = fish(知识) + cognitive(搜索) — 对立统一
  三 (Three)   = fish + cognitive + eon-core — 三角闭环
  万物 (All)   = 从三角派生的领域专精模板 (P₁江豚 P₂刀鲚 ...Pₙ)

  三角形内通路: P1(fish↔cognitive) P4(health→eon-core)
  派生通路:     P3(cognitive→P₁/P₂) — 三角赋能领域专精

用法:
  from scripts.pathway_contracts import PATHWAYS, verify_pathway
  result = verify_pathway("P1_fish_to_cognitive", species_name="Ochetobius elongatus")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# 点 (Points) — 5 个核心专精函数签名
# ═══════════════════════════════════════════════════════════════

@dataclass
class CoreCompetency:
    """一个项目的核心专精 — 唯一能力声明。

    每个项目只能有一个核心专精。这是该项目的存在理由。
    """
    project: str                                   # 项目名
    vertex: str                                    # 顶点 (S/V0 | V/V1 | P₁/V2 | P₂/V3 | Coord)
    function_name: str                             # 核心函数名
    signature: str                                 # 函数签名 (工程语言)
    one_liner: str                                 # 一句话描述
    entry_point: str                               # 入口路径
    input_type: str = ""                           # 输入类型 (可选)
    output_type: str = ""                          # 输出类型 (可选)


# 五项目的核心专精定义
# 核心专精分为两层: 三角形 (道→一→二→三) + 派生模板 (万物)
CORES: Dict[str, CoreCompetency] = {
    # ═══ 三角形 (三): fish + cognitive + eon-core ═══
    "fish": CoreCompetency(
        project="fish-ecology-assistant", vertex="S / V0",
        function_name="lookup_species",
        signature="lookup_species(name: str) → SpeciesProfile",
        one_liner="长江鱼类知识库查询 + 可信度评分 (三角形: 知识供给)",
        entry_point="scripts.project_loader.get_fish()",
    ),
    "cognitive": CoreCompetency(
        project="cognitive-search-engine", vertex="V / V1",
        function_name="search_species",
        signature="search_species(genus, species) → SearchResult",
        one_liner="BDI+ReAct 多源认知搜索 (三角形: 验证引擎)",
        entry_point="scripts.project_loader.get_cognitive()",
    ),
    "eon_core": CoreCompetency(
        project="eon-core", vertex="Coordinator",
        function_name="route_event",
        signature="route_event(event: Event) → VertexChain",
        one_liner="DAG拓扑路由 + 六道轮回 (三角形: 协调内核)",
        entry_point="eon-core/src/kernel/origin.py",
    ),
    # ═══ 万物: 从三角派生的领域专精模板 (可复制) ═══
    "porpoise": CoreCompetency(
        project="porpoise-agent", vertex="P₁ / V2",
        function_name="analyze_contradiction",
        signature="analyze_contradiction(question) → Route",
        one_liner="江豚专精 — 矛盾驱动路由 (三角派生模板 P₁)",
        entry_point="scripts.project_loader.get_porpoise()",
    ),
    "coilia": CoreCompetency(
        project="coilia-agent", vertex="P₂ / V3",
        function_name="assess_species",
        signature="assess_species(species, context) → Assessment",
        one_liner="刀鲚专精 — 耳石微化学 (三角派生模板 P₂)",
        entry_point="scripts.project_loader.get_coilia()",
    ),
}


# ═══════════════════════════════════════════════════════════════
# 线 (Lines) — 4 条数据流通路
# ═══════════════════════════════════════════════════════════════

class PathwayStatus(str, Enum):
    ACTIVE = "active"        # 已验证可执行
    DEFINED = "defined"      # 已定义但未端到端验证
    PLANNED = "planned"      # 已规划但未实现


@dataclass
class PathwayContract:
    """两点之间的数据流通路合约。

    每条通路精确描述:
      - 源和目标的函数签名
      - 数据转换规则
      - 验证条件
    """
    pathway_id: str                                # P1, P2, P3, P4
    name: str                                      # 通路名称
    source: str                                    # 源项目
    target: str                                    # 目标项目
    source_call: str                               # 源端调用 (函数签名)
    target_call: str                               # 目标端调用 (函数签名)
    data_flow: str                                 # 数据流转描述
    transform: str                                 # 数据转换规则 (工程语言)
    verify_condition: str                          # 验证条件
    note: str = ""                                 # 补充说明 (多对一通路等)
    status: PathwayStatus = PathwayStatus.ACTIVE


# 四条通路定义
PATHWAYS: Dict[str, PathwayContract] = {
    # ═══ 通路 1: 物种查询 → 文献搜索 ═══
    "P1_fish_to_cognitive": PathwayContract(
        pathway_id="P1",
        name="物种名→文献搜索",
        source="fish-ecology-assistant (S/V0)",
        target="cognitive-search-engine (V/V1)",
        source_call="FishEcologyAdapter.lookup_species(name: str) → SpeciesProfile",
        target_call="CognitiveSearchAdapter.search(genus, species, full_pipeline=False) → dict",
        data_flow="SpeciesProfile.genus + SpeciesProfile.species → CognitiveSearchAdapter.search()",
        transform="""
            INPUT  species_name: str
            STEP 1 profile = fish.lookup_species(species_name)
            STEP 2 IF profile.found THEN
                    result = cognitive.search(profile.genus, profile.species)
                  ELSE
                    result = cognitive.search(guess_genus(species_name), species_name)
            STEP 3 RETURN { profile, result }
        """,
        verify_condition="profile.found == True AND result.papers_found >= 0",
    ),

    # ═══ 通路 2: 搜索结果 → 可信度评分 ═══
    "P2_cognitive_to_fish": PathwayContract(
        pathway_id="P2",
        name="搜索结果→可信度评分",
        source="cognitive-search-engine (V/V1)",
        target="fish-ecology-assistant (S/V0)",
        source_call="CognitiveSearchAdapter.search() → dict { papers: [...] }",
        target_call="FishEcologyAdapter.score_credibility(papers: List[dict]) → List[dict]",
        data_flow="SearchResult.papers → FishEcologyAdapter.score_credibility() → scored_papers",
        transform="""
            INPUT  papers: List[dict]  (from cognitive.search)
            FOR EACH paper IN papers:
                paper.credibility_score = fish.score_credibility(paper)
                IF paper.credibility_score >= 80 THEN paper.flag = '🟢 高可信度'
                ELIF paper.credibility_score >= 60 THEN paper.flag = '🟡 中可信度'
                ELSE paper.flag = '🟠 需交叉验证'
            RETURN papers (with credibility_score + flag)
        """,
        verify_condition="ALL papers have credibility_score >= 0 AND credibility_score <= 100",
    ),

    # ═══ 通路 3: 文献结果 → 领域分析 ═══
    "P3_cognitive_to_domain": PathwayContract(
        pathway_id="P3",
        name="三角→派生: 认知赋能领域专精",
        source="cognitive-search-engine (V/V1, 三角形)",
        target="porpoise-agent | coilia-agent (P₁/V2 | P₂/V3, 三角派生)",
        note="P₁/P₂ 非三角形成员，而是三角稳定后派生的可复制模板",
        source_call="CognitiveSearchAdapter.search(genus, species) → dict { papers, graph }",
        target_call="PorpoiseAdapter.search(query, domain='porpoise') | CoiliaAdapter.search(query)",
        data_flow="SearchResult.papers + SearchResult.graph → DomainAdapter.search() → analysis",
        transform="""
            INPUT  search_result: dict  (from cognitive.search)
            STEP 1 domain = route_by_species(search_result.species)
            STEP 2 IF domain == 'porpoise' THEN
                    analysis = porpoise.analyze_contradiction(search_result)
                  ELIF domain == 'coilia' THEN
                    analysis = coilia.assess_species(search_result.species, search_result)
            STEP 3 RETURN analysis
        """,
        verify_condition="analysis.findings IS NOT EMPTY AND analysis.phase IS NOT NULL",
    ),

    # ═══ 通路 4: 健康状态 → 业力评估 ═══
    "P4_health_to_karma": PathwayContract(
        pathway_id="P4",
        name="健康状态→业力评估 (三角形内)",
        source="所有适配器 (三角形 + 派生)",
        target="eon-core (Samsara Ring, 三角形内核)",
        source_call="adapter.health() → dict { status, uptime, error_count }",
        target_call="eon-core KarmaEngine.evaluate(agent_id, health_dict) → KarmaResult",
        data_flow="health.status → KarmaEngine.evaluate() → realm_transition",
        transform="""
            FOR EACH vertex IN [V0, V1, V2, V3]:
                health = adapter.health()
                karma = eon_core.evaluate_karma(vertex, health)
                IF karma.realm == NARAKA THEN isolate(vertex)
                ELIF karma.realm == DEVA THEN boost(vertex, token_mul=1.5)
        """,
        verify_condition="karma.realm IN [DEVA, HUMAN, ASURA, ANIMAL, PRETA, NARAKA]",
    ),
}


# ═══════════════════════════════════════════════════════════════
# 面 (Surfaces) — 2 个多项目工作流
# ═══════════════════════════════════════════════════════════════

@dataclass
class WorkflowContract:
    """多项目工作流 — 由多条通路组成。

    面是线的闭合组合。工作流定义了从用户问题到最终答案
    经过多个项目的完整路径。
    """
    workflow_id: str
    name: str
    description: str
    pathway_sequence: List[str]                   # 通路ID序列 (按执行顺序)
    entry_condition: str                          # 触发条件
    exit_criteria: str                            # 停止条件
    token_budget: int = 50000                     # 总token预算


WORKFLOWS: Dict[str, WorkflowContract] = {
    "WF_A_full_stack_search": WorkflowContract(
        workflow_id="WF_A",
        name="全栈物种搜索",
        description="用户查询物种 → 知识库查找 → 多源搜索 → 可信度评分 → 图谱更新",
        pathway_sequence=["P1_fish_to_cognitive", "P2_cognitive_to_fish"],
        entry_condition="user asks about a specific species",
        exit_criteria="all papers scored AND graph updated",
        token_budget=30000,
    ),
    "WF_B_domain_conservation": WorkflowContract(
        workflow_id="WF_B",
        name="领域保护评估",
        description="物种搜索 → 矛盾分析 → 保护建议 → 业力评估",
        pathway_sequence=["P1_fish_to_cognitive", "P3_cognitive_to_domain", "P4_health_to_karma"],
        entry_condition="user asks about conservation/threat/assessment",
        exit_criteria="contradiction analyzed AND recommendations generated",
        token_budget=50000,
    ),
}


# ═══════════════════════════════════════════════════════════════
# 体 (Volume) — eon-core 闭合反馈环
# ═══════════════════════════════════════════════════════════════

@dataclass
class VolumeContract:
    """闭合反馈环 — 五项目全连接的体。

    体是整个系统的最高抽象：所有通路、所有工作流
    在一个闭合的反馈环中运行，通过 Samsara 业力自我调节。
    """
    volume_id: str = "V_eon_samsara_loop"
    name: str = "eon-core Samsara 闭合反馈环"
    description: str = """
        十个层次的同心架构:
        L0 OriginKernel → L1 YinYang → L2 Vertices → L3 Trigrams →
        L4 Tetrahedron → L5 WuXing → L6 Samsara → L7 Sphere →
        L8 Tendrils → L9 Evolution → (回到 L0)
    """
    layers: int = 10
    cycle_period_sec: int = 60                     # 业力评估周期
    vertices: List[str] = field(default_factory=lambda: ["V0", "V1", "V2", "V3"])
    karma_states: List[str] = field(default_factory=lambda: [
        "DEVA", "HUMAN", "ASURA", "ANIMAL", "PRETA", "NARAKA"
    ])
    invariants: List[str] = field(default_factory=lambda: [
        "Topology IS DAG → nx.is_directed_acyclic_graph() at bootstrap",
        "YangPole SHALL NOT verify (mypy strict)",
        "YinPole SHALL NOT expand (mypy strict)",
        "Inter-vertex via EventBus or gRPC → no direct import",
        "λ₂ ≥ 0.1 × baseline → spectral gap connectivity check",
        "NARAKA auto-rebirth → self-healing after cooldown",
        "Reincarnation atomic → 7-step protocol with snapshot rollback",
    ])


VOLUME = VolumeContract()


# ═══════════════════════════════════════════════════════════════
# 通路验证工具
# ═══════════════════════════════════════════════════════════════

def verify_pathway_structure(pathway_id: str) -> Dict[str, Any]:
    """验证通路定义的结构完整性 (不执行实际调用)。

    检查:
      1. 通路ID存在于 PATHWAYS
      2. 源和目标项目在 CORES 中注册
      3. 数据转换规则是有效的工程语言
      4. 验证条件可解析
    """
    if pathway_id not in PATHWAYS:
        return {"pathway_id": pathway_id, "status": "NOT_FOUND"}

    pw = PATHWAYS[pathway_id]
    issues: List[str] = []

    # 检查源和目标是否在核心定义中 (允许"所有适配器"等多对一通路)
    for role, name in [("source", pw.source), ("target", pw.target)]:
        if "所有" in name or "全部" in name:
            continue  # 多对一通路的源/目标是合法通配
        project_key = None
        for key, core in CORES.items():
            if core.project in name:
                project_key = key
                break
        if project_key is None and "eon-core" not in name.lower():
            issues.append(f"{role} project not found in CORES: {name}")

    # 检查数据转换规则是否包含工程语言关键字
    engineering_keywords = ["INPUT", "STEP", "FOR EACH", "IF", "THEN", "ELSE", "RETURN"]
    has_engineering = any(kw in pw.transform for kw in engineering_keywords)
    if not has_engineering:
        issues.append("transform rule missing engineering language keywords")

    return {
        "pathway_id": pathway_id,
        "name": pw.name,
        "status": "VALID" if not issues else "ISSUES",
        "issues": issues,
        "source": pw.source,
        "target": pw.target,
    }


def verify_all_pathways() -> Dict[str, Any]:
    """验证所有通路的结构完整性。"""
    results = {}
    for pw_id in PATHWAYS:
        results[pw_id] = verify_pathway_structure(pw_id)
    return {
        "total": len(results),
        "valid": sum(1 for r in results.values() if r["status"] == "VALID"),
        "issues": sum(1 for r in results.values() if r["status"] != "VALID"),
        "pathways": results,
    }
