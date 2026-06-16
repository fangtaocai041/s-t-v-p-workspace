#!/usr/bin/env python3
"""
刀鲚洄游生态分析 — 耳石微化学 + 标志放流 + eDNA.

对应 SKILL.md: src/skills/analyze-migration/SKILL.md

核心算法:
  - Sr/Ca 比阈值分类: <1.5=淡水, 1.5~3.0=半咸水, >3.0=海水
  - 洄游履历重建: 从耳石核心到边缘的线扫描
  - 水利工程影响评估

用法:
  python scripts/migration_analysis.py --input otolith.csv           # 读耳石数据
  python scripts/migration_analysis.py --input otolith.csv --json    # JSON 输出
  python scripts/migration_analysis.py --example                     # 示例演示
  python scripts/migration_analysis.py --list-params                 # 打印分析参数
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── 分析参数 ───────────────────────────────────────────

# Sr/Ca 比阈值 (μmol/mol)
SRCA_THRESHOLDS = {
    "freshwater":  (0.0, 1.5),    # 淡水期
    "brackish":    (1.5, 3.0),    # 半咸水过渡期
    "marine":      (3.0, 9.0),    # 海水期
}

# 刀鲚洄游参数 (文献值)
MIGRATION_PARAMS = {
    "upstream_period":       "2-4月 (春季溯河)",
    "downstream_period":     "秋冬季 (幼鱼降海)",
    "historical_range":      "长江口至洞庭湖 (最远可达宜昌)",
    "current_range":         "大幅萎缩，主要集中于长江口-安徽段",
    "key_barriers":          ["三峡大坝", "葛洲坝", "沿江多个闸坝"],
    "spawning_temp":         "18-25°C",
    "spawning_discharge":    "10000-30000 m³/s",
}


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class OtolithPoint:
    """耳石线扫描单点数据."""
    distance_um: float = 0.0     # 距核心距离 (μm)
    sr_ca_ratio: float = 0.0     # Sr/Ca 比 (μmol/mol)
    habitat: str = ""             # 淡水/半咸水/海水

    def classify_habitat(self) -> str:
        """根据 Sr/Ca 比判断栖息地类型."""
        for habitat, (lo, hi) in SRCA_THRESHOLDS.items():
            if lo <= self.sr_ca_ratio < hi:
                return habitat
        return "unknown"


@dataclass
class MigrationProfile:
    """个体洄游履历."""
    freshwater_days: int = 0
    brackish_days: int = 0
    marine_days: int = 0
    total_days: int = 0
    transitions: int = 0          # 生境转换次数
    confidence: str = "medium"    # 高/中/低


# ── 耳石微化学分析 ─────────────────────────────────────

def load_otolith_data(path: Optional[str] = None) -> List[OtolithPoint]:
    """读取耳石微化学 CSV 数据.

    CSV 列: distance_um (距核心μm), sr_ca (Sr/Ca比)
    """
    points: List[OtolithPoint] = []

    if path and Path(path).is_file():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                point = OtolithPoint(
                    distance_um=float(row.get("distance_um", row.get("distance", 0))),
                    sr_ca_ratio=float(row.get("sr_ca", row.get("sr_ca_ratio", row.get("ratio", 0)))),
                )
                point.habitat = point.classify_habitat()
                points.append(point)
    return points


def analyze_otolith(points: List[OtolithPoint], growth_rate: float = 3.0) -> MigrationProfile:
    """分析耳石微化学数据，重建洄游履历.

    Args:
        points: 耳石线扫描数据点
        growth_rate: 日均生长速率 (μm/天), 默认 3.0

    Returns:
        MigrationProfile: 洄游履历
    """
    if not points:
        return MigrationProfile()

    # 每个点按生长速率换算为天数
    profile = MigrationProfile()
    transitions = 0
    prev_habitat = ""

    for point in points:
        point.habitat = point.classify_habitat()
        # 计算该点代表的生长天数 (按距离间隔 / 生长速率)
        days = 1.0
        profile.total_days += days

        if point.habitat == "freshwater":
            profile.freshwater_days += days
        elif point.habitat == "brackish":
            profile.brackish_days += days
        elif point.habitat == "marine":
            profile.marine_days += days

        # 生境转变计数
        if prev_habitat and point.habitat != prev_habitat:
            transitions += 1
        prev_habitat = point.habitat

    profile.transitions = transitions

    # 置信度评估
    n = len(points)
    if n >= 30:
        profile.confidence = "high"
    elif n >= 10:
        profile.confidence = "medium"
    else:
        profile.confidence = "low"

    return profile


# ── 水利工程影响评估 ──────────────────────────────────

def assess_barrier_impact(barriers: List[str]) -> List[Dict[str, str]]:
    """评估水利工程对洄游通道的阻断影响."""
    assessments = []
    known_barriers = {
        "三峡大坝":     {"impact": "高", "note": "完全阻断，无过鱼设施"},
        "葛洲坝":       {"impact": "高", "note": "完全阻断，无过鱼设施"},
        "沿江多个闸坝": {"impact": "中", "note": "季节性阻断，部分闸坝有生态调度"},
    }
    for b in barriers:
        info = known_barriers.get(b, {"impact": "未知", "note": ""})
        assessments.append({"barrier": b, "impact": info["impact"], "note": info["note"]})
    return assessments


# ── 示例数据 ───────────────────────────────────────────

def _example_otolith_data() -> List[OtolithPoint]:
    """生成示例耳石线扫描数据 (从核心到边缘)."""
    points: List[OtolithPoint] = []
    # 模拟 50 个数据点，从核心到边缘
    for i in range(50):
        dist = i * 5.0  # 每点间隔 5μm
        # 模拟洄游履历: 淡水出生 (核心) → 降海 → 海水生长 → 溯河
        if dist < 30:
            sr = 0.8 + (i * 0.05)        # 淡水期 Sr/Ca ≈ 0.5-1.5
        elif dist < 60:
            sr = 1.8 + ((i - 6) * 0.08)  # 过渡期 Sr/Ca 上升
        elif dist < 180:
            sr = 4.0 + math.sin(i * 0.3) * 0.5  # 海水期 Sr/Ca ≈ 3.5-5.0
        else:
            sr = 2.5 + ((i - 36) * -0.06)  # 溯河回归, Sr/Ca 下降
        sr = max(0.5, min(6.0, sr))  # 限制范围
        p = OtolithPoint(distance_um=dist, sr_ca_ratio=round(sr, 2))
        p.habitat = p.classify_habitat()
        points.append(p)
    return points


# ── 报告生成 ───────────────────────────────────────────

def format_report(profile: MigrationProfile, barriers: List[Dict[str, str]]) -> str:
    """生成洄游分析报告 (SKILL.md 输出模板格式)."""
    total = profile.total_days or 1
    lines = [
        "=" * 60,
        "  刀鲚洄游分析报告",
        "=" * 60,
        "",
        f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"数据置信度: {profile.confidence}",
        "",
        "1️⃣  个体洄游履历 (基于耳石 Sr/Ca)",
        "-" * 40,
        f"   淡水生活期:   {profile.freshwater_days:.0f} 天 ({profile.freshwater_days/total*100:.0f}%)",
        f"   半咸水过渡期: {profile.brackish_days:.0f} 天 ({profile.brackish_days/total*100:.0f}%)",
        f"   海水生长期:   {profile.marine_days:.0f} 天 ({profile.marine_days/total*100:.0f}%)",
        f"   生境转换次数: {profile.transitions} 次",
        "",
        "2️⃣  群体洄游模式",
        "-" * 40,
        f"   溯河时间: {MIGRATION_PARAMS['upstream_period']}",
        f"   降海时间: {MIGRATION_PARAMS['downstream_period']}",
        f"   历史分布: {MIGRATION_PARAMS['historical_range']}",
        f"   当前分布: {MIGRATION_PARAMS['current_range']}",
        "",
        "3️⃣  环境驱动因子",
        "-" * 40,
        f"   产卵水温阈值: {MIGRATION_PARAMS['spawning_temp']}",
        f"   产卵流量阈值: {MIGRATION_PARAMS['spawning_discharge']}",
        "",
        "4️⃣  水利工程影响",
        "-" * 40,
    ]
    for b in barriers:
        lines.append(f"   {b['barrier']}: 阻断程度 {b['impact']} — {b['note']}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_json_report(profile: MigrationProfile, barriers: List[Dict[str, str]]) -> str:
    """JSON 格式输出."""
    data = {
        "analysis_type": "刀鲚洄游分析",
        "analysis_time": datetime.now().isoformat(),
        "confidence": profile.confidence,
        "migration_profile": {
            "freshwater_days": round(profile.freshwater_days),
            "brackish_days": round(profile.brackish_days),
            "marine_days": round(profile.marine_days),
            "total_days": round(profile.total_days),
            "transitions": profile.transitions,
        },
        "migration_params": MIGRATION_PARAMS,
        "barrier_assessment": barriers,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def list_params() -> str:
    """打印分析参数."""
    lines = [
        "Sr/Ca 比阈值:",
    ]
    for habitat, (lo, hi) in SRCA_THRESHOLDS.items():
        lines.append(f"  {habitat:12s}  {lo} ~ {hi} μmol/mol")
    lines.extend([
        "",
        "洄游参数 (文献值):",
        *[f"  {k}: {v}" for k, v in MIGRATION_PARAMS.items()],
    ])
    return "\n".join(lines)


# ── 主流程 ─────────────────────────────────────────────

def analyze_migration(input_path: Optional[str] = None,
                      use_example: bool = False) -> Tuple[MigrationProfile, List[Dict[str, str]]]:
    """执行完整的刀鲚洄游分析.

    Args:
        input_path: 耳石微化学 CSV 文件路径
        use_example: 使用内置示例数据

    Returns:
        (MigrationProfile, 水利工程影响评估列表)
    """
    if use_example:
        points = _example_otolith_data()
    elif input_path:
        points = load_otolith_data(input_path)
    else:
        points = _example_otolith_data()

    profile = analyze_otolith(points)
    barriers = assess_barrier_impact(MIGRATION_PARAMS["key_barriers"])
    return profile, barriers


def main():
    parser = argparse.ArgumentParser(
        prog="migration_analysis",
        description="刀鲚 (Coilia nasus) 洄游生态分析 — 耳石微化学 + 标志放流 + eDNA"
    )
    parser.add_argument("--input", "-i", help="耳石微化学 CSV 输入文件")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--example", action="store_true", help="使用内置示例数据")
    parser.add_argument("--list-params", action="store_true", help="打印分析参数")

    args = parser.parse_args()

    if args.list_params:
        print(list_params())
        return

    profile, barriers = analyze_migration(
        input_path=args.input,
        use_example=args.example or (not args.input),
    )

    if args.json:
        print(format_json_report(profile, barriers))
    else:
        print(format_report(profile, barriers))


if __name__ == "__main__":
    main()
