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
    ws = v.get("workspace", {})
    proj = v.get("projects", {})
    ver_str = (
        f"{ws.get('version', '?')} · {ws.get('date', '?')} · "
        f"cognitive {proj.get('cognitive-search-engine', {}).get('version', '?')} / "
        f"fish {proj.get('fish-ecology-assistant', {}).get('version', '?')} / "
        f"porpoise {proj.get('porpoise-agent', {}).get('version', '?')} / "
        f"coilia {proj.get('coilia-agent', {}).get('version', '?')} / "
        f"eon-core {proj.get('eon-core', {}).get('version', '?')}"
    )
    print(f"\n═══ 版本同步: {ver_str} ═══")

    # Update Eon-Taiji evolution docs (renamed from 五项目进化全量图谱)
    md = WORKSPACE / "docs" / "Eon-Taiji 进化全量图谱.md"
    if md.exists():
        c = md.read_text(encoding="utf-8")
        c = re.sub(r'> \*\*最新\*\*: v[\d.]+.*', f'> **最新**: {ver_str}', c)
        md.write_text(c, encoding="utf-8")
        print(f"  ✅ {md.name}")

    html = WORKSPACE / "docs" / "Eon-Taiji 进化全量图谱.html"
    if html.exists():
        c = html.read_text(encoding="utf-8")
        c = re.sub(
            r'<p><strong>最新</strong>: v[\d.]+.*?</p>',
            f'<p><strong>最新</strong>: {ver_str}</p>', c
        )
        html.write_text(c, encoding="utf-8")
        print(f"  ✅ {html.name}")

    # Update each project README (Latest/最新 lines)
    for name, p in proj.items():
        pver = p.get('version', '?')
        pdate = p.get('date', '?')
        for lang in ["README.md", "README.zh.md"]:
            rp = WORKSPACE / name / lang
            if rp.exists():
                c = rp.read_text(encoding="utf-8")
                c = re.sub(
                    r'> \*\*Latest\*\*: v[\d.]+.*',
                    f"> **Latest**: {pver} · {pdate}",
                    c
                )
                c = re.sub(
                    r'> \*\*最新\*\*: v[\d.]+.*',
                    f"> **最新**: {pver} · {pdate}",
                    c
                )
                rp.write_text(c, encoding="utf-8")
                print(f"  ✅ {name}/{lang} → {pver}")

    print(f"\n✅ 全部同步完成\n")

if __name__ == "__main__":
    main()
