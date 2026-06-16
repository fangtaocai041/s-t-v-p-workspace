#!/usr/bin/env python3
"""
规则3+4: Git 提交纪律 + 工作流 — 检查全部仓库的 commit/push/force-push 状态。

用法:
    python scripts/check_git_discipline.py              # 检查全部
    python scripts/check_git_discipline.py --json       # JSON 输出
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent

SUB_PROJECTS = [
    "fish-ecology-assistant",
    "cognitive-search-engine",
    "eon-core",
    "porpoise-agent",
    "coilia-agent",
    "culter-agent",
    "conflict-arbiter",
]


@dataclass
class RepoStatus:
    name: str
    path: Path
    head: str = ""
    branch: str = ""
    dirty_files: int = 0
    unpushed_commits: int = 0
    has_force_push: bool = False
    errors: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.dirty_files == 0 and self.unpushed_commits == 0 and not self.errors

    @property
    def status_icon(self) -> str:
        if self.errors:
            return "❌"
        if self.dirty_files > 0 or self.unpushed_commits > 0:
            return "⚠️"
        return "✅"


def check_repo(name: str, path: Path) -> RepoStatus:
    """检查单个仓库的 Git 状态。"""
    status = RepoStatus(name=name, path=path)

    git_dir = path / ".git"
    if not git_dir.exists():
        status.errors.append("no .git directory")
        return status

    def run(args: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(path)] + args,
            capture_output=True, text=True, timeout=10,
        )

    try:
        # HEAD
        r = run(["rev-parse", "--short", "HEAD"])
        if r.returncode == 0:
            status.head = r.stdout.strip()

        # branch
        r = run(["rev-parse", "--abbrev-ref", "HEAD"])
        if r.returncode == 0:
            status.branch = r.stdout.strip()

        # dirty files
        r = run(["status", "--porcelain"])
        if r.returncode == 0:
            status.dirty_files = len([l for l in r.stdout.split("\n") if l.strip()])

        # unpushed commits
        if status.branch:
            r = run(["rev-list", "--count", f"origin/{status.branch}..HEAD"])
            if r.returncode == 0:
                try:
                    status.unpushed_commits = int(r.stdout.strip())
                except ValueError:
                    pass

        # check reflog for force-push evidence
        r = run(["reflog", "--max-count=20"])
        if r.returncode == 0 and "force-push" in r.stdout.lower():
            status.has_force_push = True

    except subprocess.TimeoutExpired:
        status.errors.append("timeout")
    except Exception as e:
        status.errors.append(str(e))

    return status


def check_all() -> Dict[str, RepoStatus]:
    """检查主工作区 + 全部子项目。"""
    results: Dict[str, RepoStatus] = {}

    # 主空间
    results["workspace"] = check_repo("workspace (主空间)", ROOT)

    # 子项目
    for proj in SUB_PROJECTS:
        results[proj] = check_repo(proj, ROOT / proj)

    return results


def main() -> int:
    json_out = "--json" in sys.argv

    results = check_all()
    issues = 0

    if json_out:
        output = {
            name: {
                "head": s.head,
                "branch": s.branch,
                "dirty_files": s.dirty_files,
                "unpushed_commits": s.unpushed_commits,
                "has_force_push": s.has_force_push,
                "clean": s.is_clean,
                "errors": s.errors,
            }
            for name, s in results.items()
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0 if all(s.is_clean for s in results.values()) else 1

    # 彩色终端输出
    for name, s in results.items():
        icon = s.status_icon
        head = s.head[:8] if s.head else "????"
        parts = [f"  {icon} {name:30s} {head}"]

        if s.dirty_files:
            parts.append(f"DIRTY({s.dirty_files})")
            issues += 1
        if s.unpushed_commits:
            parts.append(f"UNPUSHED({s.unpushed_commits})")
            issues += 1
        if s.has_force_push:
            parts.append("FORCE-PUSH")
            issues += 1
        if s.errors:
            parts.append(f"ERR:{';'.join(s.errors)}")
            issues += 1

        print("  ".join(parts))

    print()
    if issues:
        print(f"⚠️  {issues} 个 Git 纪律违规。执行 commit + push 修复。")
        return 1
    else:
        print("✅ Git 提交纪律: 全部通过（干净 + 已推送）")
        return 0


if __name__ == "__main__":
    sys.exit(main())
