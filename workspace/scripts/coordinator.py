#!/usr/bin/env python
"""coordinator.py — Workspace Species Coordinator (v2.0)

从本地知识库 (config/root_config/species_kb.yaml) 加载物种数据，
为 pipeline_search_species.py 各阶段提供统一协调接口。

接口:
    coordinator.call("fish", query=species)       → Phase 1: 知识库查询
    coordinator.info("cognitive")                 → Phase 2: 搜索模式
    coordinator.call("cognitive", query=sci)      → Phase 2: 文献搜索 (本地图谱)
    coordinator.call("fish", "credibility", ...)  → Phase 3: 可信度评分
    coordinator.pathway("P5_all_to_conflict", ...) → Phase 4: 冲突仲裁

数据源:
    config/root_config/species_kb.yaml (主)
    config/root_config/species_graph.yaml (备: 图谱论文)

用法:
    from scripts.coordinator import coordinator
    result = coordinator.call("fish", query="珠星三块鱼")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_WORKSPACE = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════
# YAML 加载 (可选依赖 — 不可用时 fallback)
# ═══════════════════════════════════════════════════════════════

_HAS_YAML = False
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    pass


def _load_yaml(path: Path) -> Optional[dict]:
    """安全加载 YAML，失败返回 None。"""
    if not _HAS_YAML:
        return None
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# 知识库加载
# ═══════════════════════════════════════════════════════════════

def _load_species_kb() -> dict:
    """从 species_kb.yaml 加载物种知识库。"""
    kb_path = _WORKSPACE / "config" / "root_config" / "species_kb.yaml"
    data = _load_yaml(kb_path)
    if data and isinstance(data, dict):
        return data
    return {"species": [], "metadata": {}}


def _load_species_graph() -> list:
    """从 species_graph.yaml 加载图谱论文 (备选搜索源)。"""
    graph_path = _WORKSPACE / "config" / "root_config" / "species_graph.yaml"
    data = _load_yaml(graph_path)
    if data and isinstance(data, dict):
        return data.get("graph", {}).get("papers", [])
    return []


def _match_species(query: str, kb_data: dict) -> Optional[dict]:
    """在知识库中匹配物种 (中文名/学名/别名/异名)。"""
    q = query.strip().lower()
    species_list = kb_data.get("species", [])
    for sp in species_list:
        # 中文名
        if sp.get("name", "").lower() == q:
            return sp
        # 学名
        if sp.get("scientific", "").lower() == q:
            return sp
        # 别名
        for alias in sp.get("aliases", []):
            if alias.lower() == q:
                return sp
        # 异名
        for syn in sp.get("synonyms", []):
            if isinstance(syn, dict) and syn.get("name", "").lower() == q:
                return sp
            elif isinstance(syn, str) and syn.lower() == q:
                return sp
        # 学名部分匹配 (如 "hakonensis" 匹配 "Pseudaspius hakonensis")
        sci = sp.get("scientific", "").lower()
        if q in sci and len(q) >= 3:
            return sp
        # 中文名部分匹配 (如 "三块鱼" 匹配 "珠星三块鱼")
        name = sp.get("name", "").lower()
        if len(q) >= 2 and q in name:
            return sp
    return None


def _build_species_portrait(species: dict, kb_data: dict) -> dict:
    """从知识库条目构建完整的物种画像。"""
    research = species.get("research_directions", {})

    # 计算论文总数 (从 literature 列表)
    literature = species.get("literature", [])
    paper_count = len(literature)

    # 按研究方向分组
    papers_by_category: Dict[str, list] = {}
    for p in literature:
        cat = p.get("category", "unknown")
        if cat not in papers_by_category:
            papers_by_category[cat] = []
        papers_by_category[cat].append(p)

    # 研究方向标签映射
    cat_labels = {
        "genomics": "🧬 基因组学",
        "parasitology": "🧫 寄生虫学",
        "genetics": "🧪 遗传学",
        "ecology": "🌿 生态学",
        "morphology": "🔬 形态学",
        "physiology": "⚡ 生理学",
        "toxicology": "☣️ 毒理与环境",
        "unknown": "📋 其他",
    }

    direction_summary = {}
    for cat, cat_meta in research.items():
        label = cat_meta.get("label", cat_labels.get(cat, cat))
        count = cat_meta.get("count", len(papers_by_category.get(cat, [])))
        keywords = cat_meta.get("keywords", [])
        direction_summary[cat] = {
            "label": label,
            "count": count,
            "keywords": keywords,
        }

    # 构建论文列表
    paper_list = []
    for p in literature:
        paper_list.append({
            "doi": p.get("doi", ""),
            "title": p.get("title", ""),
            "year": p.get("year", 0),
            "journal": p.get("journal", ""),
            "authors": p.get("authors", []),
            "category": p.get("category", ""),
            "source": p.get("source", ""),
        })

    # 分类变更
    tax_log = species.get("taxonomy_log", [])

    return {
        "scientific_name": species.get("scientific", ""),
        "chinese_name": species.get("name", ""),
        "family": f"{species.get('family', '')}",
        "subfamily": species.get("subfamily", ""),
        "genus": species.get("genus", ""),
        "conservation": species.get("conservation", ""),
        "ecology": species.get("ecology", ""),
        "max_length_cm": species.get("max_length_cm", ""),
        "description": species.get("description", ""),
        "economic_value": species.get("economic_value", ""),
        "distribution": species.get("distribution", {}),
        "aliases": species.get("aliases", []),
        "synonyms": [s["name"] if isinstance(s, dict) else s for s in species.get("synonyms", [])],
        "taxonomy_log": tax_log,
        "paper_count": paper_count,
        "papers": paper_list,
        "papers_by_category": {
            cat: {"label": cat_labels.get(cat, cat), "count": len(plist)}
            for cat, plist in papers_by_category.items()
        },
        "direction_summary": direction_summary,
        "research_directions": list(direction_summary.values()),
    }


def _query_fish_kb(query: str) -> dict:
    """查询鱼类知识库 — 从 YAML 加载并匹配。"""
    kb = _load_species_kb()
    matched = _match_species(query, kb)

    if matched is None:
        return {
            "status": "ok",
            "known_species": False,
            "species_data": {},
            "search_queries": [query],
            "ocr_variants": [],
            "paper_count": 0,
        }

    portrait = _build_species_portrait(matched, kb)

    # 生成搜索查询词列表
    search_queries = [portrait["scientific_name"]]
    for syn in portrait["synonyms"]:
        search_queries.append(syn)
    search_queries.append(portrait["chinese_name"])

    # 冲突裁决 (基于分类变更)
    tax_log = portrait["taxonomy_log"]
    conflict_verdict = {}
    if len(tax_log) >= 2:
        last = tax_log[-1]
        conflict_verdict = {
            "conflict_level": "taxonomy_change",
            "verdict": f"分类变更: {last.get('year','')} {last.get('event','')}",
            "consensus": last.get("event", ""),
        }

    return {
        "status": "ok",
        "known_species": True,
        "species_data": portrait,
        "search_queries": search_queries,
        "ocr_variants": [],
        "paper_count": portrait["paper_count"],
        "conflict_verdict": conflict_verdict,
    }


# ═══════════════════════════════════════════════════════════════
# 可信度评分
# ═══════════════════════════════════════════════════════════════

def _score_credibility(papers: list) -> list:
    """论文可信度评分 (0-100)。

    基于来源可信度 + 期刊影响因子 + 作者 h-index 的简化评分。
    """
    source_weights = {
        "auto_ingest": 60,
        "manual_ingest": 85,
        "crossref": 55,
        "europe_pmc": 70,
        "ncbi": 80,
        "scholar": 50,
    }

    scored = []
    for p in papers:
        if not isinstance(p, dict):
            scored.append({"credibility": 50, "title": str(p)})
            continue
        source = p.get("source", "auto_ingest")
        base = source_weights.get(source, 55)
        # 有 DOI 加分
        if p.get("doi"):
            base += 10
        # 有期刊名加分
        if p.get("journal"):
            base += 5
        # 有作者加分
        if p.get("authors"):
            base += 5
        # 有摘要加分
        if p.get("abstract"):
            base += 5
        credibility = min(base, 100)
        scored.append({"credibility": credibility, **p})

    return scored


# ═══════════════════════════════════════════════════════════════
# 冲突仲裁 (简化版)
# ═══════════════════════════════════════════════════════════════

def _check_conflicts(species: str) -> dict:
    """冲突仲裁 — 从知识库 tax_log 推断分类争议。"""
    kb = _load_species_kb()
    matched = _match_species(species, kb)
    if matched is None:
        return {"verdict": {"verdict": "", "consensus": "", "conflict_level": ""}}

    tax_log = matched.get("taxonomy_log", [])
    family = matched.get("family", "")

    conflicts = []
    if "争议" in family or "争议" in str(tax_log):
        conflicts.append(f"科分类争议: {family}")

    if len(tax_log) >= 2:
        last = tax_log[-1]
        conflicts.append(f"最新变更: {last.get('year','')} {last.get('event','')}")

    return {
        "verdict": {
            "verdict": "; ".join(conflicts) if conflicts else "",
            "consensus": tax_log[-1].get("event", "") if tax_log else "",
            "conflict_level": "taxonomy_change" if conflicts else "none",
        }
    }


# ═══════════════════════════════════════════════════════════════
# Coordinator 类
# ═══════════════════════════════════════════════════════════════

class Coordinator:
    """物种搜索协调器 — 统一所有项目调用入口。"""

    def call(self, service: str, query: str = "", **kwargs) -> dict:
        """统一调用接口 — 项目间流通。

        流通链:
          fish:    fish-ecology-assistant → 未命中 → workspace 本地 YAML
          cognitive: 图谱搜索 (fallback 模式)

        Args:
            service: "fish" 知识库 | "cognitive" 搜索
            query: 物种名或指令
            **kwargs: 额外参数 (如 _papers)
        """
        if service == "fish" and query == "credibility":
            # Phase 3: 可信度评分
            papers = kwargs.get("_papers", [])
            scored = _score_credibility(papers)
            return {"scored_papers": scored, "result": {"papers": scored}}

        if service == "fish":
            # Phase 1: 项目间流通 — 优先走子项目
            try:
                from scripts.project_loader import get_fish
                fish = get_fish()
                if fish:
                    result = fish.search(query, mode="lookup")
                    if result.get("known_species"):
                        return result
            except Exception:
                pass
            # Fallback: workspace 本地 YAML 知识库
            return _query_fish_kb(query)

        if service == "cognitive":
            # Phase 2: 本地搜索 (从图谱中找匹配论文)
            return self._local_cognitive_search(query)

        return {"status": "error", "error": f"Unknown service: {service}"}

    def info(self, service: str) -> dict:
        """获取服务信息。"""
        if service == "cognitive":
            return {"search_mode": "exact_search"}
        return {"search_mode": "local"}

    def pathway(self, name: str, **kwargs) -> dict:
        """执行预定义路径。

        Args:
            name: "P5_all_to_conflict" 等路径名
        """
        if name == "P5_all_to_conflict":
            species = kwargs.get("species", "")
            return _check_conflicts(species)
        return {"verdict": {}, "error": f"Unknown pathway: {name}"}

    def _local_cognitive_search(self, query: str) -> dict:
        """本地认知搜索 — 从 species_graph.yaml 匹配论文。"""
        papers = _load_species_graph()
        q = query.lower()

        # 匹配学名和异名
        matched = []
        seen_dois = set()
        for p in papers:
            doi = p.get("doi", "")
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)

            species_list = p.get("species", [])
            hit = False
            for s in species_list:
                if isinstance(s, str) and (
                    q in s.lower()
                    or q.split()[-1].lower() in s.lower()
                ):
                    hit = True
                    break

            if hit:
                matched.append(p)

        return {
            "papers": matched,
            "result": {"papers": matched},
            "total": len(matched),
        }


# ═══════════════════════════════════════════════════════════════
# 单例
# ═══════════════════════════════════════════════════════════════

coordinator = Coordinator()


# ═══════════════════════════════════════════════════════════════
# CLI 测试
# ═══════════════════════════════════════════════════════════════

def _print_portrait(portrait: dict):
    """打印物种画像。"""
    print(f"\n📊 {portrait.get('chinese_name', '?')} ({portrait.get('scientific_name', '?')})")
    print(f"   科: {portrait.get('family', '?')}")
    print(f"   保护: {portrait.get('conservation', '?')}")
    print(f"   生态: {portrait.get('ecology', '?')}")

    dist = portrait.get("distribution", {})
    if dist:
        parts = []
        for k in ["continents", "countries", "basins"]:
            v = dist.get(k)
            if isinstance(v, list):
                parts.append(f"{k}: {', '.join(v)}")
            elif isinstance(v, dict):
                sub = [f"{sk}: {', '.join(sv) if isinstance(sv, list) else sv}" for sk, sv in v.items()]
                parts.append(f"{k}: {'; '.join(sub)}")
        if parts:
            print(f"   分布: {' | '.join(parts)}")

    if portrait.get("aliases"):
        print(f"   别名: {', '.join(portrait['aliases'][:6])}")
    if portrait.get("synonyms"):
        print(f"   同义词: {', '.join(portrait['synonyms'][:4])}")
    print(f"   图谱论文: {portrait.get('paper_count', 0)} 篇")

    tax_log = portrait.get("taxonomy_log", [])
    if tax_log:
        print(f"   分类变更:")
        for t in tax_log[-4:]:
            print(f"     {t.get('year','?')} {t.get('event','')[:80]}")

    directions = portrait.get("research_directions", [])
    if directions:
        print(f"   研究方向:")
        for d in directions:
            kw = ", ".join(d.get("keywords", [])[:3])
            print(f"     {d.get('label', '?')} ({d.get('count', '?')}) — {kw}")

    papers = portrait.get("papers", [])
    if papers:
        print(f"\n  最新论文 ({min(5, len(papers))}/{len(papers)} 篇):")
        for p in papers[:5]:
            print(f"    [{p.get('year','?')}] {p.get('title','')[:70]}")
            print(f"          {p.get('journal','')} | DOI: {p.get('doi','')}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python scripts/coordinator.py <物种名>")
        sys.exit(1)

    query = sys.argv[1]
    result = coordinator.call("fish", query=query)

    if result.get("known_species"):
        data = result.get("species_data", {})
        _print_portrait(data)
        cv = result.get("conflict_verdict", {})
        if cv and cv.get("conflict_level") not in (None, "", "none"):
            print(f"\n   ⚖️ 冲突: {cv.get('verdict', '')}")
    else:
        print(f"\n  ✗ 知识库未命中: {query}")
