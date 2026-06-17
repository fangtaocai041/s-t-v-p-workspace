"""Raw database dump — shows every table's data directly."""
import sqlite3

db = sqlite3.connect(r'D:\Reasonix\fish-ecology-assistant\data\species.db')

# Get all tables
tables = [r[0] for r in db.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)]

for table in tables:
    rows = db.execute(f"SELECT * FROM [{table}]").fetchall()
    if not rows:
        continue
    
    cols = [d[1] for d in db.execute(f"PRAGMA table_info([{table}])")]
    print(f"\n{'='*80}")
    print(f"  {table}  ({len(rows)} rows, {len(cols)} cols)")
    print(f"{'='*80}")
    print(" | ".join(cols))
    print("-"*80)
    for row in rows:
        print(" | ".join(str(v) if v is not None else "-" for v in row))

db.close()
