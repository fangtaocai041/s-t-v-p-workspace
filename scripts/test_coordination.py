"""
Coordination test — verify all layers work together across projects.

Tests:
  1. Catalog loads from cognitive-search-engine/config/
  2. Domain scoring with context rules
  3. Graph routing with health awareness
  4. Cross-project import from sibling projects
  5. Tendril health integration with eon-core
  6. End-to-end: query → ranked DBs → tool resolution
"""

import sys
from pathlib import Path

# Ensure cognitive-search-engine/src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cognitive-search-engine" / "src"))

from catalog_loader import (
    load_catalog,
    score_domains,
    graph_route,
    load_tendril_health,
    compare_routing,
    resolve_tools,
)

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}  — {detail}")


# ── Test 1: Catalog loading ──
print("1. Catalog Loading")
catalog = load_catalog()
check("catalog loaded", catalog is not None and "domains" in catalog)
check("8 domains present", len(catalog["domains"]) == 8,
      f"got {len(catalog.get('domains', {}))}")
check("topology present", "topology" in catalog)
check("tendril_map present", "tendril_map" in catalog["topology"])
check("context_rules present", "context_rules" in catalog["topology"])
total_dbs = sum(len(d.get("databases", [])) for d in catalog["domains"].values())
check(f"35+ databases ({total_dbs})", total_dbs >= 35,
      f"only {total_dbs} found")

# ── Test 2: Domain scoring ──
print("\n2. Domain Scoring")
scores = dict(score_domains(catalog, "鳤的线粒体基因组测序"))
check("genetics leads for genetics query",
      scores.get("molecular_genetics", 0) > scores.get("fisheries_ichthyology", 0),
      f"genetics={scores.get('molecular_genetics', 0):.3f} vs fisheries={scores.get('fisheries_ichthyology', 0):.3f}")

scores2 = dict(score_domains(catalog, "PFAS对鱼类的毒性效应"))
check("toxicology dominates PFAS+fish query",
      scores2.get("toxicology", 0) > 0.2 and scores2.get("fisheries_ichthyology", 0) < 0.1,
      f"tox={scores2.get('toxicology', 0):.3f} fish={scores2.get('fisheries_ichthyology', 0):.3f}")

scores3 = dict(score_domains(catalog, "深度学习transformer模型优化"))
check("AI/ML only for pure AI query",
      "ai_ml" in scores3 and len(scores3) <= 2,
      f"domains={list(scores3.keys())}")

# ── Test 3: Graph routing ──
print("\n3. Graph Routing")
dbs = graph_route(catalog, "鳤的遗传多样性")
check("returns top-8", len(dbs) <= 8)
check("scores present", all("_graph_score" in d for d in dbs))
check("genetics DBs rank high",
      any("ncbi" in d["id"] for d in dbs[:3]),
      f"top 3: {[d['id'] for d in dbs[:3]]}")

# ── Test 4: Health-aware routing ──
print("\n4. Tendril Health Integration")
health_dbs = graph_route(catalog, "鳤的遗传多样性", health_aware=True)
check("health_aware returns tendril flags",
      any("_tendril" in d for d in health_dbs))
tendril_health = load_tendril_health()
check("tendril health loaded from eon-core",
      len(tendril_health) >= 7,
      f"got {len(tendril_health)} tendrils")
check("pubmed tendril found",
      "tendril_pubmed" in tendril_health)

# Database with tendril → should show 'healthy', without → 'unknown'
pubmed_in_result = [d for d in health_dbs if d["id"] == "pubmed"]
if pubmed_in_result:
    check("pubmed marked healthy",
          pubmed_in_result[0].get("_tendril") == "healthy",
          f"got {pubmed_in_result[0].get('_tendril')}")

# ── Test 5: Tool resolution ──
print("\n5. Tool Resolution")
db = next((d for d in dbs if d["id"] == "pubmed"), None)
if db:
    tools = resolve_tools(db, "Ochetobius elongatus")
    check("pubmed resolves to ncbi tools",
          any("ncbi" in t["tool"] for t in tools),
          f"tools={[t['tool'] for t in tools]}")

# ── Test 6: Cross-project import ──
print("\n6. Cross-project Access")
# Simulate what fish-ecology-assistant would do
catalog_path = Path(__file__).resolve().parent.parent / "cognitive-search-engine" / "config" / "database_catalog.yaml"
check("catalog accessible from workspace root",
      catalog_path.exists(),
      str(catalog_path))

# ── Summary ──
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed ({passed+failed} total)")
if failed == 0:
    print("All coordination tests passed ✅")
else:
    print(f"FAILURES DETECTED ❌")
    sys.exit(1)
