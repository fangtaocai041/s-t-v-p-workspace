"""Call c项目 for 珠星三块鱼 — with timeout handling"""
import sys, os, json, traceback

sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine")
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine\src")
os.chdir(r"D:\Reasonix\cognitive-search-engine")

# 1) Graph lookup first — 0 token cost
try:
    from src.graph_updater import SpeciesGraph
    graph = SpeciesGraph()
    graph.load()
    entry = graph.get_species("tribolodon_brandti")
    if entry:
        print("=== 图谱记录 ===")
        print(json.dumps(entry, ensure_ascii=False, indent=2, default=str))
    else:
        print("图谱无 tribolodon_brandti 记录")
        # Try searching by alias
        for sid, data in graph._data.items():
            if "tribolodon" in str(data).lower() or "三块" in str(data):
                print(f"✅ Found by alias: {sid}")
                print(json.dumps(data, ensure_ascii=False, indent=2, default=str)[:2000])
except Exception as e:
    print(f"Graph lookup: {e}")
    traceback.print_exc()

print("\n" + "="*60)

# 2) Check species_graph.yaml directly
import yaml
try:
    yaml_path = r"D:\Reasonix\cognitive-search-engine\config\species_graph.yaml"
    with open(yaml_path, encoding="utf-8") as f:
        g = yaml.safe_load(f)
    species = g.get("species", {})
    found = {k: v for k, v in species.items() if "tribolodon" in str(k).lower() or "三块" in str(v.get("name",""))}
    if found:
        print(f"\n=== species_graph.yaml 中找到 {len(found)} 条 ===")
        for kid, kdata in found.items():
            print(f"  {kid}: {json.dumps(kdata, ensure_ascii=False)[:500]}")
    else:
        print("\nspecies_graph.yaml 中无 tribolodon 记录")
except Exception as e:
    print(f"YAML read: {e}")

print("\n" + "="*60)

# 3) Run search with short timeout via unified_search
try:
    from src.unified_search import coordinated_search
    print("\n=== 调用 coordinated_search('珠星三块鱼') ===")
    result = coordinated_search("珠星三块鱼", genus="Tribolodon", species="brandti")
    
    # Print summary
    if hasattr(result, "summary"):
        print(result.summary())
    elif isinstance(result, dict):
        # Print key fields
        for k in ["total_papers", "papers", "categories", "directions", "error"]:
            if k in result:
                val = result[k]
                if isinstance(val, list) and len(val) > 20:
                    print(f"{k}: [{len(val)} items, showing first 3]")
                    for item in val[:3]:
                        print(f"  - {json.dumps(item, ensure_ascii=False)[:200]}")
                else:
                    print(f"{k}: {json.dumps(val, ensure_ascii=False)[:1000]}")
    else:
        print(str(result)[:2000])
except Exception as e:
    print(f"Search call failed: {e}")
    traceback.print_exc()
