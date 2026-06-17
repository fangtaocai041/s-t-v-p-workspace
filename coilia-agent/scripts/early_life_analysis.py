#!/usr/bin/env python3
"""
刀鲚早期资源与繁殖分析 — 产卵场 + 仔鱼资源 + 繁殖生物学.

对应 SKILL.md: src/skills/analyze-migration/SKILL.md (早期资源主题)

核心算法 (纯 Python):
  - 产卵场适宜性评估: 水温 + 流量 + 底质综合评分
  - 仔鱼资源量估算: 单位水体密度 → 总资源量
  - 补充群体动态: 年际变异系数 + 环境驱动因子分析

用法:
  python scripts/early_life_analysis.py --input larvae.csv         # 读仔鱼数据
  python scripts/early_life_analysis.py --spawning spawning.csv    # 读产卵场数据
  python scripts/early_life_analysis.py --json                     # JSON 输出
  python scripts/early_life_analysis.py --example                  # 示例演示
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── 常量 ───────────────────────────────────────────────

# 刀鲚繁殖参数 (文献值)
SPAWNING_PARAMS = {
    "spawning_season":    "4-6月",
    "peak_spawning":      "5月上旬-6月上旬",
    "spawning_temp":      "18-25°C",
    "optimal_temp":       "20-22°C",
    "spawning_discharge": "10000-30000 m³/s",
    "egg_type":           "浮性卵 (pelagic eggs)",
    "incubation_period":  "36-48小时 (20°C)",
    "first_feeding":      "3-4天 (卵黄囊吸收后)",
}

# 产卵场适宜性评分权重
SUITABILITY_WEIGHTS = {
    "temperature": 0.35,   # 水温权重
    "discharge":   0.30,   # 流量权重
    "substrate":   0.15,   # 底质权重
    "turbidity":   0.10,   # 浊度权重
    "depth":       0.10,   # 水深权重
}


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class LarvalRecord:
    """仔鱼调查单次记录."""
    year: int = 0
    month: int = 0
    station: str = ""
    density: float = 0.0        # 单位: ind./1000m³
    temperature: float = 0.0    # 水温 °C
    discharge: float = 0.0      # 流量 m³/s
    length_mm: float = 0.0      # 平均体长 mm
    species: str = "Coilia nasus"


@dataclass
class SpawningGround:
    """产卵场信息."""
    name: str = ""
    river_section: str = ""
    suitability_score: float = 0.0   # 0-1
    estimated_area_km2: float = 0.0
    key_features: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)


@dataclass
class LarvalStats:
    """仔鱼资源量统计."""
    years: List[int] = field(default_factory=list)
    mean_density: float = 0.0
    max_density: float = 0.0
    min_density: float = 0.0
    cv: float = 0.0                # 年际变异系数
    trend: str = "stable"          # increasing/stable/decreasing
    confidence: str = "medium"


# ── 产卵场适宜性评估 ──────────────────────────────────

def calc_temperature_suitability(temp: float) -> float:
    """水温适宜性评分 (0-1)."""
    lo, hi = 18.0, 25.0
    opt_lo, opt_hi = 20.0, 22.0
    if opt_lo <= temp <= opt_hi:
        return 1.0
    if temp < lo or temp > hi:
        return 0.0
    if temp < opt_lo:
        return (temp - lo) / (opt_lo - lo)
    return (hi - temp) / (hi - opt_hi)


def calc_discharge_suitability(discharge: float) -> float:
    """流量适宜性评分 (0-1)."""
    lo, hi = 10000, 30000
    opt_lo, opt_hi = 15000, 25000
    if opt_lo <= discharge <= opt_hi:
        return 1.0
    if discharge < lo or discharge > hi:
        return 0.3
    if discharge < opt_lo:
        return 0.3 + 0.7 * (discharge - lo) / (opt_lo - lo)
    return 0.3 + 0.7 * (hi - discharge) / (hi - opt_hi)


def assess_spawning_ground(name: str, river_section: str,
                            temp: float, discharge: float,
                            substrate_score: float = 0.7,
                            turbidity_score: float = 0.6,
                            depth_score: float = 0.7) -> SpawningGround:
    """综合评估一个产卵场的适宜性."""
    scores = {
        "temperature": calc_temperature_suitability(temp),
        "discharge": calc_discharge_suitability(discharge),
        "substrate": substrate_score,
        "turbidity": turbidity_score,
        "depth": depth_score,
    }

    total = sum(scores[k] * SUITABILITY_WEIGHTS[k] for k in SUITABILITY_WEIGHTS)

    features = []
    if scores["temperature"] >= 0.8:
        features.append("水温适宜")
    if scores["discharge"] >= 0.8:
        features.append("流量适宜")
    if substrate_score >= 0.7:
        features.append("底质条件良好")

    threats = []
    if scores["discharge"] < 0.5:
        threats.append("流量异常 (可能受水利工程影响)")
    if substrate_score < 0.5:
        threats.append("底质退化")
    threats.append("航运干扰")
    threats.append("捕捞兼捕")

    return SpawningGround(
        name=name,
        river_section=river_section,
        suitability_score=round(total, 3),
        estimated_area_km2=round(50 + total * 100, 1),
        key_features=features,
        threats=threats,
    )


# ── 仔鱼资源量分析 ────────────────────────────────────

def load_larval_data(path: Optional[str] = None) -> List[LarvalRecord]:
    """读取仔鱼调查 CSV 数据.

    CSV 列: year, month, station, density, temperature, discharge, length_mm
    """
    records: List[LarvalRecord] = []
    if not path or not Path(path).is_file():
        return records
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(LarvalRecord(
                year=int(row.get("year", 0)),
                month=int(row.get("month", 0)),
                station=row.get("station", ""),
                density=float(row.get("density", 0)),
                temperature=float(row.get("temperature", 20)),
                discharge=float(row.get("discharge", 15000)),
                length_mm=float(row.get("length_mm", 0)),
            ))
    return records


def analyze_larval_resources(records: List[LarvalRecord]) -> LarvalStats:
    """分析仔鱼资源量."""
    if not records:
        return LarvalStats()

    # 按年份汇总
    yearly: Dict[int, List[float]] = {}
    for r in records:
        yearly.setdefault(r.year, []).append(r.density)

    years = sorted(yearly.keys())
    yearly_means = [sum(v) / len(v) for v in [yearly[y] for y in years]]

    mean_d = sum(yearly_means) / len(yearly_means) if yearly_means else 0
    max_d = max(yearly_means) if yearly_means else 0
    min_d = min(yearly_means) if yearly_means else 0

    # 变异系数
    cv = 0.0
    if mean_d > 0 and len(yearly_means) > 1:
        std = math.sqrt(sum((v - mean_d) ** 2 for v in yearly_means) / (len(yearly_means) - 1))
        cv = std / mean_d

    # 趋势判断 (简单线性: 比较前后半段均值)
    trend = "stable"
    if len(yearly_means) >= 4:
        half = len(yearly_means) // 2
        first_half = sum(yearly_means[:half]) / half
        second_half = sum(yearly_means[half:]) / (len(yearly_means) - half)
        ratio = second_half / first_half if first_half > 0 else 1.0
        if ratio > 1.15:
            trend = "increasing"
        elif ratio < 0.85:
            trend = "decreasing"

    # 置信度
    confidence = "low"
    if len(years) >= 5:
        confidence = "high"
    elif len(years) >= 3:
        confidence = "medium"

    return LarvalStats(
        years=years,
        mean_density=round(mean_d, 1),
        max_density=round(max_d, 1),
        min_density=round(min_d, 1),
        cv=round(cv, 2),
        trend=trend,
        confidence=confidence,
    )


# ── 示例数据 ───────────────────────────────────────────

def _example_larval_records() -> List[LarvalRecord]:
    """示例仔鱼调查数据 (2018-2025)."""
    import random
    random.seed(42)
    records = []
    base_density = {2018: 12.5, 2019: 15.2, 2020: 14.8,
                    2021: 18.5, 2022: 22.3, 2023: 28.7,
                    2024: 32.1, 2025: 35.6}
    for year, base in base_density.items():
        for month in [4, 5, 6]:
            noise = random.uniform(-3, 3)
            records.append(LarvalRecord(
                year=year,
                month=month,
                station="长江口崇明段",
                density=round(max(0.5, base + noise), 1),
                temperature=round(18 + month * 2 + random.uniform(-1, 1), 1),
                discharge=round(20000 + random.uniform(-3000, 3000), 0),
                length_mm=round(8 + month * 3 + random.uniform(-1, 1), 1),
            ))
    return records


def _example_spawning_grounds() -> List[SpawningGround]:
    """示例产卵场."""
    return [
        assess_spawning_ground("长江口崇明段", "长江口南支", 22.5, 28000, 0.8, 0.5, 0.7),
        assess_spawning_ground("靖江段", "长江下游干流", 21.0, 22000, 0.7, 0.6, 0.8),
        assess_spawning_ground("鄱阳湖入江口", "鄱阳湖-长江交汇处", 23.0, 15000, 0.6, 0.7, 0.6),
        assess_spawning_ground("安庆段", "长江下游干流", 20.5, 18000, 0.5, 0.4, 0.5),
    ]


# ── 报告生成 ───────────────────────────────────────────

def format_report(larval_stats: LarvalStats,
                   spawning_grounds: List[SpawningGround],
                   species_id: str = "coilia_nasus") -> str:
    """生成早期资源与繁殖分析报告."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    species_cn = cfg.get("species_chinese", ["刀鲚"])[0]
    species_sci = cfg.get("species_scientific", "Coilia nasus")
    lines = [
        "=" * 60,
        f"  {species_cn} ({species_sci}) 早期资源与繁殖分析报告",
        "=" * 60,
        f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"数据置信度: {larval_stats.confidence}",
    ]

    # 产卵场
    lines.append("\n1️⃣  产卵场评估")
    lines.append("-" * 40)
    for sg in spawning_grounds:
        stars = "█" * int(sg.suitability_score * 20) + "░" * (20 - int(sg.suitability_score * 20))
        lines.append(f"\n  {sg.name} ({sg.river_section})")
        lines.append(f"  适宜性: {sg.suitability_score:.2f}  {stars}")
        lines.append(f"  估算面积: {sg.estimated_area_km2:.0f} km²")
        if sg.key_features:
            lines.append(f"  优势: {', '.join(sg.key_features)}")
        if sg.threats:
            lines.append(f"  威胁: {', '.join(sg.threats[:3])}")

    # 仔鱼资源量
    lines.append("\n2️⃣  仔鱼资源量")
    lines.append("-" * 40)
    lines.append(f"  调查年份: {larval_stats.years}")
    lines.append(f"  平均密度: {larval_stats.mean_density:.1f} ind./1000m³")
    lines.append(f"  密度范围: {larval_stats.min_density:.1f} ~ {larval_stats.max_density:.1f}")
    lines.append(f"  年际变异 (CV): {larval_stats.cv:.2f}")
    trend_icon = {"increasing": "↑", "decreasing": "↓", "stable": "→"}
    lines.append(f"  变化趋势: {trend_icon.get(larval_stats.trend, '?')} {larval_stats.trend}")

    # 繁殖参数
    lines.append("\n3️⃣  繁殖生物学参数")
    lines.append("-" * 40)
    for k, v in SPAWNING_PARAMS.items():
        lines.append(f"  {k}: {v}")

    # 保护建议
    lines.append("\n4️⃣  保护与管理建议")
    lines.append("-" * 40)
    declining_grounds = [sg for sg in spawning_grounds if sg.suitability_score < 0.5]
    if declining_grounds:
        lines.append(f"  ⚠️ {len(declining_grounds)} 个产卵场适宜性偏低，建议优先保护")
    if larval_stats.trend == "increasing":
        lines.append("  ✅ 仔鱼资源呈上升趋势 (可能与禁捕有关)")
    elif larval_stats.trend == "decreasing":
        lines.append("  ⚠️ 仔鱼资源持续下降，需关注补充群体")
    lines.append("  📋 建议: 4-6月产卵期加强核心产卵场保护")
    lines.append("  📋 建议: 持续开展仔鱼资源监测 (每年至少3次)")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json_report(larval_stats: LarvalStats,
                        spawning_grounds: List[SpawningGround],
                        species_id: str = "coilia_nasus") -> str:
    """JSON 格式输出."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    data: Dict[str, Any] = {
        "analysis_type": f"{cfg.get('species_chinese', ['刀鲚'])[0]}早期资源与繁殖分析",
        "species": cfg.get("species_scientific", "Coilia nasus"),
        "species_id": species_id,
        "analysis_time": datetime.now().isoformat(),
        "spawning_grounds": [
            {
                "name": sg.name,
                "river_section": sg.river_section,
                "suitability_score": sg.suitability_score,
                "estimated_area_km2": sg.estimated_area_km2,
                "key_features": sg.key_features,
                "threats": sg.threats,
            }
            for sg in spawning_grounds
        ],
        "larval_resources": {
            "years": larval_stats.years,
            "mean_density": larval_stats.mean_density,
            "max_density": larval_stats.max_density,
            "min_density": larval_stats.min_density,
            "cv": larval_stats.cv,
            "trend": larval_stats.trend,
            "confidence": larval_stats.confidence,
        },
        "spawning_params": SPAWNING_PARAMS,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────

def analyze_early_life(larval_path: Optional[str] = None,
                        use_example: bool = False) -> Tuple[LarvalStats, List[SpawningGround]]:
    """执行完整的刀鲚早期资源与繁殖分析.

    Args:
        larval_path: 仔鱼调查 CSV 文件路径
        use_example: 使用内置示例数据

    Returns:
        (LarvalStats, 产卵场列表)
    """
    if use_example or not larval_path:
        records = _example_larval_records()
        grounds = _example_spawning_grounds()
    else:
        records = load_larval_data(larval_path)
        grounds = [
            assess_spawning_ground("长江口崇明段", "长江口", 22.0, 25000),
            assess_spawning_ground("靖江段", "长江下游", 21.0, 20000),
        ]

    stats = analyze_larval_resources(records)
    return stats, grounds


def main():
    import sys as _sys
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in _sys.path:
        _sys.path.insert(0, _project)
    from src.agent.species_registry import get_registry
    available_species = get_registry().list_species()

    parser = argparse.ArgumentParser(
        prog="early_life_analysis",
        description="鲚属 (Coilia) 早期资源与繁殖分析 — 产卵场 + 仔鱼资源 + 繁殖生物学"
    )
    parser.add_argument("--input", "-i", help="仔鱼调查 CSV 输入文件")
    parser.add_argument("--species", "-s", choices=available_species,
                        default="coilia_nasus", help="目标物种 (默认: coilia_nasus)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")

    args = parser.parse_args()

    stats, grounds = analyze_early_life(
        larval_path=args.input,
        use_example=args.example or (not args.input),
    )

    if args.json:
        print(format_json_report(stats, grounds, species_id=args.species))
    else:
        print(format_report(stats, grounds, species_id=args.species))


if __name__ == "__main__":
    main()
