"""c项目快速测试 — 图谱直读 + 轻量搜索"""
import sys, os, json, time
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine")
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine\src")
os.chdir(r"D:\Reasonix\cognitive-search-engine")

# 1) 直接读 species_graph.yaml
import yaml
yaml_path = r"D:\Reasonix\cognitive-search-engine\config\species_graph.yaml"
with open(yaml_path, encoding="utf-8") as f:
    g = yaml.safe_load(f)

species_entries = g.get("species", {})
print(f"图谱中共 {len(species_entries)} 个物种记录")

# 查找 tribolodon 相关
for sid, sdata in species_entries.items():
    name = sdata.get("name", "")
    sci = sdata.get("scientific", "")
    aliases = sdata.get("aliases", [])
    if any(kw in sid.lower() or kw in name or kw in sci.lower() or kw in str(aliases).lower()
           for kw in ["tribolodon", "三块", "珠星", "brandti", "pseudaspius", "ugui"]):
        print(f"\n✅ 找到: {sid}")
        print(f"   中文: {name}")
        print(f"   学名: {sci}")
        print(f"   别名: {aliases}")
        papers = sdata.get("papers", [])
        print(f"   论文数: {len(papers)}")
        for i, p in enumerate(papers[:5]):
            print(f"   #{i+1}: {p.get('title','?')[:70]}")
        break
else:
    print("❌ 图谱中无 tribolodon / 三块鱼 记录")

# 2) 尝试直接 import parallel_search 做轻量搜索
print("\n\n=== 尝试轻量 ParallelSearch ===")
try:
    from src.parallel_search import ParallelSearch
    engine = ParallelSearch()
    print(f"ParallelSearch 初始化成功，引擎: {dir(engine)}")
except Exception as e:
    print(f"ParallelSearch import: {e}")

# 3) 直接读取 search_rules.yaml 看配置
rules_path = r"D:\Reasonix\cognitive-search-engine\config\search_rules.yaml"
with open(rules_path, encoding="utf-8") as f:
    rules = yaml.safe_load(f)
print(f"\n搜索规则中物种配置: {len(rules.get('species', {}))} 条")
print(json.dumps({k: v for k, v in rules.items() if k != 'species'}, ensure_ascii=False)[:500])
