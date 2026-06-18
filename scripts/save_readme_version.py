#!/usr/bin/env python3
"""save_readme_version.py — README 版本归档工具

用法:
    python scripts/save_readme_version.py                     # 自动版本号
    python scripts/save_readme_version.py --version v6.6.0    # 指定版本
    python scripts/save_readme_version.py --list               # 列出所有版本
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
VERSIONS_DIR = ROOT / ".reasonix" / "readme-versions"


def list_versions():
    versions = sorted(VERSIONS_DIR.glob("README-*.md"))
    if not versions:
        print("No saved README versions found.")
        return
    print(f"Saved {len(versions)} README versions:\n")
    for v in versions:
        print(f"  {v.stem.replace('README-', '', 1):<55} {v.stat().st_size:>6}B")


def get_next_version() -> str:
    existing = list(VERSIONS_DIR.glob("README-v*.md"))
    if not existing:
        return "v0.1.0"
    versions = []
    for f in existing:
        m = re.search(r"v(\d+)\.(\d+)\.(\d+)", f.name)
        if m:
            versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    if not versions:
        return "v0.1.0"
    latest = max(versions)
    return f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"


def save_version(version=""):
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not README.exists():
        print(f"Error: README.md not found: {README}")
        return False
    if not version:
        version = get_next_version()
    date_str = datetime.now().strftime("%Y%m%d-%H%M")
    dest = VERSIONS_DIR / f"README-{version}-{date_str}.md"
    shutil.copy2(README, dest)
    print(f"Saved: {dest.name} ({dest.stat().st_size}B)")
    return True


def main():
    import argparse
    p = argparse.ArgumentParser(description="README version archiver")
    p.add_argument("--version", "-v", default="", help="Version tag")
    p.add_argument("--list", "-l", action="store_true", help="List saved versions")
    args = p.parse_args()
    if args.list:
        list_versions()
    else:
        save_version(args.version)


if __name__ == "__main__":
    main()
