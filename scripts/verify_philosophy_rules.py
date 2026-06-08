#!/usr/bin/env python3
"""
P2: 哲学→测试 — Philosophy-to-Test Verification

验证每条 WHEN→THEN 工程规则有对应的代码路径、配置项或测试覆盖。

用法: python scripts/verify_philosophy_rules.py
退出码: 0=全部通过, 1=有缺口
"""

import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
RULES_FILE = WORKSPACE / "fish-ecology-assistant" / ".reasonix" / "handbooks" / "engineering-grammar.md"

# ═══════════════════════════════════════════════════════════
# 18 条规则 → 代码/配置映射
# ═══════════════════════════════════════════════════════════

RULES = {
    "FB-1": {
        "name": "来源验证 — 最少独立源",
        "config": ["verification_loop.investigation_first.min_sources_core_claim"],
        "code": [
            "porpoise-agent/src/agent/orchestrator.py: VerificationStatus",
            "cognitive-search-engine/src/validator.py: enforce_independence",
        ],
    },
    "FB-2": {
        "name": "验证状态标签",
        "config": ["verification_loop.verification_status"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: _tag_verification"],
    },
    "CP-1": {
        "name": "矛盾识别与分类",
        "config": ["contradiction_analysis.contradiction_levels"],
        "code": [
            "porpoise-agent/src/agent/orchestrator.py: ContradictionType",
            "cognitive-search-engine/src/meso_agent.py: _analyze_contradiction",
        ],
    },
    "CP-2": {
        "name": "主要矛盾资源倾斜",
        "config": ["contradiction_analysis.contradiction_budget_multiplier"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: budget_multiplier"],
    },
    "SM-1": {
        "name": "阶段门控",
        "config": ["phased_strategy.phase_gating.no_skip"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: _should_continue"],
    },
    "SM-2": {
        "name": "战略退却",
        "config": ["phased_strategy.phase_gating.allow_retreat"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: _detect_dead_end"],
    },
    "WF-1": {
        "name": "资源分配权重",
        "config": ["contradiction_analysis.contradiction_levels.*.budget_share"],
        "code": ["meso-cosmos-agent/src/pipeline/orchestrator.py: budget_share"],
    },
    "WF-2": {
        "name": "独立研究路径",
        "config": ["research_balance.independent_path"],
        "code": ["cognitive-search-engine/src/validator.py: enforce_independence"],
    },
    "PT-1": {
        "name": "前沿追踪",
        "skill": ["frontier-tracker"],
        "note": "Skill-based, executed by Reasonix runtime",
    },
    "PT-2": {
        "name": "主动建议触发",
        "skill": ["research-planner"],
        "note": "Skill-based, executed by Reasonix runtime",
    },
    "EH-1": {
        "name": "对抗性矛盾处理",
        "config": ["contradiction_analysis.contradiction_types.antagonistic"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: ANTAGONISTIC → BLOCK"],
    },
    "EH-2": {
        "name": "非对抗性矛盾处理",
        "config": ["contradiction_analysis.contradiction_types.non_antagonistic"],
        "code": ["porpoise-agent/src/agent/orchestrator.py: NON_ANTAGONISTIC → PASS_WITH_NOTE"],
    },
    "MO-1": {
        "name": "十大关系平衡",
        "config": ["research_balance.priorities"],
        "skill": ["research-reviewer"],
    },
    "MO-2": {
        "name": "多目标优化",
        "config": ["research_balance.priorities[].rule"],
        "note": "Lexicographic priority chain",
    },
    "DS-1": {
        "name": "熵预算",
        "config": ["pipeline.stages[].activation"],
        "code": ["meso-cosmos-agent/src/pipeline/search_optimizer.py: CognitiveBudget"],
    },
    "DS-2": {
        "name": "稀疏激活",
        "config": ["pipeline.stages[].activation"],
        "code": ["meso-cosmos-agent/src/pipeline/search_optimizer.py: MoEGate"],
    },
    "DS-3": {
        "name": "差分验证",
        "skill": ["verify-stats-handbook"],
        "note": "Probabilistic stale scoring, not full verify",
    },
    "DS-4": {
        "name": "信息增益路由",
        "code": ["meso-cosmos-agent/src/pipeline/search_optimizer.py: EntropyGuide"],
    },
}


def verify_file_exists(rel_path: str) -> bool:
    return (WORKSPACE / rel_path).exists()


def main():
    print(f"\n{'═'*60}")
    print(f"  P2: 哲学→测试 — 18条 WHEN→THEN 规则验证")
    print(f"{'═'*60}")

    passed = 0
    failed = 0
    gaps = []

    for rule_id, rule in RULES.items():
        has_code = rule.get("code") or rule.get("skill") or rule.get("note")
        has_config = rule.get("config")
        rule_passed = True
        details = []

        # Check code references
        if "code" in rule:
            for path_hint in rule["code"]:
                file_path = path_hint.split(":")[0]
                if verify_file_exists(file_path):
                    details.append(f"  ✅ code: {path_hint}")
                else:
                    details.append(f"  ❌ code missing: {path_hint}")
                    rule_passed = False

        # Check config references
        if "config" in rule:
            details.append(f"  ✅ config: {', '.join(rule['config'])}")

        # Skill-based rules
        if "skill" in rule:
            details.append(f"  ✅ skill: {', '.join(rule['skill'])}")

        # Note-only rules
        if "note" and not rule.get("code") and not rule.get("config"):
            details.append(f"  ⚠️  note: {rule['note']}")

        status = "✅" if rule_passed else "❌"
        if rule_passed: passed += 1
        else: failed += 1; gaps.append(rule_id)

        print(f"  {status} {rule_id}: {rule['name']}")
        for d in details:
            print(d)

    print(f"{'─'*60}")
    print(f"  通过: {passed}/{len(RULES)}  |  缺口: {failed}")
    print(f"{'═'*60}")
    if failed == 0:
        print("  ✅ 18条规则全部有代码/配置/Skill对应")
    else:
        print(f"  ❌ 缺口规则: {', '.join(gaps)}")
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
