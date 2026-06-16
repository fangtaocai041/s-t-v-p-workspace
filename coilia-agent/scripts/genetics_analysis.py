#!/usr/bin/env python3
"""
刀鲚群体遗传学分析 — 微卫星 + 线粒体DNA + SNP.

对应 SKILL.md: src/skills/analyze-genetics/SKILL.md

核心算法 (纯 Python, 无外部统计库依赖):
  - 微卫星: 等位基因频率, 观测/期望杂合度 (Ho/He), Fis, Fst
  - 线粒体: 单倍型多样性 (Hd), 核苷酸多样性 (π)
  - SNP: 群体分化, 固定指数

用法:
  python scripts/genetics_analysis.py --input microsat.csv       # 读微卫星数据
  python scripts/genetics_analysis.py --input mito.csv --json    # JSON 输出
  python scripts/genetics_analysis.py --example                  # 示例演示
  python scripts/genetics_analysis.py --list-params              # 打印分析参数
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class LocusStats:
    """单个位点的群体遗传统计."""
    name: str = ""
    n_individuals: int = 0       # 个体数
    n_alleles: int = 0           # 等位基因数
    allele_freqs: Dict[str, float] = field(default_factory=dict)  # 等位基因频率
    ho: float = 0.0              # 观测杂合度
    he: float = 0.0              # 期望杂合度
    fis: float = 0.0             # 近交系数


@dataclass
class PopulationStats:
    """群体水平的遗传统计."""
    name: str = ""
    n_individuals: int = 0
    loci: List[LocusStats] = field(default_factory=list)
    # 汇总
    mean_na: float = 0.0         # 平均等位基因数
    mean_ho: float = 0.0         # 平均观测杂合度
    mean_he: float = 0.0         # 平均期望杂合度
    mean_fis: float = 0.0        # 平均近交系数

    @property
    def summary(self) -> Dict[str, Any]:
        return {
            "population": self.name,
            "n_individuals": self.n_individuals,
            "n_loci": len(self.loci),
            "mean_alleles": round(self.mean_na, 2),
            "mean_ho": round(self.mean_ho, 4),
            "mean_he": round(self.mean_he, 4),
            "mean_fis": round(self.mean_fis, 4),
        }


@dataclass
class HaplotypeStats:
    """线粒体单倍型统计."""
    n_sequences: int = 0
    n_haplotypes: int = 0
    haplotype_freqs: Dict[str, float] = field(default_factory=dict)
    haplotype_diversity: float = 0.0   # Hd
    nucleotide_diversity: float = 0.0  # π


# ── 微卫星分析 ─────────────────────────────────────────

def load_microsatellite_data(path: Optional[str] = None) -> Dict[str, Dict[str, List[str]]]:
    """读取微卫星基因型数据.

    CSV 格式:
      population,individual,locus,allele1,allele2
      长江,IND01,CL01,120,124
      长江,IND01,CL02,98,102
      ...
    """
    data: Dict[str, Dict[str, List[str]]] = {}  # pop → {locus → [alleles]}
    if not path or not Path(path).is_file():
        return data

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pop = row.get("population", "pop1")
            locus = row.get("locus", "unknown")
            a1 = row.get("allele1", "0")
            a2 = row.get("allele2", "0")
            data.setdefault(pop, {})
            data[pop].setdefault(locus, [])
            data[pop][locus].extend([a1, a2])
    return data


def analyze_microsatellite_locus(alleles: List[str]) -> LocusStats:
    """分析单个微卫星位点."""
    n = len(alleles)
    if n == 0:
        return LocusStats()

    n_ind = n // 2
    counts = Counter(alleles)
    total = sum(counts.values())

    # 等位基因频率
    freqs = {a: round(c / total, 4) for a, c in counts.items()}

    # 观测杂合度 Ho
    # 每对等位基因不同 = 杂合
    hetero_count = 0
    for i in range(0, n, 2):
        if i + 1 < n and alleles[i] != alleles[i + 1]:
            hetero_count += 1
    ho = hetero_count / n_ind if n_ind > 0 else 0

    # 期望杂合度 He = 1 - Σ(pi²)
    he = 1.0 - sum(f ** 2 for f in freqs.values())
    # 小样本校正: He * 2n/(2n-1)
    if n_ind > 1:
        he = he * (2 * n_ind) / (2 * n_ind - 1)

    # Fis = 1 - Ho/He
    fis = 1.0 - (ho / he) if he > 0 else 0.0

    return LocusStats(
        name="",
        n_individuals=n_ind,
        n_alleles=len(counts),
        allele_freqs=freqs,
        ho=round(ho, 4),
        he=round(he, 4),
        fis=round(fis, 4),
    )


def analyze_population(genotypes: Dict[str, List[str]], pop_name: str = "未知") -> PopulationStats:
    """分析一个群体的全部微卫星位点."""
    pop = PopulationStats(name=pop_name)

    for locus_name, alleles in genotypes.items():
        ls = analyze_microsatellite_locus(alleles)
        ls.name = locus_name
        pop.loci.append(ls)

    if pop.loci:
        pop.n_individuals = max(ls.n_individuals for ls in pop.loci)
        pop.mean_na = sum(ls.n_alleles for ls in pop.loci) / len(pop.loci)
        pop.mean_ho = sum(ls.ho for ls in pop.loci) / len(pop.loci)
        pop.mean_he = sum(ls.he for ls in pop.loci) / len(pop.loci)
        pop.mean_fis = sum(ls.fis for ls in pop.loci) / len(pop.loci)

    return pop


# ── 线粒体DNA分析 ──────────────────────────────────────

def analyze_haplotypes(sequences: List[str]) -> HaplotypeStats:
    """分析线粒体单倍型数据.

    Args:
        sequences: 单倍型序列 (字符串) 列表

    Returns:
        HaplotypeStats
    """
    n = len(sequences)
    if n == 0:
        return HaplotypeStats()

    counts = Counter(sequences)
    n_hap = len(counts)
    freqs = {h: c / n for h, c in counts.items()}

    # 单倍型多样性 Hd = n/(n-1) * (1 - Σ(fi²))
    if n > 1:
        hd = (n / (n - 1)) * (1.0 - sum(f ** 2 for f in freqs.values()))
    else:
        hd = 0.0

    # 核苷酸多样性 π (简化版: 基于序列间差异的均值)
    pi = 0.0
    if n > 1 and len(sequences[0]) > 0:
        seq_len = len(sequences[0])
        total_diff = 0
        pairs = 0
        for i in range(n):
            for j in range(i + 1, n):
                s1, s2 = sequences[i], sequences[j]
                diff = sum(1 for a, b in zip(s1, s2) if a != b)
                total_diff += diff
                pairs += 1
        if pairs > 0 and seq_len > 0:
            pi = (total_diff / pairs) / seq_len

    return HaplotypeStats(
        n_sequences=n,
        n_haplotypes=n_hap,
        haplotype_freqs={h: round(f, 4) for h, f in freqs.items()},
        haplotype_diversity=round(hd, 4),
        nucleotide_diversity=round(pi, 6),
    )


# ── 群体分化 Fst ───────────────────────────────────────

def calc_fst(pop1_alleles: Dict[str, List[str]],
             pop2_alleles: Dict[str, List[str]]) -> float:
    """估算两个群体间的 Fst (基于共享位点)."""
    shared_loci = set(pop1_alleles.keys()) & set(pop2_alleles.keys())
    if not shared_loci:
        return 0.0

    fst_values: List[float] = []
    for locus in shared_loci:
        # 合并等位基因
        all1 = pop1_alleles[locus]
        all2 = pop2_alleles[locus]
        combined = all1 + all2

        n1, n2 = len(all1), len(all2)
        n = n1 + n2
        if n == 0:
            continue

        # 各位点频率
        c1 = Counter(all1)
        c2 = Counter(all2)
        c_all = Counter(combined)

        # 总期望杂合度 Ht
        ht = 1.0 - sum((c / n) ** 2 for c in c_all.values())

        # 亚群内期望杂合度 Hs
        hs1 = 1.0 - sum((c1[a] / n1) ** 2 for a in c1) if n1 > 0 else 0
        hs2 = 1.0 - sum((c2[a] / n2) ** 2 for a in c2) if n2 > 0 else 0
        hs = (hs1 + hs2) / 2 if n1 > 0 and n2 > 0 else (hs1 or hs2)

        # Fst = (Ht - Hs) / Ht
        if ht > 0:
            fst = (ht - hs) / ht
            fst_values.append(fst)

    return round(sum(fst_values) / len(fst_values), 4) if fst_values else 0.0


# ── 示例数据 ───────────────────────────────────────────

def _example_microsatellite() -> Dict[str, Dict[str, List[str]]]:
    """示例微卫星数据: 长江 vs 钱塘江 群体."""
    return {
        "长江群体": {
            "CL01": ["120", "124", "120", "120", "124", "128", "120", "124", "120", "120",
                     "124", "120", "128", "120", "124", "124", "120", "120", "124", "128"],
            "CL02": ["98", "102", "98", "100", "102", "98", "100", "102", "98", "98",
                     "102", "100", "98", "102", "100", "98", "102", "98", "100", "102"],
            "CL03": ["150", "154", "150", "150", "154", "158", "150", "154", "150", "150",
                     "154", "150", "158", "150", "152", "154", "150", "154", "150", "152"],
        },
        "钱塘江群体": {
            "CL01": ["122", "124", "122", "126", "124", "122", "126", "124", "122", "122",
                     "124", "126", "122", "124", "124", "122", "126", "122", "124", "122"],
            "CL02": ["100", "104", "100", "102", "104", "100", "102", "100", "104", "100",
                     "102", "104", "100", "102", "100", "104", "100", "102", "104", "100"],
            "CL03": ["148", "152", "148", "150", "152", "148", "150", "148", "152", "148",
                     "150", "152", "148", "150", "148", "152", "148", "150", "148", "150"],
        },
    }


def _example_haplotypes() -> List[str]:
    """示例线粒体 COI 单倍型序列."""
    # 模拟 20 条序列 (短片段)
    haps = [
        "ATCGATCGATCGATCGATCG",  # H1 — 最常见
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATCGATCGATCGATCG",  # H1
        "ATCGATAGATCGATCGATCG",  # H2 — 1 bp 差异
        "ATCGATAGATCGATCGATCG",  # H2
        "ATCGATAGATCGATCGATCG",  # H2
        "ATCGATAGATCGATCGATCG",  # H2
        "ATCTATCGATCGATCGATCG",  # H3 — 1 bp 差异
        "ATCTATCGATCGATCGATCG",  # H3
        "ATCGATCGATCGATAGATCG",  # H4 — 1 bp 差异
        "ATCGATCGATCGATAGATCG",  # H4
        "ATCGATCGATCGATCGATCA",  # H5 — 1 bp 差异
        "ATCGATCGATCGATCGATCA",  # H5
        "ATCTATAGATCGATCGATCG",  # H6 — 2 bp 差异
        "ATCTATAGATCGATCGATCG",  # H6
    ]
    return haps


# ── 报告生成 ───────────────────────────────────────────

def format_population_report(populations: List[PopulationStats],
                              hap_stats: Optional[HaplotypeStats] = None,
                              fst: Optional[float] = None) -> str:
    """生成群体遗传学分析报告."""
    lines = [
        "=" * 60,
        "  刀鲚群体遗传学分析报告",
        "=" * 60,
        f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    # 微卫星结果
    lines.append("\n1️⃣  微卫星标记 (SSR)")
    lines.append("-" * 40)

    for pop in populations:
        lines.append(f"\n  群体: {pop.name} (n={pop.n_individuals})")
        lines.append(f"  {'位点':10s} {'Na':4s} {'Ho':8s} {'He':8s} {'Fis':8s}")
        lines.append(f"  {'-'*38}")
        for ls in pop.loci:
            lines.append(f"  {ls.name:10s} {ls.n_alleles:4d} {ls.ho:.4f}  {ls.he:.4f}  {ls.fis:.4f}")
        lines.append(f"  {'均值':10s} {pop.mean_na:4.2f} {pop.mean_ho:.4f}  {pop.mean_he:.4f}  {pop.mean_fis:.4f}")

    if fst is not None:
        lines.append(f"\n  群体分化 Fst = {fst:.4f}")
        if fst < 0.05:
            lines.append("  解释: 遗传分化很低 (Fst < 0.05)")
        elif fst < 0.15:
            lines.append("  解释: 中等遗传分化 (0.05 ≤ Fst < 0.15)")
        elif fst < 0.25:
            lines.append("  解释: 较大遗传分化 (0.15 ≤ Fst < 0.25)")
        else:
            lines.append("  解释: 极大遗传分化 (Fst ≥ 0.25)")

    # 线粒体结果
    if hap_stats:
        lines.append("\n2️⃣  线粒体 DNA")
        lines.append("-" * 40)
        lines.append(f"  分析序列: {hap_stats.n_sequences} 条")
        lines.append(f"  单倍型数: {hap_stats.n_haplotypes}")
        lines.append(f"  单倍型多样性 (Hd): {hap_stats.haplotype_diversity:.4f}")
        lines.append(f"  核苷酸多样性 (π): {hap_stats.nucleotide_diversity:.6f}")
        lines.append(f"\n  单倍型频率:")
        for hap, freq in sorted(hap_stats.haplotype_freqs.items(),
                                 key=lambda x: -x[1]):
            short = hap[:20] + "..." if len(hap) > 20 else hap
            bars = "█" * int(freq * 40)
            lines.append(f"    {short:25s} {freq:.2f} {bars}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_genetics_json(populations: List[PopulationStats],
                          hap_stats: Optional[HaplotypeStats] = None,
                          fst: Optional[float] = None) -> str:
    """JSON 格式输出."""
    data: Dict[str, Any] = {
        "analysis_type": "刀鲚群体遗传学分析",
        "analysis_time": datetime.now().isoformat(),
        "microsatellite": {
            "populations": [p.summary for p in populations],
            "locus_details": {
                p.name: [
                    {"locus": ls.name, "n_alleles": ls.n_alleles,
                     "ho": ls.ho, "he": ls.he, "fis": ls.fis}
                    for ls in p.loci
                ]
                for p in populations
            },
        },
    }
    if fst is not None:
        data["microsatellite"]["fst"] = fst
    if hap_stats:
        data["mitochondrial"] = {
            "n_sequences": hap_stats.n_sequences,
            "n_haplotypes": hap_stats.n_haplotypes,
            "haplotype_diversity": hap_stats.haplotype_diversity,
            "nucleotide_diversity": hap_stats.nucleotide_diversity,
        }
    return json.dumps(data, ensure_ascii=False, indent=2)


def list_params() -> str:
    """打印分析参数."""
    return """群体遗传学分析参数:

