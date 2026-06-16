#!/usr/bin/env python3
"""
run_lit_search.py — lit-search v3.1 命令行入口

一键执行: 读图谱 → 三角验证评分 → 摘要输出 → 交互展开

用法:
  python scripts/run_lit_search.py "珠星三块鱼"
  python scripts/run_lit_search.py "Pseudaspius hakonensis" --mode exhaustive
  python scripts/run_lit_search.py "珠星三块鱼" --graph-only   # 仅图谱

v1.0 — lit-search v3.1 配套, 遵循 FS-1 规则
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add scripts to path for credibility_scorer (now in cognitive-search-engine)
_SCRIPTS = Path(__file__).resolve().parent
_COG = _SCRIPTS.parent.parent / "cognitive-search-engine" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_COG))  # cognitive first, so credibility_scorer resolves to real file

import yaml

from credibility_scorer import score_papers


def load_graph() -> dict:
    """Load species_graph.yaml from cognitive-search-engine."""
    path = Path(__file__).resolve().parent.parent.parent / "cognitive-search-engine" / "config" / "species_graph.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_species(graph: dict, query: str) -> tuple:
    """Find species by chinese name or scientific name or alias."""
    q = query.lower().strip()
    for sp in graph["graph"]["species"]:
        sid = sp.get("id", "").lower().replace("_", " ")
        if q in sid or q in sp.get("name", "").lower() or q in sp.get("chinese", "").lower():
            return sp, sp.get("id", "")
        for alias in sp.get("aliases", []) + sp.get("variants", []):
            if q in alias.lower():
                return sp, sp.get("id", "")
    return None, None


def get_papers(graph: dict, species_id: str) -> list:
    """Get all papers for a species."""
    return [p for p in graph["graph"]["papers"] if species_id in p.get("species", [])]


def show_summary(species: dict, scored: list):
    """Print executive summary."""
    papers = scored
    sci_count = sum(1 for p in papers if p.get("_credibility_tier") == "SCI")
    cscd_count = sum(1 for p in papers if p.get("_credibility_tier") == "CSCD")
    high = sum(1 for p in papers if p["_credibility_label"] == "高")
    mid = sum(1 for p in papers if p["_credibility_label"] == "中")
    low = sum(1 for p in papers if p["_credibility_label"] == "低")
    unusable = sum(1 for p in papers if p["_credibility_label"] == "不可用")
    chinese = sum(1 for p in papers if any("\u4e00" <= c <= "\u9fff" for c in p.get("title", "")))

    print("\n" + "═" * 60)
    print(f"  📚 {species.get('chinese','?')}（{species.get('name','?')}）")
    print("═" * 60)
    print(f"  📊 总计: {len(papers)}篇 | SCI: {sci_count} | CSCD: {cscd_count}")
    print(f"  🟢 高: {high}篇 | 🟡 中: {mid}篇 | 🟠 低: {low}篇 | 🔴 不可用: {unusable}篇")
    print(f"  🇨🇳 中文: {chinese}篇")
    print("─" * 60)

    # Top 5 by credibility
    sorted_papers = sorted(papers, key=lambda p: p["_credibility_score"], reverse=True)
    print("\n  最高置信度论文:")
    for p in sorted_papers[:5]:
        print(f"  {p['_credibility_flag']} {p['_credibility_score']:3d} | "
              f"{p.get('title','?')[:55]:55s} | {p.get('journal','')[:20]}")
    print()


def show_papers(scored: list, n: int = 10):
    """Print paper table."""
    sorted_p = sorted(scored, key=lambda p: p["_credibility_score"], reverse=True)
    print(f"  {'#':>3} | {'年':>4} | {'标题':<55} | {'置信':>6} | DOI")
    print("  " + "-" * 95)
    for i, p in enumerate(sorted_p[:n], 1):
        title = (p.get("title", "") or "")[:55]
        doi = (p.get("doi", "") or "")[:30] or "-"
        year = p.get("year", "") or ""
        flag = p["_credibility_flag"]
        score = p["_credibility_score"]
        print(f"  {i:>3} | {str(year):>4} | {title:<55} | {flag} {score:3d} | {doi}")


def cli():
    parser = argparse.ArgumentParser(description="lit-search v3.1 命令行入口")
    parser.add_argument("query", nargs="?", default="珠星三块鱼", help="物种中文名或学名")
    parser.add_argument("--graph-only", action="store_true", help="仅输出图谱缓存")
    parser.add_argument("--mode", choices=["satisficing", "exhaustive"], default="satisficing")
    parser.add_argument("--n", type=int, default=10, help="展示论文数")
    parser.add_argument("--format", choices=["summary", "table", "json", "all"], default="summary")
    parser.add_argument("--output", help="输出到文件")
    args = parser.parse_args()

    graph = load_graph()
    species, species_id = find_species(graph, args.query)

    if not species:
        print(f"❌ 未找到物种: {args.query}")
        print(f"   图谱中有 {len(graph['graph']['species'])} 个物种:")
        for sp in graph["graph"]["species"]:
            print(f"    {sp.get('chinese','')} ({sp.get('name','')})")
        sys.exit(1)

    papers = get_papers(graph, species_id)
    scored = score_papers(papers, species_name=species.get("name", ""))

    if args.format == "json":
        import json
        out = json.dumps({
            "species": species.get("name"),
            "chinese": species.get("chinese"),
            "total": len(scored),
            "papers": scored[:args.n] if args.n else scored,
        }, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"✅ 已写入 {args.output}")
        else:
            print(out)
        return

    show_summary(species, scored)

    if args.format == "all" or args.format == "table":
        show_papers(scored, args.n)

    # Self-evolve log
    try:
        from self_evolve import log_search
        log_search(species_id, {
            "mode": args.mode,
            "layers_activated": ["L1", "L2", "L3"],
            "layers_producing": {"L1": len(papers)},
            "known_papers": len(papers),
            "new_papers": 0,
            "total_papers": len(papers),
            "tokens_estimated": 0,
            "mode_auto": False,
        })
    except ImportError:
        pass


if __name__ == "__main__":
    cli()