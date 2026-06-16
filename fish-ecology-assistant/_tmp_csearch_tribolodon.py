"""Call c项目 (cognitive-search-engine) to search for 珠星三块鱼"""
import sys, json, os

sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine")
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine\src")

os.chdir(r"D:\Reasonix\cognitive-search-engine")

from src.search_coordinator import search

result = search("珠星三块鱼")

if hasattr(result, "summary"):
    print(result.summary())
elif hasattr(result, "model_dump"):
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2, default=str))
elif hasattr(result, "dict"):
    print(json.dumps(result.dict(), ensure_ascii=False, indent=2, default=str))
else:
    print(str(result))
