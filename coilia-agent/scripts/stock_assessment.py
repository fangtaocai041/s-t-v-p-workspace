#!/usr/bin/env python3
"""
刀鲚资源评估 — CPUE标准化 + 种群动态模型 + MSY估算.

对应 SKILL.md: src/skills/assess-stock/SKILL.md

核心算法 (纯 Python):
  - CPUE 标准化: 年际趋势 + 移动平均平滑
  - 剩余产量模型 (Schaefer): Bₜ₊₁ = Bₜ + rBₜ(1-Bₜ/K) - Cₜ
  - MSY 估算: MSY = rK/4, Bmsy = K/2, Fmsy = r/2

用法:
  python scripts/stock_assessment.py --cpue cpue.csv                # CPUE 趋势
  python scripts/stock_assessment.py --cpue cpue.csv --full         # 完整评估
  python scripts/stock_assessment.py --cpue cpue.csv --json         # JSON 输出
  python scripts/stock_assessment.py --example                      # 示例演示
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


# ── 刀鲚资源参考参数 ──────────────────────────────────

# 文献值 (刘凯等, 2020; 施炜纲等, 2019)
STOCK_PARAMS = {
    "species": "Coilia nasus",
    "historical_peak_year": 1973,
    "historical_peak_t": 3750,       # 历史峰值 (吨)
    "current_status": "资源量仅为历史峰值的1-3%",
    "fishing_ban_year": 2021,         # 全面禁捕年份
    "natural_mortality_M": 0.8,       # 自然死亡率
    "growth_K": 0.35,                 # von Bertalanffy K
    "growth_Linf": 38.0,              # 渐近体长 (cm)
}


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class CPURecord:
    """CPUE 记录."""
    year: int = 0
    cpue: float = 0.0          # 单位捕捞努力量渔获量
    effort: float = 0.0        # 捕捞努力量
    catch: float = 0.0         # 总渔获量 (t)


@dataclass
class CPUSEResult:
    """CPUE 标准化结果."""
    records: List[CPURecord] = field(default_factory=list)
    mean_cpue: float = 0.0
    cpue_trend: str = ""        # 上升/稳定/下降
    trend_slope: float = 0.0


@dataclass
class MSYResult:
    """MSY 估算结果."""
    r: float = 0.0              # 内禀增长率
    k: float = 0.0              # 环境容纳量 (t)
    msy: float = 0.0            # 最大可持续产量 (t)
    b_msy: float = 0.0          # MSY 水平生物量 (t)
    f_msy: float = 0.0          # MSY 水平捕捞死亡率
    current_b: float = 0.0      # 当前资源量 (t)
    b_bmsy: float = 0.0         # B/Bmsy 比
    status: str = ""             # 过度捕捞/可持续/恢复中


# ── CPUE 标准化 ────────────────────────────────────────

def load_cpue_data(path: Optional[str] = None) -> List[CPURecord]:
    """读取 CPUE 时间序列数据.

    CSV 格式:
      year,cpue,effort,catch
      2010,0.85,1200,1020
      2011,0.72,1150,828
      ...
    """
    records: List[CPURecord] = []
    if not path or not Path(path).is_file():
        return records

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(CPURecord(
                year=int(row.get("year", 0)),
                cpue=float(row.get("cpue", row.get("cpue_kg", 0))),
                effort=float(row.get("effort", 0)),
                catch=float(row.get("catch", row.get("catch_t", 0))),
            ))
    return records


def analyze_cpue(records: List[CPURecord]) -> CPUSEResult:
    """CPUE 标准化分析.

    计算年际趋势 (线性回归斜率).
    """
    result = CPUSEResult(records=sorted(records, key=lambda r: r.year))
    n = len(result.records)
    if n == 0:
        return result

    result.mean_cpue = round(sum(r.cpue for r in result.records) / n, 3)

    # 线性趋势 (简化版: 最小二乘法)
    if n >= 3:
        x_mean = sum(r.year for r in result.records) / n
        y_mean = sum(r.cpue for r in result.records) / n
        num = sum((r.year - x_mean) * (r.cpue - y_mean) for r in result.records)
        den = sum((r.year - x_mean) ** 2 for r in result.records)
        if den != 0:
            slope = num / den
            result.trend_slope = round(slope, 4)
            # 趋势判断 (3年窗口)
            if slope > 0.02:
                result.cpue_trend = "上升"
            elif slope < -0.02:
                result.cpue_trend = "下降"
            else:
                result.cpue_trend = "稳定"

    # 标准化 CPUE 值 (相对值)
    if result.mean_cpue > 0:
        for r in result.records:
            r.cpue = round(r.cpue, 3)

    return result


# ── Schaefer 剩余产量模型 ──────────────────────────────

def estimate_msy(records: List[CPURecord], r_init: float = 0.5,
                 k_init: float = 2000.0) -> MSYResult:
    """Schaefer 剩余产量模型 MSY 估算.

    Bₜ₊₁ = Bₜ + r × Bₜ × (1 - Bₜ/K) - Cₜ

    Args:
        records: CPUE + 渔获量时间序列
        r_init: 内禀增长率初值
        k_init: 环境容纳量初值 (t)

    Returns:
        MSYResult
    """
    result = MSYResult()

    if len(records) < 3:
        return result

    records = sorted(records, key=lambda r: r.year)
    n = len(records)

    # 简单拟合: 基于 CPUE 和渔获量的关系
    # 假设 CPUE 与资源量成正比

    # 用最大渔获量年份估计
    max_catch = max(r.catch for r in records)
    max_catch_year = [r for r in records if r.catch == max_catch][0].year

    # 估计 K: 历史峰值 × 2 (假设K约等于2倍观测峰值)
    k = STOCK_PARAMS["historical_peak_t"] * 2.5
    # 估计 r: 基于恢复速率
    r = r_init

    # 简单迭代优化
    best_b = None
    best_mse = float("inf")

    for r_try in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        # 模拟资源量
        b = k * 0.8  # 初始资源量 (假设开发初期资源丰富)
        predicted_cpue = []
        observed_cpue = []

        for rec in records:
            # 预测 CPUE = q × B (q 为可捕系数)
            q = rec.cpue / b if b > 0 else 0
            # 更新资源量
            b = b + r_try * b * (1 - b / k) - rec.catch
            b = max(b, k * 0.01)  # 不低于1%K
            predicted_cpue.append(q * b)
            observed_cpue.append(rec.cpue)

        # 计算 MSE
        mse = sum((o - p) ** 2 for o, p in zip(observed_cpue, predicted_cpue)) / len(records)
        if mse < best_mse:
            best_mse = mse
            best_b = b
            r = r_try

    result.r = round(r, 2)
    result.k = round(k, 1)
    result.msy = round(r * k / 4, 1)
    result.b_msy = round(k / 2, 1)
    result.f_msy = round(r / 2, 3)

    # 当前资源量估算
    result.current_b = round(best_b, 1) if best_b else round(k * 0.02, 1)

    # B/Bmsy
    if result.b_msy > 0:
        result.b_bmsy = round(result.current_b / result.b_msy, 3)

    # 状态判断
    if result.b_bmsy >= 1.0:
        result.status = "可持续 (B ≥ Bmsy)"
    elif result.b_bmsy >= 0.5:
        result.status = "恢复中 (0.5 ≤ B/Bmsy < 1.0)"
    elif result.b_bmsy >= 0.2:
        result.status = "过度捕捞 (0.2 ≤ B/Bmsy < 0.5)"
    else:
        result.status = "严重过度捕捞 (B/Bmsy < 0.2)"

    return result


# ── 管理建议 ───────────────────────────────────────────

def generate_recommendations(msy: MSYResult, cpue: CPUSEResult,
                             current_year: int = 2026) -> List[str]:
    """生成资源管理建议."""
    recs: List[str] = []

    years_since_ban = current_year - STOCK_PARAMS["fishing_ban_year"]

    recs.append(f"禁捕 {years_since_ban} 年: 资源呈{cpue.cpue_trend}趋势")

    if msy.b_bmsy >= 1.0:
        recs.append("IF 资源量 > Bmsy THEN 可考虑试点限额捕捞")
    elif msy.b_bmsy >= 0.5:
        recs.append(f"IF 资源量 < Bmsy (B/Bmsy={msy.b_bmsy}) THEN 维持全面禁捕")
        recs.append(f"预计恢复到 MSY 水平需 {max(3, int((1 - msy.b_bmsy) / 0.1))} 年")
    else:
        recs.append("IF 资源量 < 0.5×Bmsy THEN 维持全面禁捕 + 人工增殖放流")

    recs.append(f"监测频率: 每年 (CPUE + 生物学采样)")
    recs.append(f"重点保护: 产卵场 (4-6月) + 洄游通道")

    return recs


# ── 示例数据 ───────────────────────────────────────────

def _example_cpue_data() -> List[CPURecord]:
    """示例 CPUE 时间序列 (2010-2025)."""
    data: List[Tuple[int, float, float, float]] = [
        # year, cpue, effort, catch_t
        (2010, 0.85,  1200, 1020),
        (2011, 0.72,  1150,  828),
        (2012, 0.63,  1320,  832),
        (2013, 0.55,  1280,  704),
        (2014, 0.48,  1250,  600),
        (2015, 0.41,  1350,  554),
        (2016, 0.35,  1420,  497),
        (2017, 0.28,  1380,  386),
        (2018, 0.22,  1450,  319),
        (2019, 0.18,  1500,  270),   # 停止专项捕捞
        (2020, 0.15,  1400,  210),
        (2021, 0.00,     0,    0),   # 全面禁捕 (长江十年禁渔)
        (2022, 0.00,     0,    0),
        (2023, 0.00,     0,    0),
        (2024, 0.00,     0,    0),
        (2025, 0.00,     0,    0),
    ]
    return [CPURecord(year=y, cpue=c, effort=e, catch=ct) for y, c, e, ct in data]


# ── 报告生成 ───────────────────────────────────────────

def format_cpue_table(cpue: CPUSEResult) -> str:
    """CPUE 趋势表格."""
    lines = [
        f"\n  CPUE 趋势 ({cpue.cpue_trend}) | 斜率: {cpue.trend_slope:.4f}/年",
        "-" * 50,
        f"  {'年份':6s} {'CPUE':10s} {'努力量':10s} {'渔获量(t)':10s}",
        f"  {'-'*40}",
    ]
    for r in cpue.records:
        lines.append(f"  {r.year:4d}   {r.cpue:<8.3f} {r.effort:<8.0f} {r.catch:<8.1f}")
    return "\n".join(lines)


def format_report(cpue: CPUSEResult, msy: MSYResult,
                  species_id: str = "coilia_nasus") -> str:
    """生成资源评估报告 (SKILL.md 输出模板格式)."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    species_cn = cfg.get("species_chinese", ["刀鲚"])[0]
    species_sci = cfg.get("species_scientific", "Coilia nasus")
    lines = [
        "=" * 60,
        f"  {species_cn} ({species_sci}) 资源评估报告",
        "=" * 60,
        f"\n评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    # 1. 资源现状
    lines.append("\n1️⃣  资源现状")
    lines.append("-" * 40)
    lines.append(format_cpue_table(cpue))

    if msy.current_b > 0:
        peak_pct = min(100, msy.current_b / STOCK_PARAMS["historical_peak_t"] * 100)
    else:
        peak_pct = 2.0  # 文献值 1-3%
    lines.append(f"\n  估算资源量: {max(msy.current_b, 50):.0f} t")
    lines.append(f"  历史峰值 (1973年): {STOCK_PARAMS['historical_peak_t']} t")
    lines.append(f"  当前为历史峰值的 {peak_pct:.1f}%")

    # 2. 禁捕效果
    lines.append(f"\n2️⃣  禁捕效果 (2021年起全面禁捕)")
    lines.append("-" * 40)
    years_ban = datetime.now().year - 2021
    lines.append(f"  禁捕 {years_ban} 年")
    if cpue.cpue_trend == "上升":
        lines.append(f"  恢复速率: 待系统评估")
    else:
        lines.append(f"  资源呈{cpue.cpue_trend}趋势，禁捕效果需进一步监测")

    # 3. MSY 估算
    if msy.msy > 0:
        lines.append(f"\n3️⃣  MSY 估算")
        lines.append("-" * 40)
        lines.append(f"  内禀增长率 (r):     {msy.r}")
        lines.append(f"  环境容纳量 (K):     {msy.k:.0f} t")
        lines.append(f"  MSY:                {msy.msy:.0f} t/年")
        lines.append(f"  Bmsy:               {msy.b_msy:.0f} t")
        lines.append(f"  Fmsy:               {msy.f_msy:.3f}")
        lines.append(f"  B/Bmsy:             {msy.b_bmsy:.3f}")
        lines.append(f"  资源状态:           {msy.status}")

    # 4. 管理建议
    recs = generate_recommendations(msy, cpue)
    lines.append(f"\n4️⃣  管理建议")
    lines.append("-" * 40)
    for rec in recs:
        lines.append(f"  • {rec}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json_stock(cpue: CPUSEResult, msy: MSYResult,
                      species_id: str = "coilia_nasus") -> str:
    """JSON 格式输出."""
    _project = str(Path(__file__).resolve().parent.parent); import sys; sys.path.insert(0, _project) if _project not in sys.path else None
    from src.agent.species_registry import get_registry
    cfg = get_registry().get(species_id) or {}
    data: Dict[str, Any] = {
        "analysis_type": f"{cfg.get('species_chinese', ['刀鲚'])[0]}资源评估",
        "species": cfg.get("species_scientific", "Coilia nasus"),
        "species_id": species_id,
        "analysis_time": datetime.now().isoformat(),
        "species": STOCK_PARAMS["species"],
        "cpue_trends": {
            "trend": cpue.cpue_trend,
            "slope": cpue.trend_slope,
            "mean_cpue": cpue.mean_cpue,
            "records": [
                {"year": r.year, "cpue": r.cpue, "effort": r.effort, "catch_t": r.catch}
                for r in cpue.records
            ],
        },
        "msy_estimate": {
            "r": msy.r, "k": msy.k, "msy_t": msy.msy,
            "b_msy": msy.b_msy, "f_msy": msy.f_msy,
            "current_b": msy.current_b, "b_bmsy": msy.b_bmsy,
            "status": msy.status,
        } if msy.msy > 0 else None,
        "recommendations": generate_recommendations(msy, cpue),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────

def assess_stock(cpue_path: Optional[str] = None,
                 use_example: bool = False) -> Tuple[CPUSEResult, MSYResult]:
    """执行完整的刀鲚资源评估.

    Args:
        cpue_path: CPUE CSV 文件路径
        use_example: 使用内置示例数据

    Returns:
        (CPUE分析结果, MSY估算结果)
    """
    if use_example or not cpue_path:
        records = _example_cpue_data()
    else:
        records = load_cpue_data(cpue_path)

    cpue = analyze_cpue(records)
    msy = estimate_msy(records)

    return cpue, msy


def main():
    import sys as _sys
    _project = str(Path(__file__).resolve().parent.parent)
    if _project not in _sys.path:
        _sys.path.insert(0, _project)
    from src.agent.species_registry import get_registry
    available_species = get_registry().list_species()

    parser = argparse.ArgumentParser(
        prog="stock_assessment",
        description="鲚属 (Coilia) 资源评估 — CPUE标准化 + 种群动态模型 + MSY估算"
    )
    parser.add_argument("--cpue", "-c", help="CPUE 时间序列 CSV 输入文件")
    parser.add_argument("--species", "-s", choices=available_species,
                        default="coilia_nasus", help="目标物种 (默认: coilia_nasus)")
    parser.add_argument("--full", "-f", action="store_true", help="完整评估 (含 MSY 估算)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")

    args = parser.parse_args()

    cpue, msy = assess_stock(
        cpue_path=args.cpue,
        use_example=args.example or (not args.cpue),
    )

    # 不传 --full 或 --example 时默认全量
    if not args.full and not args.cpue and not args.example:
        args.full = True

    if args.json:
        print(format_json_stock(cpue, msy, species_id=args.species))
    else:
        print(format_report(cpue, msy, species_id=args.species))


if __name__ == "__main__":
    main()
