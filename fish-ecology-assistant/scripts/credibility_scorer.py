#!/usr/bin/env python3
"""
credibility_scorer.py — 三角验证评分 (credibility_score 0–100)

与 lit-search v3.1 §2.1 配套。对论文列表执行:
  1. 期刊等级识别 (SCI/SSCI/CSCD/科技核心)
  2. DOI/PMID/PMC 存在性检测
  3. 引用数加分
  4. 预印本/掠夺性/撤稿扣分
  5. 来源独立性检查 (三角验证)

用法:
  from credibility_scorer import score_papers, format_credibility

  papers = [{"doi": "10.xxx", "journal": "Nature", ...}]
  scored = score_papers(papers, species_name="Pseudaspius hakonensis")
  for p in scored:
      print(format_credibility(p["_credibility_score"]), p["title"][:60])

命令行:
  python scripts/credibility_scorer.py < papers.json
  python scripts/credibility_scorer.py --example

v1.0 — lit-search v3.1 配套
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── SCI/SSCI 期刊特征检测 ──
# 这不是完整的期刊白名单，而是基于常见 SCI 出版商/期刊名的启发式检测
_SCI_INDICATORS = [
    r"\bNature\b", r"\bScience\b", r"\bCell\b",
    r"Proceedings of the National Academy",
    r"\bPLOS\b", r"\bBMC\b", r"\bFrontiers in\b",
    r"\bEcology\b", r"\bEvolution\b", r"\bGenetics\b",
    r"\bMolecular\b", r"\bBioinformatics\b",
    r"\bJournal of\s+(?:Fish|Ichthyol|Helminthol|Parasitol|Zool)",
    r"\bEnvironmental\s+(?:Biology|Science|Toxicology)",
    r"\bComparative\s+Biochem",
    r"\bGenes\b", r"\bDiversity\b", r"\biScience\b",
    r"Scientific Reports", r"BMC\s+Biology",
    r"\bOecologia\b", r"\bZygote\b",
    r"\bAquaculture\b", r"\bHydrobiologia\b",
]

# CSCD 核心期刊 (中国科学引文数据库) — 不完全列表
_CSCD_JOURNALS = [
    "中国水产科学",
    "水生生物学报",
    "水产学报",
    "中国科学",
    "科学通报",
    "生物多样性",
    "生态学报",
    "动物学研究",
    "遗传",
    "湖泊科学",
    "海洋与湖沼",
]

# 科技核心期刊
_KEJI_CORE = [
    "水产学杂志",
    "上海海洋大学学报",
    "安徽师范大学学报",
]

# 掠夺性期刊特征 (域名/出版商黑名单)
_PREDATORY_INDICATORS = [
    "omics", "imedpub", "hindawi", "longdom", "scitechnol",
    "scholarena", "oaic", "waset", "academicia",
]


def detect_journal_tier(journal: str) -> str:
    """检测期刊等级: 'SCI' / 'CSCD' / 'keji_core' / 'unknown'."""
    if not journal:
        return "unknown"
    j = journal.strip()

    for pat in _CSCD_JOURNALS:
        if pat in j:
            return "CSCD"
    for pat in _KEJI_CORE:
        if pat in j:
            return "keji_core"
    for pat in _SCI_INDICATORS:
        if re.search(pat, j):
            return "SCI"

    return "unknown"


def is_predatory(journal: str) -> bool:
    """检测是否为疑似掠夺性期刊."""
    if not journal:
        return False
    j = journal.lower().strip()
    for ind in _PREDATORY_INDICATORS:
        if ind in j:
            return True
    return False


def score_paper(paper: Dict[str, Any], species_name: str = "") -> Dict[str, Any]:
    """对单篇论文执行三角验证评分，返回带 _credibility_score 和 _credibility_label 的论文。

    Args:
        paper: 论文字典，可选字段: doi, pmid, pmcid, journal, title,
               authors, year, source, citation_count
        species_name: 目标物种名 (用于相关性加分)

    Returns:
        带评分标记的论文字典:
          _credibility_score: 0-100
          _credibility_label: "高" / "中" / "低" / "不可用"
          _credibility_flag:  "🟢" / "🟡" / "🟠" / "🔴"
          _credibility_detail: 评分明细
    """
    score = 30  # 基础分

    detail_parts = [f"基础:30"]
    sci = None  # SCI期刊 (用于最终标识)

    # ── 期刊等级加分 ──
    journal = paper.get("journal", "")
    tier = detect_journal_tier(journal)
    if tier == "SCI":
        score += 30
        sci = True
        detail_parts.append("SCI:+30")
    elif tier == "CSCD":
        score += 25
        detail_parts.append("CSCD:+25")
    elif tier == "keji_core":
        score += 20
        detail_parts.append("科技核心:+20")

    # ── 标识符加分 ──
    doi = paper.get("doi", "")
    pmid = paper.get("pmid", "")
    pmcid = paper.get("pmcid", "")

    if doi and doi.startswith("10."):
        score += 15
        detail_parts.append("DOI:+15")
    if pmid:
        score += 10
        detail_parts.append("PMID:+10")
    if pmcid:
        score += 10
        detail_parts.append("PMC:+10")

    # ── 标题相关性 ──
    title = paper.get("title", "")
    if species_name and species_name.lower() in title.lower():
        score += 10
        detail_parts.append("物种相关:+10")

    # ── 引用数加分 ──
    citation_count = paper.get("citation_count", 0) or 0
    if citation_count >= 50:
        score += 10
        detail_parts.append(f"引用≥50:+10")
    elif citation_count >= 10:
        score += 5
        detail_parts.append(f"引用≥10:+5")

    # ── 已知作者加分 ──
    # 注: 此功能需要外部图谱数据，暂不实现
    # known_authors check would go here

    # ── CN 渠道加分 ──
    source = paper.get("source", "")
    if any(cn in source.lower() for cn in ["chinese", "cn", "\u4e2d\u6587"]):
        score += 25
        detail_parts.append("CN渠道:+25")

    # ── 扣分项 ──
    # 预印本
    title_lower = title.lower()
    journal_lower = journal.lower()
    if any(k in title_lower + journal_lower
           for k in ["arxiv", "biorxiv", "researchsquare", "preprint", "ssrn"]):
        score -= 30
        detail_parts.append("预印本:-30")

    # 会议摘要
    if "abstract" in title_lower and "conference" in title_lower:
        score -= 10
        detail_parts.append("会议:-10")

    # 掠夺性期刊
    if is_predatory(journal):
        score -= 40
        detail_parts.append("掠夺性:-40")

    # 撤稿 (绝对剔除)
    if "retract" in title_lower:
        score = 0
        detail_parts = ["撤稿:已撤销"]
        paper["_credibility_retracted"] = True

    # ── 来源独立性检查 ──
    sources = paper.get("_sources", []) or []
    if not sources and source:
        sources = [source]
    unique_sources = set(sources)
    if len(unique_sources) >= 3:
        score += 5
        detail_parts.append(f"多源验证:+5 ({len(unique_sources)}来源)")
    elif len(unique_sources) == 1:
        detail_parts.append("⚠️ 来源单一")

    # ── 最终评分 ──
    score = max(0, min(100, score))

    if score >= 80:
        label = "高"
        flag = "🟢"
    elif score >= 50:
        label = "中"
        flag = "🟡"
    elif score >= 20:
        label = "低"
        flag = "🟠"
    else:
        label = "不可用"
        flag = "🔴"

    paper["_credibility_score"] = score
    paper["_credibility_label"] = label
    paper["_credibility_flag"] = flag
    paper["_credibility_detail"] = ", ".join(detail_parts)
    paper["_credibility_tier"] = tier if tier != "unknown" else ("SCI" if sci else "standard")

    return paper


def score_papers(papers: List[Dict], species_name: str = "") -> List[Dict]:
    """批量评分."""
    return [score_paper(p, species_name) for p in papers]


def format_credibility(score: int, flag: str = "") -> str:
    """将得分格式化为可视化标识.

    Args:
        score: 0-100 的得分
        flag: 可选，已有标记 (🟢/🟡/🟠/🔴)

    Returns:
        如 "🟢 高 85" 或 "🔴 不可用 15"
    """
    if not flag:
        if score >= 80:
            flag = "🟢"
            label = "高"
        elif score >= 50:
            flag = "🟡"
            label = "中"
        elif score >= 20:
            flag = "🟠"
            label = "低"
        else:
            flag = "🔴"
            label = "不可用"
    else:
        label = {"🟢": "高", "🟡": "中", "🟠": "低", "🔴": "不可用"}.get(flag, "?")

    return f"{flag} {label} {score}"


# ── CLI ──
def _example():
    """演示评分."""
    papers = [
        {"title": "Genomic insights into seawater adaptation in Cyprinidae",
         "journal": "BMC Biology", "doi": "10.1186/s12915-024-01885-2",
         "pmid": "38637780", "pmcid": "PMC11027309",
         "citation_count": 25, "source": "europe_pmc"},
        {"title": "中国绥芬河三块鱼不同群体的种属划分及起源",
         "journal": "中国水产科学", "doi": "10.3724/SP.J.1118.2018.18056",
         "source": "lit_search_v3"},
        {"title": "A thermostable trypsin from Japanese dace",
         "journal": "Fish Physiology and Biochemistry",
         "doi": "10.1007/s10695-018-0600-3", "pmid": "30547269",
         "citation_count": 15, "source": "pubmed"},
        {"title": "Prevalence of zoonotic trematode metacercariae in freshwater fish",
         "journal": "Korean Journal of Parasitology",
         "doi": "10.3347/kjp.2014.52.4.399",
         "source": "web_search"},
    ]

    scored = score_papers(papers, species_name="Pseudaspius hakonensis")
    print("═" * 60)
    print("  三角验证评分示例")
    print("═" * 60)
    for p in scored:
        print(f"  {p['_credibility_flag']} {p['_credibility_label']:4s} {p['_credibility_score']:3d}  | "
              f"{p['title'][:55]:55s} | {p.get('journal','')[:20]}")
        print(f"     明细: {p['_credibility_detail']}")
    print("═" * 60)

    # 统计
    print(f"\n  统计:")
    by_tier = {}
    for p in scored:
        t = p["_credibility_label"]
        by_tier[t] = by_tier.get(t, 0) + 1
    for tier, count in sorted(by_tier.items()):
        print(f"    {tier}: {count}篇")


def _cli():
    """命令行入口: 从 stdin 读取 JSON 数组并评分."""
    data = json.load(sys.stdin)
    if isinstance(data, dict):
        papers = data.get("papers", [data])
    elif isinstance(data, list):
        papers = data
    else:
        print("❌ 输入必须是论文列表或包含 papers 字段的 dict", file=sys.stderr)
        sys.exit(1)

    species = sys.argv[1] if len(sys.argv) > 1 else ""
    scored = score_papers(papers, species_name=species)
    print(json.dumps(scored, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if "--example" in sys.argv:
        _example()
    else:
        _cli()
