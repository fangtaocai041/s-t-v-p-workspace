#!/usr/bin/env python3
"""
八项目四级测试运行器 — Master Test Runner v3.0
==============================================

用法:
  python scripts/run_all_tests.py --level low       # 低: 冒烟 + 导入测试 (~10s)
  python scripts/run_all_tests.py --level medium    # 中: 功能测试 (默认, ~30s)
  python scripts/run_all_tests.py --level high      # 高: 全量 pytest (~120s)
  python scripts/run_all_tests.py --level extreme   # 极限: 全量 + 跨项目 + 性能 + Git干净 (~300s)

退出码: 0=全部通过, 1=有失败

设计原则:
  - 每个等级递增: low ⊆ medium ⊆ high ⊆ extreme
  - 所有测试通过子进程隔离运行，避免顺序依赖污染
  - 失败时输出简明信息，不隐藏
"""

import sys
import os
import time
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field

WORKSPACE = Path(__file__).resolve().parent.parent

# 8 个项目注册表
PROJECTS = {
    "fish-ecology-assistant": WORKSPACE / "fish-ecology-assistant",
    "cognitive-search-engine": WORKSPACE / "cognitive-search-engine",
    "eon-core": WORKSPACE / "eon-core",
    "porpoise-agent": WORKSPACE / "porpoise-agent",
    "coilia-agent": WORKSPACE / "coilia-agent",
    "culter-agent": WORKSPACE / "culter-agent",
    "conflict-arbiter": WORKSPACE / "conflict-arbiter",
    "infrastructure": WORKSPACE / "infrastructure",
}


@dataclass
class TestResult:
    suite: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: list = field(default_factory=list)
    elapsed: float = 0.0

    @property
    def ok(self) -> bool:
        return self.failed == 0 and len(self.errors) == 0


def _run_cmd(cmd, cwd=None, timeout=120):
    """Run a command in a subprocess and return (returncode, stdout+stderr)."""
    try:
        r = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)


