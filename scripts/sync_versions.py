#!/usr/bin/env python3
"""
sync_versions.py — 从 VERSION.yaml 同步版本号到所有文件
一源真相 · 一处修改 · 全局同步 · Python-only (safe UTF-8)

用法: python scripts/sync_versions.py
"""

import sys, re
from pathlib import Path

try: import yaml
except ImportError: print("pip install pyyaml"); sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent

def load():
    with open(WORKSPACE / "VERSION.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    v = load()
    evo = v["evolution_doc"]
    proj = v["projects"]
    ver_str = (
        f"{evo['latest_version']} · {evo['latest_date']} · "
        f"cognitive {proj['cognitive-search-engine']['version']} / "
        f"fish {proj['fish-ecology-assistant']['version']} / "
        f"porpoise {proj['porpoise-agent']['version']} / "
        f"coilia {proj['coilia-agent']['version']} / "
        f"meso-cosmos {proj['meso-cosmos-agent']['version']}"
    )
    print(f"\n═══ 版本同步: {ver_str} ═══")

    # Update MD
    md = WORKSPACE / "docs" / "五项目进化全量图谱.md"
    if md.exists():
        c = md.read_text(encoding="utf-8")
        c = re.sub(r'> \*\*最新\*\*: v[\d.]+.*', f'> **最新**: {ver_str}', c)
        md.write_text(c, encoding="utf-8")
        print(f"  ✅ {md.name}")

    # Update HTML (Python-only safe encoding)
    html = WORKSPACE / "docs" / "五项目进化全量图谱.html"
    if html.exists():
        c = html.read_text(encoding="utf-8")
        c = re.sub(
            r'<p><strong>最新</strong>: v[\d.]+.*?</p>',
            f'<p><strong>最新</strong>: {ver_str}</p>', c
        )
        html.write_text(c, encoding="utf-8")
        print(f"  ✅ {html.name}")

    # Update each project README
    for name, p in proj.items():
        for lang in ["README.md", "README.zh.md"]:
            rp = WORKSPACE / name / lang
            if rp.exists():
                c = rp.read_text(encoding="utf-8")
                c = re.sub(
                    r'> \*\*Latest\*\*: v[\d.]+.*',
                    f"> **Latest**: {p['version']} · {p['date']} · `{p['commit']}`", c
                )
                c = re.sub(
                    r'> \*\*最新\*\*: v[\d.]+.*',
                    f"> **最新**: {p['version']} · {p['date']}", c
                )
                rp.write_text(c, encoding="utf-8")
                print(f"  ✅ {name}/{lang} → {p['version']}")

    print(f"\n✅ 全部同步完成\n")

if __name__ == "__main__":
    main()
