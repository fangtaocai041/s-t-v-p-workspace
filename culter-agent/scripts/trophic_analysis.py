#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲌类稳定同位素营养生态位分析 — 营养级估算 + 生态位宽度 + 种间重叠 + 凸包面积.

对应 SKILL.md: src/skills/analyze-trophic/SKILL.md

核心算法 (纯 Python, 无 numpy/scipy):
  - 营养级估算: TL = λ + (δ¹⁵N_consumer - δ¹⁵N_baseline) / Δδ¹⁵N
  - Pianka 生态位重叠指数: O_jk = Σ(p_ij·p_ik) / √(Σp_ij²·Σp_ik²)
  - Levin 标准生态位宽度: Ba = (B-1)/(n-1), B = 1/Σ(p_i²)
  - δ¹³C-δ¹⁵N 双同位素生态位面积 (凸包法, Andrew's Monotone Chain)
  - TEF 分馏因子: δ¹³C = 0.4±1.3‰, δ¹⁵N = 3.4±1.0‰

支持物种:
  - 翘嘴鲌 (Culter alburnus)
  - 蒙古鲌 (Culter mongolicus)
  - 尖头鲌 (Culter oxycephalus)
  - 红鳍原鲌 (Chanodichthys erythropterus)

用法:
  python scripts/trophic_analysis.py --input isotope.csv
  python scripts/trophic_analysis.py --method niche_overlap --example --json
  python scripts/trophic_analysis.py --baseline 8.0 --tef 3.4 --example
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ── 常量 ───────────────────────────────────────────────

# 基线营养级 (初级消费者)
DEFAULT_BASELINE_TROPHIC_LEVEL = 2.0   # λ

# 每营养级 δ¹⁵N 富集因子 (常用 3.4‰)
DEFAULT_DELTA_N15 = 3.4                 # Δδ¹⁵N

# TEF (Trophic Enrichment Factor)
TEF_C13_MEAN = 0.4       # δ¹³C 分馏均值 (‰)
TEF_C13_SD = 1.3         # δ¹³C 分馏标准差
TEF_N15_MEAN = 3.4       # δ¹⁵N 分馏均值 (‰)
TEF_N15_SD = 1.0         # δ¹⁵N 分馏标准差

# 生态位重叠显著阈值
OVERLAP_THRESHOLD = 0.6

# 凸包计算浮点容差
EPS = 1e-9


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class IsotopeSample:
    """单个稳定同位素样本."""
    species: str = ""
    sample_id: str = ""
    d13c: float = 0.0            # δ¹³C (‰, VPDB)
    d15n: float = 0.0            # δ¹⁵N (‰, AIR)
    tissue: str = "肌肉"         # 组织类型
    group: str = ""              # 分组 (季节/体长/栖息地)
    c_n_ratio: float = 0.0       # C:N 比
    length_cm: Optional[float] = None   # 体长 (cm, 可选)
    weight_g: Optional[float] = None    # 体重 (g, 可选)


@dataclass
class TrophicResult:
    """营养级分析结果."""
    species: str = ""
    n_samples: int = 0
    mean_d13c: float = 0.0
    sd_d13c: float = 0.0
    mean_d15n: float = 0.0
    sd_d15n: float = 0.0
    trophic_level: float = 0.0           # TL
    trophic_level_sd: float = 0.0        # TL 不确定性
    baseline_d15n: float = 0.0           # 使用的基线 δ¹⁵N
    delta_n15: float = DEFAULT_DELTA_N15  # 使用的 Δδ¹⁵N


@dataclass
class NicheOverlap:
    """生态位重叠分析结果."""
    species_a: str = ""
    species_b: str = ""
    pianka_overlap: float = 0.0          # Pianka O_jk
    schoener_overlap: float = 0.0         # Schoener α
    is_significant: bool = False         # 是否 ≥ 0.6 显著重叠
    n_dimensions: int = 2


@dataclass
class NicheMetrics:
    """综合生态位指标."""
    species: str = ""
    n_samples: int = 0
    levin_index: float = 0.0              # Levin B
    levin_standardized: float = 0.0       # Ba (标准化)
    convex_hull_area: float = 0.0         # 凸包面积 (‰²)
    ellipse_area: float = 0.0             # 标准椭圆面积 (‰², 简易)
    d13c_range: float = 0.0               # δ¹³C 跨度
    d15n_range: float = 0.0               # δ¹⁵N 跨度
    mean_d13c: float = 0.0
    mean_d15n: float = 0.0


# ── 二维凸包计算 (Andrew's Monotone Chain) ───────────

def _cross(o: Tuple[float, float], a: Tuple[float, float],
           b: Tuple[float, float]) -> float:
    """二维叉积 — 判断转向方向."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Andrew's Monotone Chain 算法计算二维凸包.

    Args:
        points: 点集 [(x1, y1), (x2, y2), ...]

    Returns:
        凸包顶点列表 (逆时针方向)
    """
    n = len(points)
    if n <= 2:
        return list(points)

    # 去重 + 排序
    unique = sorted(set(points), key=lambda p: (p[0], p[1]))
    if len(unique) <= 2:
        return unique

    # 下半凸包
    lower: List[Tuple[float, float]] = []
    for p in unique:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= EPS:
            lower.pop()
        lower.append(p)

    # 上半凸包
    upper: List[Tuple[float, float]] = []
    for p in reversed(unique):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= EPS:
            upper.pop()
        upper.append(p)

    # 合并 (去掉首尾重复)
    return lower[:-1] + upper[:-1]


def polygon_area(vertices: List[Tuple[float, float]]) -> float:
    """计算简单多边形面积 (Shoelace formula)."""
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def convex_hull_area(points: List[Tuple[float, float]]) -> float:
    """计算二维凸包面积."""
    hull = convex_hull(points)
    return polygon_area(hull)


# ── 营养级计算 ────────────────────────────────────────

def estimate_trophic_level(d15n_consumer: float,
                           d15n_baseline: float,
                           lambda_val: float = DEFAULT_BASELINE_TROPHIC_LEVEL,
                           delta_n: float = DEFAULT_DELTA_N15) -> float:
    """估算个体营养级.

    TL = λ + (δ¹⁵N_consumer - δ¹⁵N_baseline) / Δδ¹⁵N
    """
    return lambda_val + (d15n_consumer - d15n_baseline) / delta_n


def analyze_trophic_level(samples: List[IsotopeSample],
                          baseline_d15n: float,
                          baseline_level: float = DEFAULT_BASELINE_TROPHIC_LEVEL,
                          delta_n: float = DEFAULT_DELTA_N15) -> TrophicResult:
    """批量营养级分析.

    Args:
        samples: 同位素样本列表 (单物种)
        baseline_d15n: 基线生物 δ¹⁵N 值
        baseline_level: 基线生物营养级 (λ)
        delta_n: 每营养级 δ¹⁵N 富集因子 (Δδ¹⁵N)

    Returns:
        TrophicResult
    """
    result = TrophicResult(baseline_d15n=baseline_d15n, delta_n15=delta_n)
    if not samples:
        return result

    species = samples[0].species
    n = len(samples)

    result.species = species
    result.n_samples = n

    d13c_vals = [s.d13c for s in samples]
    d15n_vals = [s.d15n for s in samples]

    result.mean_d13c = round(sum(d13c_vals) / n, 4)
    result.mean_d15n = round(sum(d15n_vals) / n, 4)

    # 标准差
    if n > 1:
        result.sd_d13c = round(math.sqrt(
            sum((v - result.mean_d13c) ** 2 for v in d13c_vals) / (n - 1)
        ), 4)
        result.sd_d15n = round(math.sqrt(
            sum((v - result.mean_d15n) ** 2 for v in d15n_vals) / (n - 1)
        ), 4)

    # 个体营养级
    tl_vals = [estimate_trophic_level(d15n, baseline_d15n, baseline_level, delta_n)
               for d15n in d15n_vals]
    result.trophic_level = round(sum(tl_vals) / n, 4)
    if n > 1:
        result.trophic_level_sd = round(math.sqrt(
            sum((tl - result.trophic_level) ** 2 for tl in tl_vals) / (n - 1)
        ), 4)

    return result


# ── 生态位重叠指数 ────────────────────────────────────

def pianka_overlap(p_ij: Sequence[float], p_ik: Sequence[float]) -> float:
    """Pianka (1973) 生态位重叠指数.

    O_jk = Σ(p_ij · p_ik) / √(Σp_ij² · Σp_ik²)

    Args:
        p_ij: 物种 j 在各饵料维度的比例
        p_ik: 物种 k 在各饵料维度的比例

    Returns:
        O_jk ∈ [0, 1]  (0 = 完全分离, 1 = 完全重叠)
    """
    if len(p_ij) != len(p_ik):
        raise ValueError("两个比例向量长度必须相同")

    numerator = sum(p_ij[i] * p_ik[i] for i in range(len(p_ij)))
    sum_sq_j = sum(p ** 2 for p in p_ij)
    sum_sq_k = sum(p ** 2 for p in p_ik)

    denom = math.sqrt(sum_sq_j * sum_sq_k)
    if denom < EPS:
        return 0.0

    return round(numerator / denom, 4)


def schoener_overlap(p_ij: Sequence[float], p_ik: Sequence[float]) -> float:
    """Schoener (1970) 生态位重叠指数.

    α = 1 - 0.5 × Σ|p_ij - p_ik|
    """
    if len(p_ij) != len(p_ik):
        raise ValueError("两个比例向量长度必须相同")

    diff_sum = sum(abs(p_ij[i] - p_ik[i]) for i in range(len(p_ij)))
    return round(max(0.0, 1.0 - 0.5 * diff_sum), 4)


def levin_niche_breadth(proportions: Sequence[float]) -> Tuple[float, float]:
    """Levin (1968) 生态位宽度.

    B = 1 / Σ(p_i²)
    Ba = (B - 1) / (n - 1)

    Args:
        proportions: 各资源维度比例

    Returns:
        (B, Ba) 原始 + 标准化 Levin 指数
    """
    n = len(proportions)
    if n <= 1:
        return 1.0, 0.0

    sum_sq = sum(p ** 2 for p in proportions)
    if sum_sq < EPS:
        return float(n), 1.0

    b = 1.0 / sum_sq
    ba = (b - 1) / (n - 1)
    return round(b, 4), round(max(0.0, min(1.0, ba)), 4)


# ── δ¹³C-δ¹⁵N 同位素生态位面积 ─────────────────────

def _bootstrap_ellipse_area(d13c_vals: Sequence[float],
                            d15n_vals: Sequence[float]) -> float:
    """简易标准椭圆面积 (SEA).

    SEA = π × σ¹³C × σ¹⁵N  (不包含协方差校正).
    """
    n = len(d13c_vals)
    if n < 2:
        return 0.0

    mean_c = sum(d13c_vals) / n
    mean_n = sum(d15n_vals) / n

    var_c = sum((v - mean_c) ** 2 for v in d13c_vals) / (n - 1)
    var_n = sum((v - mean_n) ** 2 for v in d15n_vals) / (n - 1)

    cov = sum((d13c_vals[i] - mean_c) * (d15n_vals[i] - mean_n) for i in range(n)) / (n - 1)

    # 椭圆面积 = π × √(λ₁ × λ₂) = π × √(var_c × var_n - cov²)
    # 此处用标准椭圆: π × σc × σn
    discrimin = var_c * var_n - cov ** 2
    if discrimin < 0:
        discrimin = 0
    return round(math.pi * math.sqrt(discrimin), 4)


def analyze_niche_metrics(samples: List[IsotopeSample]) -> NicheMetrics:
    """计算同位素生态位指标.

    基于 δ¹³C 和 δ¹⁵N 双同位素空间.
    """
    if not samples:
        return NicheMetrics()

    species = samples[0].species
    d13c_vals = [s.d13c for s in samples]
    d15n_vals = [s.d15n for s in samples]
    n = len(samples)

    metrics = NicheMetrics(
        species=species,
        n_samples=n,
    )

    if n < 2:
        metrics.mean_d13c = round(d13c_vals[0], 4) if n else 0.0
        metrics.mean_d15n = round(d15n_vals[0], 4) if n else 0.0
        return metrics

    # 均值
    metrics.mean_d13c = round(sum(d13c_vals) / n, 4)
    metrics.mean_d15n = round(sum(d15n_vals) / n, 4)

    # 范围
    metrics.d13c_range = round(max(d13c_vals) - min(d13c_vals), 4)
    metrics.d15n_range = round(max(d15n_vals) - min(d15n_vals), 4)

    # 凸包面积 — 需要 ≥ 3 个点
    if n >= 3:
        points = list(zip(d13c_vals, d15n_vals))
        metrics.convex_hull_area = round(convex_hull_area(points), 4)

    # 椭圆面积
    metrics.ellipse_area = _bootstrap_ellipse_area(d13c_vals, d15n_vals)

    # Levin 生态位宽度 (基于双同位素分布的离散化)
    # 因连续空间, 使用 1/(1+CV²) 近似; 此处提供基于离散的版本
    metrics.levin_index = round(1.0 / (1.0 + metrics.ellipse_area / 10.0), 4)
    metrics.levin_standardized = metrics.levin_index  # 连续空间下不做标准化

    return metrics


def analyze_niche_overlap(samples_a: List[IsotopeSample],
                          samples_b: List[IsotopeSample],
                          grid_size: int = 15) -> NicheOverlap:
    """计算两物种 δ¹³C-δ¹⁵N 生态位重叠.

    将 δ¹³C-δ¹⁵N 空间网格化, 计算占用频次分布,
    然后应用 Pianka 和 Schoener 公式.

    Args:
        samples_a: 物种 A 样本
        samples_b: 物种 B 样本
        grid_size: 每个维度的网格数

    Returns:
        NicheOverlap
    """
    species_a = samples_a[0].species if samples_a else "物种A"
    species_b = samples_b[0].species if samples_b else "物种B"

    if not samples_a or not samples_b:
        return NicheOverlap(species_a=species_a, species_b=species_b)

    # 确定网格边界 (包围所有点)
    all_c = [s.d13c for s in samples_a] + [s.d13c for s in samples_b]
    all_n = [s.d15n for s in samples_a] + [s.d15n for s in samples_b]

    c_min, c_max = min(all_c), max(all_c)
    n_min, n_max = min(all_n), max(all_n)

    # 扩展边界 +5% 防止边界点沉积
    c_pad = (c_max - c_min) * 0.05 + 0.1
    n_pad = (n_max - n_min) * 0.05 + 0.1
    c_min -= c_pad
    c_max += c_pad
    n_min -= n_pad
    n_max += n_pad

    c_step = (c_max - c_min) / grid_size
    n_step = (n_max - n_min) / grid_size

    def _grid_occupancy(samps: List[IsotopeSample]) -> List[float]:
        counts = [0.0] * (grid_size * grid_size)
        for s in samps:
            ci = min(int((s.d13c - c_min) / c_step), grid_size - 1)
            ni = min(int((s.d15n - n_min) / n_step), grid_size - 1)
            idx = ci * grid_size + ni
            counts[idx] += 1.0
        total = max(sum(counts), 1.0)
        return [c / total for c in counts]

    p_a = _grid_occupancy(samples_a)
    p_b = _grid_occupancy(samples_b)

    pianka = pianka_overlap(p_a, p_b)
    schoener = schoener_overlap(p_a, p_b)

    return NicheOverlap(
        species_a=species_a,
        species_b=species_b,
        pianka_overlap=pianka,
        schoener_overlap=schoener,
        is_significant=(pianka >= OVERLAP_THRESHOLD or schoener >= OVERLAP_THRESHOLD),
    )


# ── 数据加载 ───────────────────────────────────────────

def load_isotope_data(path: Optional[str] = None) -> List[IsotopeSample]:
    """从 CSV 读取稳定同位素数据.

    CSV 格式:
      species,sample_id,d13c,d15n,tissue,group,c_n_ratio,length_cm,weight_g
      翘嘴鲌,A01,-22.5,14.2,肌肉,成鱼,3.2,45.0,1200
      ...
    """
    samples: List[IsotopeSample] = []
    if not path or not Path(path).is_file():
        return samples

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            length = None
            if row.get("length_cm") and row["length_cm"].strip():
                try:
                    length = float(row["length_cm"])
                except ValueError:
                    pass
            weight = None
            if row.get("weight_g") and row["weight_g"].strip():
                try:
                    weight = float(row["weight_g"])
                except ValueError:
                    pass

            samples.append(IsotopeSample(
                species=row.get("species", ""),
                sample_id=row.get("sample_id", row.get("id", "")),
                d13c=float(row.get("d13c", 0)),
                d15n=float(row.get("d15n", 0)),
                tissue=row.get("tissue", "肌肉"),
                group=row.get("group", ""),
                c_n_ratio=float(row.get("c_n_ratio", 0)),
                length_cm=length,
                weight_g=weight,
            ))
    return samples


# ── 内置示例数据 ──────────────────────────────────────

# 4 种鲌类的典型稳定同位素参考值 (淡水湖泊环境)
SPECIES_ISOTOPE_PROFILES: Dict[str, Dict[str, Any]] = {
    "culter_alburnus": {
        "chinese": "翘嘴鲌",
        "scientific": "Culter alburnus",
        "d13c_mean": -22.5,
        "d13c_sd": 1.5,
        "d15n_mean": 14.0,
        "d15n_sd": 1.2,
        "n": 10,
        "trophic_niche": "顶级捕食者 (TL 3.8-4.5)",
        "source": "长江中下游湖泊",
    },
    "culter_mongolicus": {
        "chinese": "蒙古鲌",
        "scientific": "Culter mongolicus",
        "d13c_mean": -24.0,
        "d13c_sd": 1.0,
        "d15n_mean": 12.0,
        "d15n_sd": 1.0,
        "n": 10,
        "trophic_niche": "高级捕食者 (TL 3.2-3.8)",
        "source": "长江中下游 (梁子湖/洞庭湖)",
    },
    "culter_oxycephalus": {
        "chinese": "尖头鲌",
        "scientific": "Culter oxycephalus",
        "d13c_mean": -23.0,
        "d13c_sd": 1.2,
        "d15n_mean": 12.8,
        "d15n_sd": 1.1,
        "n": 10,
        "trophic_niche": "高级捕食者 (TL 3.3-4.0)",
        "source": "长江中上游支流",
    },
    "chanodichthys_erythropterus": {
        "chinese": "红鳍原鲌",
        "scientific": "Chanodichthys erythropterus",
        "d13c_mean": -23.5,
        "d13c_sd": 1.0,
        "d15n_mean": 11.0,
        "d15n_sd": 0.9,
        "n": 10,
        "trophic_niche": "中级捕食者 (TL 2.8-3.5)",
        "source": "长江中下游及东亚水体",
    },
}

# 饵料源同位素参考值 (淡水湖泊)
PREY_ISOTOPE_BASELINE: Dict[str, Dict[str, float]] = {
    "鱼类 (小型)": {"d13c": -22.0, "d15n": 13.0, "proportion": 0.45},
    "虾类": {"d13c": -23.0, "d15n": 11.0, "proportion": 0.25},
    "水生昆虫": {"d13c": -25.0, "d15n": 8.0, "proportion": 0.20},
    "浮游动物": {"d13c": -26.0, "d15n": 6.0, "proportion": 0.10},
}


def _generate_isotope_samples(mean_c: float, sd_c: float,
                               mean_n: float, sd_n: float,
                               species: str, n: int = 10) -> List[IsotopeSample]:
    """生成模拟同位素样本."""
    import random as _random
    samples: List[IsotopeSample] = []
    for i in range(n):
        samples.append(IsotopeSample(
            species=species,
            sample_id=f"{species[:3].upper()}-{i+1:02d}",
            d13c=round(_random.gauss(mean_c, sd_c), 2),
            d15n=round(_random.gauss(mean_n, sd_n), 2),
            tissue="肌肉",
            c_n_ratio=round(_random.gauss(3.25, 0.15), 2),
        ))
    return samples


def _example_data_all() -> Dict[str, List[IsotopeSample]]:
    """所有 4 种鲌类的示例同位素数据."""
    import random as _random
    _random.seed(42)
    result: Dict[str, List[IsotopeSample]] = {}
    for key, info in SPECIES_ISOTOPE_PROFILES.items():
        result[key] = _generate_isotope_samples(
            mean_c=info["d13c_mean"], sd_c=info["d13c_sd"],
            mean_n=info["d15n_mean"], sd_n=info["d15n_sd"],
            species=info["chinese"],
            n=info["n"],
        )
    return result


# ── 报告生成 ───────────────────────────────────────────

def format_trophic_report(trophic: TrophicResult) -> str:
    """格式化营养级分析报告."""
    lines = [
        f"\n  🎯 营养级分析 — {trophic.species}",
        "-" * 58,
        f"  样本数:      {trophic.n_samples}",
        f"  δ¹³C 均值:   {trophic.mean_d13c:.2f} ± {trophic.sd_d13c:.2f}‰",
        f"  δ¹⁵N 均值:   {trophic.mean_d15n:.2f} ± {trophic.sd_d15n:.2f}‰",
        f"  基线 δ¹⁵N:   {trophic.baseline_d15n:.2f}‰",
        f"  Δδ¹⁵N:       {trophic.delta_n15:.2f}‰",
        f"  营养级 (TL):  {trophic.trophic_level:.2f} ± {trophic.trophic_level_sd:.2f}",
    ]
    return "\n".join(lines)


def format_niche_metrics_report(metrics: NicheMetrics) -> str:
    """格式化生态位指标报告."""
    lines = [
        f"\n  🕸️  生态位指标 — {metrics.species}",
        "-" * 58,
        f"  样本数:          {metrics.n_samples}",
        f"  δ¹³C 均值:       {metrics.mean_d13c:.2f}‰",
        f"  δ¹⁵N 均值:       {metrics.mean_d15n:.2f}‰",
        f"  δ¹³C 跨度:       {metrics.d13c_range:.2f}‰",
        f"  δ¹⁵N 跨度:       {metrics.d15n_range:.2f}‰",
        f"  凸包面积 (TA):    {metrics.convex_hull_area:.4f} ‰²",
        f"  椭圆面积 (SEA):   {metrics.ellipse_area:.4f} ‰²",
        f"  Levin 指数 (B):   {metrics.levin_index:.4f}",
    ]
    return "\n".join(lines)


def format_overlap_report(overlap: NicheOverlap) -> str:
    """格式化生态位重叠报告."""
    sig_mark = " ✓ 显著" if overlap.is_significant else ""
    lines = [
        f"\n  🔀 生态位重叠 — {overlap.species_a} ↔ {overlap.species_b}",
        "-" * 58,
        f"  Pianka O_jk:     {overlap.pianka_overlap:.4f}{sig_mark}",
        f"  Schoener α:      {overlap.schoener_overlap:.4f}{sig_mark}",
        f"  重叠阈值:        {OVERLAP_THRESHOLD} (≥ 此值视为显著)",
        f"  网格维度:        {overlap.n_dimensions}D (δ¹³C × δ¹⁵N)",
    ]
    return "\n".join(lines)


def format_trophic_report_full(
    trophic_results: Dict[str, TrophicResult],
    niche_metrics: Dict[str, NicheMetrics],
    overlaps: List[NicheOverlap],
    baseline_d15n: float,
    delta_n: float,
) -> str:
    """生成完整营养生态位分析报告."""
    lines = [
        "=" * 60,
        "  鲌类稳定同位素营养生态位分析报告",
        "=" * 60,
        f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"基线 δ¹⁵N: {baseline_d15n:.2f}‰",
        f"Δδ¹⁵N:     {delta_n:.2f}‰",
        f"TEF δ¹³C:  {TEF_C13_MEAN:.1f} ± {TEF_C13_SD:.1f}‰",
        f"TEF δ¹⁵N:  {TEF_N15_MEAN:.1f} ± {TEF_N15_SD:.1f}‰",
    ]

    lines.append("\n1️⃣  营养级估算")
    lines.append("-" * 40)
    for key in sorted(trophic_results.keys()):
        lines.append(format_trophic_report(trophic_results[key]))

    lines.append("\n2️⃣  同位素生态位指标")
    lines.append("-" * 40)
    for key in sorted(niche_metrics.keys()):
        lines.append(format_niche_metrics_report(niche_metrics[key]))

    if overlaps:
        lines.append("\n3️⃣  种间生态位重叠")
        lines.append("-" * 40)
        for ov in overlaps:
            lines.append(format_overlap_report(ov))

    # 饵料源贡献参考
    lines.append("\n4️⃣  饵料源参考值")
    lines.append("-" * 40)
    lines.append(f"  {'饵料源':12s}  {'δ¹³C (‰)':>10s}  {'δ¹⁵N (‰)':>10s}  {'参考比例':>10s}")
    lines.append(f"  {'-'*42}")
    for prey, vals in PREY_ISOTOPE_BASELINE.items():
        lines.append(f"  {prey:12s}  {vals['d13c']:>10.1f}  {vals['d15n']:>10.1f}  {vals['proportion']:>10.1%}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_trophic_json(
    trophic_results: Dict[str, TrophicResult],
    niche_metrics: Dict[str, NicheMetrics],
    overlaps: List[NicheOverlap],
) -> str:
    """JSON 格式输出."""
    data: Dict[str, Any] = {
        "analysis_type": "稳定同位素营养生态位分析",
        "analysis_time": datetime.now().isoformat(),
        "tef": {
            "d13c_mean": TEF_C13_MEAN,
            "d13c_sd": TEF_C13_SD,
            "d15n_mean": TEF_N15_MEAN,
            "d15n_sd": TEF_N15_SD,
        },
        "trophic_levels": {
            key: {
                "species": tr.species,
                "n_samples": tr.n_samples,
                "mean_d13c": tr.mean_d13c,
                "mean_d15n": tr.mean_d15n,
                "trophic_level": tr.trophic_level,
                "trophic_level_sd": tr.trophic_level_sd,
                "baseline_d15n": tr.baseline_d15n,
            }
            for key, tr in trophic_results.items()
        },
        "niche_metrics": {
            key: {
                "species": nm.species,
                "n_samples": nm.n_samples,
                "convex_hull_area_permil2": nm.convex_hull_area,
                "ellipse_area_permil2": nm.ellipse_area,
                "levin_index": nm.levin_index,
                "d13c_range": nm.d13c_range,
                "d15n_range": nm.d15n_range,
            }
            for key, nm in niche_metrics.items()
        },
        "niche_overlaps": [
            {
                "species_a": ov.species_a,
                "species_b": ov.species_b,
                "pianka_overlap": ov.pianka_overlap,
                "schoener_overlap": ov.schoener_overlap,
                "is_significant": ov.is_significant,
            }
            for ov in overlaps
        ],
        "prey_sources": [
            {"name": k, "d13c": v["d13c"], "d15n": v["d15n"]}
            for k, v in PREY_ISOTOPE_BASELINE.items()
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────

def analyze_trophic(
    samples: List[IsotopeSample],
    baseline_d15n: float,
    baseline_level: float = DEFAULT_BASELINE_TROPHIC_LEVEL,
    delta_n: float = DEFAULT_DELTA_N15,
    method: str = "all",
) -> Tuple[Dict[str, TrophicResult], Dict[str, NicheMetrics], List[NicheOverlap]]:
    """执行完整的稳定同位素营养生态位分析.

    Args:
        samples: 所有同位素样本
        baseline_d15n: 基线 δ¹⁵N
        baseline_level: 基线营养级 λ
        delta_n: 富集因子 Δδ¹⁵N
        method: 分析模式

    Returns:
        (trophic_results, niche_metrics, overlaps)
    """
    # 按物种分组
    species_groups: Dict[str, List[IsotopeSample]] = {}
    for s in samples:
        species_groups.setdefault(s.species, []).append(s)

    species_keys = sorted(species_groups.keys())

    trophic_results: Dict[str, TrophicResult] = {}
    niche_metrics: Dict[str, NicheMetrics] = {}
    overlaps: List[NicheOverlap] = []

    for key in species_keys:
        group = species_groups[key]

        if method in ("trophic_level", "all"):
            trophic_results[key] = analyze_trophic_level(
                group, baseline_d15n, baseline_level, delta_n
            )

        if method in ("convex_hull", "all"):
            niche_metrics[key] = analyze_niche_metrics(group)

    # 种间重叠 (需要至少 2 个物种)
    if method in ("niche_overlap", "all") and len(species_keys) >= 2:
        for i in range(len(species_keys)):
            for j in range(i + 1, len(species_keys)):
                a, b = species_keys[i], species_keys[j]
                ov = analyze_niche_overlap(species_groups[a], species_groups[b])
                overlaps.append(ov)

    return trophic_results, niche_metrics, overlaps


def run_example_demo(method: str = "all",
                     baseline_d15n: float = 7.0,
                     delta_n: float = 3.4,
                     as_json: bool = False) -> None:
    """运行内置示例数据完整分析."""
    all_data = _example_data_all()
    all_samples: List[IsotopeSample] = []
    for key, samps in all_data.items():
        all_samples.extend(samps)

    print("=" * 60)
    print("  鲌类稳定同位素营养生态位 — 示例演示")
    print("=" * 60)
    print(f"  总样本数: {len(all_samples)}")
    print(f"  物种数:   {len(all_data)}")
    print(f"  方法:     {method}")
    print(f"  基线 δ¹⁵N: {baseline_d15n:.1f}‰")
    print(f"  Δδ¹⁵N:     {delta_n:.1f}‰")
    print()

    # 逐物种展示参考信息
    for key, info in SPECIES_ISOTOPE_PROFILES.items():
        print(f"  🐟 {info['chinese']} ({info['scientific']})")
        print(f"     δ¹³C: {info['d13c_mean']:.1f} ± {info['d13c_sd']:.1f}‰")
        print(f"     δ¹⁵N: {info['d15n_mean']:.1f} ± {info['d15n_sd']:.1f}‰")
        print(f"     生态位: {info['trophic_niche']}")
        print(f"     来源: {info['source']}")
        print()

    trophic_results, niche_metrics, overlaps = analyze_trophic(
        all_samples,
        baseline_d15n=baseline_d15n,
        delta_n=delta_n,
        method=method,
    )

    if as_json:
        print(format_trophic_json(trophic_results, niche_metrics, overlaps))
    else:
        print(format_trophic_report_full(
            trophic_results, niche_metrics, overlaps,
            baseline_d15n, delta_n
        ))


def main():
    parser = argparse.ArgumentParser(
        prog="trophic_analysis",
        description="鲌类 (Culter spp.) 稳定同位素营养生态位分析 — 营养级 + 生态位宽度 + 种间重叠 + 凸包面积",
    )
    parser.add_argument("--input", "-i", help="稳定同位素 CSV 输入文件 (列: species, d13c, d15n)")
    parser.add_argument("--baseline", type=float, default=7.0,
                        help="基线生物 δ¹⁵N 值 (默认: 7.0‰, 对应浮游动物)")
    parser.add_argument("--tef", type=float, default=3.4,
                        help="每营养级 δ¹⁵N 富集因子 (默认: 3.4‰)")
    parser.add_argument("--method", "-m",
                        choices=["trophic_level", "niche_overlap", "convex_hull", "all"],
                        default="all",
                        help="分析模式 (默认: all)")
    parser.add_argument("--example", action="store_true",
                        help="使用内置示例数据运行完整演示")
    parser.add_argument("--json", "-j", action="store_true",
                        help="JSON 格式输出")

    args = parser.parse_args()

    # --example 模式
    if args.example:
        run_example_demo(
            method=args.method,
            baseline_d15n=args.baseline,
            delta_n=args.tef,
            as_json=args.json,
        )
        return

    # --input 模式
    if args.input:
        samples = load_isotope_data(args.input)
        if not samples:
            print(f"错误: 未能从 '{args.input}' 读取数据或文件为空")
            return

        trophic_results, niche_metrics, overlaps = analyze_trophic(
            samples,
            baseline_d15n=args.baseline,
            delta_n=args.tef,
            method=args.method,
        )

        if args.json:
            print(format_trophic_json(trophic_results, niche_metrics, overlaps))
        else:
            print(format_trophic_report_full(
                trophic_results, niche_metrics, overlaps,
                args.baseline, args.tef,
            ))
        return

    # 无参数 — 显示帮助并运行示例
    print("未指定输入文件或 --example。运行内置示例演示...\n")
    run_example_demo(
        method=args.method,
        baseline_d15n=args.baseline,
        delta_n=args.tef,
        as_json=args.json,
    )


if __name__ == "__main__":
    main()
