#!/usr/bin/env python3
"""
鲚属文献搜索 — P₂ 6步搜索协议的可执行实现.

对应 SKILL.md: src/skills/search-literature/SKILL.md
搜索协议: Unified Search Protocol v1.0

Step 1: 精确名搜索 (Primary)     — <学名>
Step 2: 宽网搜索 (Secondary)     — 补漏
Step 3: OCR 变体搜索 (Safety)    — 拼写变体
Step 4: 合并去重                 — DOI/标题
Step 5: 按研究方向分类
Step 6: 格式化输出

支持多物种: --species coilia_nasus | coilia_brachygnathus | coilia_mystus | coilia_grayii

用法:
  python scripts/literature_search.py --query "洄游"               # 搜索+分类输出
  python scripts/literature_search.py --query "migration" --theme migration  # 按主题过滤
  python scripts/literature_search.py --species coilia_mystus --query "食性" --json  # 凤鲚+JSON
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

# ── 物种约束 (从 SpeciesRegistry 动态加载) ────────────

def _get_species_config(species_id: Optional[str] = None) -> Dict[str, Any]:
    """从 SpeciesRegistry 加载物种配置，包装为兼容 SPECIES_CONFIG 格式."""
    # 确保项目根在 sys.path
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in sys.path:
        sys.path.insert(0, _project)

    from src.agent.species_registry import get_registry
    registry = get_registry()
    if species_id is None:
        species_id = registry.default_id()
    raw = registry.get(species_id)
    if raw is None:
        raw = registry.default()

    return {
        "agent_id": "P₂",
        "species_scientific": raw.get("species_scientific", "Coilia nasus"),
        "species_chinese": raw.get("species_chinese", []),
        "species_variants": raw.get("species_variants", []),
        "research_themes": {
            tid: theme.get("label", tid)
            for tid, theme in raw.get("research_themes", {}).items()
        },
    }


def _get_theme_keywords(species_id: Optional[str] = None) -> Dict[str, List[str]]:
    """从 SpeciesRegistry 加载主题关键词."""
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in sys.path:
        sys.path.insert(0, _project)

    from src.agent.species_registry import get_registry
    registry = get_registry()
    if species_id is None:
        species_id = registry.default_id()
    raw = registry.get(species_id)
    if raw is None:
        raw = registry.default()

    return {
        tid: theme.get("keywords", [])
        for tid, theme in raw.get("research_themes", {}).items()
    }


# ── 向后兼容：模块级 SPECIES_CONFIG ──
SPECIES_CONFIG = _get_species_config()
THEME_KEYWORDS = _get_theme_keywords()


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

def classify_paper(paper: Paper, keywords: Dict[str, List[str]] = None) -> str:
    """根据标题+摘要关键词归类到研究方向."""
    if keywords is None:
        keywords = THEME_KEYWORDS
    text = f"{paper.title} ".lower()
    scores: Dict[str, int] = {}
    for theme, kws in keywords.items():
        scores[theme] = sum(1 for kw in kws if kw.lower() in text)
    if not scores or max(scores.values()) == 0:
        return "unclassified"
    return max(scores, key=scores.get)


def classify_papers(papers: List[Paper], keywords: Dict[str, List[str]] = None) -> List[Paper]:
    """批量分类."""
    for p in papers:
        if p.theme == "unclassified":
            p.theme = classify_paper(p, keywords)
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


def search_cognitive(query: str, theme: Optional[str] = None,
                     cfg: Optional[Dict] = None) -> Dict[str, Any]:
    """通过 coordinator 调用 cognitive-search-engine 执行搜索.

    Args:
        query: 搜索查询
        theme: 可选的主题过滤
        cfg: 物种配置 (默认使用 SPECIES_CONFIG)

    Returns:
        {status, items, total, ...}
    """
    if cfg is None:
        cfg = SPECIES_CONFIG

    coord = _try_import_coordinator()
    if coord is None:
        return {"status": "coordinator_unavailable", "items": [],
                "total": 0, "error": "cognitive-search-engine 不可用"}

    # 构造搜索参数 (遵循 Unified Search Protocol)
    full_query = f"{cfg['species_scientific']} {query}"
    if theme:
        cn = cfg["research_themes"].get(theme, theme)
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

def format_table(papers: List[Paper], theme: Optional[str] = None,
                 cfg: Optional[Dict] = None) -> str:
    """格式化为主题分类表格."""
    if cfg is None:
        cfg = SPECIES_CONFIG

    # 按主题分组
    by_theme: Dict[str, List[Paper]] = {}
    for p in papers:
        by_theme.setdefault(p.theme, []).append(p)

    species_cn = '/'.join(cfg["species_chinese"]) if cfg["species_chinese"] else cfg["species_scientific"]

    lines: List[str] = []
    lines.append(f"{species_cn} ({cfg['species_scientific']}) 文献搜索结果")
    lines.append(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"总计: {len(papers)} 篇\n")

    theme_cn = cfg["research_themes"]

    for tid in list(theme_cn.keys()) + ["unclassified"]:
        if theme and tid != theme:
            continue
        group = by_theme.get(tid, [])
        cn = theme_cn.get(tid, tid)
        icon = {"migration": "🐟", "genetics": "🧬", "stock": "📊",
                "feeding": "🍽️", "early_life": "🥚", "morphology": "🔬",
                "unclassified": "📎"}.get(tid, "📄")
        lines.append(f"\n{icon} {cn} ({len(group)} 篇)")
        lines.append("-" * 60)
        for p in group:
            doi_str = f" DOI:{p.doi}" if p.doi else ""
            lines.append(f"  {p.authors} ({p.year}) {p.title}{doi_str}")
            lines.append(f"  {p.journal}")

    return "\n".join(lines)


def format_json(papers: List[Paper], theme: Optional[str] = None,
                cfg: Optional[Dict] = None) -> str:
    """JSON 格式输出."""
    if cfg is None:
        cfg = SPECIES_CONFIG
    data = {
        "species": cfg["species_scientific"],
        "species_chinese": cfg["species_chinese"],
        "total": len(papers),
        "papers": [p.as_dict() for p in papers if not theme or p.theme == theme],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def list_species(cfg: Optional[Dict] = None) -> str:
    """打印物种约束参数."""
    if cfg is None:
        cfg = SPECIES_CONFIG
    lines = [
        f"Agent:     {cfg['agent_id']}",
        f"Species:   {cfg['species_scientific']}",
        f"中文名:    {'/'.join(cfg['species_chinese'])}",
        f"拼写变体:  {', '.join(cfg['species_variants'])}",
        "",
        "研究方向:",
    ]
    for tid, cn in cfg["research_themes"].items():
        lines.append(f"  {tid:12s} → {cn}")
    return "\n".join(lines)


# ── 主流程 ─────────────────────────────────────────────

def search_coilia(query: str, theme: Optional[str] = None,
                  use_example: bool = False,
                  species_id: Optional[str] = None) -> Tuple[List[Paper], str]:
    """执行完整的鲚属文献搜索流程.

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
        species_id: 物种 ID (默认 coilia_nasus)

    Returns:
        (papers列表, 格式化输出字符串)
    """
    cfg = _get_species_config(species_id)
    keywords = _get_theme_keywords(species_id)

    if use_example:
        papers = _example_papers()
    else:
        # Step 1-3: 通过 cognitive-search-engine 搜索
        result = search_cognitive(query, theme, cfg=cfg)
        papers = papers_from_coordinator(result)

    # Step 4: 去重
    papers = deduplicate(papers)

    # Step 5: 分类
    papers = classify_papers(papers, keywords=keywords)

    # Step 6: 输出
    return papers, ""  # 由调用方选择格式


def main():
    # 提前加载注册表以获取可用 species 列表
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in sys.path:
        sys.path.insert(0, _project)
    from src.agent.species_registry import get_registry
    registry = get_registry()
    available_species = registry.list_species()

    parser = argparse.ArgumentParser(
        prog="literature_search",
        description="鲚属 (Coilia) 文献搜索 — P₂ 6步搜索协议"
    )
    parser.add_argument("--query", "-q", help="搜索关键词")
    parser.add_argument("--species", "-s", choices=available_species,
                        default=None, help="目标物种 (默认: coilia_nasus)")
    parser.add_argument("--theme", "-t", default=None,
                        help="按研究方向过滤")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")
    parser.add_argument("--list-species", action="store_true", help="打印物种约束参数")

    args = parser.parse_args()

    # 按 species 参数加载配置
    cfg = _get_species_config(args.species) if args.species else SPECIES_CONFIG

    if args.list_species:
        print(list_species(cfg))
        return

    # 动态更新 theme choices
    if args.theme and args.theme not in cfg["research_themes"] and args.theme != "all":
        pass  # 允许自由文本

    if args.example:
        papers, _ = search_coilia("", use_example=True, species_id=args.species)
    elif args.query:
        papers, _ = search_coilia(args.query, theme=args.theme, species_id=args.species)
    else:
        # 默认: 示例演示
        papers, _ = search_coilia("", use_example=True, species_id=args.species)

    theme_filter = None if args.theme == "all" else args.theme

    if args.json:
        print(format_json(papers, theme=theme_filter, cfg=cfg))
    else:
        print(format_table(papers, theme=theme_filter, cfg=cfg))


if __name__ == "__main__":
    main()