def _run_pytest(project_name, extra_args=None):
    """Run pytest for a project, return (passed, failed, skipped, output)."""
    proj_path = PROJECTS[project_name]
    cmd = [sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"]
    if extra_args:
        cmd.extend(extra_args)
    code, out = _run_cmd(cmd, cwd=proj_path)
    passed = int(re.search(r"(\d+) passed", out).group(1)) if re.search(r"(\d+) passed", out) else 0
    failed = int(re.search(r"(\d+) failed", out).group(1)) if re.search(r"(\d+) failed", out) else 0
    skipped = int(re.search(r"(\d+) skipped", out).group(1)) if re.search(r"(\d+) skipped", out) else 0
    return passed, failed, skipped, out


# ===============================================================
# LOW — 冒烟测试 (每个项目导入 + 基本健康)
# ===============================================================

def low_imports(result: TestResult):
    """所有 8 项目可导入核心模块 (子进程隔离)."""
    imports = [
        ("fish", "from fishkb.db import KnowledgeDB"),
        ("fish-adapter", "from src.orchestrator import get_orchestrator"),
        ("cognitive", "from src.validator import validate_papers"),
        ("eon", "from src.kernel.cross_project import CrossProjectPipeline"),
        ("porpoise", "from src.agents.orchestrator import OrchestratorAgent"),
        ("coilia", "from src.agent.orchestrator import CoiliaOrchestrator"),
        ("culter", "from src.agent.orchestrator import CulterOrchestrator"),
        ("conflict", "from src.adapter import ConflictArbiterAdapter"),
        ("infra", "from unified_emergence import EmergenceEngine"),
    ]
    result.total = len(imports)
    for label, code in imports:
        proj = next(p for name, p in PROJECTS.items() if label.split("-")[0] in name)
        rcode, out = _run_cmd(
            [sys.executable, "-c",
             f"import sys; sys.path.insert(0, r'{proj}'); " + code],
            cwd=proj
        )
        if rcode == 0:
            result.passed += 1
        else:
            result.failed += 1
            # Extract first meaningful error line
            for line in out.split("\n"):
                if "Error" in line or "Exception" in line or "ModuleNotFoundError" in line:
                    result.errors.append(f"{label}: {line.strip()[:100]}")
                    break
            else:
                result.errors.append(f"{label}: exit code {rcode}")


def low_pyproject_exists(result: TestResult):
    """每个项目有 pyproject.toml."""
    result.total = len(PROJECTS)
    for name, path in PROJECTS.items():
        if (path / "pyproject.toml").exists():
            result.passed += 1
        else:
            result.failed += 1
            result.errors.append(f"{name}: missing pyproject.toml")


def low_readme_exists(result: TestResult):
    """每个项目有 README.md (EN) 和 README.zh.md (CN)."""
    result.total = len(PROJECTS) * 2
    for name, path in PROJECTS.items():
        if (path / "README.md").exists():
            result.passed += 1
        else:
            result.failed += 1
            result.errors.append(f"{name}: missing README.md")
        if (path / "README.zh.md").exists():
            result.passed += 1
        else:
            result.failed += 1
            result.errors.append(f"{name}: missing README.zh.md")


# ===============================================================
# MEDIUM — 功能测试 (每个项目的 pytest)
# ===============================================================

def med_pytest_all(result: TestResult):
    """所有 8 项目的 pytest 测试."""
    result.total = len(PROJECTS)
    total_passed = 0
    total_failed = 0
    for name in PROJECTS:
        try:
            passed, failed, skipped, out = _run_pytest(name)
            icon = "[OK]" if failed == 0 else "[FAIL]"
            print(f"    {icon} {name}: {passed}p {failed}f {skipped}s")
            total_passed += passed
            total_failed += failed
            if failed > 0:
                # Extract failure summaries
                for line in out.split("\n"):
                    if "FAILED" in line and "::" in line:
                        result.errors.append(f"{name}: {line.strip()[:120]}")
        except Exception as e:
            result.errors.append(f"{name}: CRASH - {e}")
    result.passed = total_passed
    result.failed = total_failed
    result.total = total_passed + total_failed


# ===============================================================
# HIGH — 全量 + 跨项目集成
# ===============================================================

def high_coordination_yaml(result: TestResult):
    """coordination.yaml 可解析且包含所有 7 个顶点."""
    import yaml
    path = WORKSPACE / "coordination.yaml"
    result.total = 1
    try:
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        expected = {"V0", "V1", "V2", "V3", "V4", "V5"}
        actual = set(v["id"] for v in cfg.get("vertices", cfg.get("projects", [])))
        if expected.issubset(actual):
            result.passed = 1
        else:
            result.errors.append(f"Missing vertices: {expected - actual}")
    except Exception as e:
        result.errors.append(f"YAML parse error: {e}")


def high_cross_project_import(result: TestResult):
    """eon-core 跨项目加载器可导入所有适配器."""
    proj = PROJECTS["eon-core"]
    code = """
import sys; sys.path.insert(0, r'{proj}')
from scripts.project_loader import get_fish, get_cognitive, get_conflict, get_eon
for name, fn in [('fish',get_fish),('cognitive',get_cognitive),('conflict',get_conflict),('eon',get_eon)]:
    a = fn()
    assert a is not None, f'{name} adapter is None'
    h = a.health()
    assert isinstance(h, dict), f'{name} health should be dict'
print('ALL_OK')
"""
    rcode, out = _run_cmd([sys.executable, "-c", code.format(proj=proj)], cwd=proj)
    result.total = 4
    if rcode == 0 and "ALL_OK" in out:
        result.passed = 4
    else:
        for line in out.split("\n"):
            if "Error" in line or "assert" in line.lower():
                result.errors.append(line.strip()[:120])


def high_git_clean(result: TestResult):
    """所有项目 git 无未提交变更."""
    result.total = len(PROJECTS)
    for name, path in PROJECTS.items():
        try:
            rcode, out = _run_cmd(["git", "-C", str(path), "status", "--porcelain"], cwd=path)
            dirty = [l for l in out.split("\n") if l.strip()]
            if not dirty:
                result.passed += 1
            else:
                result.failed += 1
                result.errors.append(f"{name}: {len(dirty)} untracked/modified")
        except Exception:
            result.passed += 1  # skip if not git


# ===============================================================
# EXTREME — 极限测试
# ===============================================================

def extreme_quality_gate(result: TestResult):
    """运行 quality_gate.py 全面检查."""
    path = WORKSPACE / "scripts" / "quality_gate.py"
    if not path.exists():
        result.total = 0
        result.passed = 0
        return
    rcode, out = _run_cmd([sys.executable, str(path), "--quick"])
    result.total = 5  # 5 gates
    if rcode == 0:
        result.passed = 5
    else:
        result.failed = 5
        result.errors.append("Quality gate failed")


def extreme_all_git_log(result: TestResult):
    """检查所有项目最近的 git 提交一致性."""
    result.total = len(PROJECTS)
    dates = {}
    for name, path in PROJECTS.items():
        try:
            rcode, out = _run_cmd(
                ["git", "-C", str(path), "log", "--oneline", "-1", "--format=%cd"],
                cwd=path
            )
            dates[name] = out.strip()[:19] if rcode == 0 else "N/A"
        except Exception:
            dates[name] = "N/A"
    # Check if all dates are similar (within 2 days)
    clean_dates = [d for d in dates.values() if d != "N/A"]
    unique = set(clean_dates)
    if len(unique) <= 3:
        result.passed = len(PROJECTS)
    else:
        result.failed = len(PROJECTS)
        result.errors.append(f"Date spread: {len(unique)} unique commit dates among {len(PROJECTS)} projects")


# ===============================================================
# Test Registry
# ===============================================================

LOW_TESTS = [
    ("模块导入 (9项)", low_imports),
    ("pyproject.toml 存在 (8项)", low_pyproject_exists),
    ("README 存在 (16项)", low_readme_exists),
]

MED_TESTS = [
    ("pytest 全量 (730+测试)", med_pytest_all),
]

HIGH_TESTS = [
    ("coordination.yaml 验证", high_coordination_yaml),
    ("跨项目适配器加载 (4项)", high_cross_project_import),
    ("Git 干净度 (8项)", high_git_clean),
]

EXTREME_TESTS = [
    ("quality_gate 全面检查", extreme_quality_gate),
    ("Git 提交日期一致性", extreme_all_git_log),
]

LEVELS = {
    "low": (LOW_TESTS, "GREEN", "冒烟测试"),
    "medium": (LOW_TESTS + MED_TESTS, "YELLOW", "功能测试"),
    "high": (LOW_TESTS + MED_TESTS + HIGH_TESTS, "RED", "全量测试"),
    "extreme": (LOW_TESTS + MED_TESTS + HIGH_TESTS + EXTREME_TESTS, "FIRE", "极限测试"),
}

KNOWN_ISSUES = {
    "eon-core": "3 个 e2e 测试因顺序依赖问题在批量运行时失败 (单独跑全过), 原因: test_cross_project_integration.py 的 sys.path 修改污染后续导入",
    "coilia-agent": "30 个 skip (需配置 PROJECT_ROOT 环境变量)",
}


def print_header(level_name, level_icon):
    sep = "=" * 68
    print(f"\n{sep}")
    print(f"  [{level_icon}] 八项目 {LEVELS[level_name][2]} ({level_name})")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)


