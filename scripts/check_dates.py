#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则5: 日期准确性 — 检查 README/CHANGELOG 中的日期是否为实际日期而非未来计划日期。

用法:
    python scripts/check_dates.py              # 检查全部
    python scripts/check_dates.py --fix        # 输出修正建议
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# ── 日期提取正则 ──
# "最后更新：2026-06-20" / "Last updated: 2026-06-20" / "2026-06-20"
DATE_PATTERNS = [
    re.compile(r"最后更新[：:]\s*(\d{4}-\d{2}-\d{2})"),
    re.compile(r"Last\s+updated?[：:]\s*(\d{4}-\d{2}-\d{2})"),
    re.compile(r"最后修改[：:]\s*(\d{4}-\d{2}-\d{2})"),
]

# 版本计划日期（来自 agent.yaml / CHANGELOG 版本历史）
# 这些是预期的发布日期，不应该被照搬到 README 中
VERSION_PLAN_DATES = {
    "v6.5.0": "2026-06-12",
    "v6.5.1": "2026-06-17",
    "v6.4.0": "2026-06-09",
}

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def check_file(filepath: Path) -> List[Tuple[str, str]]:
    """
    检查单个文件的日期。
    返回 (级别, 消息) 列表。
    """
    issues: List[Tuple[str, str]] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []  # 跳过无法读取的文件（二进制/编码问题）

    rel_path = str(filepath.relative_to(ROOT))

    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(content):
            date_str = match.group(1)
            # 检查是否为未来日期
            if date_str > TODAY:
                issues.append((
                    "⚠️",
                    f"{rel_path}: '最后更新={date_str}' 是未来日期（今天={TODAY}）",
                ))
            # 检查是否照搬了版本计划日期
            for ver, plan_date in VERSION_PLAN_DATES.items():
                if date_str == plan_date and "最后更新" in match.group(0):
                    issues.append((
                        "⚠️",
                        f"{rel_path}: '最后更新={date_str}' 可能是照搬 {ver} 版本计划日期",
                    ))

    return issues


def main() -> int:
    projects = [
        "fish-ecology-assistant",
        "cognitive-search-engine",
        "eon-core",
        "porpoise-agent",
        "coilia-agent",
        "culter-agent",
        "conflict-arbiter",
    ]

    total_issues = 0
    for proj in projects:
        proj_root = ROOT / proj
        if not proj_root.exists():
            continue
        for md_file in sorted(proj_root.glob("*.md")):
            issues = check_file(md_file)
            for level, msg in issues:
                print(f"  {level} {msg}")
                if level != "✅":
                    total_issues += 1

    # 也检查根目录
    for md_file in sorted(ROOT.glob("*.md")):
        issues = check_file(md_file)
        for level, msg in issues:
            print(f"  {level} {msg}")
            if level != "✅":
                total_issues += 1

    print()
    print(f"📅 今天: {TODAY}")
    if total_issues:
        print(f"⚠️  {total_issues} 个日期问题 — 请使用实际当天日期")
        return 1
    else:
        print("✅ 日期准确性: 全部通过")
        return 0


if __name__ == "__main__":
    sys.exit(main())
