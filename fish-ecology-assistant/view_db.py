# -*- coding: utf-8 -*-
"""View the SanShengWanWu knowledge base — double-click or run: python view_db.py"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'species.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

print("=" * 70)
print("  SanShengWanWu Knowledge Base Viewer")
print("  File:", DB)
print("  Size:", f"{os.path.getsize(DB):,} bytes")
print("=" * 70)

# Species list
print("\n=== 30 Yangtze Fish Species ===")
hdr = f"{'Chinese':<10} {'Scientific':<45} {'Family':<25} {'Conservation'}"
print(hdr)
print("-" * 100)
for r in db.execute("SELECT chinese, scientific, family, conservation FROM species ORDER BY chinese"):
    cn = r['chinese'] or '?'
    sn = r['scientific'] or '?'
    fm = r['family'] or '?'
    cs = r['conservation'] or '-'
    print(f"{cn:<10} {sn:<45} {fm:<25} {cs}")

# Trait data
print("\n\n=== Trait Database ===")
tables_info = [
    ('traits_feeding', 'Feeding & Trophic'),
    ('traits_migration', 'Migration'),
    ('traits_conservation', 'Conservation Status'),
    ('traits_morphology', 'Morphology'),
]
for table, label in tables_info:
    rows = db.execute("SELECT * FROM " + table).fetchall()
    if rows:
        print("\n  >> " + label + " (" + str(len(rows)) + " records)")
        for r in rows:
            d = dict(r)
            sid = d.get('species_id', '?')
            for k, v in d.items():
                if k not in ('id', 'species_id') and v is not None and v != '':
                    print("      " + sid + "." + k + " = " + str(v))

# Literature
print("\n\n=== Literature Database ===")
for r in db.execute("SELECT * FROM literature ORDER BY year DESC"):
    yr = str(r['year'])
    sid = r['species_id'] or '?'
    title = (r['title'] or '')[:80]
    journal = r['journal'] or ''
    print("  [" + yr + "] " + sid)
    print("    " + title)
    if journal:
        print("    " + journal)

# Stats
print("\n\n=== Database Statistics ===")
for t in ['species', 'literature', 'aliases']:
    n = db.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
    print("  " + t + ": " + str(n))
for t in [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'traits_%'")]:
    n = db.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
    print("  " + t + ": " + str(n))
ns = db.execute("SELECT COUNT(*) FROM trait_sources").fetchone()[0]
print("  trait_sources: " + str(ns))

db.close()
