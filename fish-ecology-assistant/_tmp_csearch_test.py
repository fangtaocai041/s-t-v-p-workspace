"""Quick test of c项目 import"""
import sys
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine")
sys.path.insert(0, r"D:\Reasonix\cognitive-search-engine\src")

import os
os.chdir(r"D:\Reasonix\cognitive-search-engine")

print("sys.path:", sys.path[:5])
try:
    from src.search_coordinator import search
    print("✅ import search_coordinator.search OK")
    from src.meso_agent import MesoAgent
    print("✅ import MesoAgent OK")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
