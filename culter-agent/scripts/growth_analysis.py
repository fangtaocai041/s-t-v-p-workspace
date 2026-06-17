#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲌类 von Bertalanffy 生长方程分析 — Ford-Walford 图解法 + 非线性最小二乘拟合.

对应 SKILL.md: src/skills/analyze-growth/SKILL.md

核心算法 (纯 Python, 无 numpy/scipy):
  - Ford-Walford 图解法: Lt+1 = a + b×Lt, L∞ = a/(1-b), K = -ln(b)
  - 非线性最小二乘 VBGF 拟合: 网格搜索 L∞/K/t0
  - 生长性能指数: φ' = log10(K) + 2×log10(L∞)
  - 体重生长拐点年龄: t拐 = ln((n+1)/1)/K + t0  (n=3)

支持物种:
  - 翘嘴鲌 (Culter alburnus)
  - 蒙古鲌 (Culter mongolicus)
  - 尖头鲌 (Culter oxycephalus)
  - 红鳍原鲌 (Chanodichthys erythropterus)

用法:
  python scripts/growth_analysis.py --input age_length.csv
  python scripts/growth_analysis.py --species culter_alburnus --method nonlinear --json
  python scripts/growth_analysis.py --example
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

# 体重-体长关系指数 (b ≈ 3 为等速生长)
ALLOMETRY_EXPONENT = 3  # n in VBGF weight inflection formula

# 参数搜索范围
LINF_RANGE = (60.0, 120.0)        # cm
K_RANGE = (0.10, 0.35)            # yr⁻¹
T0_RANGE = (-0.5, 0.0)            # yr
GRID_STEPS_LINF = 60               # grid resolution for L∞
GRID_STEPS_K = 50                  # grid resolution for K
GRID_STEPS_T0 = 30                 # grid resolution for t0


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class GrowthParams:
    """VBGF 参数集."""
    linfty: float = 0.0          # L∞ — 渐进体长 (cm)
    k: float = 0.0               # K — 生长系数 (yr⁻¹)
    t0: float = 0.0              # t0 — 理论生长起点年龄 (yr)
    phi_prime: float = 0.0       # φ' — 生长性能指数
    t_inflection: float = 0.0    # t拐 — 体重生长拐点年龄 (yr)
    method: str = ""             # 拟合方法
    r_squared: float = 0.0       # R² (仅线性回归)
    rmse: float = 0.0            # RMSE (cm)

    def __post_init__(self):
        if self.k > 0 and self.linfty > 0:
            self.phi_prime = round(math.log10(self.k) + 2 * math.log10(self.linfty), 4)
        if self.k > 0:
            self.t_inflection = round(math.log(ALLOMETRY_EXPONENT + 1) / self.k + self.t0, 4)

    def predict(self, age: float) -> float:
        """预测给定年龄的体长."""
        return self.linfty * (1 - math.exp(-self.k * (age - self.t0)))

    def predict_ages(self, ages: Sequence[float]) -> List[float]:
        """批量预测."""
        return [self.predict(a) for a in ages]

    def predict_weight(self, age: float, a_coeff: float = 0.01) -> float:
        """预测体重 (W = a·L^b)."""
        length = self.predict(age)
        return a_coeff * (length ** ALLOMETRY_EXPONENT)


@dataclass
class AgeLengthData:
    """年龄-体长观测数据."""
    age: float = 0.0             # 年龄 (yr)
    length_cm: float = 0.0       # 实测体长 (cm)
    weight_g: Optional[float] = None   # 实测体重 (g, 可选)
    n: int = 1                   # 该龄组样本数

    @property
    def length_mm(self) -> float:
        return self.length_cm * 10.0


@dataclass
class VBGFResult:
    """VBGF 分析完整结果."""
    species: str = ""
    method: str = ""
    params: GrowthParams = field(default_factory=GrowthParams)
    data_points: List[AgeLengthData] = field(default_factory=list)
    predicted: List[float] = field(default_factory=list)
    residuals: List[float] = field(default_factory=list)

    @property
    def n_points(self) -> int:
        return len(self.data_points)

    @property
    def max_age(self) -> float:
        return max((d.age for d in self.data_points), default=0)

    def summary(self) -> Dict[str, Any]:
        return {
            "species": self.species,
            "method": self.method,
            "L∞_cm": self.params.linfty,
            "K_yr1": self.params.k,
            "t0_yr": self.params.t0,
            "phi_prime": self.params.phi_prime,
            "t_inflection_yr": self.params.t_inflection,
            "rmse_cm": self.params.rmse,
            "n_points": self.n_points,
            "max_age_yr": round(self.max_age, 2),
        }


