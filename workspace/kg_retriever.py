
"""Knowledge Graph Retriever for workspace. 
Usage: from workspace.kg_retriever import knowledge_graph_retrieve
result = knowledge_graph_retrieve("Coilia nasus")
print(result["matched"]["name"], result["same_family"])
"""
import yaml, os

_graph = None
def _load():
    global _graph
    if _graph: return _graph
    path = os.path.join(os.path.dirname(__file__), "..", "cognitive-search-engine", "config", "species_graph.yaml")
    with open(path, encoding="utf-8") as f:
        _graph = yaml.safe_load(f)
    return _graph

def retrieve(query, k=5):
    g = _load()
    species = g.get("graph",{}).get("species",[])
    by_name = {}
    by_family = {}
    for s in species:
        name = s.get("name","").lower()
        cn = s.get("chinese","")
        family = s.get("family","")
        entry = {"name":s.get("name",""),"chinese":cn,"family":family,"habitat":s.get("habitat",""),"variants":s.get("variants",[])}
        [by_name.__setitem__(v.lower(),entry) for v in [name,cn]+entry["variants"]]
        by_family.setdefault(family,[]).append(entry["name"])

    key = query.lower()
    matched = by_name.get(key, {})
    siblings = [s for s in by_family.get(matched.get("family",""),[]) if s.lower()!=key][:k] if matched else []
    return {"query":query, "matched":matched, "same_family":siblings, "graph_size":len(species)}