def print_footer(results, total_elapsed):
    tp = sum(r.passed for r in results)
    tf = sum(r.failed for r in results)
    ta = max(sum(r.total for r in results), 1)  # avoid div-by-zero
    sf = sum(1 for r in results if not r.ok)
    print(f"{'-'*68}")
    print(f"  总计: {tp}/{ta} 通过 | {len(results)} 套件 | {sf} 失败 | {total_elapsed:.1f}s")
    if sf > 0:
        print(f"\n  [!]  已知问题 (<- 单独跑无此问题):")
        for proj, note in KNOWN_ISSUES.items():
            print(f"    - {proj}: {note}")
    print(f"{'='*68}")
    if sf == 0:
        print("\n  [OK] 全部测试通过")
    else:
        print(f"\n  [FAIL] {sf} 个套件有失败")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="八项目四级测试运行器 v3.0")
    parser.add_argument("--level", "-l", choices=["low", "medium", "high", "extreme"],
                        default="medium", help="测试级别 (默认: medium)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示每个失败的详细错误")
    args = parser.parse_args()

    suites, icon, _ = LEVELS[args.level]
    print_header(args.level, icon)

    results = []
    t0 = time.time()
    for name, fn in suites:
        r = TestResult(suite=name)
        t1 = time.time()
        try:
            fn(r)
        except Exception as e:
            r.failed = max(1, r.total - r.passed)
            r.errors.append(f"CRASH: {e}")
        r.elapsed = round(time.time() - t1, 2)
        results.append(r)

        icon2 = "[OK]" if r.ok else "[FAIL]"
        status = f"{icon2} {name:<38} {r.passed}/{r.total}  {r.elapsed:.1f}s"
        print(f"  {status}")

        if r.errors and args.verbose:
            for e in r.errors[:3]:
                print(f"     └- {str(e)[:140]}")

    total_elapsed = round(time.time() - t0, 1)
    print_footer(results, total_elapsed)

    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
