#!/usr/bin/env python3
"""
self_evolve.py — Post-search feedback loop for lit-search v3.1

每次搜索完成后自动记录指标，对比历史，输出优化建议。
与 lit-search §3.3 配套。

用法:
  from self_evolve import log_search, get_recommendations

  result = log_search(species_id, {
      "mode": "SATISFICING",
      "layers_activated": ["L1","L2","L3"],
      "layers_producing": {"L2": 7, "L3": 2},
      "known_papers": 48,
      "new_papers": 9,
      "total_papers": 57,
      "tokens_estimated": 4500,
      "mode_auto": True,
  })
  print(result["recommendations"])

v1.0 — lit-search v3.1 配套
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Config ──────────────────────────────────────────────────
EVOLVE_LOG = Path(__file__).resolve().parent.parent / "logs" / "self_evolve.jsonl"

# ── Adaptive thresholds ─────────────────────────────────────
THRESHOLDS = {
    "known_papers_rich": 20,        # ≥20 → SATISFICING
    "known_papers_classified": 5,   # 5-19 → CLASSIFIED
    "new_papers_sufficient": 8,     # SATISFICING 停止阈值
    "layer_zero_yield_max": 3,      # 连续 N 次零产出 → 降级
    "chinese_min_expected": 2,      # 中文文献最低期望
    "token_per_paper_max": 500,     # 每篇论文最大 token 成本
}

# ── Layer productivity tracker ──────────────────────────────

def _load_history(species_id: str) -> List[Dict]:
    """Load search history for a species."""
    if not EVOLVE_LOG.exists():
        return []
    history = []
    with open(EVOLVE_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("species_id") == species_id:
                    history.append(entry)
            except json.JSONDecodeError:
                pass
    return history


def log_search(species_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Log a search and return recommendations."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "species_id": species_id,
        **metrics,
    }

    # Ensure log directory exists
    EVOLVE_LOG.parent.mkdir(parents=True, exist_ok=True)

    # Append to log
    with open(EVOLVE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Load history for this species
    history = _load_history(species_id)
    history.append(entry)

    # Generate recommendations
    recommendations = _analyze(species_id, history, entry)

    return {
        "logged": True,
        "history_count": len(history),
        "recommendations": recommendations,
    }


def _analyze(species_id: str, history: List[Dict], current: Dict) -> List[str]:
    """Analyze search history and generate recommendations."""
    recs = []

    mode = current.get("mode", "?")
    known = current.get("known_papers", 0)
    new = current.get("new_papers", 0)
    total = current.get("total_papers", 0)
    tokens = current.get("tokens_estimated", 0)
    layers_prod = current.get("layers_producing", {})
    auto = current.get("mode_auto", True)

    # 1. Mode appropriateness
    if auto and mode == "SATISFICING" and new >= 8 and known >= 30:
        recs.append(
            f"✅ SATISFICING 合理: 已知{known}篇充足, 仍发现{new}篇新论文。"
            f" 下次继续 SATISFICING。"
        )
    elif auto and mode == "SATISFICING" and new < 3 and known >= 50:
        recs.append(
            f"💡 饱和信号: 已知{known}篇, 仅{new}篇新发现。"
            f" 建议下次跳过搜索, 直接看缓存。"
        )
    elif auto and mode == "SATISFICING" and new >= 15:
        recs.append(
            f"⚠️ 高产信号: {new}篇新发现远超阈值(8)。"
            f" 建议下次升级到 CLASSIFIED 模式。"
        )

    # 2. Chinese literature gap
    cn_count = layers_prod.get("L3", 0)
    if cn_count < THRESHOLDS["chinese_min_expected"]:
        recs.append(
            f"🇨🇳 中文文献缺口: 仅{cn_count}篇。"
            f" 建议: 补充中文别名 + 知网/万方定向搜索。"
        )

    # 3. Layer productivity analysis
    total_activated = len(current.get("layers_activated", []))
    productive_layers = len([k for k, v in layers_prod.items() if v > 0])
    if productive_layers < total_activated * 0.4 and total_activated > 3:
        dead_layers = [k for k in current.get("layers_activated", [])
                       if layers_prod.get(k, 0) == 0]
        recs.append(
            f"📉 层级效率低: {productive_layers}/{total_activated}层有产出。"
            f" 零产出层: {dead_layers}。考虑降级激活条件。"
        )

    # 4. Historical comparison
    if len(history) >= 2:
        prev = history[-2]
        prev_new = prev.get("new_papers", 0)
        prev_total = prev.get("total_papers", 0)
        if total > prev_total:
            growth = total - prev_total
            recs.append(
                f"📈 图谱增长: {prev_total}→{total}篇 (+{growth})。"
            )

    # 5. Token efficiency
    if new > 0 and tokens > 0:
        tpp = tokens / new
        if tpp > THRESHOLDS["token_per_paper_max"]:
            recs.append(
                f"💰 高token成本: {tpp:.0f} tokens/篇 (阈值{THRESHOLDS['token_per_paper_max']})。"
                f" 建议: 减少激活层数或降低 max_results。"
            )

    # 6. CR/EN species alert
    if total < 10:
        recs.append(
            f"🔴 数据稀缺: 仅{total}篇论文。"
            f" 建议: 强制 EXHAUSTIVE + 作者回溯 + 引用全网遍历。"
        )

    return recs


def get_species_stats(species_id: str) -> Dict[str, Any]:
    """Get cumulative stats for a species."""
    history = _load_history(species_id)
    if not history:
        return {"species_id": species_id, "searches": 0}

    last = history[-1]
    return {
        "species_id": species_id,
        "searches": len(history),
        "last_search": last.get("timestamp", ""),
        "total_papers": last.get("total_papers", 0),
        "known_papers": last.get("known_papers", 0),
        "total_new_ever": sum(h.get("new_papers", 0) for h in history),
        "modes_used": list(set(h.get("mode", "") for h in history)),
    }


# ── CLI ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python self_evolve.py <species_id>")
        print("       python self_evolve.py --stats <species_id>")
        sys.exit(1)

    if sys.argv[1] == "--stats":
        sid = sys.argv[2] if len(sys.argv) > 2 else "Pseudaspius_hakonensis"
        stats = get_species_stats(sid)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        sid = sys.argv[1]
        result = log_search(sid, {
            "mode": "SATISFICING",
            "layers_activated": ["L1", "L2", "L3"],
            "layers_producing": {"L2": 7, "L3": 2},
            "known_papers": 48,
            "new_papers": 9,
            "total_papers": 57,
            "tokens_estimated": 4500,
            "mode_auto": True,
        })
        for r in result["recommendations"]:
            print(f"  {r}")
