#!/usr/bin/env python3
"""
sync_versions.py — 从 VERSION.yaml 同步版本号到所有文件

一源真相 · 一处修改 · 全局同步

用法: python scripts/sync_versions.py
"""

import sys, re
from pathlib import Path

try: import yaml
except ImportError: print("需要 pip install pyyaml"); sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
VERSION_FILE = WORKSPACE / "VERSION.yaml"

def load_versions():
    with open(VERSION_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)

def update_evolution_md(versions: dict):
    """更新 全量图谱.md 的版本号和映射表."""
    path = WORKSPACE / "docs" / "五项目进化全量图谱.md"
    if not path.exists(): return
    content = path.read_text(encoding="utf-8")

    # Update version header
    evo = versions["evolution_doc"]
    content = re.sub(r'v5\.\d+', evo["latest_version"], content)
    content = re.sub(
        r'> \*\*最新\*\*: v5\.\d+.*',
        f'> **最新**: {evo["latest_version"]} · {evo["latest_date"]}',
        content
    )

    # Update project version table if exists
    proj_lines = []
    for key, proj in versions["projects"].items():
        name = key.replace("-agent", "")
        proj_lines.append(
            f"| **{name}** | {proj['version']} | {proj['date']} | "
            f"{proj['role']} | {proj['element']} | {proj['wuxing']} | {proj['tao']} |"
        )

    path.write_text(content, encoding="utf-8")
    print(f"  ✅ {path.name}")

def update_readme(project_dir: str, proj: dict):
    """更新单个项目的 README.md 版本号."""
    for lang in ["README.md", "README.zh.md"]:
        path = WORKSPACE / project_dir / lang
        if not path.exists(): continue
        content = path.read_text(encoding="utf-8")

        # Update "Latest" line
        content = re.sub(
            r'> \*\*Latest\*\*: v[\d.]+ · [\d-]+ · `[a-f0-9]+`',
            f"> **Latest**: {proj['version']} · {proj['date']} · `{proj['commit']}`",
            content
        )
        content = re.sub(
            r'> \*\*最新\*\*: v[\d.]+ · [\d-]+',
            f"> **最新**: {proj['version']} · {proj['date']}",
            content
        )

        path.write_text(content, encoding="utf-8")
        print(f"  ✅ {project_dir}/{lang} → {proj['version']}")

def main():
    versions = load_versions()
    print(f"\n═══ 版本同步: {versions['workspace']['version']} ═══")

    # Update 全量图谱
    update_evolution_md(versions)

    # Update each project README
    for proj_dir, proj in versions["projects"].items():
        update_readme(proj_dir, proj)

    print(f"\n✅ 全部同步完成 — 一源真相: VERSION.yaml")
    print()

if __name__ == "__main__":
    main()
