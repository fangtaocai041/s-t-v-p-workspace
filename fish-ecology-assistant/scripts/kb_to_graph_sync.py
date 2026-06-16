#!/usr/bin/env python3
"""
kb_to_graph_sync.py — Batch sync fish_species_kb.yaml → species_graph.yaml

读取 f 项目的 fish_species_kb.yaml，对每个物种:
  1. 检查 species_graph.yaml 中是否已有该 species_id
  2. 若无 → 生成最小 graph 节点（id/name/chinese/aliases/family/conservation/variants）
  3. 输出 diff 报告

用法:
  python scripts/kb_to_graph_sync.py              # 仅报告差异
  python scripts/kb_to_graph_sync.py --apply       # 写入 species_graph.yaml
  python scripts/kb_to_graph_sync.py --dry-run     # 预览将要写入的内容

v1.0 — lit-search v3.0 配套工具
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parent.parent.parent
KB_PATH = WORKSPACE / "fish-ecology-assistant" / "config" / "fish_species_kb.yaml"
GRAPH_PATH = WORKSPACE / "cognitive-search-engine" / "config" / "species_graph.yaml"

# ── YAML loader (stdlib fallback) ──────────────────────────
try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> dict:
    """Load YAML, fall back to basic parser if pyyaml not installed."""
    if yaml:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        return _load_yaml_basic(path)


def _load_yaml_basic(path: Path) -> dict:
    """Minimal YAML parser for species_graph.yaml structure."""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    result = {"graph": {"species": [], "papers": [], "authors": [], "journals": [], "edges": []}}

    # Parse species nodes
    in_species = False
    current: dict = {}
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current and "id" in current:
                result["graph"]["species"].append(current)
            current = {"id": stripped.split("id:")[1].strip()}
            in_species = True
        elif in_species:
            if stripped.startswith("- ") and ":" not in stripped.split(":")[0] if ":" in stripped else False:
                continue
            if ":" in stripped and not stripped.startswith("- "):
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                current[key] = val
            elif stripped.startswith("  - "):
                key = list(current.keys())[-1] if current else "aliases"
                val = stripped[4:].strip().strip('"').strip("'")
                if key not in current:
                    current[key] = []
                if isinstance(current[key], list):
                    current[key].append(val)
            elif stripped == "" or stripped.startswith("- id:"):
                if current and "id" in current:
                    result["graph"]["species"].append(current)
                current = {}
                if stripped.startswith("- id:"):
                    current = {"id": stripped.split("id:")[1].strip()}
    if current and "id" in current:
        result["graph"]["species"].append(current)

    return result


def dump_yaml(data: dict, path: Path):
    """Write YAML, preserving structure."""
    if yaml:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    else:
        print("⚠️  pyyaml not installed; writing with basic serializer.", file=sys.stderr)
        _dump_yaml_basic(data, path)


def _dump_yaml_basic(data: dict, path: Path):
    """Append species nodes to existing graph file."""
    species_nodes = data.get("graph", {}).get("species", [])
    if not species_nodes:
        print("No new species to write.", file=sys.stderr)
        return

    indent = "  "
    lines = []
    for sp in species_nodes:
        lines.append(f"{indent}- id: {sp.get('id', '')}")
        for key in ["name", "chinese", "family", "genus", "conservation"]:
            if key in sp and sp[key]:
                lines.append(f"{indent}  {key}: {sp[key]}")
        for list_key in ["aliases", "variants"]:
            if list_key in sp and sp[list_key] and isinstance(sp[list_key], list):
                for item in sp[list_key]:
                    lines.append(f"{indent}  - {item}" if list_key in ["aliases"] else f"{indent}  - {item}")
        # Write aliases and variants as lists
        if "aliases" in sp and sp["aliases"]:
            lines.append(f"{indent}  aliases:")
            for a in sp["aliases"]:
                lines.append(f"{indent}  - {a}")
        if "variants" in sp and sp["variants"]:
            lines.append(f"{indent}  variants:")
            for v in sp["variants"]:
                lines.append(f"{indent}  - {v}")

    # Append after last species node
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find insertion point: after the last "  - id:" in the species section
    last_id_line = content.rfind("\n  - id:")
    if last_id_line == -1:
        # Fall back: append before first paper
        papers_marker = content.find("\npapers:")
        if papers_marker == -1:
            print("❌ Cannot find species or papers section in graph.", file=sys.stderr)
            return
        # Find end of last species entry
        insert_pos = papers_marker
    else:
        # Find end of the last species entry's block
        next_block = content.find("\n  - id:", last_id_line + 1)
        if next_block == -1:
            next_block = content.find("\npapers:", last_id_line)
        if next_block == -1:
            next_block = len(content)
        # Walk forward to find the start of next section or next species
        insert_pos = next_block

    new_content = content[:insert_pos] + "\n" + "\n".join(lines) + content[insert_pos:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Appended {len(species_nodes)} species to {path}")


# ── Core Logic ──────────────────────────────────────────────

def extract_species_id(name: str) -> str:
    """Convert scientific name to graph species_id format."""
    return name.replace(" ", "_")


def build_graph_node(kb_entry: dict) -> dict | None:
    """Convert a KB species entry into a minimal graph node."""
    sci = kb_entry.get("scientific", "")
    if not sci:
        return None

    node = {
        "id": extract_species_id(sci),
        "name": sci,
        "chinese": kb_entry.get("name", ""),
    }

    if kb_entry.get("aliases"):
        node["aliases"] = [a for a in kb_entry["aliases"] if a != kb_entry.get("name", "")]
    if kb_entry.get("family"):
        node["family"] = kb_entry["family"]
    if kb_entry.get("conservation"):
        node["conservation"] = kb_entry["conservation"]
    if kb_entry.get("synonyms"):
        node["variants"] = [s for s in kb_entry["synonyms"] if s != sci]

    return node


def sync(kb: dict, graph: dict, apply: bool = False, dry_run: bool = False) -> dict:
    """Main sync logic."""
    kb_species = kb.get("species", [])
    graph_species_ids = {s.get("id", "") for s in graph.get("graph", {}).get("species", []) if s}

    new_nodes = []
    skipped = []
    already_exist = []

    for entry in kb_species:
        if not isinstance(entry, dict):
            continue
        sci = entry.get("scientific", "")
        if not sci:
            continue

        sid = extract_species_id(sci)
        if sid in graph_species_ids:
            already_exist.append(sid)
            continue

        node = build_graph_node(entry)
        if node:
            new_nodes.append(node)
        else:
            skipped.append(entry.get("name", "?"))

    # Report
    print(f"\n{'='*60}")
    print(f"kb_to_graph_sync — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  KB 物种总数: {len(kb_species)}")
    print(f"  图谱已有:    {len(already_exist)}")
    print(f"  待新增:      {len(new_nodes)}")
    print(f"  跳过:        {len(skipped)}")
    print(f"{'='*60}")

    if already_exist:
        print(f"\n✅ 已在图谱中 ({len(already_exist)}):")
        for sid in sorted(already_exist):
            print(f"   {sid}")

    if new_nodes:
        print(f"\n🆕 待新增 ({len(new_nodes)}):")
        for n in new_nodes:
            variants_str = ", ".join(n.get("variants", [])[:3])
            print(f"   {n['id']} — {n['chinese']} ({n['name']})" +
                  (f" ← {variants_str}" if variants_str else ""))

    if skipped:
        print(f"\n⚠️  跳过 ({len(skipped)}):")
        for name in skipped:
            print(f"   {name}")

    # Apply
    if apply and new_nodes:
        data = {"graph": {"species": new_nodes}}
        dump_yaml(data, GRAPH_PATH)
    elif dry_run and new_nodes:
        print("\n── DRY RUN (preview of YAML to append) ──")
        for n in new_nodes:
            print(f"  - id: {n['id']}")
            print(f"    name: {n['name']}")
            print(f"    chinese: {n.get('chinese', '')}")
            if n.get('aliases'):
                print(f"    aliases:")
                for a in n['aliases']:
                    print(f"    - {a}")
            if n.get('family'):
                print(f"    family: {n['family']}")
            if n.get('variants'):
                print(f"    variants:")
                for v in n['variants']:
                    print(f"    - {v}")
            print()

    return {
        "total_kb": len(kb_species),
        "already_in_graph": len(already_exist),
        "new": len(new_nodes),
        "skipped": len(skipped),
    }


# ── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync fish_species_kb.yaml → species_graph.yaml")
    parser.add_argument("--apply", action="store_true", help="Write new species to species_graph.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be written")
    args = parser.parse_args()

    if not KB_PATH.exists():
        print(f"❌ KB not found: {KB_PATH}", file=sys.stderr)
        sys.exit(1)
    if not GRAPH_PATH.exists():
        print(f"❌ Graph not found: {GRAPH_PATH}", file=sys.stderr)
        sys.exit(1)

    kb = load_yaml(KB_PATH)
    graph = load_yaml(GRAPH_PATH)

    result = sync(kb, graph, apply=args.apply, dry_run=args.dry_run)

    if result["new"] > 0 and not args.apply and not args.dry_run:
        print("\n💡 提示: 使用 --apply 写入图谱, --dry-run 预览内容")
    elif result["new"] == 0:
        print("\n✅ KB 与图谱已完全同步，无需新增节点。")


if __name__ == "__main__":
    main()
