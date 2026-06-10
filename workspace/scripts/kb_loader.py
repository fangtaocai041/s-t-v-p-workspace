"""kb_loader.py — 统一数据加载器 v2

数据流: 图谱(主) → KB(可选富集)

图谱是论文数据的唯一真实来源。
KB 只存手工整理的物种画像 (中文名/科/生态/分类变更)，不存论文。
没有 KB 时直接从图谱加载 + 标题关键词推断方向分类。

用法:
  from scripts.kb_loader import get_papers, get_profile

  papers = get_papers("Tribolodon brandti")   # 从图谱加载
  profile = get_profile("珠星三块鱼")           # 从KB加载富信息
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_WORKSPACE = Path(__file__).resolve().parent.parent
KB_PATH = _WORKSPACE / "config" / "root_config" / "species_kb.yaml"
GRAPH_PATH = _WORKSPACE / "config" / "root_config" / "species_graph.yaml"

CATEGORY_KEYWORDS = {
    "ecology":       ["habitat", "spawning", "trophic", "cascade", "predation",
                      "distribution", "feeding", "diet", "migration", "population",
                      "diversity", "river", "estuary", "freshwater",
                      "产卵", "栖息地", "食性", "分布", "种群", "洄游", "生态"],
    "genetics":      ["DNA", "genetic", "mitochondrial", "cyt b", "COI", "barcoding",
                      "microsatellite", "phylogeny", "phylogeograph", "hybrid",
                      "遗传", "分子", "系统发育", "杂交"],
    "genomics":      ["genome", "transcriptome", "RNA-seq", "gene expression",
                      "mitogenome", "sequencing", "基因组", "转录组"],
    "morphology":    ["morpholog", "pharyngeal teeth", "retina", "scale",
                      "形态", "解剖", "咽齿", "鳞"],
    "physiology":    ["physiology", "spectral", "vitelline", "enzyme", "sperm",
                      "osmoregulation", "视觉", "生理", "酶活"],
    "parasitology":  ["trematode", "digenea", "parasite", "helminth", "Metagonimus",
                      "Zoogonidae", "worm", "fluke", "吸虫", "绦虫", "寄生虫"],
    "toxicology":    ["heavy metal", "Cs-137", "radiocesium", "Fukushima", "pollution",
                      "mercury", "福岛", "重金属"],
}


def _norm(name: str) -> str:
    return name.lower().replace(" ", "").replace("_", "").replace("-", "")


def _infer_category(title: str, journal: str = "") -> str:
    text = (title + " " + journal).lower()
    scores = {cat: sum(1 for kw in kws if kw.lower() in text)
              for cat, kws in CATEGORY_KEYWORDS.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "others"


def _get_sci_names(name: str) -> set:
    """获取物种所有已知名称（含中文/学名/异名）"""
    result = {_norm(name)}
    if not KB_PATH.exists():
        return result
    with open(KB_PATH, "r", encoding="utf-8") as f:
        kb = yaml.safe_load(f) or {}
    for sp in kb.get("species", []):
        candidates = [sp.get("name", ""), sp.get("scientific", "")]
        candidates += sp.get("aliases", [])
        candidates += [s.get("name", "") for s in sp.get("synonyms", [])]
        all_norm = [_norm(c) for c in candidates if c]
        if _norm(name) in all_norm:
            result.update(all_norm)
            break
    return result


def get_papers(species_name: str) -> List[dict]:
    """从图谱加载论文（主数据源），带方向分类推断"""
    if not GRAPH_PATH.exists():
        return []
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = yaml.safe_load(f) or {}
    names = _get_sci_names(species_name)
    result = []
    seen_dois = set()
    for p in graph.get("graph", {}).get("papers", []):
        sp = p.get("species", [])
        if isinstance(sp, list):
            matched = any(_norm(s) in names for s in sp)
        else:
            matched = _norm(str(sp)) in names
        if matched:
            doi = p.get("doi", "")
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            result.append({
                "doi": doi,
                "title": p.get("title", ""),
                "year": p.get("year", 0),
                "journal": p.get("journal", ""),
                "authors": p.get("authors", []),
                "category": _infer_category(p.get("title", ""), p.get("journal", "")),
                "source": p.get("source", "graph"),
            })
    return result


def get_profile(species_name: str) -> Optional[dict]:
    """从KB加载物种画像 (可选富集信息)"""
    if not KB_PATH.exists():
        return None
    with open(KB_PATH, "r", encoding="utf-8") as f:
        kb = yaml.safe_load(f) or {}
    q = _norm(species_name)
    for sp in kb.get("species", []):
        names = [_norm(n) for n in [sp.get("name", ""), sp.get("scientific", "")] +
                 sp.get("aliases", [])]
        if q in names:
            return {
                "name": sp.get("name", ""),
                "scientific": sp.get("scientific", ""),
                "aliases": sp.get("aliases", []),
                "synonyms": sp.get("synonyms", []),
                "family": sp.get("family", ""),
                "ecology": sp.get("ecology", ""),
                "conservation": sp.get("conservation", ""),
                "distribution": sp.get("distribution", {}),
                "taxonomy_log": sp.get("taxonomy_log", []),
                "research_directions": sp.get("research_directions", {}),
            }
    return None


def list_species() -> List[str]:
    """列出图谱中所有物种"""
    if not GRAPH_PATH.exists():
        return []
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = yaml.safe_load(f) or {}
    names = set()
    for p in graph.get("graph", {}).get("papers", []):
        sp = p.get("species", [])
        if isinstance(sp, list):
            names.update(sp)
    return sorted(n for n in names if _norm(n) != "test")
