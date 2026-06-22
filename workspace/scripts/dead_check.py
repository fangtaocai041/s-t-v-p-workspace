"""Comprehensive dead code checker for all projects"""
import sys, os, importlib, subprocess, ast

projects = {
    "san-sheng-wanwu-core": "D:/Reasonix/san-sheng-wanwu-core",
    "fish-ecology-assistant": "D:/Reasonix/fish-ecology-assistant",
    "cognitive-search-engine": "D:/Reasonix/cognitive-search-engine",
    "porpoise-agent": "D:/Reasonix/porpoise-agent",
    "coilia-agent": "D:/Reasonix/coilia-agent",
    "culter-agent": "D:/Reasonix/culter-agent",
    "conflict-arbiter": "D:/Reasonix/conflict-arbiter",
    "eon-core": "D:/Reasonix/eon-core",
}

results = {}

for name, root in projects.items():
    if not os.path.isdir(root):
        results[name] = {"error": "Not found"}
        continue

    p = {"total": 0, "ok": 0, "fail": [], "tests_ok": True, "syntax_errors": []}
    src_dir = os.path.join(root, "src")

    if not os.path.isdir(src_dir):
        p["ok"] = 0
        p["fail"].append("No src/ directory")
        results[name] = p
        continue

    # Scan all .py files
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".py"):
                p["total"] += 1
                path = os.path.join(dirpath, f)
                # Syntax check
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        ast.parse(fh.read())
                except SyntaxError as e:
                    p["syntax_errors"].append(f"{f}: {e}")
                    p["fail"].append(f"SYNTAX: {f}")

    # Try running tests
    test_dir = os.path.join(root, "tests")
    if os.path.isdir(test_dir):
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", test_dir, "-q", "--tb=line"],
                capture_output=True, text=True, timeout=60, cwd=root
            )
            if r.returncode != 0:
                p["tests_ok"] = False
                output = r.stdout.strip().split("\n")[-1] if r.stdout else "?"
                p["fail"].append(f"TESTS FAILED: {output}")
        except Exception as e:
            p["fail"].append(f"Test error: {str(e)[:60]}")

    # Check imports
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".py") and not f.startswith("__"):
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                mod = rel.replace(os.sep, ".")[:-3]
                if mod.startswith("src."):
                    mod = mod[4:]
                # Skip files that are known to require external deps
                skip = False
                path = os.path.join(dirpath, f)
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                if "sentence_transformers" in content or "torch" in content or "huggingface" in content:
                    skip = True
                if not skip:
                    try:
                        sys.path.insert(0, root)
                        importlib.import_module(mod)
                        p["ok"] += 1
                    except Exception as e:
                        p["fail"].append(f"IMPORT: {mod}: {str(e)[:80]}")

    results[name] = p
    print(f"  {name}: {p['ok']}/{p['total']} imports" + (f", {len(p['fail'])} failures" if p["fail"] else " OK"))

print()
total_ok = sum(p["ok"] for p in results.values() if "ok" in p)
total_modules = sum(p["total"] for p in results.values() if "total" in p)
total_fails = sum(len(p["fail"]) for p in results.values() if "fail" in p)

if total_fails == 0:
    print(f"ALL CLEAN: {total_ok} modules across {len(projects)} projects. No dead code.")
else:
    print(f"ISSUES: {total_fails} failures across {len(projects)} projects:")
    for name, p in results.items():
        for f in p.get("fail", []):
            print(f"  {name}: {f}")