# ── Ford-Walford 图解法 ───────────────────────────────

def _make_walford_pairs(data: List[AgeLengthData]) -> List[Tuple[float, float]]:
    """构造 Ford-Walford 配对 (Lt, Lt+1).

    要求年龄间距均匀 (通常 Δt = 1 yr).
    """
    sorted_data = sorted(data, key=lambda d: d.age)
    pairs: List[Tuple[float, float]] = []
    for i in range(len(sorted_data) - 1):
        delta = sorted_data[i + 1].age - sorted_data[i].age
        if abs(delta - 1.0) < 0.3:  # 允许小幅偏差
            pairs.append((sorted_data[i].length_cm, sorted_data[i + 1].length_cm))
    return pairs


def _linear_regression(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, float, float]:
    """纯 Python 一元线性回归 y = a + b·x. 返回 (a, b, r_squared)."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    ss_xy = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    ss_yy = sum((y - mean_y) ** 2 for y in ys)

    if ss_xx == 0:
        return mean_y, 0.0, 0.0

    b = ss_xy / ss_xx
    a = mean_y - b * mean_x

    # R²
    y_pred = [a + b * x for x in xs]
    ss_res = sum((ys[i] - y_pred[i]) ** 2 for i in range(n))
    r_squared = 1 - ss_res / ss_yy if ss_yy > 0 else 0.0

    return a, b, r_squared


def ford_walford_fit(data: List[AgeLengthData]) -> GrowthParams:
    """Ford-Walford 图解法拟合 VBGF 参数.

    原理:
      Lt+1 = a + b × Lt
      其中: L∞ = a / (1 - b)
            K  = -ln(b)

    Args:
        data: 年龄-体长观测数据列表

    Returns:
        GrowthParams 包含 L∞, K, t0=0 (Ford-Walford 无法估计 t0)
    """
    params = GrowthParams(method="Ford-Walford")

    if len(data) < 3:
        return params

    pairs = _make_walford_pairs(data)
    if len(pairs) < 2:
        return params

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    a, b, r_squared = _linear_regression(xs, ys)

    if b <= 0 or b >= 1:
        # 无效斜率
        params.k = 0.0
        params.linfty = 0.0
        params.r_squared = r_squared
        return params

    params.linfty = round(a / (1 - b), 2)
    params.k = round(-math.log(b), 4)
    params.r_squared = round(r_squared, 4)

    # 显式重新计算派生参数 (__post_init__ 在构造时已执行, 此时属性变更不会触发)
    if params.k > 0 and params.linfty > 0:
        params.phi_prime = round(math.log10(params.k) + 2 * math.log10(params.linfty), 4)
        params.t_inflection = round(math.log(ALLOMETRY_EXPONENT + 1) / params.k + params.t0, 4)

    # 计算 RMSE
    predicted = [params.predict(d.age) for d in data]
    se = sum((data[i].length_cm - predicted[i]) ** 2 for i in range(len(data)))
    params.rmse = round(math.sqrt(se / len(data)), 4)

    return params


# ── 非线性最小二乘 VBGF 拟合 ──────────────────────────

def _vbgt_residual(params_tuple: Tuple[float, float, float],
                   data: List[AgeLengthData]) -> float:
    """计算 VBGF 残差平方和."""
    linf, k, t0 = params_tuple
    if k <= 0 or linf <= 0:
        return float("inf")
    sse = 0.0
    for d in data:
        pred = linf * (1 - math.exp(-k * (d.age - t0)))
        sse += (d.length_cm - pred) ** 2
    return sse


def _grid_refine(data: List[AgeLengthData]) -> GrowthParams:
    """网格搜索 + 局部细化 — VBGF 非线性最小二乘拟合.

    策略: 先粗网格确定区域, 再在最优解附近细化.
    """
    best_linf, best_k, best_t0 = 80.0, 0.20, -0.30
    best_sse = float("inf")

    # 阶段 1: 粗网格搜索
    linf_vals = [LINF_RANGE[0] + i * (LINF_RANGE[1] - LINF_RANGE[0]) / GRID_STEPS_LINF
                 for i in range(GRID_STEPS_LINF + 1)]
    k_vals = [K_RANGE[0] + i * (K_RANGE[1] - K_RANGE[0]) / GRID_STEPS_K
              for i in range(GRID_STEPS_K + 1)]
    t0_vals = [T0_RANGE[0] + i * (T0_RANGE[1] - T0_RANGE[0]) / GRID_STEPS_T0
               for i in range(GRID_STEPS_T0 + 1)]

    for linf in linf_vals:
        for k in k_vals:
            for t0 in t0_vals:
                sse = _vbgt_residual((linf, k, t0), data)
                if sse < best_sse:
                    best_sse = sse
                    best_linf, best_k, best_t0 = linf, k, t0

    # 阶段 2: 在最优解附近细化 (局部更密搜索)
    delta_linf = (LINF_RANGE[1] - LINF_RANGE[0]) / GRID_STEPS_LINF
    delta_k = (K_RANGE[1] - K_RANGE[0]) / GRID_STEPS_K
    delta_t0 = (T0_RANGE[1] - T0_RANGE[0]) / GRID_STEPS_T0

    for d_linf in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
        for d_k in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
            for d_t0 in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
                linf = best_linf + d_linf * delta_linf * 0.5
                k = best_k + d_k * delta_k * 0.5
                t0 = best_t0 + d_t0 * delta_t0 * 0.5
                if linf <= 0 or k <= 0:
                    continue
                sse = _vbgt_residual((linf, k, t0), data)
                if sse < best_sse:
                    best_sse = sse
                    best_linf, best_k, best_t0 = linf, k, t0

    params = GrowthParams(
        linfty=round(best_linf, 2),
        k=round(best_k, 4),
        t0=round(best_t0, 4),
        method="nonlinear_ls (grid-search)",
    )
    params.rmse = round(math.sqrt(best_sse / len(data)) if data else 0.0, 4)
    return params


def nonlinear_vbgf_fit(data: List[AgeLengthData]) -> GrowthParams:
    """非线性最小二乘 VBGF 拟合.

    使用网格搜索法寻找最优 L∞, K, t0.
    """
    if len(data) < 3:
        return GrowthParams(method="nonlinear_ls (insufficient data)")

    return _grid_refine(data)


# ── 数据加载 ───────────────────────────────────────────

def load_age_length_data(path: Optional[str] = None) -> List[AgeLengthData]:
    """从 CSV 读取年龄-体长数据.

    CSV 格式:
      age,length_cm,weight_g,n
      1,15.2,,5
      2,28.7,,
      ...
    """
    data: List[AgeLengthData] = []
    if not path or not Path(path).is_file():
        return data

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            weight = None
            if row.get("weight_g") and row["weight_g"].strip():
                try:
                    weight = float(row["weight_g"])
                except ValueError:
                    pass
            n = int(row.get("n", 1))
            data.append(AgeLengthData(
                age=float(row["age"]),
                length_cm=float(row["length_cm"]),
                weight_g=weight,
                n=n,
            ))
    return data


# ── 内置示例数据 ──────────────────────────────────────

# 4 种鲌类的参考 VBGF 参数 (基于文献综合)
REFERENCE_VBGF: Dict[str, Dict[str, Any]] = {
    "culter_alburnus": {
        "chinese": "翘嘴鲌",
        "scientific": "Culter alburnus",
        "linfty": 105.0,
        "k": 0.18,
        "t0": -0.45,
        "source": "长江中下游湖泊 (鄱阳湖/洞庭湖 综合)",
        "max_age": 15,
    },
    "culter_mongolicus": {
        "chinese": "蒙古鲌",
        "scientific": "Culter mongolicus",
        "linfty": 65.0,
        "k": 0.22,
        "t0": -0.40,
        "source": "长江中下游 (梁子湖/洞庭湖 综合)",
        "max_age": 12,
    },
    "culter_oxycephalus": {
        "chinese": "尖头鲌",
        "scientific": "Culter oxycephalus",
        "linfty": 55.0,
        "k": 0.25,
        "t0": -0.35,
        "source": "长江中上游支流",
        "max_age": 10,
    },
    "chanodichthys_erythropterus": {
        "chinese": "红鳍原鲌",
        "scientific": "Chanodichthys erythropterus",
        "linfty": 70.0,
        "k": 0.20,
        "t0": -0.38,
        "source": "长江中下游及东亚水体",
        "max_age": 14,
    },
}


def _generate_example_data(linfty: float, k: float, t0: float,
                           max_age: int, noise_sigma: float = 1.5) -> List[AgeLengthData]:
    """根据 VBGF 参数生成含噪声的模拟年龄-体长数据."""
    import random as _random
    data: List[AgeLengthData] = []
    for age in range(1, max_age + 1):
        true_len = linfty * (1 - math.exp(-k * (age - t0)))
        noisy = true_len + _random.gauss(0, noise_sigma)
        noisy = max(noisy, 1.0)
        data.append(AgeLengthData(age=float(age), length_cm=round(noisy, 2)))
    return data


def _example_data_all() -> Dict[str, List[AgeLengthData]]:
    """所有 4 种鲌类的示例数据."""
    result: Dict[str, List[AgeLengthData]] = {}
    # 固定随机种子保证可复现
    import random as _random
    _random.seed(42)
    for key, ref in REFERENCE_VBGF.items():
        result[key] = _generate_example_data(
            linfty=ref["linfty"], k=ref["k"], t0=ref["t0"],
            max_age=ref["max_age"]
        )
    return result


# ── 报告生成 ───────────────────────────────────────────

def format_growth_params(params: GrowthParams, species_name: str = "") -> str:
    """格式化 VBGF 参数表."""
    lines = [
        f"\n  📏 von Bertalanffy 生长参数 — {species_name}" if species_name else
        f"\n  📏 von Bertalanffy 生长参数",
        "-" * 58,
        f"  方法:       {params.method}",
        f"  L∞:         {params.linfty:.2f} cm",
        f"  K:          {params.k:.4f} yr⁻¹",
        f"  t0:         {params.t0:.4f} yr",
        f"  φ' (生长性能): {params.phi_prime:.4f}",
        f"  t拐 (体重拐点): {params.t_inflection:.4f} yr",
    ]
    if params.r_squared:
        lines.append(f"  R²:         {params.r_squared:.4f}")
    if params.rmse:
        lines.append(f"  RMSE:       {params.rmse:.4f} cm")
    return "\n".join(lines)


def format_growth_table(data: List[AgeLengthData], params: GrowthParams,
                         species_name: str = "") -> str:
    """格式化年龄-体长对照表."""
    lines = [
        f"\n  📊 年龄-体长数据 — {species_name}" if species_name else
        f"\n  📊 年龄-体长数据",
        "-" * 58,
        f"  {'年龄(yr)':>8s}  {'实测(cm)':>10s}  {'预测(cm)':>10s}  {'残差(cm)':>10s}",
        f"  {'-'*46}",
    ]
    for i, d in enumerate(data):
        pred = params.predict(d.age) if params.linfty > 0 else 0.0
        res = d.length_cm - pred
        lines.append(f"  {d.age:>8.1f}  {d.length_cm:>10.2f}  {pred:>10.2f}  {res:>10.2f}")
    return "\n".join(lines)


def format_growth_report(result: VBGFResult) -> str:
    """生成完整生长分析报告."""
    lines = [
        "=" * 60,
        f"  鲌类 von Bertalanffy 生长分析报告",
        "=" * 60,
        f"\n分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"分析物种: {result.species}",
        f"数据点数: {result.n_points}",
    ]
    lines.append(format_growth_params(result.params, result.species))
    lines.append(format_growth_table(result.data_points, result.params, result.species))

    # 生长预测 (0-max_age)
    if result.params.linfty > 0:
        lines.append(f"\n  🔮 生长预测")
        lines.append("-" * 58)
        lines.append(f"  {'年龄(yr)':>8s}  {'体长(cm)':>10s}  {'体重(g)*':>10s}")
        lines.append(f"  {'-'*31}")
        max_a = int(math.ceil(result.max_age))
        for a in range(0, max_a + 1):
            lt = result.params.predict(float(a))
            wt = result.params.predict_weight(float(a))
            lines.append(f"  {a:>8d}  {lt:>10.2f}  {wt:>10.1f}")
        lines.append(f"  * 假设 W = 0.01·L³ (等速生长)")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_growth_json(result: VBGFResult) -> str:
    """JSON 格式输出."""
    data: Dict[str, Any] = {
        "analysis_type": "VBGF生长分析",
        "analysis_time": datetime.now().isoformat(),
        "species": result.species,
        "method": result.method,
        "parameters": result.summary(),
        "data": [
            {
                "age_yr": d.age,
                "length_cm_obs": d.length_cm,
                "length_cm_pred": round(result.params.predict(d.age), 2) if result.params.linfty > 0 else None,
                "weight_g": d.weight_g,
                "n_samples": d.n,
            }
            for d in result.data_points
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────

def analyze_growth(data: List[AgeLengthData],
                   species_key: str = "",
                   method: str = "ford_walford") -> VBGFResult:
    """执行 VBGF 生长分析.

    Args:
        data: 年龄-体长观测数据
        species_key: 物种标识 (culter_alburnus 等)
        method: 拟合方法 (ford_walford | nonlinear)

    Returns:
        VBGFResult
    """
    # 物种中文名
    species_info = REFERENCE_VBGF.get(species_key, {})
    chinese_name = species_info.get("chinese", species_key)
    scientific_name = species_info.get("scientific", "")
    species_label = f"{chinese_name} ({scientific_name})" if scientific_name else chinese_name

    if method == "ford_walford":
        params = ford_walford_fit(data)
    elif method == "nonlinear":
        params = nonlinear_vbgf_fit(data)
    else:
        raise ValueError(f"未知方法: {method}. 可选: ford_walford | nonlinear")

    # 如果 Ford-Walford 未能估计, 回退至非线性拟合
    if params.linfty <= 0 and method == "ford_walford":
        print("  ⚠️  Ford-Walford 未能得到有效参数, 自动回退至非线性拟合...")
        params = nonlinear_vbgf_fit(data)
        params.method = "nonlinear_ls (fallback from Ford-Walford)"

    predicted = [params.predict(d.age) for d in data] if params.linfty > 0 else []
    residuals = [data[i].length_cm - predicted[i] for i in range(len(data))] if predicted else []

    return VBGFResult(
        species=species_label,
        method=params.method,
        params=params,
        data_points=data,
        predicted=predicted,
        residuals=residuals,
    )


def run_example_demo(species_key: Optional[str] = None,
                     method: str = "nonlinear",
                     as_json: bool = False) -> None:
    """运行内置示例数据完整分析.

    Args:
        species_key: 指定单一物种 (None 则全部分析)
        method: 拟合方法
        as_json: 是否 JSON 输出
    """
    all_data = _example_data_all()

    if species_key and species_key in all_data:
        targets = {species_key: all_data[species_key]}
    else:
        targets = all_data

    print("=" * 60)
    print("  鲌类 von Bertalanffy 生长分析 — 示例演示")
    print("=" * 60)
    print(f"  物种数: {len(targets)}")
    print(f"  方法:   {method}")
    print()

    for key, data in targets.items():
        info = REFERENCE_VBGF.get(key, {})
        print(f"\n{'─' * 60}")
        print(f"  🐟 {info.get('chinese', key)} ({info.get('scientific', '')})")
        print(f"  文献参考来源: {info.get('source', '未知')}")
        print(f"  文献参考参数: L∞={info.get('linfty')} cm, K={info.get('k')}, t0={info.get('t0')}")

        result = analyze_growth(data, species_key=key, method=method)

        if as_json:
            print(format_growth_json(result))
        else:
            print(format_growth_report(result))


def main():
    parser = argparse.ArgumentParser(
        prog="growth_analysis",
        description="鲌类 (Culter spp.) von Bertalanffy 生长方程分析 — Ford-Walford + 非线性最小二乘",
    )
    parser.add_argument("--input", "-i", help="年龄-体长 CSV 输入文件 (列: age, length_cm)")
    parser.add_argument("--species", "-s",
                        choices=list(REFERENCE_VBGF.keys()),
                        help="目标物种")
    parser.add_argument("--method", "-m",
                        choices=["ford_walford", "nonlinear"],
                        default="nonlinear",
                        help="VBGF 拟合方法 (默认: nonlinear)")
    parser.add_argument("--example", action="store_true",
                        help="使用内置示例数据运行完整演示")
    parser.add_argument("--json", "-j", action="store_true",
                        help="JSON 格式输出")

    args = parser.parse_args()

    # --example 模式
    if args.example:
        run_example_demo(species_key=args.species, method=args.method, as_json=args.json)
        return

    # --input 模式
    if args.input:
        data = load_age_length_data(args.input)
        if not data:
            print(f"错误: 未能从 '{args.input}' 读取数据或文件为空")
            return
        result = analyze_growth(data, species_key=args.species or "", method=args.method)
        if args.json:
            print(format_growth_json(result))
        else:
            print(format_growth_report(result))
        return

    # 无参数 — 显示帮助并运行示例
    print("未指定输入文件或 --example。运行内置示例演示...\n")
    run_example_demo(species_key=args.species, method=args.method, as_json=args.json)


if __name__ == "__main__":
    main()
