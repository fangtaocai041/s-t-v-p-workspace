#!/usr/bin/env python3
"""
文献自动追加工具 (鱼类生态学版) — DOI 元数据抓取 + 自动分类 + 格式化追加

用法:
    python scripts/add_literature.py --doi 10.xxxx/xxxxx
    python scripts/add_literature.py --doi 10.xxxx/xxxxx --dry-run
    python scripts/add_literature.py --manual

自动分类: 物种 (Culter/Tachysurus/Ochetobius/鱼类通识)
          × 主题 (生态/形态/同位素/遗传/保护/综述)
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── 鱼类生态学分类体系 ──────────────────────────────────
KB = Path(__file__).resolve().parent.parent

# 物种关键词
SPECIES_KW = {
    "Culter (鲌属)":   ["culter", "鲌", "alburnus", "mongolicus", "dabryi"],
    "Tachysurus (䱨属)": ["tachysurus", "䱨", "bagrid", "nitidus", "albomarginatus"],
    "Ochetobius (鳤属)": ["ochetobius", "鳤", "elongatus"],
    "其他鲤科":          ["cyprinid", "carp", "鲤", "xenocypris", "hemiculter"],
}

# 主题关键词
TOPIC_KW = {
    "ecology-distribution":    ["population", "distribution", "abundance", "community",
                                "种群", "分布", "群落", "diversity", "biodiversity"],
    "morphology-morphometrics":["morpholog", "morphometric", "landmark", "shape",
                                "形态", "几何形态", "procrustes", "phenotypic"],
    "isotope-diet":            ["stable isotope", "δ13C", "δ15N", "diet", "stomach",
                                "同位素", "食性", "trophic", "niche", "SIBER"],
    "genetics-edna":           ["genetic", "genome", "eDNA", "RAD-seq", "microsatellite",
                                "遗传", "基因组", "分子", "phylogeograph"],
    "conservation-management": ["conservation", "fishing ban", "protected area",
                                "保护", "禁渔", "management", "threat"],
    "methods-review":          ["review", "method", "综述", "方法", "comparison"],
}

# 国内关键词
DOMESTIC_KW = ["yangtze", "china", "chinese", "长江", "中国", "鄱阳湖", "洞庭湖",
                "汉江", "珠江", "刘凯", "淡水渔业", "水生生物"]


def fetch_crossref(doi: str) -> dict | None:
    url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FishEcology/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            msg = data.get("message", {})
            authors = [f"{a.get('given','')} {a.get('family','')}".strip()
                       for a in msg.get("author", [])]
            return {
                "title": " ".join(msg.get("title", [""])),
                "authors": authors[:5],
                "year": msg.get("published-print", {}).get("date-parts", [[None]])[0][0]
                        or msg.get("created", {}).get("date-parts", [[None]])[0][0],
                "journal": " ".join(msg.get("container-title", [""])),
                "doi": doi,
                "keywords": msg.get("subject", []),
                "abstract": msg.get("abstract", ""),
                "type": msg.get("type", ""),
            }
    except Exception as e:
        print(f"  ⚠️ Crossref 错误: {e}")
        return None


def classify(text: str, kw_map: dict) -> str:
    text_lower = text.lower()
    scores = {}
    for name, keywords in kw_map.items():
        scores[name] = sum(1 for kw in keywords if kw.lower() in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else list(kw_map.keys())[0]


def classify_region(text: str) -> str:
    if any(kw.lower() in text.lower() for kw in DOMESTIC_KW):
        return "domestic"
    if any("\u4e00" <= c <= "\u9fff" for c in text):
        return "domestic"
    return "international"


def format_entry(meta: dict) -> str:
    text = f"{meta['title']} {' '.join(meta.get('keywords',[]))} {meta.get('abstract','')}"
    species = classify(text, SPECIES_KW)
    topic = classify(text, TOPIC_KW)

    tier = "✅ SCI"
    if meta.get("type") not in ("journal-article",):
        tier = "⚠️ 待验证"

    entry = f"""
### {meta['title']}
| 字段 | 值 |
|------|-----|
| 作者 | {", ".join(meta.get('authors', ['未知']))} |
| 年份 | {meta['year'] or '未知'} |
| 期刊 | {meta.get('journal', '未知')} |
| DOI | {meta['doi']} |
| 物种 | {species} |
| 主题 | {topic} |
| 等级 | {tier} |
"""
    if meta.get("abstract"):
        short = meta["abstract"][:250].strip()
        if len(meta["abstract"]) > 250:
            short += "..."
        entry += f"| 摘要 | {short} |\n"
    entry += "\n"
    return entry


def append_literature(meta: dict, dry_run: bool = False) -> str:
    text = f"{meta['title']} {' '.join(meta.get('keywords',[]))} {meta.get('abstract','')}"
    region = classify_region(text)
    topic = classify(text, TOPIC_KW)
    filename = topic.replace(" ", "-").lower()

    out_dir = KB / "research_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    entry = format_entry(meta)

    if dry_run:
        print(f"\n📋 [DRY-RUN] 区域={region}  主题={filename}")
        print(entry)
        return ""

    bib_file = out_dir / "literature_bibliography.md"
    header = (
        "\n---\n"
        f"<!-- {datetime.now().strftime('%Y-%m-%d')} | {region} | {filename} -->\n"
    )
    with open(bib_file, "a", encoding="utf-8") as f:
        if not bib_file.exists() or bib_file.stat().st_size == 0:
            f.write("# 鱼类生态学文献库 (自动追加)\n\n")
        f.write(header + entry)

    return f"✅ 已追加 → research_output/literature_bibliography.md"


def manual_mode():
    print("\n📝 手动文献输入\n")
    meta = {
        "title": input("标题: ").strip(),
        "authors": [a.strip() for a in input("作者 (逗号分隔): ").strip().split(",") if a.strip()],
        "year": int(y) if (y := input("年份: ").strip()).isdigit() else None,
        "journal": input("期刊: ").strip(),
        "doi": input("DOI (可选): ").strip(),
        "keywords": [k.strip() for k in input("关键词 (逗号分隔): ").strip().split(",") if k.strip()],
        "abstract": input("摘要 (可选): ").strip(),
        "type": "journal-article",
    }
    print(append_literature(meta))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="鱼类生态学文献自动追加")
    parser.add_argument("--doi", type=str)
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.manual:
        manual_mode()
        return
    if not args.doi:
        parser.print_help()
        sys.exit(1)

    print(f"\n🔍 Crossref: {args.doi}")
    meta = fetch_crossref(args.doi)
    if not meta:
        print("❌ 获取失败，尝试 --manual")
        sys.exit(1)
    print(f"   标题: {meta['title'][:80]}...")
    print(append_literature(meta, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
