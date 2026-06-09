"""ConflictArbiter — 冲突仲裁核心引擎 (火 🟥)

多源保护推荐冲突检测 + 可信度加权仲裁 + 熔断逻辑。

区域规则:
  - region="china": 中国保护等级为权威，IUCN/CITES 仅参考
    中国来源权重: chinese_red_list=100, provincial_protection=90
    国际来源权重: iucn=40, cites=40
    裁决: 以最高优先级中国来源为准

典型场景:
  - 中国物种: IUCN "极危(CR)" vs 中国红色名录 "濒危(EN)"
    → 冲突等级 1, 裁决以中国为准
  - 文献A "2010年长江中游种群下降30%" vs 文献B "2025年长江下游种群稳定"
    → 时空不一致, 不构成冲突 (不同年不同地区)
  - 文献A "2010年长江中游种群下降30%" vs 文献B "2010年长江中游种群稳定"
    → 时空一致, 三级冲突, 熔断
  - 省级保护 vs 国家保护 vs IUCN → 跨层级矛盾检测, 中国分类为准
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── 保护等级标准化映射 ──
# 将所有来源的保护等级映射到统一数值轴 [0-100], 0=无危, 100=灭绝

IUCN_MAP = {
    "灭绝(EX)": 100, "extinct": 100, "EX": 100,
    "野外灭绝(EW)": 95, "extinct in the wild": 95, "EW": 95,
    "极危(CR)": 85, "critically endangered": 85, "CR": 85,
    "濒危(EN)": 70, "endangered": 70, "EN": 70,
    "易危(VU)": 55, "vulnerable": 55, "VU": 55,
    "近危(NT)": 35, "near threatened": 35, "NT": 35,
    "无危(LC)": 10, "least concern": 10, "LC": 10,
    "数据缺乏(DD)": 5, "data deficient": 5, "DD": 5,
    "未评估(NE)": 0, "not evaluated": 0, "NE": 0,
}

CHINESE_RED_LIST_MAP = {
    "国家一级": 90, "一级": 90,
    "国家二级": 70, "二级": 70,
    "省级重点": 50,
    "三有保护": 30,
    "无": 0,
}

CITES_MAP = {
    "附录Ⅰ": 95, "Appendix Ⅰ": 95, "I": 95,
    "附录Ⅱ": 75, "Appendix Ⅱ": 75, "II": 75,
    "附录Ⅲ": 50, "Appendix Ⅲ": 50, "III": 50,
}


class ConflictArbiter:
    """冲突仲裁引擎 — 多源保护推荐一致性检测 + 加权仲裁 + 熔断。"""

    # 默认数据源权重
    DEFAULT_SOURCE_WEIGHTS: Dict[str, int] = {
        "iucn": 90,
        "cites": 90,
        "chinese_red_list": 80,
        "provincial_protection": 70,
        "peer_reviewed_literature": 75,
        "survey_report": 60,
        "news_media": 30,
        "citizen_science": 20,
    }

    # 熔断阈值
    CIRCUIT_BREAKER = {
        "max_conflict_level": 3,
        "min_sources_for_consensus": 3,
    }

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self._source_weights = dict(self.DEFAULT_SOURCE_WEIGHTS)
        self._cb = dict(self.CIRCUIT_BREAKER)
        if config_path and config_path.is_file():
            self._load_config(config_path)

    def _load_config(self, path: Path) -> None:
        """从 agent.yaml 加载仲裁配置。"""
        try:
            import yaml
            cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            arb = cfg.get("arbiter", {})
            if "source_weights" in arb:
                self._source_weights.update(arb["source_weights"])
            if "circuit_breaker" in arb:
                self._cb.update(arb["circuit_breaker"])
        except Exception as exc:
            logger.warning(f"Config load failed: {exc}")

    # ── 公共 API ──

    def detect_conflicts(
        self,
        species_name: str,
        sources: List[Dict[str, Any]],
        region: str = "china",
    ) -> Dict[str, Any]:
        """检测多源保护推荐冲突。

        Args:
            species_name: 物种名 (中文/学名)
            sources: 数据源列表, 每项 {source, protection_level, status, iucn, ...}
            region: 区域策略. "china"=中国保护等级为权威, "global"=常规加权

        Returns:
            {species_name, conflict_level, consensus, sources_analyzed, verdict, details}
        """
        if not sources:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": "无数据", "score": None},
                "sources_analyzed": 0,
                "verdict": "无数据来源, 无法仲裁",
                "details": [],
            }

        # Step 1: 标准化所有来源的保护等级到统一数值轴
        normalized: List[Dict[str, Any]] = []
        for s in sources:
            norm = self._normalize_source(s)
            if norm is not None:
                normalized.append(norm)

        if len(normalized) < 2:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": "仅单源", "score": normalized[0]["score"] if normalized else None},
                "sources_analyzed": len(normalized),
                "verdict": "仅单一数据源, 无需仲裁",
                "details": normalized,
            }

        # Step 1.5: 区域权重覆盖 — 中国物种以中国保护等级为准
        has_chinese_source = any(
            n["source"] in ("chinese_red_list", "provincial_protection")
            for n in normalized
        )
        china_authoritative = (region == "china" and has_chinese_source)

        if china_authoritative:
            for n in normalized:
                src = n["source"]
                if src == "chinese_red_list":
                    n["weight"] = 100
                    n["authority"] = "primary"
                elif src == "provincial_protection":
                    n["weight"] = 90
                    n["authority"] = "secondary"
                elif src in ("iucn", "cites"):
                    n["weight"] = 40
                    n["authority"] = "reference"
                else:
                    n["weight"] = self._source_weights.get(src, 50)
                    n["authority"] = "reference"
                n["weighted_score"] = n["score"] * n["weight"] / 100

        # Step 2: 计算冲突等级
        scores = [n["score"] for n in normalized]
        weights = [n["weight"] for n in normalized]
        conflict_level, max_gap = self._compute_conflict_level(scores)

        # Step 3: 加权仲裁
        consensus = self._weighted_arbitration(scores, weights, conflict_level)

        # Step 3.5: 中国物种 — 以中国来源数值覆盖仲裁结果
        if china_authoritative:
            chinese_primary = None
            for src_priority in ("chinese_red_list", "provincial_protection"):
                chinese_primary = next(
                    (n for n in normalized if n["source"] == src_priority), None
                )
                if chinese_primary:
                    break
            if chinese_primary:
                authoritative_score = chinese_primary["score"]
                authoritative_level = self._score_to_level(authoritative_score)
                consensus["score"] = authoritative_score
                consensus["mapped_level"] = authoritative_level
                consensus["authority"] = "chinese_classification"
                consensus["authoritative_source"] = chinese_primary["source"]
                consensus["level"] = (
                    "中国分类为准"
                    if conflict_level <= 1
                    else f"⚠️ 冲突等级 {conflict_level}，但按中国分类执行"
                )

        # Step 4: 熔断判断
        verdict = self._circuit_judgment(
            conflict_level, consensus, len(normalized), china_authoritative
        )

        return {
            "species_name": species_name,
            "conflict_level": conflict_level,
            "max_gap": max_gap,
            "consensus": consensus,
            "sources_analyzed": len(normalized),
            "region_policy": region if china_authoritative else "global",
            "verdict": verdict,
            "details": normalized,
        }

    def arbitrate(
        self,
        species_name: str,
        claims: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """通用声明仲裁 — 对任意带权声明做一致性检测。

        时空一致性规则: 只有同一时间+同一地区的声明才构成冲突。
        不同年份/不同地区的声明 -> "不同时空数据，不构成冲突"。

        Args:
            species_name: 物种名
            claims: [{claim, source, weight, confidence, value,
                       time_period: {start, end}, region}]

        Returns:
            {conflict_level, consensus, verdict, details, spatiotemporal}
        """
        if not claims:
            return {"conflict_level": 0, "consensus": None, "verdict": "无声明"}

        # Step 1: 检查声明是否时空可比
        comparable, st_result = self._check_spatiotemporal_comparability(claims)

        if not comparable:
            return {
                "species_name": species_name,
                "conflict_level": 0,
                "consensus": {"agreed": True, "level": st_result["reason"],
                              "score": None},
                "claims_analyzed": len(claims),
                "spatiotemporal": st_result,
                "verdict": (
                    f"🟢 不同时空数据，不构成冲突。"
                    f" {st_result['detail']}"
                ),
                "details": claims,
            }

        # Step 2: 时空可比 → 正常仲裁
        values = [c.get("value", 0) for c in claims]
        weights = [c.get("weight", 50) for c in claims]
        conflict_level, _ = self._compute_conflict_level(values)
        consensus = self._weighted_arbitration(values, weights, conflict_level)

        return {
            "species_name": species_name,
            "conflict_level": conflict_level,
            "consensus": consensus,
            "claims_analyzed": len(claims),
            "spatiotemporal": st_result,
            "verdict": self._circuit_judgment(conflict_level, consensus, len(claims)),
            "details": claims,
        }

    @staticmethod
    def _check_spatiotemporal_comparability(
        claims: List[Dict[str, Any]],
    ) -> tuple[bool, dict]:
        """检查声明集是否时空一致才比较。

        返回:
            (True, {"status": "comparable"|"info_incomplete",
                     "time_periods": [...], "regions": [...]})
            或
            (False, {"status": "incomparable", "reason": "...", "detail": "..."})
        """
        time_periods = [c.get("time_period") for c in claims]
        regions = [c.get("region") for c in claims]

        all_have_time = all(t is not None for t in time_periods)
        all_have_region = all(r is not None for r in regions)

        if all_have_time and all_have_region:
            # 检查时间是否重叠
            time_overlap = True
            for i in range(len(claims)):
                for j in range(i + 1, len(claims)):
                    if not ConflictArbiter._times_overlap(
                        time_periods[i], time_periods[j]
                    ):
                        time_overlap = False
                        break
                if not time_overlap:
                    break

            # 检查区域是否相同
            same_region = len(set(regions)) == 1

            if not time_overlap and not same_region:
                return False, {
                    "status": "incomparable",
                    "reason": "时空均不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"时间: {time_periods}, 地区: {regions}",
                }
            if not time_overlap:
                return False, {
                    "status": "incomparable",
                    "reason": "时间不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"时间不重叠: {time_periods}",
                }
            if not same_region:
                return False, {
                    "status": "incomparable",
                    "reason": "地区不同",
                    "time_periods": time_periods,
                    "regions": regions,
                    "detail": f"地区不同: {regions}",
                }
            return True, {
                "status": "comparable",
                "time_periods": time_periods,
                "regions": regions,
            }

        # 部分声明缺时空信息 → 仍比较，但标记信息不全
        return True, {
            "status": "info_incomplete",
            "time_periods": time_periods,
            "regions": regions,
        }

    @staticmethod
    def _times_overlap(t1: dict, t2: dict) -> bool:
        """检查两个时间段是否重叠。{start, end} 年份。"""
        s1 = t1.get("start", 0)
        e1 = t1.get("end", 9999)
        s2 = t2.get("start", 0)
        e2 = t2.get("end", 9999)
        return max(s1, s2) <= min(e1, e2)

    # ── 内部方法 ──

    def _normalize_source(self, source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """将单个数据源的保护等级标准化到数值轴 [0-100]。"""
        src_name = source.get("source", "unknown")
        weight = self._source_weights.get(src_name, 50)

        # 尝试各映射表
        score = None

        # IUCN 状态
        iucn_val = source.get("iucn", "")
        if iucn_val:
            for key, val in IUCN_MAP.items():
                if key.lower() in iucn_val.lower():
                    score = val
                    break

        # 中国保护等级
        if score is None:
            prot = source.get("protection_level", "")
            for key, val in CHINESE_RED_LIST_MAP.items():
                if key in prot:
                    score = val
                    break

        # CITES
        if score is None:
            cites = source.get("cites", "")
            for key, val in CITES_MAP.items():
                if key in cites:
                    score = val
                    break

        # 数值直给
        if score is None:
            score = source.get("score", source.get("value", None))

        if score is None:
            return None

        return {
            "source": src_name,
            "original": source.get("protection_level", source.get("iucn", str(source))),
            "score": score,
            "weight": weight,
            "weighted_score": score * weight / 100,
        }

    @staticmethod
    def _compute_conflict_level(scores: List[float]) -> Tuple[int, float]:
        """计算冲突等级 [0-3] 和最大分差。

        0 = 完全一致 (max_gap ≤ 5)
        1 = 轻微差异 (max_gap ≤ 15)
        2 = 显著差异 (max_gap ≤ 35)
        3 = 严重对立 (max_gap > 35)
        """
        if not scores:
            return 0, 0.0
        max_gap = max(scores) - min(scores)
        if max_gap <= 5:
            return 0, max_gap
        elif max_gap <= 15:
            return 1, max_gap
        elif max_gap <= 35:
            return 2, max_gap
        else:
            return 3, max_gap

    def _weighted_arbitration(
        self, scores: List[float], weights: List[float], conflict_level: int
    ) -> Dict[str, Any]:
        """加权仲裁 — 计算加权均值和可信区间。"""
        total_weight = sum(weights)
        if total_weight == 0:
            return {"agreed": False, "level": "无法计算", "score": None, "ci": None}

        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / total_weight

        # 置信区间: 按权重计算标准差
        variance = sum(w * (s - weighted_avg) ** 2 for s, w in zip(scores, weights)) / total_weight
        std_dev = variance ** 0.5

        # 判定
        if conflict_level == 0:
            agreed = True
            level = "完全一致"
        elif conflict_level == 1:
            agreed = True
            level = "基本一致"
        elif conflict_level == 2:
            agreed = False
            level = "显著差异 — 加权仲裁"
        else:
            agreed = False
            level = "严重对立 — 触发熔断"

        # 数值映射回文字等级
        mapped_level = self._score_to_level(weighted_avg)

        return {
            "agreed": agreed,
            "level": level,
            "score": round(weighted_avg, 1),
            "mapped_level": mapped_level,
            "std_dev": round(std_dev, 1),
            "ci_95": (
                round(max(0, weighted_avg - 1.96 * std_dev), 1),
                round(min(100, weighted_avg + 1.96 * std_dev), 1),
            ),
        }

    def _circuit_judgment(
        self, conflict_level: int, consensus: Dict[str, Any],
        n_sources: int, china_authoritative: bool = False,
    ) -> str:
        """熔断判断 + 生成裁决文本。"""
        max_level = self._cb.get("max_conflict_level", 3)
        min_consensus = self._cb.get("min_sources_for_consensus", 3)

        # 中国物种: 以中国保护等级为准，冲突仅做参考提示
        if china_authoritative:
            auth_src = consensus.get("authoritative_source", "chinese_red_list")
            mapped = consensus.get("mapped_level", "N/A")
            score = consensus.get("score", "N/A")
            if conflict_level <= 1:
                return (
                    f"🟢 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" 国际来源与之一致。"
                )
            elif conflict_level == 2:
                return (
                    f"🟡 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" ⚠️ 国际来源有显著差异 (冲突等级 {conflict_level}/3)，仅供参考。"
                )
            else:
                return (
                    f"🟠 按中国保护等级执行 [{auth_src}: {mapped} ({score}/100)]。"
                    f" 🔴 国际来源严重对立 (冲突等级 {conflict_level}/3)，建议人工复核差异原因。"
                )

        # 常规裁决逻辑 (region != "china" 或无中国来源)
        if conflict_level >= max_level:
            return (
                f"🔴 熔断! 冲突等级 {conflict_level}/{max_level}, "
                f"超过熔断阈值。建议人工复核。"
            )
        if n_sources < min_consensus:
            return (
                f"🟡 数据源不足 ({n_sources}/{min_consensus}), "
                f"仲裁结果仅供参考。共识: {consensus.get('mapped_level', 'N/A')}"
            )
        if consensus.get("agreed"):
            return (
                f"🟢 仲裁通过。共识: {consensus.get('mapped_level', 'N/A')} "
                f"(得分 {consensus.get('score', 'N/A')}/100)"
            )
        return (
            f"🟠 显著差异, 加权仲裁结果: {consensus.get('mapped_level', 'N/A')} "
            f"(得分 {consensus.get('score', 'N/A')}/100)。建议交叉验证。"
        )

    @staticmethod
    def _score_to_level(score: float) -> str:
        """将数值分数映射回保护等级文字。"""
        if score >= 95:
            return "灭绝/野外灭绝"
        elif score >= 80:
            return "极危"
        elif score >= 65:
            return "濒危"
        elif score >= 50:
            return "易危"
        elif score >= 30:
            return "近危"
        elif score >= 10:
            return "无危"
        else:
            return "未评估/数据缺乏"

    def health(self) -> Dict[str, Any]:
        return {
            "project": "conflict-arbiter",
            "status": "HEALTHY",
            "source_weights_loaded": len(self._source_weights),
            "circuit_breaker": self._cb,
        }

    def info(self) -> Dict[str, Any]:
        return {
            "project": "conflict-arbiter",
            "version": "1.0.0",
            "role": "V4_ArbitrateVertex (C-Conflict)",
            "element": "火 🟥",
            "capabilities": [
                "protection_level_conflict_detection",
                "weighted_arbitration",
                "circuit_breaker",
                "multi_source_normalization",
                "cross_project_consensus",
            ],
        }


# ── 便捷工厂 ──

def get_arbiter(config_path: Optional[Path] = None) -> ConflictArbiter:
    return ConflictArbiter(config_path=config_path)
