#!/usr/bin/env python3
"""
刀鲚食性与营养生态分析 — 胃含物 + 稳定同位素 + DNA宏条形码.

对应 SKILL.md: src/skills/analyze-feeding/SKILL.md

核心算法 (纯 Python):
  - 胃含物: 出现频率(F%), 数量百分比(N%), IRI相对重要指数
  - 稳定同位素: δ¹³C/δ¹⁵N, 营养级估算, 生态位宽度
  - Levin's 生态位宽度指数

用法:
  python scripts/feeding_analysis.py --input stomach.csv          # 读胃含物数据
  python scripts/feeding_analysis.py --input isotope.csv --json   # JSON 输出
  python scripts/feeding_analysis.py --example                    # 示例演示
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── 常量 ───────────────────────────────────────────────

# 营养级转换: Δ¹⁵N = 3.4‰ (每营养级富集)
TROPHIC_ENRICHMENT = 3.4
# 基线营养级 (浮游动物/初级消费者)
BASE_TROPHIC_LEVEL = 2.0


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class PreyItem:
    """单个饵料种类."""
    name: str = ""
    frequency: int = 0          # 出现次数 (含该饵料的胃数)
    count: int = 0              # 个体数
    weight: float = 0.0         # 重量 (g)
    f_pct: float = 0.0          # 出现频率 (%)
    n_pct: float = 0.0          # 数量百分比 (%)
    w_pct: float = 0.0          # 重量百分比 (%)
    iri: float = 0.0            # 相对重要指数


@dataclass
class StomachContentResult:
    """胃含物分析结果."""
    n_stomachs: int = 0
    prey_items: List[PreyItem] = field(default_factory=list)
    vacuity_rate: float = 0.0   # 空胃率

    @property
    def dominant_prey(self) -> List[PreyItem]:
        """主要饵料 (IRI 排序前 5)."""
        return sorted(self.prey_items, key=lambda x: -x.iri)[:5]


@dataclass
class IsotopeSample:
    """稳定同位素单样本."""
    species: str = ""
    tissue: str = ""
    d13c: float = 0.0           # δ¹³C (‰)
    d15n: float = 0.0           # δ¹⁵N (‰)
    group: str = ""             # 分组 (季节/体长/栖息地)
    c_n_ratio: float = 0.0      # C:N 比


@dataclass
class IsotopeResult:
    """稳定同位素分析结果."""
    samples: List[IsotopeSample] = field(default_factory=list)
    mean_d13c: float = 0.0
    mean_d15n: float = 0.0
    trophic_level: float = 0.0   # 营养级
    niche_width: float = 0.0     # 生态位宽度 (SEAc)


# ── 胃含物分析 ─────────────────────────────────────────

def load_stomach_data(path: Optional[str] = None) -> Dict[str, List[Dict]]:
    """读取胃含物数据.

    CSV 格式:
      stomach_id,prey_name,count,weight_g,stage
      S01,虾类,3,0.45,成鱼
      S01,小鱼,1,0.30,成鱼
      ...
    """
    groups: Dict[str, List[Dict]] = defaultdict(list)
    if not path or not Path(path).is_file():
        return groups

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = row.get("stage", row.get("group", "全部"))
            groups[group].append({
                "stomach_id": row.get("stomach_id", ""),
                "prey_name": row.get("prey_name", ""),
                "count": float(row.get("count", 0)),
                "weight_g": float(row.get("weight_g", row.get("weight", 0))),
            })
    return groups


def analyze_stomach_content(records: List[Dict]) -> StomachContentResult:
    """分析胃含物数据.

    IRI = (N% + W%) × F%
    """
    result = StomachContentResult()

    # 统计
    stomachs: Dict[str, Dict[str, Any]] = {}  # stomach_id → {prey: count/weight}
    for rec in records:
        sid = rec["stomach_id"]
        if sid not in stomachs:
            stomachs[sid] = {}
        prey = rec["prey_name"]
        if prey not in stomachs[sid]:
            stomachs[sid][prey] = {"count": 0, "weight": 0.0}
        stomachs[sid][prey]["count"] += rec["count"]
        stomachs[sid][prey]["weight"] += rec["weight_g"]

    result.n_stomachs = len(stomachs)

    # 空胃统计
    empty_count = sum(1 for v in stomachs.values() if not v)
    result.vacuity_rate = empty_count / result.n_stomachs if result.n_stomachs > 0 else 0

    # 按饵料汇总
    prey_data: Dict[str, Dict] = {}
    for sid, prey_dict in stomachs.items():
        for prey_name, data in prey_dict.items():
            if prey_name not in prey_data:
                prey_data[prey_name] = {"frequency": 0, "total_count": 0, "total_weight": 0.0}
            prey_data[prey_name]["frequency"] += 1
            prey_data[prey_name]["total_count"] += data["count"]
            prey_data[prey_name]["total_weight"] += data["weight"]

    # 计算百分比
    n_stomachs_nonempty = result.n_stomachs - empty_count
    total_count = sum(d["total_count"] for d in prey_data.values())
    total_weight = sum(d["total_weight"] for d in prey_data.values())

    for name, data in prey_data.items():
        item = PreyItem(name=name)
        item.frequency = data["frequency"]
        item.count = int(data["total_count"])
        item.weight = round(data["total_weight"], 4)

        # F% = 出现次数 / 非空胃数 × 100
        if n_stomachs_nonempty > 0:
            item.f_pct = round(data["frequency"] / n_stomachs_nonempty * 100, 2)

        # N% = 该饵料个体数 / 总个体数 × 100
        if total_count > 0:
            item.n_pct = round(data["total_count"] / total_count * 100, 2)

        # W% = 该饵料重量 / 总重量 × 100
        if total_weight > 0:
            item.w_pct = round(data["total_weight"] / total_weight * 100, 2)

        # IRI = (N% + W%) × F%
        item.iri = round((item.n_pct + item.w_pct) * item.f_pct, 2)

        result.prey_items.append(item)

    # IRI 排序
    result.prey_items.sort(key=lambda x: -x.iri)

    return result


# ── 稳定同位素分析 ─────────────────────────────────────

def load_isotope_data(path: Optional[str] = None) -> List[IsotopeSample]:
    """读取稳定同位素数据.

    CSV 格式:
      species,tissue,d13c,d15n,group,c_n_ratio
      刀鲚,肌肉,-18.5,12.3,成鱼,3.2
      ...
    """
    samples: List[IsotopeSample] = []
    if not path or not Path(path).is_file():
        return samples

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append(IsotopeSample(
                species=row.get("species", "刀鲚"),
                tissue=row.get("tissue", "肌肉"),
                d13c=float(row.get("d13c", 0)),
                d15n=float(row.get("d15n", 0)),
                group=row.get("group", "全部"),
                c_n_ratio=float(row.get("c_n_ratio", 0)),
            ))
    return samples


def analyze_isotopes(samples: List[IsotopeSample],
                     baseline_d15n: float = 8.0) -> IsotopeResult:
    """分析稳定同位素数据.

    Args:
        samples: 同位素样本列表
        baseline_d15n: 基线 δ¹⁵N (浮游动物/初级消费者), 默认 8.0‰

    Returns:
        IsotopeResult
    """
    result = IsotopeResult(samples=samples)
    if not samples:
        return result

    # 均值
    n = len(samples)
    result.mean_d13c = round(sum(s.d13c for s in samples) / n, 2)
    result.mean_d15n = round(sum(s.d15n for s in samples) / n, 2)

    # 营养级: TL = 2 + (δ¹⁵N_consumer - δ¹⁵N_base) / 3.4
    result.trophic_level = round(
        BASE_TROPHIC_LEVEL + (result.mean_d15n - baseline_d15n) / TROPHIC_ENRICHMENT, 2
    )

    # 生态位宽度: 基于 δ¹³C-δ¹⁵N 椭圆面积 (简化版)
    # 使用标准椭圆面积 SEA = π × σ¹³C × σ¹⁵N
    if n > 1:
        var_c = sum((s.d13c - result.mean_d13c) ** 2 for s in samples) / (n - 1)
        var_n = sum((s.d15n - result.mean_d15n) ** 2 for s in samples) / (n - 1)
        # 简单椭圆面积 (忽略协方差)
        result.niche_width = round(math.pi * math.sqrt(var_c) * math.sqrt(var_n), 2)
    else:
        result.niche_width = 0.0

    return result


# ── 示例数据 ───────────────────────────────────────────

def _example_stomach_data() -> Dict[str, List[Dict]]:
    """示例胃含物数据."""
    return {
        "成鱼": [
            {"stomach_id": "A01", "prey_name": "虾类", "count": 3, "weight_g": 0.45},
            {"stomach_id": "A01", "prey_name": "小鱼", "count": 1, "weight_g": 0.30},
            {"stomach_id": "A02", "prey_name": "虾类", "count": 2, "weight_g": 0.38},
            {"stomach_id": "A02", "prey_name": "端足类", "count": 5, "weight_g": 0.12},
            {"stomach_id": "A03", "prey_name": "虾类", "count": 1, "weight_g": 0.22},
            {"stomach_id": "A03", "prey_name": "小鱼", "count": 2, "weight_g": 0.55},
            {"stomach_id": "A04", "prey_name": "多毛类", "count": 4, "weight_g": 0.18},
            {"stomach_id": "A04", "prey_name": "虾类", "count": 1, "weight_g": 0.15},
            {"stomach_id": "A05", "prey_name": "虾类", "count": 2, "weight_g": 0.31},
            {"stomach_id": "A05", "prey_name": "小鱼", "count": 1, "weight_g": 0.28},
        ],
        "幼鱼": [
            {"stomach_id": "J01", "prey_name": "桡足类", "count": 15, "weight_g": 0.05},
            {"stomach_id": "J01", "prey_name": "枝角类", "count": 8, "weight_g": 0.02},
            {"stomach_id": "J02", "prey_name": "桡足类", "count": 12, "weight_g": 0.04},
            {"stomach_id": "J02", "prey_name": "端足类", "count": 3, "weight_g": 0.03},
            {"stomach_id": "J03", "prey_name": "桡足类", "count": 20, "weight_g": 0.06},
            {"stomach_id": "J03", "prey_name": "枝角类", "count": 5, "weight_g": 0.01},
            {"stomach_id": "J04", "prey_name": "桡足类", "count": 10, "weight_g": 0.03},
            {"stomach_id": "J04", "prey_name": "虾类幼体", "count": 2, "weight_g": 0.02},
        ],
    }


def _example_isotope_data() -> List[IsotopeSample]:
    """示例稳定同位素数据 (刀鲚成鱼 vs 幼鱼)."""
    return [
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-17.8, d15n=13.5, group="成鱼", c_n_ratio=3.2),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-18.2, d15n=12.8, group="成鱼", c_n_ratio=3.3),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-17.5, d15n=13.2, group="成鱼", c_n_ratio=3.1),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-18.8, d15n=12.5, group="成鱼", c_n_ratio=3.2),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-17.2, d15n=13.8, group="成鱼", c_n_ratio=3.2),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-19.5, d15n=10.2, group="幼鱼", c_n_ratio=3.4),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-20.1, d15n=9.8, group="幼鱼", c_n_ratio=3.3),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-19.8, d15n=10.5, group="幼鱼", c_n_ratio=3.5),
        IsotopeSample(species="刀鲚", tissue="肌肉", d13c=-20.5, d15n=9.5, group="幼鱼", c_n_ratio=3.4),
    ]


# ── 报告生成 ───────────────────────────────────────────

def format_stomach_report(stomach: StomachContentResult, group_name: str = "全部") -> str:
    """格式化胃含物分析报告."""
    lines = [
        f"\n  🍽️  胃含物分析 — {group_name}",
        "-" * 50,
        f"  分析胃数: {stomach.n_stomachs}",
        f"  空胃率: {stomach.vacuity_rate:.1%}",
        f"  饵料种类: {len(stomach.prey_items)}",
        "",
        f"  {'饵料':12s} {'F%':8s} {'N%':8s} {'W%':8s} {'IRI':10s}",
        f"  {'-'*46}",
    ]
    for item in stomach.prey_items:
        lines.append(f"  {item.name:12s} {item.f_pct:7.1f}% {item.n_pct:7.1f}% {item.w_pct:7.1f}% {item.iri:>8.1f}")
    return "\n".join(lines)


def format_isotope_report(isotope: IsotopeResult, group_name: str = "全部") -> str:
    """格式化稳定同位素分析报告."""
    lines = [
        f"\n  🔬 稳定同位素分析 — {group_name}",
        "-" * 50,
        f"  样本数: {len(isotope.samples)}",
        f"  δ¹³C 均值: {isotope.mean_d13c:.2f}‰",
        f"  δ¹⁵N 均值: {isotope.mean_d15n:.2f}‰",
        f"  营养级: {isotope.trophic_level:.2f}",
        f"  生态位宽度 (SEAc): {isotope.niche_width:.2f}",
    ]
    return "\n".join(lines)


def format_feeding_report(stomach_results: Dict[str, StomachContentResult],
                          isotope_results: Dict[str, IsotopeResult],
                          species_id: str = "coilia_nasus") -> str:
    """生成完整食性分析报告."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    species_cn = cfg.get("species_chinese", ["刀鲚"])[0]
    lines = [
        "=" * 60,
        f"  {species_cn}食性分析报告",
        "=" * 60,
        f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    lines.append("\n1️⃣  胃含物组成")
    lines.append("-" * 40)
    for group, result in stomach_results.items():
        lines.append(format_stomach_report(result, group))

    lines.append("\n2️⃣  营养生态位")
    lines.append("-" * 40)
    for group, result in isotope_results.items():
        lines.append(format_isotope_report(result, group))

    # 食性转变 (多阶段对比)
    if len(stomach_results) > 1:
        lines.append("\n3️⃣  食性转变 (生活史阶段)")
        lines.append("-" * 40)
        for group, result in stomach_results.items():
            tops = ", ".join(p.name for p in result.dominant_prey[:3])
            lines.append(f"  {group}: {tops}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json_feeding(stomach_results: Dict[str, StomachContentResult],
                        isotope_results: Dict[str, IsotopeResult],
                        species_id: str = "coilia_nasus") -> str:
    """JSON 格式输出."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    data: Dict[str, Any] = {
        "analysis_type": f"{cfg.get('species_chinese', ['刀鲚'])[0]}食性分析",
        "species": cfg.get("species_scientific", "Coilia nasus"),
        "species_id": species_id,
        "analysis_time": datetime.now().isoformat(),
        "stomach_content": {
            group: {
                "n_stomachs": s.n_stomachs,
                "vacuity_rate": s.vacuity_rate,
                "n_prey_types": len(s.prey_items),
                "dominant_prey": [{"name": p.name, "iri": p.iri} for p in s.dominant_prey],
                "prey_items": [
                    {"name": p.name, "f_pct": p.f_pct, "n_pct": p.n_pct,
                     "w_pct": p.w_pct, "iri": p.iri}
                    for p in s.prey_items
                ],
            }
            for group, s in stomach_results.items()
        },
        "stable_isotopes": {
            group: {
                "n_samples": len(r.samples),
                "mean_d13c": r.mean_d13c,
                "mean_d15n": r.mean_d15n,
                "trophic_level": r.trophic_level,
                "niche_width": r.niche_width,
            }
            for group, r in isotope_results.items()
        },
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────

def analyze_feeding(input_path: Optional[str] = None,
                    isotope_path: Optional[str] = None,
                    use_example: bool = False) -> Tuple[Dict[str, StomachContentResult], Dict[str, IsotopeResult]]:
    """执行完整的刀鲚食性分析.

    Returns:
        (stomach_results_by_group, isotope_results_by_group)
    """
    if use_example or not input_path:
        stomach_data = _example_stomach_data()
        isotope_samples = _example_isotope_data()
    else:
        stomach_data = load_stomach_data(input_path)
        isotope_samples = load_isotope_data(isotope_path)

    # 胃含物分析 (按阶段分组)
    stomach_results: Dict[str, StomachContentResult] = {}
    for group, records in stomach_data.items():
        stomach_results[group] = analyze_stomach_content(records)

    # 同位素分析 (按分组)
    isotope_results: Dict[str, IsotopeResult] = {}
    groups = set(s.group for s in isotope_samples)
    for group in groups:
        group_samples = [s for s in isotope_samples if s.group == group]
        isotope_results[group] = analyze_isotopes(group_samples)
    # 全部样本
    if isotope_samples:
        isotope_results["全部"] = analyze_isotopes(isotope_samples)

    return stomach_results, isotope_results


def main():
    import sys as _sys
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in _sys.path:
        _sys.path.insert(0, _project)
    from src.agent.species_registry import get_registry
    available_species = get_registry().list_species()

    parser = argparse.ArgumentParser(
        prog="feeding_analysis",
        description="鲚属 (Coilia) 食性与营养生态分析 — 胃含物 + 稳定同位素 + DNA宏条形码"
    )
    parser.add_argument("--input", "-i", help="胃含物 CSV 输入文件")
    parser.add_argument("--isotope", help="稳定同位素 CSV 输入文件")
    parser.add_argument("--species", "-s", choices=available_species,
                        default="coilia_nasus", help="目标物种 (默认: coilia_nasus)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")

    args = parser.parse_args()

    stomach_results, isotope_results = analyze_feeding(
        input_path=args.input,
        isotope_path=args.isotope,
        use_example=args.example or (not args.input and not args.isotope),
    )

    if args.json:
        print(format_json_feeding(stomach_results, isotope_results, species_id=args.species))
    else:
        print(format_feeding_report(stomach_results, isotope_results, species_id=args.species))


if __name__ == "__main__":
    main()
