"""Call c项目 for 珠星三块鱼 — fixed version"""
import sys, os, json
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine")
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine\src")
os.chdir(r"D:\Reasonix\cognitive-search-engine")

from src.unified_search import coordinated_search

print("=== coordinated_search('珠星三块鱼', limit=20) ===")
result = coordinated_search("珠星三块鱼", limit=20)

print(f"\n物种: {result.species_name}")
print(f"学名: {result.scientific_name}")
print(f"中文: {result.chinese_name}")
print(f"保护: {result.conservation}")
print(f"模式: {result.mode}")
print(f"变体: {result.all_variants}")
print(f"总论文: {result.total_papers}")
print(f"论文数: {len(result.papers)}")

# Print categories
if result.categories:
    print(f"\n分类: {len(result.categories)} 个方向")
    for cat, papers in result.categories.items():
        print(f"  [{cat}] {len(papers)} 篇")

# Print first 5 papers
print("\n--- 前5篇论文 ---")
for i, p in enumerate(result.papers[:5]):
    print(f"\n  #{i+1}: {p.get('title','?')}")
    print(f"      作者: {p.get('authors','?')[:80]}")
    print(f"      期刊: {p.get('journal','?')} ({p.get('year','?')})")
    print(f"      DOI: {p.get('doi','?')}")
    if p.get('credibility_score') is not None:
        print(f"      可信度: {p['credibility_score']}")

# Print full JSON for reference
print("\n=== 完整JSON输出 (截断) ===")
json_str = json.dumps({
    "species_name": result.species_name,
    "scientific_name": result.scientific_name,
    "chinese_name": result.chinese_name,
    "mode": result.mode,
    "total_papers": result.total_papers,
    "categories": {k: len(v) for k, v in result.categories.items()} if result.categories else {},
    "paper_titles": [p.get("title","")[:60] for p in result.papers[:10]],
}, ensure_ascii=False, indent=2)
print(json_str)
