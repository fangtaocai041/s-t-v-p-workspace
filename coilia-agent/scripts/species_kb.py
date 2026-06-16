#!/usr/bin/env python3
"""
P₂ 刀鲚知识库查询脚本 — 对应 data/knowledge_base/species/coilia-nasus.md

用法:
  python scripts/species_kb.py                    # 打印全部
  python scripts/species_kb.py --theme migration  # 查特定方向
  python scripts/species_kb.py --json             # JSON 输出
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

_KB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base" / "species" / "coilia-nasus.md"


def load_kb() -> Dict[str, Any]:
    """读取本地刀鲚知识库，返回结构化数据."""
    if not _KB_PATH.is_file():
        return {"error": f"知识库文件不存在: {_KB_PATH}"}

    text = _KB_PATH.read_text(encoding="utf-8")

    data = {}

    # 提取 species 部分
    species_start = text.find("species:")
    themes_start = text.find("research_themes:")
    if species_start >= 0 and themes_start >= 0:
        species_text = text[species_start:themes_start]
        parsed = yaml.safe_load(species_text)
        if parsed and "species" in parsed:
            data["species"] = parsed["species"]

    # 提取 research_themes 部分
    themes_start = text.find("research_themes:")
    groups_start = text.find("key_research_groups:")
    if themes_start >= 0 and groups_start >= 0:
        themes_text = text[themes_start:groups_start]
        data["research_themes"] = yaml.safe_load(themes_text).get("research_themes", [])

    # 提取 key_research_groups 部分 (到文件末尾)
    groups_start = text.find("key_research_groups:")
    if groups_start >= 0:
        groups_text = text[groups_start:]
        data["key_research_groups"] = yaml.safe_load(groups_text).get("key_research_groups", [])

    return data


def query_theme(data: Dict, theme_keyword: str) -> Optional[Dict]:
    """按关键词查询研究方向 (主题名/方法名/关键词)."""
    # 中英文关键词映射
    en_to_cn = {
        "migration": "洄游", "otolith": "耳石",
        "genetic": "遗传", "stock": "资源", "cpue": "资源",
        "feeding": "食性", "diet": "食性", "isotope": "食性",
        "spawning": "繁殖", "early": "早期", "larvae": "早期",
    }
    kw = theme_keyword.lower()
    # 英文关键词 → 中文
    for en, cn in en_to_cn.items():
        if en in kw:
            kw = cn
            break
    for theme in data.get("research_themes", []):
        if kw in theme["theme"].lower():
            return theme
        if any(kw in m.lower() for m in theme.get("methods", [])):
            return theme
        for q in theme.get("key_questions", []):
            if kw in q.lower():
                return theme
    return None


def format_summary(data: Dict) -> str:
    """格式化为可读摘要."""
    s = data.get("species", {})
    lines = [
        f"物种: {s.get('scientific', '?')} ({s.get('chinese', '?')})",
        f"保护: {s.get('conservation', {}).get('iucn', '?')}",
        f"洄游: {s.get('biology', {}).get('migration_type', '?')}",
        f"产卵: {s.get('biology', {}).get('spawning_season', '?')}",
        f"峰值: {s.get('population_trend', {}).get('historical_peak', '?')}",
        f"现状: {s.get('population_trend', {}).get('current_status', '资源量仅为历史峰值的1-3%')}",
    ]
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="P₂ 刀鲚知识库查询")
    parser.add_argument("--theme", "-t", help="研究方向关键词 (migration/genetics/stock/feeding/early_life)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    data = load_kb()
    if "error" in data:
        print(data["error"])
        sys.exit(1)

    if args.json:
        if args.theme:
            t = query_theme(data, args.theme)
            print(json.dumps(t if t else {"not_found": args.theme}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.theme:
        t = query_theme(data, args.theme)
        if t:
            print(f"研究方向: {t['theme']}")
            print(f"方法: {', '.join(t.get('methods', []))}")
            for q in t.get("key_questions", []):
                print(f"  • {q}")
        else:
            print(f"未找到: {args.theme}")
        return

    # 默认: 打印全部
    print(format_summary(data))
    print(f"\n研究方向 ({len(data.get('research_themes', []))} 个):")
    for t in data.get("research_themes", []):
        print(f"  • {t['theme']}")
    print(f"\n核心团队 ({len(data.get('key_research_groups', []))} 个):")
    for g in data.get("key_research_groups", []):
        print(f"  • {g['institution']}: {', '.join(g['researchers'])}")


if __name__ == "__main__":
    main()
