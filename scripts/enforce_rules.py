#!/usr/bin/env python3
"""
enforce_rules.py — 一键执行全部规则检查。

规则来源: RULES.md (工作区根目录)
等同于依次运行:
    python scripts/check_feature_scripts.py
    python scripts/check_git_discipline.py
    python scripts/check_dates.py

用法:
    python scripts/enforce_rules.py              # 全部检查
    python scripts/enforce_rules.py --quick       # 仅快速检查（跳过大文件扫描）
    python scripts/enforce_rules.py --json        # JSON 输出（CI 友好）
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("功能脚本化", "scripts/check_feature_scripts.py"),
    ("Git 提交纪律", "scripts/check_git_discipline.py"),
    ("日期准确性", "scripts/check_dates.py"),
]


def run_check(name: str, script: str) -> Tuple[str, bool, str]:
    """运行单个检查脚本，返回 (名称, 通过, 输出)。"""
    script_path = ROOT / script
    if not script_path.exists():
        return (name, False, f"脚本不存在: {script}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, timeout=60,
        )
        output = result.stdout.strip()
        passed = result.returncode == 0
        return (name, passed, output)
    except subprocess.TimeoutExpired:
        return (name, False, "超时 (>60s)")
    except Exception as e:
        return (name, False, str(e))


def main() -> int:
    json_out = "--json" in sys.argv
    quick = "--quick" in sys.argv
    checks_to_run = CHECKS[:2] if quick else CHECKS  # quick: skip date scan

    results: List[Dict] = []
    all_pass = True

    print("═══════════════════════════════════════════")
    print("  📋 规则强制执行检查")
    print("═══════════════════════════════════════════")
    print()

    for name, script in checks_to_run:
        name, passed, output = run_check(name, script)
        icon = "✅" if passed else "❌"
        print(f"── {icon} {name} ──")
        print(output)
        print()
        if not passed:
            all_pass = False

        results.append({
            "rule": name,
            "passed": passed,
            "script": script,
            "output": output[:500],
        })

    print("═══════════════════════════════════════════")
    if all_pass:
        print("  ✅ 全部规则通过")
    else:
        failed = [r["rule"] for r in results if not r["passed"]]
        print(f"  ❌ {len(failed)} 条规则违规: {', '.join(failed)}")
    print("═══════════════════════════════════════════")

    if json_out:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
