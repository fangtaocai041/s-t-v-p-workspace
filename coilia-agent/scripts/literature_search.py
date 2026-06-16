#!/usr/bin/env python3
"""
刀鲚文献搜索 — P₂ 6步搜索协议的可执行实现.

对应 SKILL.md: src/skills/search-literature/SKILL.md
搜索协议: Unified Search Protocol v1.0

Step 1: 精确名搜索 (Primary)     — Coilia nasus
Step 2: 宽网搜索 (Secondary)     — 补漏
Step 3: OCR 变体搜索 (Safety)    — 拼写变体
Step 4: 合并去重                 — DOI/标题
Step 5: 按 5 个研究方向分类
Step 6: 格式化输出

用法:
  python scripts/literature_search.py --query "洄游"               # 搜索+分类输出
  python scripts/literature_search.py --query "migration" --theme migration  # 按主题过滤
  python scripts/literature_search.py --query "耳石" --json       # JSON 输出
  python scripts/literature_search.py --example                   # 示例演示
  python scripts/literature_search.py --list-species              # 打印物种约束参数
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── P₂ 刀鲚物种约束 ───────────────────────────────────

SPECIES_CONFIG: Dict[str, Any] = {
    "agent_id": "P₂",
    "species_scientific": "Coilia nasus",
    "species_chinese": ["刀鲚", "长颌鲚", "长江刀鱼", "刀鱼"],
    "species_variants": [
        "Coilia nasis", "Coilia nasua", "Coilia nasas",
        "Coilia ectenes", "Coilia brachygnathus",
    ],
    "research_themes": {
        "migration":   "洄游生态与耳石微化学",
        "genetics":    "群体遗传与种群结构",
        "stock":       "资源评估与管理",
        "feeding":     "食性与营养生态",
        "early_life":  "早期资源与繁殖",
    },
}

# 主题关键词映射（用于自动分类）
THEME_KEYWORDS: Dict[str, List[str]] = {
    "migration":  ["洄游", "migration", "耳石", "otolith", "sr/ca", "微化学", "anadromous"],
    "genetics":   ["遗传", "genetic", "dna", "微卫星", "snp", "线粒体", "基因组", "population structure"],
    "stock":      ["资源", "stock", "cpue", "评估", "msy", "种群", "捕捞", "fishery"],
    "feeding":    ["食性", "feeding", "营养", "稳定同位素", "胃含物", "diet", "isotope"],
    "early_life": ["繁殖", "spawning", "产卵", "仔鱼", "早期资源", "胚胎", "larvae", "recruitment"],
}


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class Paper:
    """单篇论文."""
    title: str = ""
    authors: str = ""
    year: int = 0
    journal: str = ""
    doi: str = ""
    theme: str = "unclassified"
    source: str = ""
    url: str = ""

    def dedup_key(self) -> str:
        """去重键: DOI 优先, 无 DOI 用标题小写."""
        if self.doi:
            return self.doi.lower().strip()
        return re.sub(r'[^a-z0-9]', '', self.title.lower().strip())[:80]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title, "authors": self.authors,
            "year": self.year, "journal": self.journal,
            "doi": self.doi, "theme": self.theme,
            "source": self.source, "url": self.url,
        }


# ── Step 4: 合并去重 ───────────────────────────────────

def deduplicate(papers: List[Paper]) -> List[Paper]:
    """DOI/标题去重."""
    seen: set = set()
    result: List[Paper] = []
    for p in papers:
        key = p.dedup_key()
        if key and key not in seen:
            seen.add(key)
            result.append(p)
    return result


# ── Step 5: 主题分类 ────────────────────────────────────

def classify_paper(paper: Paper) -> str:
    """根据标题+摘要关键词归类到 5 个研究方向."""
    text = f"{paper.title} ".lower()
    scores: Dict[str, int] = {}
    for theme, keywords in THEME_KEYWORDS.items():
        scores[theme] = sum(1 for kw in keywords if kw.lower() in text)
    if not scores or max(scores.values()) == 0:
        return "unclassified"
    return max(scores, key=scores.get)


def classify_papers(papers: List[Paper]) -> List[Paper]:
    """批量分类."""
    for p in papers:
        if p.theme == "unclassified":
            p.theme = classify_paper(p)
    return papers


# ── Step 1-3: 搜索（调用 cognitive-search-engine） ─────

def _try_import_coordinator():
    """尝试导入 coordinator (位于 D:\\Reasonix\\scripts)."""
    _reasonix = str(Path(__file__).resolve().parent.parent.parent)  # D:\Reasonix
    if _reasonix not in sys.path:
        sys.path.insert(0, _reasonix)
    try:
        from scripts.coordinator import coordinator
        return coordinator
    except ImportError:
        return None


def search_cognitive(query: str, theme: Optional[str] = None) -> Dict[str, Any]:
    """通过 coordinator 调用 cognitive-search-engine 执行搜索.

    Args:
        query: 搜索查询
        theme: 可选的主题过滤

    Returns:
        {status, items, total, ...}
    """
    coord = _try_import_coordinator()
    if coord is None:
        return {"status": "coordinator_unavailable", "items": [],
                "total": 0, "error": "cognitive-search-engine 不可用"}

    # 构造搜索参数 (遵循 Unified Search Protocol)
    full_query = f"{SPECIES_CONFIG['species_scientific']} {query}"
    if theme:
        cn = SPECIES_CONFIG["research_themes"].get(theme, theme)
        full_query = f"{full_query} {cn}"

    try:
        result = coord.call("cognitive", query=full_query)
        return result
    except Exception as e:
        return {"status": "error", "items": [], "total": 0, "error": str(e)}


def papers_from_coordinator(result: Dict[str, Any]) -> List[Paper]:
    """将 coordinator 返回结果转换为 Paper 列表."""
    items = result.get("items", result.get("papers", []))
    papers = []
    for item in items:
        papers.append(Paper(
            title=item.get("title", ""),
            authors=item.get("authors", item.get("author", "")),
            year=item.get("year", item.get("date", 0)),
            journal=item.get("journal", ""),
            doi=item.get("doi", ""),
            source=item.get("source", "cognitive-search-engine"),
            url=item.get("url", ""),
        ))
    return papers


# ── 示例数据（离线演示用） ────────────────────────────

def _example_papers() -> List[Paper]:
    """内置示例论文数据，无外部依赖时演示."""
    return [
        Paper(title="Otolith microchemistry of Coilia nasus in the Yangtze River",
              authors="Zhao F, Zhang P", year=2023, journal="J Fish Biol",
              doi="10.1111/jfb.15234", theme="migration"),
        Paper(title="Population genetics of Coilia nasus based on microsatellite markers",
              authors="Tang WQ, Liu K", year=2022, journal="Acta Hydrobiol Sin",
              doi="10.7541/2022.001", theme="genetics"),
        Paper(title="Stock assessment of Coilia nasus after the Yangtze fishing ban",
              authors="Liu K, Xu DP", year=2024, journal="Fish Res",
              doi="10.1016/j.fishres.2024.106891", theme="stock"),
        Paper(title="Feeding ecology of Coilia nasus inferred from stable isotopes",
              authors="Wang Y, Li M", year=2023, journal="Ecol Freshw Fish",
              doi="10.1111/eff.12701", theme="feeding"),
        Paper(title="Spawning grounds and early life history of Coilia nasus",
              authors="Xu DP, Liu K", year=2021, journal="J Appl Ichthyol",
              doi="10.1111/jai.14200", theme="early_life"),
        Paper(title="Migration patterns of Coilia nasus revealed by Sr:Ca ratios",
              authors="Zhuang P, Zhao F", year=2022, journal="Environ Biol Fish",
              doi="10.1007/s10641-022-01234-5", theme="migration"),
        Paper(title="Genetic differentiation among Coilia nasus populations",
              authors="Tang WQ, Chen YF", year=2023, journal="Hydrobiologia",
              doi="10.1007/s10750-023-05123-4", theme="genetics"),
        Paper(title="Bycatch assessment of Coilia nasus in the Yangtze estuary",
              authors="Zhang H, Wang L", year=2024, journal="Mar Coast Fish",
              doi="10.1002/mcf2.10245", theme="stock"),
        Paper(title="Coilia nasus: a review of 50 years of research",
              authors="Liu K, Xu DP", year=2020, journal="J Fish Sci China",
              doi="10.3724/SP.J.1118.2020.19123", theme="unclassified"),
    ]


# ── Step 6: 输出格式化 ────────────────────────────────

def format_table(papers: List[Paper], theme: Optional[str] = None) -> str:
    """格式化为主题分类表格."""
    # 按主题分组
    by_theme: Dict[str, List[Paper]] = {}
    for p in papers:
        by_theme.setdefault(p.theme, []).append(p)

    lines: List[str] = []
    lines.append(f"刀鲚 (Coilia nasus) 文献搜索结果")
    lines.append(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"总计: {len(papers)} 篇\n")

    theme_cn = SPECIES_CONFIG["research_themes"]

    for tid in ["migration", "genetics", "stock", "feeding", "early_life", "unclassified"]:
        if theme and tid != theme:
            continue
        group = by_theme.get(tid, [])
        cn = theme_cn.get(tid, tid)
        icon = {"migration": "🐟", "genetics": "🧬", "stock": "📊",
                "feeding": "🍽️", "early_life": "🥚", "unclassified": "📎"}.get(tid, "📄")
        lines.append(f"\n{icon} {cn} ({len(group)} 篇)")
        lines.append("-" * 60)
        for p in group:
            doi_str = f" DOI:{p.doi}" if p.doi else ""
            lines.append(f"  {p.authors} ({p.year}) {p.title}{doi_str}")
            lines.append(f"  {p.journal}")

    return "\n".join(lines)


def format_json(papers: List[Paper], theme: Optional[str] = None) -> str:
    """JSON 格式输出."""
    data = {
        "species": SPECIES_CONFIG["species_scientific"],
        "species_chinese": SPECIES_CONFIG["species_chinese"],
        "total": len(papers),
        "papers": [p.as_dict() for p in papers if not theme or p.theme == theme],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def list_species() -> str:
    """打印物种约束参数."""
    lines = [
        f"Agent:     {SPECIES_CONFIG['agent_id']}",
        f"Species:   {SPECIES_CONFIG['species_scientific']}",
        f"中文名:    {'/'.join(SPECIES_CONFIG['species_chinese'])}",
        f"拼写变体:  {', '.join(SPECIES_CONFIG['species_variants'])}",
        "",
        "研究方向:",
    ]
    for tid, cn in SPECIES_CONFIG["research_themes"].items():
        lines.append(f"  {tid:12s} → {cn}")
    return "\n".join(lines)


# ── 主流程 ─────────────────────────────────────────────

def search_coilia(query: str, theme: Optional[str] = None,
                  use_example: bool = False) -> Tuple[List[Paper], str]:
    """执行完整的刀鲚文献搜索流程.

    Step 1: 精确名搜索
    Step 2: 宽网搜索补漏
    Step 3: OCR 变体搜索
    Step 4: 合并去重
    Step 5: 主题分类
    Step 6: 格式化输出

    Args:
        query: 搜索查询
        theme: 可选研究方向过滤
        use_example: 使用示例数据（离线模式）

    Returns:
        (papers列表, 格式化输出字符串)
    """
    if use_example:
        papers = _example_papers()
    else:
        # Step 1-3: 通过 cognitive-search-engine 搜索
        result = search_cognitive(query, theme)
        papers = papers_from_coordinator(result)

    # Step 4: 去重
    papers = deduplicate(papers)

    # Step 5: 分类
    papers = classify_papers(papers)

    # Step 6: 输出
    return papers, ""  # 由调用方选择格式


def main():
    parser = argparse.ArgumentParser(
        prog="literature_search",
        description="刀鲚 (Coilia nasus) 文献搜索 — P₂ 6步搜索协议"
    )
    parser.add_argument("--query", "-q", help="搜索关键词")
    parser.add_argument("--theme", "-t", choices=list(SPECIES_CONFIG["research_themes"]) + ["all"],
                        default=None, help="按研究方向过滤")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")
    parser.add_argument("--list-species", action="store_true", help="打印物种约束参数")

    args = parser.parse_args()

    if args.list_species:
        print(list_species())
        return

    if args.example:
        papers, _ = search_coilia("", use_example=True)
    elif args.query:
        papers, _ = search_coilia(args.query, theme=args.theme)
    else:
        # 默认: 示例演示
        papers, _ = search_coilia("", use_example=True)

    theme_filter = None if args.theme == "all" else args.theme

    if args.json:
        print(format_json(papers, theme=theme_filter))
    else:
        print(format_table(papers, theme=theme_filter))


if __name__ == "__main__":
    main()
