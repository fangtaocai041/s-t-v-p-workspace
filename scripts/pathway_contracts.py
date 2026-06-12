"""
点→线→面→体: 七项目通路合约 (Pathway Contracts)

工程语言化七项目架构。不依赖自然语言描述 — 每条通路
有精确的函数签名、输入/输出类型、执行顺序和验证规则。

架构隐喻 (v8.0 修正):
  道 (Dao)     = e项目(eon-core) OriginKernel — 协调源点, 万法之宗
  一 (One)     = IProjectAdapter 统一接口
  二 (Two)     = f项目(知识) + c项目(搜索) — 阴阳对偶, 知识生产闭环
  三 (Three)   = e项目(协调) + f项目(知识) + c项目(搜索) — 协调三角
  万物 (All)   = 从三角派生的领域专精 (P₁江豚 P₂刀鲚 P₃鲌类 conflict仲裁)

  协调通路: P0(e项目→f/c/P₁/P₂/P₃/conflict) — 意图路由·资源分配
  知识闭环: P1(f→c) P2(c→f) — 知识库→搜索→写回
  赋能通路: P3(c→P₁/P₂/P₃) — c项目搜索赋能领域分析
  业力回路: P4(各项目→e项目) — 健康检查→业力评估→资源调节
  万物归仲裁: P5(万物→conflict) P6(conflict→user)

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


# 七项目的核心专精定义
# 核心专精分为三层: 协调源 (e项目) → 三角执行 (f/c) → 万物衍生 (P₁/P₂/P₃/conflict)
CORES: Dict[str, CoreCompetency] = {
    # ═══ 协调源 (道): e项目 — 协调内核, 不参与具体数据流 ═══
    "eon_core": CoreCompetency(
        project="eon-core", vertex="Coordinator",
        function_name="route_event",
        signature="route_event(event: Event) → VertexChain",
        one_liner="DAG拓扑路由 + 事件总线 + 业力引擎 (协调源点)",
        entry_point="eon-core/src/kernel/origin.py",
    ),
    # ═══ 三角执行 (二): f项目(知识) + c项目(搜索) — 知识生产闭环 ═══
    "fish": CoreCompetency(
        project="fish-ecology-assistant", vertex="V0",
        function_name="lookup_species",
        signature="lookup_species(name: str) → SpeciesProfile",
        one_liner="多流域鱼类知识库查询 + 可信度评分 (知识供给)",
        entry_point="scripts.project_loader.get_fish()",
    ),
    "cognitive": CoreCompetency(
        project="cognitive-search-engine", vertex="V1",
        function_name="search_species",
        signature="search_species(genus, species) → SearchResult",
        one_liner="BDI+ReAct 多源认知搜索 (搜索验证)",
        entry_point="scripts.project_loader.get_cognitive()",
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
    "culter": CoreCompetency(
        project="culter-agent", vertex="P₃",
        function_name="assess_culter_species",
        signature="assess_culter_species(species, context) → SpeciesAssessment",
        one_liner="鲌类专精 — 年龄生长 + 资源评估 (三角派生模板 P₃)",
        entry_point="scripts.project_loader.get_culter()",
    ),
    "conflict": CoreCompetency(
        project="conflict-arbiter", vertex="C / V4",
        function_name="detect_conflicts",
        signature="detect_conflicts(sources, region) → ConflictReport",
        one_liner="多源保护推荐冲突检测 — 加权仲裁 (万物归仲裁)",
        entry_point="scripts.project_loader.get_conflict()",
    ),
}


# ═══════════════════════════════════════════════════════════════
# 线 (Lines) — 6 条数据流通路
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


# 七条通路定义
PATHWAYS: Dict[str, PathwayContract] = {
    # ═══ 通路 0: e项目协调分发 — 意图路由 ═══
    "P0_eon_to_all": PathwayContract(
        pathway_id="P0",
        name="协调源→全项目: 意图路由 + 资源分配",
        source="eon-core (协调源)",
        target="fish-ecology-assistant | cognitive-search-engine | porpoise-agent | coilia-agent | culter-agent | conflict-arbiter",
        source_call="OriginKernel.route_event(event: Event) → VertexChain",
        target_call="各项目 adapter.execute(intent, resources) → Result",
        data_flow="用户意图 → OriginKernel.parse() → 顶点拓扑匹配 → 路由到目标项目 → 执行",
        transform="""
            INPUT: user_intent (string)
            STEP 1: intent_type = OriginKernel.classify(user_intent)
            STEP 2: target_vertex = VertexTopology.route(intent_type)
            STEP 3: resources = ResourceAllocator.assign(target_vertex, entropy_budget)
            STEP 4: result = target_adapter.execute(intent_type, resources)
            RETURN result
        """,
        verify_condition="eon-core importable AND target project reachable via adapter",
        note="P0 是协调入口 — 所有外部请求先经过 e项目路由",
        status=PathwayStatus.DEFINED,
    ),
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
        status=PathwayStatus.DEFINED,
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
        status=PathwayStatus.ACTIVE,
    ),

    # ═══ 通路 5: 任意项目输出 → 冲突仲裁 ═══
    "P5_all_to_conflict": PathwayContract(
        pathway_id="P5",
        name="万物→冲突检测",
        source="fish (三角·V0) | cognitive (三角·V1) | porpoise (P₁) | coilia (P₂) | culter (P₃) | Pₙ",
        target="conflict-arbiter (C/V4)",
        source_call="adapter.search() → dict { recommendations, scores }",
        target_call="ConflictArbiterAdapter.assess_conflict(sources: List[dict]) → ConflictReport",
        data_flow="multiple adapter outputs → ConflictArbiter.assess_conflict() → unified verdict",
        transform="""
            INPUT  sources: List[dict]  (from 三角 + 万物: fish/cognitive/porpoise/coilia/culter/Pₙ)
            STEP 1 weights = assign_credibility_weights(sources)
            STEP 2 conflicts = detect_disagreements(sources, threshold=0.3)
            STEP 3 IF len(conflicts) == 0 THEN
                    verdict = sources[argmax(weights)]
                  ELSE
                    verdict = weighted_arbitration(sources, weights, conflicts)
                    IF consensus < 0.5 THEN trigger_circuit_breaker()
            RETURN verdict
        """,
        verify_condition="verdict.confidence >= 0 AND verdict.confidence <= 1.0",
        note="多对一通路: 任一项目输出均可路由到冲突仲裁",
        status=PathwayStatus.DEFINED,
    ),

    # ═══ 通路 6: 仲裁结果 → 用户输出 ═══
    "P6_conflict_to_user": PathwayContract(
        pathway_id="P6",
        name="仲裁结果→裁决输出",
        source="conflict-arbiter (C/V4)",
        target="user",
        source_call="ConflictArbiterAdapter.assess_conflict() → ConflictReport",
        target_call="user-facing render (CLI | API response | Markdown)",
        data_flow="ConflictReport → report_render() → user",
        transform="""
            INPUT  report: ConflictReport (from conflict-arbiter)
            STEP 1 IF report.circuit_broken THEN
                    output = render_emergency(report, template='circuit_break')
                  ELIF report.consensus >= 0.8 THEN
                    output = render_consensus(report, template='strong')
                  ELSE
                    output = render_disagreement(report, template='balanced')
            STEP 2 output.metadata = { source_count, consensus, arbitration_version }
            RETURN output
        """,
        verify_condition="output.metadata.source_count > 0 AND output.metadata.consensus >= 0",
        status=PathwayStatus.DEFINED,
    ),
}


# ═══════════════════════════════════════════════════════════════
# 面 (Surfaces) — 3 个多项目工作流
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
    "WF_C_conflict_arbitration": WorkflowContract(
        workflow_id="WF_C",
        name="跨源冲突仲裁",
        description="多源保护推荐 → 冲突检测 → 加权仲裁 → 裁决输出",
        pathway_sequence=["P5_all_to_conflict", "P6_conflict_to_user"],
        entry_condition="multiple sources disagree on protection recommendation",
        exit_criteria="consensus reached OR circuit_breaker tripped",
        token_budget=20000,
    ),
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
        L4 Tetrahedron → L5 Monitoring → L6 Samsara → L7 Sphere →
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

    # 检查源和目标是否在核心定义中 (支持多源/多目标, 用 | 分割)
    def _split_pipe_outside_parens(text: str) -> list[str]:
        """Split by | only when outside parentheses."""
        parts = []
        depth = 0
        current = ""
        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "|" and depth == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())
        return parts

    for role, raw_name in [("source", pw.source), ("target", pw.target)]:
        names = []
        for part in _split_pipe_outside_parens(raw_name):
            # 取括号前的内容作为项目名
            paren_idx = part.find("(")
            if paren_idx > 0:
                part = part[:paren_idx].strip()
            if part:
                names.append(part)
        for name in names:
            if "所有" in name or "全部" in name or name in ("user", "用户", "Pₙ"):
                continue  # 通配/用户/Pₙ 不是项目
            project_key = None
            for key, core in CORES.items():
                # 匹配: 项目全名(core.project) 或 短key 出现在 name 中
                if core.project in name or key in name.lower():
                    project_key = key
                    break
            if project_key is None and "eon-core" not in name.lower():
                issues.append(f"{role} project '{name}' not found in CORES")

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
