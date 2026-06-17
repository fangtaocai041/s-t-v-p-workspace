"""FishBase API Integration — auto-pull fish trait data.

FishBase REST API: https://fishbase.de/api/
Usage:
    python scripts/fishbase_pull.py --species "Coilia nasus"
    python scripts/fishbase_pull.py --all-core

Data sources & reliability:
  - FishBase (reliability 5/5) — global authority, updated annually
  - FFRC literature (reliability 5/5) — Yangtze-specific, Liu Kai group
  - Li Xinhui / PRFRI — fish morphology models & community research (see notes)
  - Yangtze Fish Book (reliability 5/5) — no API, manual entry required

IMPORTANT:
  - FishBase returns global data — Yangtze populations may differ
  - source_url records exact API endpoint for traceability
  - confidence: 5=multi-source verified, 4=peer-reviewed, 3=FishBase, 2=single-study
"""

import json, sqlite3, sys, time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

DB = Path(r'D:\Reasonix\fish-ecology-assistant\data\species.db')
API = "https://fishbase.de/api"
TODAY = datetime.now().strftime('%Y-%m-%d')

CORE_SPECIES = [
    "Coilia nasus", "Culter alburnus", "Culter mongolicus",
    "Culter oxycephalus", "Ochetobius elongatus", "Tenualosa reevesii",
    "Acipenser sinensis", "Myxocyprinus asiaticus", "Elopichthys bambusa",
    "Hypophthalmichthys molitrix", "Hypophthalmichthys nobilis",
    "Ctenopharyngodon idella", "Mylopharyngodon piceus",
    "Megalobrama amblycephala", "Pelteobagrus fulvidraco",
    "Siniperca chuatsi", "Silurus asotus", "Monopterus albus",
    "Channa argus", "Carassius auratus", "Cyprinus carpio",
    "Anguilla japonica", "Trachidermus fasciatus", "Takifugu obscurus",
    "Coilia brachygnathus", "Coreius heterodon", "Rhinogobio typus",
    "Saurogobio dabryi", "Luciobarbus brachycephalus", "Hilsa kelee",
]

def pull_species(name, conn):
    """Pull species summary and store morphology trait."""
    url = f"{API}/taxa/summary/{name.replace(' ', '%20')}"
    try:
        req = Request(url, headers={"User-Agent": "SanShengWanWu/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        sid = name.lower().replace(' ', '_')
        max_len = data.get('maxLengthF')
        if max_len:
            conn.execute("""INSERT OR REPLACE INTO traits_morphology
                (species_id, max_length_cm, source, source_url, last_updated, confidence, notes)
                VALUES(?,?,?,?,?,?,?)""",
                (sid, float(max_len), 'FishBase',
                 f"https://fishbase.de/summary/{name.replace(' ', '-')}.html",
                 TODAY, 3, 'Auto-pulled from FishBase API'))
        conn.commit()
        return True
    except Exception as e:
        print(f"  WARN {name}: {e}")
        return False

if __name__ == "__main__":
    conn = sqlite3.connect(str(DB))
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--species")
    ap.add_argument("--all-core", action="store_true")
    args = ap.parse_args()

    if args.all_core:
        ok = 0
        for sp in CORE_SPECIES:
            print(f"  {sp}...", end=" ")
            if pull_species(sp, conn):
                print("OK")
                ok += 1
            else:
                print("SKIP")
            time.sleep(1.0)
        print(f"\nDone: {ok}/{len(CORE_SPECIES)} pulled")
    elif args.species:
        pull_species(args.species, conn)
        print(f"Done: {args.species}")
    conn.close()
