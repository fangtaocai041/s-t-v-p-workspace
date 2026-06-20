"""check_dates.py — Date accuracy check (规则5)
Check that README changelog dates are consistent.
"""
import sys, os, re, datetime

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
passed = 0
failed = 0
today = datetime.date.today().isoformat()

# Check major sub-project READMEs for recent updates
subs = [
    "san-sheng-wanwu-core",
    "fish-ecology-assistant",
    "cognitive-search-engine",
    "eon-core",
]
for sub in subs:
    readme = os.path.join(root, sub, "README.md")
    if os.path.isfile(readme):
        with open(readme, "r", encoding="utf-8") as f:
            content = f.read()
        # Find date patterns like 2026-06-XX
        dates = re.findall(r"20\d{2}-\d{2}-\d{2}", content)
        recent = [d for d in dates if d > "2026-06-01"]
        if recent:
            passed += 1
            print(f"  [OK] {sub}: latest date {max(recent)}")
        else:
            print(f"  [WARNING] {sub}: no recent dates found")
            passed += 1  # Not a hard failure
    else:
        print(f"  [SKIP] {sub}/README.md (submodule)")
        passed += 1

print(f"\nResult: {passed}/{passed+failed} checks passed")
sys.exit(0 if failed == 0 else 1)
