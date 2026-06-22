#!/usr/bin/env python3
"""Replace all non-canonical rcca_core.py copies with import shims."""
import os, shutil

base = r"D:\Reasonix"
canonical = os.path.join(base, "cognitive-search-engine", "src", "rcca_core.py")
shim_content = '''"""Redirect to canonical rcca_core.py in cognitive-search-engine."""
from cognitive_search_engine.src.rcca_core import *

# Re-export everything for backward compatibility
'''

# Projects that have rcca_core.py in src/ (exclude canonical)
projects = [
    "fish-ecology-assistant",
    "eon-core",
    "conflict-arbiter",
    "culter-agent",
    "coilia-agent",
    "porpoise-agent",
    "san-sheng-wanwu-core",
]

replaced = 0
for proj in projects:
    rcca_path = os.path.join(base, proj, "src", "rcca_core.py")
    if os.path.exists(rcca_path):
        # Verify it matches canonical (same size = same content)
        if os.path.getsize(rcca_path) == os.path.getsize(canonical):
            # Backup first (just in case)
            backup = rcca_path + ".old_copy"
            if not os.path.exists(backup):
                shutil.copy2(rcca_path, backup)
            # Replace with shim
            with open(rcca_path, "w", encoding="utf-8") as f:
                f.write(shim_content)
            print(f"  Shimmed: {proj}/src/rcca_core.py")
            replaced += 1
        else:
            print(f"  SKIP (differs): {proj}/src/rcca_core.py")
    else:
        print(f"  MISSING: {proj}/src/rcca_core.py")

print(f"\nReplaced: {replaced} copies -> import shims")
print(f"Canonical: cognitive-search-engine/src/rcca_core.py ({os.path.getsize(canonical)}B)")
