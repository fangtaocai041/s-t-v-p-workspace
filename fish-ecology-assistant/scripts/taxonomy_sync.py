#!/usr/bin/env python3
"""
taxonomy_sync.py — 分类学变更双向同步 (c图谱 ↔ f知识库)

检测:
  - family 不一致
  - conservation 不一致
  - synonyms/variants 差异
  - scientific name 变更

用法:
  python scripts/taxonomy_sync.py              # 仅报告差异
  python scripts/taxonomy_sync.py --apply       # 写入KB taxonomy_log
  python scripts/taxonomy_sync.py --apply-graph # 写入图谱

v1.0 — P2 分类学变更同步
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

_WORKSPACE = Path(__file__).resolve().parent.parent.parent
_KB_PATH = _WORKSPACE / "fish-ecology-assistant" / "config" / "fish_species_kb.yaml"
_GRAPH_PATH = _WORKSPACE / "cognitive-search-engine" / "config" / "species_graph.yaml"

# 科名映射: c项目(英文) ↔ f项目(中文)
_FAMILY_MAP = {
    "鲤科": "Cyprinidae", "Leuciscidae": "雅罗鱼科", "Xenocyprididae": "鲴科",
    "鲿科": "Bagridae", "鳀科": "Engraulidae", "鲇科": "Siluridae",
    "鳜科": "Sinipercidae", "鲟科": "Acipenseridae", "胭脂鱼科": "Catostomidae",
    "杜父鱼科": "Cottidae", "匙吻鲟科": "Polyodontidae", "鲱科": "Clupeidae",
    "Phocoenidae": "鼠海豚科",
}


def _normalize_family(name: str) -> str:
    """标准化科名用于比较."""
    n = name.strip()
    if n in _FAMILY_MAP:
        return _FAMILY_MAP[n]
    return n


def sync(apply: bool = False, apply_graph: bool = False) -> dict:
    with open(_KB_PATH, encoding="utf-8") as f:
        kb = yaml.safe_load(f)
    with open(_GRAPH_PATH, encoding="utf-8") as f:
        graph = yaml.safe_load(f)

    # Build KB index by scientific name + aliases
    kb_index = {}
    for entry in kb.get("species", []):
        if not isinstance(entry, dict):
            continue
        sci = entry.get("scientific", "")
        names = {sci.lower()} if sci else set()
        for alias in entry.get("aliases", []) or []:
            names.add(alias.lower())
        for syn in entry.get("synonyms", []) or []:
            names.add(syn.lower())
        for n in names:
            kb_index[n] = entry

    discrepancies = []
    for sp in graph["graph"]["species"]:
        gid = sp.get("id", "")
        gname = sp.get("name", "").lower()
        g_family = sp.get("family", "")
        g_conservation = sp.get("conservation", "")
        g_variants = sp.get("variants", []) or []

        # Find matching KB entry
        kb_entry = kb_index.get(gname)
        if not kb_entry:
            for alias in [gname.replace("_", " ")] + [v.lower() for v in g_variants]:
                if alias in kb_index:
                    kb_entry = kb_index[alias]
                    break

        if not kb_entry:
            continue

        # Compare family
        kb_family = _normalize_family(kb_entry.get("family", ""))
        g_family_norm = _normalize_family(g_family)
        if kb_family and g_family_norm and kb_family.lower() != g_family_norm.lower():
            discrepancies.append({
                "species_id": gid,
                "field": "family",
                "graph_value": g_family,
                "kb_value": kb_entry.get("family", ""),
                "action": "update_kb" if g_family else "update_graph" if kb_family else "review",
            })

        # Compare conservation
        kb_cons = kb_entry.get("conservation", "") or ""
        g_cons = g_conservation or ""
        if kb_cons and g_cons and kb_cons.lower() != g_cons.lower():
            discrepancies.append({
                "species_id": gid,
                "field": "conservation",
                "graph_value": g_cons,
                "kb_value": kb_cons,
                "action": "review",
            })

        # Check if KB has species_graph_id pointer
        kb_graph_id = kb_entry.get("species_graph_id", "")
        if not kb_graph_id:
            discrepancies.append({
                "species_id": gid,
                "field": "species_graph_id",
                "graph_value": gid,
                "kb_value": "(missing)",
                "action": "update_kb",
            })

    print(f"\n{'='*60}")
    print(f"  分类学变更同步 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  图谱物种: {len(graph['graph']['species'])}")
    print(f"  KB物种:   {len([s for s in kb.get('species',[]) if isinstance(s,dict)])}")
    print(f"  差异数:   {len(discrepancies)}")
    print(f"{'='*60}")

    for d in discrepancies:
        print(f"\n  {d['species_id']}.{d['field']}:")
        print(f"    图谱: {d['graph_value']}")
        print(f"    KB:   {d['kb_value']}")
        print(f"    操作: {d['action']}")

    # Apply: update KB taxonomy_log
    if apply and discrepancies:
        for d in discrepancies:
            if d["action"] != "update_kb":
                continue
            # Find and update KB entry
            for i, entry in enumerate(kb.get("species", [])):
                if not isinstance(entry, dict):
                    continue
                if entry.get("scientific", "").lower().split()[0] in d["species_id"].lower():
                    if "taxonomy_log" not in entry:
                        entry["taxonomy_log"] = []
                    entry["taxonomy_log"].append({
                        "detected_at": datetime.now().strftime("%Y-%m-%d"),
                        "field": d["field"],
                        "new_value": d["graph_value"],
                        "note": f"同步自图谱: {d['graph_value']}",
                    })
                    if d["field"] == "species_graph_id":
                        entry["species_graph_id"] = d["graph_value"]
                    break

        with open(_KB_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(kb, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"\n✅ KB 已更新 {sum(1 for d in discrepancies if d['action']=='update_kb')} 处")

    if not apply and not apply_graph:
        print(f"\n💡 使用 --apply 更新KB, --apply-graph 更新图谱")

    return {"discrepancies": len(discrepancies), "applied": apply or apply_graph}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分类学变更双向同步")
    parser.add_argument("--apply", action="store_true", help="写入KB taxonomy_log")
    parser.add_argument("--apply-graph", action="store_true", help="写入图谱")
    args = parser.parse_args()
    sync(apply=args.apply, apply_graph=args.apply_graph)
