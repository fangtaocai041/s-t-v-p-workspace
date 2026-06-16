#!/usr/bin/env python3
"""KB↔图谱双向同步脚本 — fish_species_kb.yaml ⇄ species_graph.yaml

ROADMAP Mid-term: V0 ⟷ V1 (KB ↔ Graph sync)

用法:
  python scripts/sync_kb_graph.py --check    # 只报告差异
  python scripts/sync_kb_graph.py --sync     # 执行同步
  python scripts/sync_kb_graph.py --diff     # 显示详细差异
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project roots
_REASONIX = Path(__file__).resolve().parent.parent  # D:\Reasonix
sys.path.insert(0, str(_REASONIX))

import yaml

# Paths
KB_PATH = _REASONIX / "fish-ecology-assistant" / "config" / "fish_species_kb.yaml"
GRAPH_PATH = _REASONIX / "cognitive-search-engine" / "config" / "species_graph.yaml"

def load_kb() -> Dict:
    return yaml.safe_load(KB_PATH.read_text(encoding="utf-8"))

def load_graph() -> Dict:
    return yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))

def save_kb(kb: Dict):
    KB_PATH.write_text(yaml.dump(kb, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")

def save_graph(g: Dict):
    GRAPH_PATH.write_text(yaml.dump(g, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")

def check() -> int:
    """Compare KB and Graph, report differences. Returns number of diffs."""
    kb = load_kb()
    g = load_graph()
    
    kb_species = {s.get("scientific", "").lower(): s for s in kb.get("species", [])}
    graph_species = {s.get("name", "").lower(): s for s in g.get("graph", {}).get("species", [])}
    
    diffs = 0
    
    # KB has but Graph missing
    for sci, s in kb_species.items():
        if sci and sci not in graph_species:
            # Try matching by common name
            matched = False
            name = s.get("name", "").lower()
            for gsci, gs in graph_species.items():
                if name == gs.get("chinese", "").lower():
                    matched = True
                    break
            if not matched:
                print(f"  KB→Graph 缺失: {s.get('scientific')} ({s.get('name')})")
                diffs += 1
    
    # Graph has but KB missing
    for sci, s in graph_species.items():
        if sci and sci not in kb_species:
            cn = s.get("chinese", "")
            if cn:
                # Check if KB has by chinese name
                if not any(kbs.get("name", "") == cn for kbs in kb_species.values()):
                    print(f"  Graph→KB 缺失: {s.get('name')} ({cn}) [{s.get('family')}]")
                    diffs += 1
    
    # Field-level diffs for common species
    common = set(kb_species.keys()) & set(graph_species.keys())
    for sci in sorted(common):
        ks = kb_species[sci]
        gs = graph_species[sci]
        # Compare conservation
        kb_cons = ks.get("conservation", "NE")
        g_cons = gs.get("conservation", "NE")
        if kb_cons != g_cons:
            print(f"  保护等级差异: {sci} KB={kb_cons} Graph={g_cons}")
            diffs += 1
        # Compare family
        kb_fam = ks.get("family", "")
        g_fam = gs.get("family", "")
        if kb_fam and g_fam and kb_fam != g_fam:
            print(f"  科差异: {sci} KB={kb_fam} Graph={g_fam}")
            diffs += 1
    
    return diffs


def sync(dry_run: bool = False) -> int:
    """Sync both directions. Returns number of changes."""
    kb = load_kb()
    g = load_graph()
    
    kb_species: Dict = {s.get("scientific", "").lower(): s for s in kb.get("species", [])}
    graph_species: Dict = {s.get("name", "").lower(): s for s in g.get("graph", {}).get("species", [])}
    
    changes = 0
    
    # KB→Graph: add missing species to graph
    for sci, s in kb_species.items():
        if not sci:
            continue
        if sci not in graph_species:
            name = s.get("name", "")
            # Check if graph has by chinese name
            already_in_graph = False
            for gsci, gs in graph_species.items():
                if gs.get("chinese", "") == name:
                    already_in_graph = True
                    break
            if not already_in_graph:
                sp_id = sci.replace(" ", "_")
                entry = {
                    "id": sp_id,
                    "name": s.get("scientific", sci),
                    "chinese": name,
                    "family": s.get("family", "未知"),
                    "conservation": s.get("conservation", "NE"),
                    "variants": [],
                }
                if not dry_run:
                    g["graph"]["species"].append(entry)
                    graph_species[sci] = entry
                print(f"  KB→Graph 添加: {s.get('scientific')} ({name})")
                changes += 1
    
    # Graph→KB: add missing species to KB
    for sci, s in graph_species.items():
        if not sci:
            continue
        if sci not in kb_species:
            cn = s.get("chinese", "")
            if cn:
                already_in_kb = False
                for kbsci, kbs in kb_species.items():
                    if kbs.get("name", "") == cn:
                        already_in_kb = True
                        break
                if not already_in_kb:
                    kid = sci.replace(" ", "_").replace(".", "")
                    entry = {
                        "id": kid,
                        "name": cn,
                        "scientific": s.get("name", sci),
                        "family": s.get("family", "未知"),
                        "conservation": s.get("conservation", "NE"),
                        "category": "yangtze",
                        "distribution": {"continents": ["亚洲"], "countries": ["中国"], "basins": ["长江流域"]},
                    }
                    if not dry_run:
                        kb["species"].append(entry)
                        kb_species[sci] = entry
                    print(f"  Graph→KB 添加: {s.get('name')} ({cn})")
                    changes += 1
    
    # Sync family+conservation for common species
    common = set(kb_species.keys()) & set(graph_species.keys())
    for sci in common:
        ks = kb_species[sci]
        gs = graph_species[sci]
        
        # Graph family → KB
        g_fam = gs.get("family", "")
        if g_fam and g_fam != "未知" and ks.get("family") != g_fam:
            if not dry_run:
                ks["family"] = g_fam
            print(f"  同步科: {sci} KB←Graph {g_fam}")
            changes += 1
        
        # KB family → Graph (if graph unknown)
        kb_fam = ks.get("family", "")
        if kb_fam and kb_fam != "未知" and gs.get("family", "未知") == "未知":
            if not dry_run:
                gs["family"] = kb_fam
            print(f"  同步科: {sci} Graph←KB {kb_fam}")
            changes += 1
        
        # Conservation sync: prefer more specific (non-NE)
        g_cons = gs.get("conservation", "NE")
        kb_cons = ks.get("conservation", "NE")
        if g_cons != "NE" and kb_cons == "NE" and g_cons != kb_cons:
            if not dry_run:
                ks["conservation"] = g_cons
            print(f"  同步保护: {sci} KB←Graph {g_cons}")
            changes += 1
        elif kb_cons != "NE" and g_cons == "NE":
            if not dry_run:
                gs["conservation"] = kb_cons
            print(f"  同步保护: {sci} Graph←KB {kb_cons}")
            changes += 1
    
    if not dry_run and changes > 0:
        save_kb(kb)
        save_graph(g)
    
    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KB↔图谱双向同步")
    parser.add_argument("--check", action="store_true", help="只检查差异，不修改")
    parser.add_argument("--sync", action="store_true", help="执行同步")
    parser.add_argument("--diff", action="store_true", help="显示详细差异")
    args = parser.parse_args()
    
    if args.sync:
        print("=== 执行同步 ===")
        c = sync(dry_run=False)
        print(f"✅ 同步完成: {c} 处变更" if c else "✅ 已一致，无需同步")
    else:
        print("=== 检查差异 ===")
        d = check()
        if d == 0:
            print("✅ KB 与 Graph 完全一致")
        else:
            print(f"\n发现 {d} 处差异")
            if args.diff:
                print("\n详细差异见上")
            print("运行 --sync 以同步")


if __name__ == "__main__":
    main()
