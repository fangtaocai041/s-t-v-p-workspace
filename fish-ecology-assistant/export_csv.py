"""Export all data to CSV files in data/reports/ — open with Excel."""
import sqlite3, csv, os

DB = r'D:\Reasonix\fish-ecology-assistant\data\species.db'
OUT = r'D:\Reasonix\fish-ecology-assistant\data\reports'
os.makedirs(OUT, exist_ok=True)

db = sqlite3.connect(DB)

tables = [r[0] for r in db.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' ORDER BY name"
)]

for table in tables:
    rows = db.execute(f"SELECT * FROM [{table}]").fetchall()
    if not rows:
        continue
    cols = [d[1] for d in db.execute(f"PRAGMA table_info([{table}])")]
    path = os.path.join(OUT, f"{table}.csv")
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for row in rows:
            w.writerow(row)
    print(f"  {table}.csv ({len(rows)} rows)")

db.close()
print(f"\nDone! Files in: {OUT}")
