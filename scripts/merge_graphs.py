#!/usr/bin/env python3
"""merge_graphs.py — Merge root config/species_graph.yaml into cognitive version."""
import yaml
from collections import Counter
from pathlib import Path

ROOT = Path("config/species_graph.yaml")
COG = Path("cognitive-search-engine/config/species_graph.yaml")

# Load
with open(ROOT, encoding="utf-8") as f:
    root = yaml.safe_load(f)
with open(COG, encoding="utf-8") as f:
    cog = yaml.safe_load(f)

# Map root species tags → cognitive species_id
TAG_MAP = {
    "Pseudaspius_hakonensis": "Pseudaspius_hakonensis",
    "Tribolodon_hakonensis": "Pseudaspius_hakonensis",
    "Tribolodon_brandti": "Tribolodon_brandti",
    "珠星三块鱼": "Pseudaspius_hakonensis",
}

# Collect cognitive DOIs and titles
cog_dois = {p.get("doi", "") for p in cog["graph"]["papers"] if p.get("doi")}
cog_titles = {p.get("title", "")[:80].lower().strip() for p in cog["graph"]["papers"]}

# Find new papers
new_papers = []
stats = Counter()
for p in root["graph"]["papers"]:
    species_tags = p.get("species", [])
    # Skip test papers
    if "test" in species_tags:
        continue
    # Map to cognitive species IDs
    mapped = []
    for tag in species_tags:
        if tag in TAG_MAP:
            mapped.append(TAG_MAP[tag])
    if not mapped:
        continue
    p["species"] = list(set(mapped))
    p["source"] = "merge_from_root"

    # Check if already in cognitive
    doi = p.get("doi", "")
    title = p.get("title", "")[:80].lower().strip()
    if doi in cog_dois or (not doi and title in cog_titles):
        continue

    new_papers.append(p)
    for s in mapped:
        stats[s] += 1

print(f"Root papers: {len(root['graph']['papers'])}")
print(f"Cog papers (before): {len(cog['graph']['papers'])}")
print(f"New to merge: {len(new_papers)}")
for s, c in stats.most_common():
    print(f"  {s}: +{c}")
years = [p.get("year") or 0 for p in new_papers]
print(f"Year range: {min(years)}-{max(years)}")

# Merge
cog["graph"]["papers"].extend(new_papers)

# Deduplicate species nodes (remove Pseudaspius_hakonensis duplicates)
seen_ids = set()
unique_species = []
for sp in cog["graph"]["species"]:
    sid = sp.get("id", "")
    if sid not in seen_ids:
        seen_ids.add(sid)
        unique_species.append(sp)
cog["graph"]["species"] = unique_species

print(f"\nAfter merge: {len(cog['graph']['species'])} species, {len(cog['graph']['papers'])} papers")

# Save
with open(COG, "w", encoding="utf-8") as f:
    yaml.safe_dump(cog, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=200)

print(f"✅ Saved to {COG}")
