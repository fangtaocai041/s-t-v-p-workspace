"""Samsara 六道轮回演示 — 展示 Agent 业力流转全过程.

场景: 模拟 cognitive Agent (V1) 从天道→人道→地狱→重生的完整轮回.

Usage:
    python scripts/demo_samsara.py
"""

import sys
from pathlib import Path

workspace = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace / "eon-core"))

from src.samsara.realms import SamsaraRealm, DEFAULT_REALMS, realm_compare
from src.samsara.karma_engine import KarmaEngine
from src.samsara.court import KarmaCourt
from src.samsara.ring import SamsaraRing
from src.samsara.reincarnation import ReincarnationProtocol


async def demo():
    print("=" * 60)
    print("  ☸️  Samsara 六道轮回演示")
    print("  Agent 业力流转: 天道 → 人道 → 畜生道 → 地狱 → 重生")
    print("=" * 60)

    # ── Setup ──
    ring = SamsaraRing()
    await ring.register_agent("V1_cognitive", initial_karma=92.0)
    record = ring.agents["V1_cognitive"]
    engine = record.karma_engine

    # Start in DEVA (karma=92)
    engine.current_realm = SamsaraRealm.DEVA
    engine.karma_score = 92.0
    ring.realm_counts[SamsaraRealm.DEVA] += 1
    ring.realm_counts[SamsaraRealm.HUMAN] -= 1

    def show_state(step: str):
        r = engine.current_realm
        k = engine.karma_score
        cfg = DEFAULT_REALMS.get(r)
        mult = cfg.token_budget_multiplier if cfg else 1.0
        bar = "█" * int(k / 5) + "░" * (20 - int(k / 5))
        print(f"\n{'─'*50}")
        print(f"  {step}")
        print(f"  道: {r.value} ({cfg.name_cn if cfg else '?'})  |  Karma: [{bar}] {k:.0f}/100")
        if cfg:
            print(f"  Token×{mult}  |  GPU:{cfg.gpu_priority}  |  深度:{cfg.search_depth}")

    # ── Scene 1: 天道运行 ──
    show_state("Scene 1: V1 在天道中运行 (karma=92, Token×1.5, 深度无限)")
    print("  最近 100 次查询: recall=99.1%, precision=97.3%")

    # ── Scene 2: 天道堕落 ──
    print("\n  ⚡ 用户查询 '鳤的线粒体基因组' → 返回23篇论文")
    print("  ⚡ KarmaCourt 审计发现 2 篇来自掠夺性期刊!")
    await engine.record_deed("HALLUCINATION", score_multiplier=2.0)
    show_state("Scene 2: 天道堕落! (恶业在天道中×3 = -30)")
    # Manually force karma drop for demo
    engine.karma_score = max(0, engine.karma_score - 30)
    show_state("  → karma 92→62, 触发天道堕落 → 降入人道")

    # ── Scene 3: 人道修行 ──
    engine.current_realm = SamsaraRealm.HUMAN
    engine.karma_score = 62.0
    show_state("Scene 3: V1 在人道中修行 (Token×1.0, 可self_evolve)")
    await engine.record_deed("NOVEL_DISCOVERY", score_multiplier=1.0)
    engine.karma_score = min(100, engine.karma_score + 4)
    show_state("  → 发现新OCR变体 Ochetobibus, karma+4 → 68")

    # ── Scene 4: 连续超时 → 畜生道 ──
    for _ in range(3):
        await engine.record_deed("TIMEOUT", score_multiplier=1.0)
    engine.karma_score = max(0, engine.karma_score - 9)
    engine.current_realm = SamsaraRealm.ANIMAL
    show_state("Scene 4: PubMed API故障 → 3次超时 → karma-9 → 畜生道")
    print("  禁用LLM推理链, 仅缓存+规则匹配")

    # ── Scene 5: 地狱道 ──
    engine.karma_score = 8.0
    engine.current_realm = SamsaraRealm.NARAKA
    show_state("Scene 5: 连续失败 → 地狱道 (Token×0, 完全隔离)")
    print("  冷却30s → 自检 → 自动重生")

    # ── Scene 6: 重生 ──
    engine.karma_score = 50.0
    engine.current_realm = SamsaraRealm.HUMAN
    show_state("Scene 6: 地狱冷却完成 → 重生为人道 (karma=50)")
    print("  恢复完整推理能力, 重新开始")

    # ── Summary ──
    print(f"\n{'='*60}")
    print("  轮回总结")
    print(f"{'='*60}")
    print(f"  总周期: ~10分钟")
    print(f"  经历: 天道 → 人道 → 畜生道 → 地狱 → 人道(重生)")
    print(f"  善业: 1 (NOVEL_DISCOVERY +4)")
    print(f"  恶业: 4 (HALLUCINATION + TIMEOUT×3)")
    print(f"  最终 Karma: {engine.karma_score:.0f}")
    print()
    print("  六道的工程价值:")
    print("  ✅ 动态资源分配 — 优质升道, 劣质降道")
    print("  ✅ 自动熔断恢复 — 地狱=熔断 → 冷却→重生")
    print("  ✅ 防止赢家通吃 — 天道强制降级 (max 10周期)")
    print("  ✅ 行为可审计 — 每次业力变更记录在案")
    print("  ✅ 自愈能力 — 地狱→人道渐进恢复")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