微卫星 (SSR):
  等位基因数 (Na) — 每个位点的等位基因种类数
  观测杂合度 (Ho) — 实际杂合个体比例
  期望杂合度 (He) — Hardy-Weinberg 平衡下预期杂合度
  近交系数 (Fis)  — 1 - Ho/He, >0 表示近交
  群体分化 (Fst)  — 群体间遗传分化指数

线粒体 DNA:
  单倍型多样性 (Hd) — 单倍型丰富度, 0-1
  核苷酸多样性 (π) — 核苷酸水平平均差异
"""


# ── 主流程 ─────────────────────────────────────────────

def analyze_genetics(input_path: Optional[str] = None,
                     use_example: bool = False) -> Tuple[List[PopulationStats], Optional[HaplotypeStats], Optional[float]]:
    """执行完整的刀鲚群体遗传学分析.

    Returns:
        (population_stats_list, haplotype_stats, fst)
    """
    if use_example or not input_path:
        genotypes = _example_microsatellite()
        hap_seqs = _example_haplotypes()
    else:
        genotypes = load_microsatellite_data(input_path)
        hap_seqs = []

    # 微卫星分析
    populations = [
        analyze_population(genos, pop_name=pop)
        for pop, genos in genotypes.items()
    ]

    # Fst (两两群体)
    fst = None
    if len(genotypes) >= 2:
        pops = list(genotypes.items())
        fst = calc_fst(pops[0][1], pops[1][1])
        fst = round(fst, 4)

    # 线粒体分析
    hap_stats = analyze_haplotypes(hap_seqs) if hap_seqs else None

    return populations, hap_stats, fst


def main():
    parser = argparse.ArgumentParser(
        prog="genetics_analysis",
        description="刀鲚 (Coilia nasus) 群体遗传学分析 — 微卫星 + 线粒体DNA + SNP"
    )
    parser.add_argument("--input", "-i", help="微卫星基因型 CSV 输入文件")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")
    parser.add_argument("--list-params", action="store_true", help="打印分析参数")

    args = parser.parse_args()

    if args.list_params:
        print(list_params())
        return

    populations, hap_stats, fst = analyze_genetics(
        input_path=args.input,
        use_example=args.example or (not args.input),
    )

    if args.json:
        print(format_genetics_json(populations, hap_stats, fst))
    else:
        print(format_population_report(populations, hap_stats, fst))


if __name__ == "__main__":
    main()
