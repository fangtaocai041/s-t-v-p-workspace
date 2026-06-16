#!/usr/bin/env python3
"""
刀鲚知识入库 — 将 Coilia nasus 补充到 fish_species_kb.yaml

三角闭环反馈: V(cognitive) 搜索发现 → 写回 S(fish) 知识库

用法:
  python scripts/fish_kb_add_species.py          # 添加刀鲚
  python scripts/fish_kb_add_species.py --list    # 列出当前物种
"""

import datetime
import sys
from pathlib import Path

import yaml

_KB_PATH = Path(r"D:\Reasonix\fish-ecology-assistant\config\fish_species_kb.yaml")

# ── 待写入的刀鲚条目 ──

COILIA_NASUS = {
    "id": "coilia_nasus",
    "name": "刀鲚",
    "scientific": "Coilia nasus",
    "chinese_name": "刀鲚",
    "common_names": ["长江刀鱼", "刀鱼", "长颌鲚", "tapertail anchovy"],
    "family": "鳀科 (Engraulidae)",
    "conservation": "濒危(EN)",
    "category": "dominant",
    "distribution": {
        "continents": ["亚洲"],
        "countries": ["中国"],
        "basins": ["长江流域"],
    },
    "migration_type": "溯河洄游 (anadromous)",
    "historical_peak": "1973年长江刀鱼产量 3750t",
    "current_status": "资源量仅为历史峰值的1-3%",
    "research_group": "淡水渔业研究中心 刘凯研究员课题组",
    "papers_count": 129,
    "key_research_themes": [
        "耳石微化学与洄游履历",
        "群体遗传学与种群结构",
        "资源评估与管理",
        "早期资源与补充群体",
        "食性与营养生态",
    ],
    "taxonomy_log": [
        {
            "detected_at": datetime.date.today().isoformat(),
            "field": "species_graph_id",
            "new_value": "Coilia_nasus",
            "note": "通过 P₂ 刀鲚专研补充 — cognitive-species-search v3.2",
        }
    ],
    "species_graph_id": "Coilia_nasus",
}


def load_kb() -> dict:
    """读取知识库."""
    if not _KB_PATH.is_file():
        print(f"❌ 知识库文件不存在: {_KB_PATH}")
        sys.exit(1)
    return yaml.safe_load(_KB_PATH.read_text(encoding="utf-8"))


def save_kb(kb: dict):
    """写回知识库."""
    with open(_KB_PATH, "w", encoding="utf-8") as f:
        yaml.dump(kb, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"✅ 已写入: {_KB_PATH}")


def list_species(kb: dict):
    """列出知识库中所有物种."""
    species = kb.get("species", [])
    if not species:
        print("(空)")
        return
    for s in species:
        sci = s.get("scientific", "?")
        name = s.get("name", "?")
        basins = ", ".join(s.get("distribution", {}).get("basins", []))
        print(f"  {sci:40s} {name:6s} | {basins}")


def add_species(kb: dict, entry: dict) -> bool:
    """添加物种条目 (去重)."""
    species = kb.setdefault("species", [])
    sci = entry["scientific"].lower()
    # 去重: 学名已存在则不重复添加
    for s in species:
        if s.get("scientific", "").lower() == sci:
            print(f"  ⏭️  {sci} 已在知识库中, 跳过")
            return False
    species.append(entry)
    print(f"  ✅ 已添加: {sci} ({entry.get('name', '')})")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="鱼力知识库物种管理")
    parser.add_argument("--list", action="store_true", help="列出所有物种")
    parser.add_argument("--add", action="store_true", default=True, help="添加刀鲚 (默认)")
    args = parser.parse_args()

    kb = load_kb()

    if args.list:
        list_species(kb)
        return

    if args.add:
        print("🔷 三角闭环反馈: V(cognitive) → S(fish)")
        added = add_species(kb, COILIA_NASUS)
        if added:
            save_kb(kb)
            print(f"\n下次查询 Coilia nasus → S(fish) 直接返回知识库数据 ✅")


if __name__ == "__main__":
    main()
