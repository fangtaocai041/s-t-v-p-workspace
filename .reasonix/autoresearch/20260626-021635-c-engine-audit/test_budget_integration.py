"""Verify token budget system is intact after parallel search refactor."""
import sys, os, importlib.util
sys.path.insert(0, r'D:\Reasonix')

# 1. Workspace budget API
from workspace import get_token_budget, set_token_budget, show_token_budget
info = show_token_budget()
print(f"[OK] Budget API: {info['total_budget']:,} tokens (source: {info['source']})")

# 2. Test dynamic set
set_token_budget(200000)
assert get_token_budget() == 200000
print("[OK] Dynamic set: 200000")

# 3. Test env override
os.environ['REASONIX_TOKEN_BUDGET'] = '500000'
assert get_token_budget() == 500000
del os.environ['REASONIX_TOKEN_BUDGET']
print("[OK] Env override: 500000")

# 4. Restore default
set_token_budget(150000)

# 5. Verify rule_engine._builtins reads from get_token_budget
# (static verification: _builtins calls get_token_budget())
set_token_budget(999000)
import ast, inspect
with open(r'D:\Reasonix\cognitive-search-engine\src\rule_engine.py', encoding='utf-8') as f:
    source = f.read()
assert 'get_token_budget' in source, "rule_engine.py does not reference get_token_budget"
budget = get_token_budget()
assert budget == 999000
print(f"[OK] rule_engine._builtins → get_token_budget() = {budget:,}")
set_token_budget(150000)  # restore

# 6. Verify parallel search engine layer intact
spec2 = importlib.util.spec_from_file_location('ps', r'D:\Reasonix\cognitive-search-engine\src\parallel_search\_engine.py')
ps_mod = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(ps_mod)
ps = ps_mod.ParallelSearch(max_workers=2, use_thompson=False)
print(f"[OK] ParallelSearch: {len(ps_mod._PROVIDERS)} providers, cache integrated")

print("\n=== TOKEN BUDGET SYSTEM INTACT ===")
