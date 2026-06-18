#!/usr/bin/env python3
"""verify_architecture.py — fish-ecology-assistant 架构完整性验证。

检查: 模块可导入、关键文件存在、测试通过、配置有效。

用法:
    python scripts/verify_architecture.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

passed = 0
failed = 0


def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [OK] {label}  {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {label}  {detail}")


# GATE 1: 核心模块可导入
modules = [
    ("fishkb", "from fishkb.db import KnowledgeDB"),
    ("src", "from src.orchestrator import get_orchestrator"),
    ("src.memory", "from src.memory import MagmaMemory, MemorySystem"),
]
for label, code in modules:
    try:
        exec(code)
        check(f"Import: {label}", True)
    except Exception as e:
        check(f"Import: {label}", False, str(e)[:60])

# GATE 2: 关键文件存在
for f in [
    "pyproject.toml", "README.md", "README.zh.md", "CHANGELOG.md",
    "PROJECT_MANIFEST.md", "HEARTBEAT.md",
    "fishkb/config/fish_species_index.yaml",
    "fishkb/config/species_variants.yaml",
    "docs/CHINA_FISH_CONSERVATION.md",
]:
    check(f"File: {f}", os.path.isfile(os.path.join(ROOT, f)))

# GATE 3: 知识库
try:
    from fishkb.db import KnowledgeDB
    kb = KnowledgeDB()
    count = kb.conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]
    check(f"Species DB: {count} species", count >= 30)
except Exception as e:
    check("Species DB", False, str(e)[:60])

# GATE 4: 测试
r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"],
    capture_output=True, text=True, timeout=60,
)
last_line = r.stdout.strip().split("\n")[-1] if r.stdout else ""
check("Tests pass", r.returncode == 0, last_line)

total = passed + failed
print(f"\n  {'='*40}")
print(f"  Architecture: {passed}/{total} checks passed")
print(f"  {'OK' if failed == 0 else f'{failed} FAILURES'}")
sys.exit(0 if failed == 0 else 1)
