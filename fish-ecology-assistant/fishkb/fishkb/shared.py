"""Shared utilities for fishkb.

Unified journal whitelist, search query builder, and OCR variant generator.
Extracted from fish-ecology-assistant/src/shared.py.
"""

from __future__ import annotations

from typing import Dict, List

# ── Journal credibility whitelist ──

JOURNAL_WHITELIST: Dict[str, int] = {
    # Chinese core journals (北大核心 / CSCD)
    "水生生物学报": 25,
    "中国水产科学": 25,
    "水产学报": 25,
    "生物多样性": 25,
    "湖泊科学": 25,
    "南方水产科学": 25,
    "淡水渔业": 25,
    "上海海洋大学学报": 25,
    "水产学杂志": 25,
    "生态科学": 20,
    "生态学报": 25,
    # International journals — high tier (Q1/Q2, IF ≥ 2.5)
    "BMC Biology": 30,
    "Scientific Data": 30,
    "Scientific Reports": 30,
    "Genes": 30,
    "Gene": 30,
    "Animals": 30,
    "Mitochondrial DNA": 30,
    "Conserv Genet Resour": 30,
    "PLOS ONE": 30,
    # International journals — standard tier (SCI, lower IF)
    "Ichthyological Research": 20,
    "Fisheries Science": 20,
    "Nippon Suisan Gakkaishi": 20,
}


def build_search_queries(scientific_name: str, chinese_name: str = "") -> List[str]:
    """Build discipline-specific search queries for a species.

    Returns richer queries than the old simple "{name} {direction}" pattern.
    """
    queries = [scientific_name]
    if chinese_name:
        queries.append(chinese_name)
    return queries


def generate_ocr_variants(name: str, limit: int = 20) -> List[str]:
    """Generate OCR error variants for a scientific name."""
    variants: set[str] = set()
    confusable = {
        "u": ["b"], "b": ["u"],
        "i": ["l", "e"], "l": ["i"],
        "n": ["m"], "m": ["n"],
    }
    for i, ch in enumerate(name):
        if ch.lower() in confusable:
            for sub in confusable[ch.lower()]:
                variants.add(name[:i] + sub + name[i + 1:])
    for i in range(len(name)):
        variants.add(name[:i] + name[i + 1:])
    for n in range(1, min(4, len(name))):
        variants.add(name[:-n])
    return list(variants)[:limit]
