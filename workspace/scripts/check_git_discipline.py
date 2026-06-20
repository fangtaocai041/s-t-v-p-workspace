"""check_git_discipline.py — Git discipline check (规则6)"""
import sys, os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
issues = []

# Check gitignore exists
gitignore = os.path.join(root, ".gitignore")
if os.path.isfile(gitignore):
    with open(gitignore, "r") as f:
        content = f.read()
    if ".reasonix" not in content:
        issues.append(".reasonix/ not in .gitignore (may contain API keys)")
    if "data/*.db" not in content:
        issues.append("data/*.db not in .gitignore")
    if ".env" not in content:
        issues.append(".env not in .gitignore")
    print("  [OK] .gitignore exists")
else:
    print("  [SKIP] .gitignore not in workspace root (submodules have their own)")

# Check no secrets in staged files
import subprocess
try:
    r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                       capture_output=True, text=True, cwd=root)
    changed = [f for f in r.stdout.strip().split("\n") if f]
    for f in changed:
        if f.endswith((".env", "*.key", "*.pem", "*.crt")):
            issues.append(f"Sensitive file in staged: {f}")
except Exception:
    pass  # CI may not have full git context

if issues:
    print(f"  Issues: {len(issues)}")
    for i in issues:
        print(f"    {i}")
else:
    print("  [OK] No issues found")

sys.exit(0 if not issues else 1)
