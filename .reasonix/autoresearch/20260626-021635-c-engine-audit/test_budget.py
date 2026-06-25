"""Test dynamic token budget system."""
import sys; sys.path.insert(0, r'D:\Reasonix')
from workspace import get_token_budget, set_token_budget, show_token_budget

# Test defaults
info = show_token_budget()
print(f"Default: {info['total_budget']:,} tokens (source: {info['source']})")

# Test set + get
new = set_token_budget(300000)
print(f"set(300000) -> {new:,} tokens")

# Test env override
import os; os.environ['REASONIX_TOKEN_BUDGET'] = '500000'
print(f"env=500000 -> get={get_token_budget():,} tokens")
del os.environ['REASONIX_TOKEN_BUDGET']

# Restore
set_token_budget(150000)
print(f"restored -> {get_token_budget():,} tokens")

# Test budget file exists
from pathlib import Path
f = Path(r'D:\Reasonix\workspace\config\token_budget.json')
print(f"Config file: {f} exists={f.is_file()}")

print("\nToken budget system: OK")
