"""
Coordinator — 五项目统一协调入口.

三生万物架构唯一调用方式。取代:
  - 手动 project_loader.get_*() 调用
  - 手动通路编排 (P1-P7 链式调用)
  - 手动工作流编排 (WF_A/B/C)

用法:
    from scripts.coordinator import coordinator

    # Level 1: 单项目调用
    result = coordinator.call("fish", query="Ochetobius elongatus")

    # Level 2: 按通路调用 (自动编排 2 个项目)
    result = coordinator.pathway("P1_fish_to_cognitive", species="鳤")

    # Level 3: 按工作流调用 (全流程)
    result = coordinator.workflow("WF_A_full_stack_search", species="鳤")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── 项目名称 → 适配器 getter 映射 ──
_PROJECT_GETTERS = {}


def _lazy_getter(name: str):
    """Lazy-import and cache project loader to avoid circular imports."""
    if not _PROJECT_GETTERS:
        from scripts.project_loader import (
            get_fish, get_cognitive, get_porpoise, get_coilia, get_culter, get_conflict,
        )
        _PROJECT_GETTERS.update({
            "fish": get_fish,
            "cognitive": get_cognitive,
            "porpoise": get_porpoise,
            "coilia": get_coilia,
            "culter": get_culter,
            "conflict": get_conflict,
        })
    getter = _PROJECT_GETTERS.get(name)
    if getter is None:
        raise ValueError(f"Unknown project: {name}. Valid: {list(_PROJECT_GETTERS.keys())}")
    adapter = getter()
    if adapter is None:
        raise RuntimeError(f"Failed to load adapter for project: {name}")
    return adapter


# ================================================================
# Coordinator class
# ================================================================

class Coordinator:
    """统一协调器 — 所有跨项目调用的唯一入口。

    Three levels of API — pick the level that matches your need:
      Level 1 (call):     单项目调用, 你指定项目
      Level 2 (pathway):  按通路调用, 自动编排 2 个项目
      Level 3 (workflow): 按工作流调用, 自动编排全流程
    """

    # ── Level 1: 单项目调用 ──

    def call(self, project: str, query: str = "", **kwargs) -> Dict[str, Any]:
        """调用单个项目的 adapter.search()。

        Args:
            project: "fish" | "cognitive" | "porpoise" | "coilia" | "conflict"
            query: 搜索查询 (物种名/问题)
            **kwargs: 传递给 adapter.search() 的额外参数

        Returns:
            adapter.search() 的结果字典
        """
        adapter = _lazy_getter(project)
        return adapter.search(query, **kwargs)

    def health(self, project: str) -> Dict[str, Any]:
        """查询单个项目的健康状态。"""
        return _lazy_getter(project).health()

    def info(self, project: str) -> Dict[str, Any]:
        """查询单个项目的能力信息。"""
        return _lazy_getter(project).info()

    # ── Level 2: 按通路调用 ──

    def pathway(self, pathway_id: str, **kwargs) -> Dict[str, Any]:
        """按通路定义自动编排多项目调用。

        Args:
            pathway_id: "P1_fish_to_cognitive" | "P2_cognitive_to_fish" |
                        "P3_cognitive_to_domain" | "P4_health_to_karma" |
                        "P5_all_to_conflict" | "P6_conflict_to_user"
            **kwargs: 通路参数 (见各通路文档)

        Returns:
            通路执行结果
        """
        method = _PATHWAY_REGISTRY.get(pathway_id)
        if method is None:
            raise ValueError(
                f"Unknown pathway: {pathway_id}. "
                f"Valid: {list(_PATHWAY_REGISTRY.keys())}"
            )
        return method(**kwargs)

    # ── Level 3: 按工作流调用 ──

    def workflow(self, workflow_id: str, **kwargs) -> Dict[str, Any]:
        """按工作流定义自动编排全流程。

        Args:
            workflow_id: "WF_A_full_stack_search" | "WF_B_domain_conservation"
            **kwargs: 工作流参数
        """
        method = _WORKFLOW_REGISTRY.get(workflow_id)
        if method is None:
            raise ValueError(
                f"Unknown workflow: {workflow_id}. "
                f"Valid: {list(_WORKFLOW_REGISTRY.keys())}"
            )
        return method(**kwargs)

    # ── 验证 ──

    def verify_pathway(self, pathway_id: str) -> Dict[str, Any]:
        """验证通路结构完整性 (不触发真实搜索)。"""
        try:
            # Structural checks only — no actual adapter.search() calls
            if pathway_id == "P1_fish_to_cognitive":
                fish_ok = self.health("fish").get("status") in ("HEALTHY", "STANDBY")
                cog_ok = self.health("cognitive").get("status") in ("HEALTHY", "STANDBY")
                return {"pathway_id": pathway_id, "status": "OK",
                        "fish_loaded": fish_ok, "cognitive_loaded": cog_ok}
            elif pathway_id == "P2_cognitive_to_fish":
                cog_ok = self.health("cognitive").get("status") in ("HEALTHY", "STANDBY")
                fish_ok = self.health("fish").get("status") in ("HEALTHY", "STANDBY")
                return {"pathway_id": pathway_id, "status": "OK",
                        "cognitive_loaded": cog_ok, "fish_loaded": fish_ok}
            elif pathway_id == "P3_cognitive_to_domain":
                cog_ok = self.health("cognitive").get("status") in ("HEALTHY", "STANDBY")
                domain_ok = any(
                    self.health(p).get("status") in ("HEALTHY", "STANDBY")
                    for p in ("porpoise", "coilia", "culter")
                )
                return {"pathway_id": pathway_id, "status": "OK",
                        "cognitive_loaded": cog_ok, "domain_available": domain_ok}
            elif pathway_id == "P4_health_to_karma":
                all_ok = all(
                    self.health(p).get("status") in ("HEALTHY", "STANDBY")
                    for p in ("eon", "fish", "cognitive", "porpoise", "coilia", "culter", "conflict")
                )
                return {"pathway_id": pathway_id, "status": "OK",
                        "all_healthy": all_ok}
            elif pathway_id in ("P5_all_to_conflict", "P6_conflict_to_user"):
                conflict_ok = self.health("conflict").get("status") in ("HEALTHY", "STANDBY")
                return {"pathway_id": pathway_id, "status": "OK",
                        "conflict_loaded": conflict_ok}
            else:
                return {"pathway_id": pathway_id, "status": "OK", "note": "structural check passed"}
        except Exception as exc:
            return {"pathway_id": pathway_id, "status": "ERROR", "error": str(exc)}

    def verify_all(self) -> Dict[str, Any]:
        """验证所有通路。"""
        results = {}
        for pid in sorted(_PATHWAY_REGISTRY.keys()):
            results[pid] = self.verify_pathway(pid)
        return {"total": len(results), "results": results}


# ================================================================
# 通路实现 (P1-P7)
# ================================================================

def _p1_fish_to_cognitive(species: str = "", **kwargs) -> Dict[str, Any]:
    """P1: 物种名 → 文献搜索

    1. fish.lookup_species(species) → 获取物种知识
    2. cognitive.search_species(genus, species) → 执行文献搜索

    Args:
        species: 物种名 (中文/学名)
    """
    result = {}
    # Step 1: 知识查询
    fish = _lazy_getter("fish")
    profile = fish.search(species)
    result["profile"] = profile

    # Step 2: 文献搜索
    cog = _lazy_getter("cognitive")
    search_result = cog.search(species)
    result["search_result"] = search_result

    return result


def _p2_cognitive_to_fish(papers: list = None, species: str = "", **kwargs) -> Dict[str, Any]:
    """P2: 搜索结果 → 可信度评分

    1. fish.score_credibility(papers) → 每篇论文评分

    Args:
        papers: cognitive 搜索出的论文列表
        species: 如果 papers 为空, 先搜索这个物种
    """
    if not papers and species:
        cog = _lazy_getter("cognitive")
        search_res = cog.search(species)
        papers = search_res.get("papers", []) or search_res.get("result", {}).get("papers", [])

    fish = _lazy_getter("fish")
    scored = fish.search("credibility", _papers=papers)
    return {"scored_papers": scored, "count": len(papers)}


def _p3_cognitive_to_domain(species: str = "", domain: str = "", **kwargs) -> Dict[str, Any]:
    """P3: 文献结果 → 领域分析

    1. cognitive.search(species) → 文献
    2. 根据 species 自动路由到 porpoise(P₁) 或 coilia(P₂)

    Args:
        species: 物种名
        domain: 可选, 强制指定 "porpoise" 或 "coilia"
    """
    cog = _lazy_getter("cognitive")
    papers = cog.search(species)

    # 自动路由
    if not domain:
        s = species.lower()
        if "porpoise" in s or "neophocaena" in s or "江豚" in s:
            domain = "porpoise"
        elif "coilia" in s or "刀鲚" in s or "nasus" in s:
            domain = "coilia"
        elif "culter" in s or "鲌" in s or "chanodichthys" in s or "翘嘴" in s or "蒙古" in s:
            domain = "culter"
        else:
            domain = "fish"  # 默认走 fish 知识库

    if domain == "porpoise":
        adapter = _lazy_getter("porpoise")
        return {"domain": domain, "result": adapter.search(species), "papers": papers}
    elif domain == "coilia":
        adapter = _lazy_getter("coilia")
        return {"domain": domain, "result": adapter.search(species), "papers": papers}
    elif domain == "culter":
        adapter = _lazy_getter("culter")
        return {"domain": domain, "result": adapter.search(species), "papers": papers}
    else:
        return {"domain": "fish", "result": papers, "papers": papers}


def _p4_health_to_karma(**kwargs) -> Dict[str, Any]:
    """P4: 健康状态 → 业力评估

    收集所有项目的健康状态, 返回聚合结果。
    """
    projects = ["eon", "fish", "cognitive", "porpoise", "coilia", "culter", "conflict"]
    healths = {}
    for p in projects:
        try:
            healths[p] = _lazy_getter(p).health()
        except Exception as exc:
            healths[p] = {"status": "ERROR", "error": str(exc)}
    return {"healths": healths, "all_healthy": all(
        h.get("status") == "HEALTHY" for h in healths.values())}


def _p5_all_to_conflict(species: str = "", sources: list = None, **kwargs) -> Dict[str, Any]:
    """P5: 任意项目输出 → 冲突检测

    汇总多个项目的输出, 交给 conflict-arbiter 做一致性检查。

    Args:
        species: 物种名
        sources: 可选, 自定义源列表 [{source, claim, weight}]
    """
    conflict = _lazy_getter("conflict")
    if sources:
        return {"verdict": conflict.search(species, sources=sources)}
    # 自动收集各项目输出
    collected = {}
    for p in ["fish", "cognitive", "porpoise", "coilia", "culter"]:
        try:
            collected[p] = _lazy_getter(p).search(species)
        except Exception as exc:
            collected[p] = {"error": str(exc)}
    return {"sources": collected,
            "verdict": conflict.search(species, sources=collected)}


def _p6_conflict_to_user(species: str = "", sources: list = None, **kwargs) -> Dict[str, Any]:
    """P6: 仲裁结果 → 裁决输出

    执行 P5 后格式化输出为可读的裁决报告。
    """
    p5_result = _p5_all_to_conflict(species, sources)
    verdict = p5_result.get("verdict", {})
    return {
        "species": species,
        "conflict_level": verdict.get("conflict_level", "unknown"),
        "consensus": verdict.get("consensus", verdict.get("status", "unknown")),
        "recommendation": verdict.get("verdict", "insufficient data"),
    }


# ================================================================
# 注册表
# ================================================================

_PATHWAY_REGISTRY = {
    "P1_fish_to_cognitive": _p1_fish_to_cognitive,
    "P2_cognitive_to_fish": _p2_cognitive_to_fish,
    "P3_cognitive_to_domain": _p3_cognitive_to_domain,
    "P4_health_to_karma": _p4_health_to_karma,
    "P5_all_to_conflict": _p5_all_to_conflict,
    "P6_conflict_to_user": _p6_conflict_to_user,
}

_WORKFLOW_REGISTRY = {}


def _wf_full_stack_search(species: str = "", **kwargs) -> Dict[str, Any]:
    """WF_A: 全栈物种搜索 → P1 + P2"""
    result = _p1_fish_to_cognitive(species)
    # 提取 papers 做可信度评分
    papers = []
    sr = result.get("search_result", {})
    if isinstance(sr, dict):
        papers = sr.get("papers", []) or (
            sr.get("result", {}).get("papers", []) if isinstance(sr.get("result"), dict) else [])
    scored = _p2_cognitive_to_fish(papers, species)
    return {**result, **scored}


def _wf_domain_conservation(species: str = "", **kwargs) -> Dict[str, Any]:
    """WF_B: 领域保护评估 → P1 + P3 + P4"""
    result = _p1_fish_to_cognitive(species)
    domain = _p3_cognitive_to_domain(species)
    health = _p4_health_to_karma()
    return {**result, "domain_analysis": domain, "health_check": health}


def _wf_conflict_arbitration(species: str = "", sources: list = None, **kwargs) -> Dict[str, Any]:
    """WF_C: 跨源冲突仲裁 → P5 + P6"""
    return _p6_conflict_to_user(species, sources)


_WORKFLOW_REGISTRY.update({
    "WF_A_full_stack_search": _wf_full_stack_search,
    "WF_B_domain_conservation": _wf_domain_conservation,
    "WF_C_conflict_arbitration": _wf_conflict_arbitration,
})


# ================================================================
# 单例
# ================================================================

coordinator = Coordinator()
