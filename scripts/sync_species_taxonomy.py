#!/usr/bin/env python3
"""
物种分类变更同步脚本 — c项目(species_graph.yaml) -> f项目(SQLite)

同步内容:
  taxonomy_change  — 分类学变更记录（属级变更、同义名确认）
  variants        — 学名变体（拼写变体、异名）

用法:
  python scripts/sync_species_taxonomy.py          # 执行同步
  python scripts/sync_species_taxonomy.py --check  # 只检查，不写入
  python scripts/sync_species_taxonomy.py --status # 查看统计
"""
import sys, json
from pathlib import Path

_REASONIX = Path(__file__).resolve().parent.parent  # D:\Reasonix
sys.path.insert(0, str(_REASONIX))

import yaml

# Paths
C_GRAPH = _REASONIX / "cognitive-search-engine" / "config" / "species_graph.yaml"
F_DB = _REASONIX / "fish-ecology-assistant" / "data" / "species.db"


def load_yaml_data():
    data = yaml.safe_load(C_GRAPH.read_text(encoding="utf-8"))
    species = {}
    for s in data.get("graph", {}).get("species", []):
        sci = s.get("name", "").lower()
        if sci:
            species[sci] = {
                "scientific": s["name"],
                "chinese": s.get("chinese", ""),
                "taxonomy_change": s.get("taxonomy_change"),
                "variants": s.get("variants", []),
                "aliases": s.get("aliases", []),
                "conservation": s.get("conservation", ""),
                "family": s.get("family", ""),
            }
    return species


def get_db():
    import sqlite3
    conn = sqlite3.connect(str(F_DB))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns(conn):
    existing = {r[1] for r in conn.execute("PRAGMA table_info(species)").fetchall()}
    added = []
    if "taxonomy_change" not in existing:
        conn.execute("ALTER TABLE species ADD COLUMN taxonomy_change TEXT DEFAULT ''")
        added.append("taxonomy_change")
    if "variants" not in existing:
        conn.execute("ALTER TABLE species ADD COLUMN variants TEXT DEFAULT ''")
        added.append("variants")
    if added:
        conn.commit()
        print(f"  Added columns: {', '.join(added)}")
    return added


def status_report(conn, c_species):
    f_has_tc = conn.execute(
        "SELECT COUNT(*) FROM species WHERE taxonomy_change IS NOT NULL AND taxonomy_change != ''"
    ).fetchone()[0]
    f_has_var = conn.execute(
        "SELECT COUNT(*) FROM species WHERE variants IS NOT NULL AND variants != ''"
    ).fetchone()[0]

    c_has_tc = sum(1 for s in c_species.values() if s["taxonomy_change"])
    c_has_var = sum(1 for s in c_species.values() if s["variants"])

    print(f"\n{'='*60}")
    print("Taxonomy sync status")
    print(f"{'='*60}")
    print(f"c project (species_graph.yaml) — {len(c_species)} species")
    print(f"  with taxonomy_change: {c_has_tc}")
    print(f"  with variants:        {c_has_var}")
    print(f"f project (species.db) — {conn.execute('SELECT COUNT(*) FROM species').fetchone()[0]} species")
    print(f"  with taxonomy_change: {f_has_tc}")
    print(f"  with variants:        {f_has_var}")

    if c_has_tc > f_has_tc:
        print("\nPending taxonomy_change sync:")
        for sci, s in sorted(c_species.items()):
            if s["taxonomy_change"]:
                row = conn.execute(
                    "SELECT scientific, chinese, taxonomy_change FROM species WHERE LOWER(scientific)=?",
                    (sci,)
                ).fetchone()
                if row:
                    existing_tc = row["taxonomy_change"] or ""
                    if not existing_tc:
                        print(f"  -> {s['chinese']:8s} | {s['scientific']:35s} | tc={s['taxonomy_change']}")

    if c_has_var > f_has_var:
        print("\nPending variants sync:")
        for sci, s in sorted(c_species.items()):
            if s["variants"]:
                row = conn.execute(
                    "SELECT scientific, chinese, variants FROM species WHERE LOWER(scientific)=?",
                    (sci,)
                ).fetchone()
                if row:
                    existing_var = row["variants"] or ""
                    if not existing_var:
                        print(f"  -> {s['chinese']:8s} | {s['scientific']:35s} | variants={s['variants']}")


def sync(conn, c_species, dry_run=False):
    updated_tc = 0
    updated_var = 0
    matched = 0

    for sci, s in sorted(c_species.items()):
        row = conn.execute(
            "SELECT scientific, chinese, taxonomy_change, variants FROM species WHERE LOWER(scientific)=?",
            (sci,)
        ).fetchone()

        if not row and s["chinese"]:
            row = conn.execute(
                "SELECT scientific, chinese, taxonomy_change, variants FROM species WHERE chinese=?",
                (s["chinese"],)
            ).fetchone()

        if row:
            matched += 1
            if s["taxonomy_change"]:
                existing = row["taxonomy_change"] or ""
                new_val = json.dumps(s["taxonomy_change"], ensure_ascii=False)
                if existing != new_val:
                    if not dry_run:
                        conn.execute(
                            "UPDATE species SET taxonomy_change=? WHERE scientific=?",
                            (new_val, row["scientific"])
                        )
                    updated_tc += 1

            if s["variants"]:
                existing = row["variants"] or ""
                new_val = json.dumps(s["variants"], ensure_ascii=False)
                if existing != new_val:
                    if not dry_run:
                        conn.execute(
                            "UPDATE species SET variants=? WHERE scientific=?",
                            (new_val, row["scientific"])
                        )
                    updated_var += 1

    if not dry_run:
        conn.commit()

    print(f"\nSync result:")
    print(f"  Matched:       {matched}/{len(c_species)}")
    print(f"  taxonomy_change updates: {updated_tc}")
    print(f"  variants updates:        {updated_var}")
    if dry_run:
        print(f"  (dry-run mode)")
    return updated_tc + updated_var


def main():
    args = set(sys.argv[1:])
    dry_run = "--check" in args
    show_status = "--status" in args

    print(f"Reading c project: {C_GRAPH.name}")
    c_species = load_yaml_data()
    print(f"  -> {len(c_species)} species entries")

    print(f"Connecting f project: {F_DB.name}")
    conn = get_db()
    ensure_columns(conn)

    if show_status or dry_run:
        status_report(conn, c_species)

    if not show_status:
        sync(conn, c_species, dry_run=dry_run)

    conn.close()
    print("\nDone")


if __name__ == "__main__":
    main()
