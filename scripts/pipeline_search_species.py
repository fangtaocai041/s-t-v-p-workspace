#!/usr/bin/env python
"""pipeline_search_species.py — 物种文献检索可执行管线 (v8.1)

工程语言:
  WHEN query 含 "检索/搜索/查找/文献" THEN intent=SEARCH_LITERATURE → 全管线直通
  WHEN query 含 "是什么/基本信息/简介" THEN intent=QUERY → KB查询 + ask_choice
  WHEN query 无明确意图 THEN intent=AUTO → KB查询 + ask_choice

管线阶段:
  Phase 0: parse_intent(query) → {species, intent, genus, species_ep}
  Phase 1: kb_lookup(species) → KB {found, data, search_queries, variants}
  Phase 2: [SEARCH_LITERATURE] cognitive_search → papers
  Phase 3: score_credibility(papers) → scored_papers
  Phase 4: check_conflicts(scored_papers) → verdict

用法:
  python scripts/pipeline_search_species.py "珠星三块鱼"
  python scripts/pipeline_search_species.py "珠星三块鱼" --intent search
  python scripts/pipeline_search_species.py "Tribolodon brandti"
  python scripts/pipeline_search_species.py --test  # 运行测试集
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))

# ── Checkpoint manager for crash resilience ──
_PIPELINE_CHECKPOINT = None  # Lazy init

def _get_checkpoint(query: str) -> Optional[object]:
    """Get pipeline checkpoint manager for crash-resilient resume."""
    global _PIPELINE_CHECKPOINT
    if _PIPELINE_CHECKPOINT is None:
        try:
            import sys as _csys
            import os as _cos
            _e = _cos.path.normpath(_cos.path.join(_cos.path.dirname(__file__), '..', 'eon-core', 'src', 'shared'))
            if _e not in _csys.path:
                _csys.path.insert(0, _e)
            from checkpoint import CheckpointManager
            safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', query)[:60]
            _PIPELINE_CHECKPOINT = CheckpointManager(f"pipeline_{safe_name}")
        except ImportError:
            class _NullCheckpoint:
                def save(self, *a, **kw): pass
                def restore(self, *a): return None
                def has_checkpoint(self, *a): return False
                def complete(self): pass
            _PIPELINE_CHECKPOINT = _NullCheckpoint()
    return _PIPELINE_CHECKPOINT


# ═══════════════════════════════════════════════════════════════
# Types
# ═══════════════════════════════════════════════════════════════

class Intent(str, Enum):
    SEARCH_LITERATURE = "search_literature"  # 明确要检索文献 → 全管线直通
    QUERY = "query"                          # 查基本信息 → KB + ask_choice
    AUTO = "auto"                            # 不明确 → KB + ask_choice


@dataclass
class PhaseResult:
    phase: str
    status: str = "ok"
    elapsed_ms: float = 0
    data: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class PipelineResult:
    query: str = ""
    intent: Intent = Intent.AUTO
    species_name: str = ""
    phases: List[PhaseResult] = field(default_factory=list)
    kb_hit: bool = False
    kb_summary: str = ""
    paper_count: int = 0
    papers: list = field(default_factory=list)
    credibility_scores: list = field(default_factory=list)
    conflict_verdict: str = ""
    total_elapsed_ms: float = 0

    def summary(self) -> str:
        lines = [
            f"═══ 检索结果: {self.species_name} ═══",
            f"意图: {self.intent.value}",
            f"阶段: {' → '.join(p.phase for p in self.phases)}",
        ]
        if self.kb_hit:
            lines.append(f"知识库: ✓ 命中 — {self.kb_summary[:80]}")
        else:
            lines.append(f"知识库: ✗ 未命中 → 直接全管线")
        if self.paper_count:
            lines.append(f"文献: {self.paper_count} 篇")
            if self.credibility_scores:
                avg = sum(self.credibility_scores) / len(self.credibility_scores)
                lines.append(f"可信度: 均值 {avg:.1f}/100")
        if self.conflict_verdict:
            lines.append(f"仲裁: {self.conflict_verdict}")
        lines.append(f"耗时: {self.total_elapsed_ms:.0f}ms")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Phase 0: Intent Parser
# ═══════════════════════════════════════════════════════════════

# 工程规则: WHEN→THEN
SEARCH_PATTERNS = [
    # 中文: 动词 + 文献/论文
    r"检索.*文献", r"搜索.*文献", r"查找.*文献",
    r"搜.*文献", r"搜.*论文", r"找.*文献", r"查.*文献", r"查.*文章",
    r"文献检索", r"文献搜索",
    # 中文: 动词独立 (末尾)
    r"检索$", r"搜一下$", r"搜$",
    # 英文
    r"search.*literature", r"search.*paper", r"find.*paper",
]
QUERY_PATTERNS = [
    r"是什么", r"基本信息", r"简介", r"介绍", r"什么是",
    r"what is", r"who is", r"describe",
]

def parse_intent(query: str) -> tuple[Intent, str]:
    """Phase 0: 解析用户意图和物种名。

    WHEN query 匹配 SEARCH_PATTERNS THEN intent=SEARCH_LITERATURE
    WHEN query 匹配 QUERY_PATTERNS THEN intent=QUERY
    ELSE intent=AUTO
    """
    q = query.lower().strip()

    # Check SEARCH first (explicit literature search → no ask_choice)
    for pat in SEARCH_PATTERNS:
        if re.search(pat, q):
            # Extract species name by removing search keywords
            species = re.sub(
                r'检索|搜索|查找|搜一下|搜|找|文献|论文|文章|的|相关|一下|search|literature|paper|find',
                '', query, flags=re.IGNORECASE
            ).strip()
            return Intent.SEARCH_LITERATURE, species

    # Check QUERY
    for pat in QUERY_PATTERNS:
        if re.search(pat, q):
            species = re.sub(r'是什么|基本信息|简介|介绍|什么是', '', query).strip()
            return Intent.QUERY, species

    # AUTO — the query IS the species name
    return Intent.AUTO, query.strip()


# ═══════════════════════════════════════════════════════════════
# Phase 1: KB Lookup
# ═══════════════════════════════════════════════════════════════

def phase_kb_lookup(species: str) -> PhaseResult:
    """Phase 1: 查询鱼知识库。

    WHEN KB 命中 THEN 返回 species_data + search_queries + OCR variants
    WHEN KB 未命中 THEN 返回空 + 标记需全管线
    """
    t0 = time.time()
    try:
        from scripts.coordinator import coordinator
        result = coordinator.call("fish", query=species)
        elapsed = (time.time() - t0) * 1000

        if result.get("status") == "ok" and result.get("known_species"):
            data = result.get("species_data", {})
            return PhaseResult(
                phase="kb_lookup",
                status="ok",
                elapsed_ms=elapsed,
                data={
                    "hit": True,
                    "scientific_name": data.get("scientific_name", species),
                    "chinese_name": data.get("chinese_name", species),
                    "family": data.get("family", ""),
                    "conservation": data.get("conservation", ""),
                    "ecology": data.get("ecology", ""),
                    "synonyms": data.get("synonyms", []),
                    "aliases": data.get("aliases", []),
                    "search_queries": result.get("search_queries", []),
                    "ocr_variants": result.get("ocr_variants", []),
                    "distribution": data.get("distribution", {}),
                },
            )
        else:
            return PhaseResult(
                phase="kb_lookup",
                status="miss",
                elapsed_ms=elapsed,
                data={"hit": False, "query": species},
            )
    except Exception as e:
        return PhaseResult(
            phase="kb_lookup",
            status="error",
            elapsed_ms=(time.time() - t0) * 1000,
            error=str(e),
        )


# ═══════════════════════════════════════════════════════════════
# Phase 2: Cognitive Search (only for SEARCH_LITERATURE)
# ═══════════════════════════════════════════════════════════════

# PID-controlled adaptive timeout for cognitive search
_SEARCH_TIMEOUT_LIMITER = None  # Lazy init

def _get_search_timeout() -> float:
    """Get adaptive timeout using PID controller.

    Starts at 8s baseline, adjusts based on past search success/failure.
    Successful fast searches → timeout decreases (speed up).
    Failed/timeout searches → timeout increases (give more time).
    """
    global _SEARCH_TIMEOUT_LIMITER
    if _SEARCH_TIMEOUT_LIMITER is None:
        try:
            import sys as _psys
            import os as _pos
            _e = _pos.path.normpath(_pos.path.join(_pos.path.dirname(__file__), '..', 'eon-core', 'src', 'shared'))
            if _e not in _psys.path:
                _psys.path.insert(0, _e)
            from pid_limiter import PIDRateLimiter
            _SEARCH_TIMEOUT_LIMITER = PIDRateLimiter(
                target_error_rate=0.1,  # Allow 10% timeout rate
                kp=0.3, ki=0.05, kd=0.1,
                min_delay=3.0,   # At least 3s
                max_delay=20.0,  # At most 20s
                base_delay=8.0,  # Start at 8s
            )
        except ImportError:
            # Fallback to fixed 8s if eon-core not available
            class _FixedLimiter:
                def wait(self, *args, **kwargs): return 8.0
                def get_stats(self): return {}
            _SEARCH_TIMEOUT_LIMITER = _FixedLimiter()
    return _SEARCH_TIMEOUT_LIMITER.wait("cognitive_search", success=True)


def phase_cognitive_search(species: str, kb_data: dict) -> PhaseResult:
    """Phase 2: 多引擎文献搜索。

    MCP-first: scholar/article/ncbi/tavily/exa (用户配置的MCP服务器)
    HTTP-fallback: PubMed/Crossref/OpenAlex direct REST APIs
    内置自适应超时 (PID控制器, 3-20s)。
    """
    import threading

    t0 = time.time()
    result_container = {"result": None, "error": None, "mode": "unknown"}
    timeout = _get_search_timeout()

    def _do_search():
        try:
            from scripts.coordinator import coordinator
            # Get search mode before search
            info = coordinator.info("cognitive")
            result_container["mode"] = info.get("search_mode", "unknown")
            sci = kb_data.get("scientific_name", species)
            result_container["result"] = coordinator.call("cognitive", query=sci)
        except Exception as e:
            result_container["error"] = str(e)

    thread = threading.Thread(target=_do_search, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    elapsed = (time.time() - t0) * 1000
    success = True

    if thread.is_alive():
        success = False
        # Update PID: failure (timeout)
        if _SEARCH_TIMEOUT_LIMITER is not None:
            try:
                _SEARCH_TIMEOUT_LIMITER.wait("cognitive_search", success=False)
            except Exception:
                pass
        return PhaseResult(
            phase="cognitive_search",
            status="timeout",
            elapsed_ms=elapsed,
            error=f"search timed out after {timeout:.0f}s (PID-adjusted)",
            data={"papers": [], "query_used": species, "timeout_sec": timeout},
        )

    if result_container["error"]:
        return PhaseResult(
            phase="cognitive_search",
            status="error",
            elapsed_ms=elapsed,
            error=result_container["error"],
            data={"papers": []},
        )

    result = result_container["result"] or {}
    papers = []
    if isinstance(result, dict):
        papers = result.get("papers", result.get("result", {}).get("papers", []))
    if not papers:
        papers = result.get("result", []) if isinstance(result, dict) else []

    # Record search result for PID adaptation
    if _SEARCH_TIMEOUT_LIMITER is not None:
        try:
            _SEARCH_TIMEOUT_LIMITER.wait("cognitive_search", success=bool(papers))
        except Exception:
            pass

    return PhaseResult(
        phase="cognitive_search",
        status="ok" if papers else "empty",
        elapsed_ms=elapsed,
        data={
            "papers": papers if isinstance(papers, list) else [],
            "query_used": kb_data.get("scientific_name", species),
            "variants_used": kb_data.get("ocr_variants", [])[:3],
            "search_mode": result_container.get("mode", "unknown"),
        },
    )


# ═══════════════════════════════════════════════════════════════
# Phase 3: Credibility Scoring
# ═══════════════════════════════════════════════════════════════

def phase_score_credibility(papers: list) -> PhaseResult:
    """Phase 3: 可信度评分 (0-100)。"""
    t0 = time.time()
    try:
        from scripts.coordinator import coordinator
        result = coordinator.call("fish", query="credibility", _papers=papers)
        elapsed = (time.time() - t0) * 1000

        scores = []
        if isinstance(result, dict):
            scored = result.get("scored_papers", result.get("result", {}))
            if isinstance(scored, list):
                scores = [s.get("credibility", 50) if isinstance(s, dict) else 50 for s in scored]
            elif isinstance(scored, dict):
                scores = [scored.get("credibility", 50)]

        return PhaseResult(
            phase="credibility_scoring",
            status="ok",
            elapsed_ms=elapsed,
            data={"scores": scores, "count": len(scores)},
        )
    except Exception as e:
        return PhaseResult(
            phase="credibility_scoring",
            status="error",
            elapsed_ms=(time.time() - t0) * 1000,
            error=str(e),
        )


# ═══════════════════════════════════════════════════════════════
# Phase 4: Conflict Arbitration
# ═══════════════════════════════════════════════════════════════

def phase_check_conflicts(species: str, papers: list) -> PhaseResult:
    """Phase 4: 多源冲突检测。"""
    t0 = time.time()
    if len(papers) < 2:
        return PhaseResult(
            phase="conflict_check",
            status="skipped",
            elapsed_ms=0,
            data={"reason": "insufficient sources"},
        )
    try:
        from scripts.coordinator import coordinator
        result = coordinator.pathway("P5_all_to_conflict", species=species)
        elapsed = (time.time() - t0) * 1000

        verdict = ""
        if isinstance(result, dict):
            v = result.get("verdict", {})
            if isinstance(v, dict):
                verdict = v.get("verdict", v.get("consensus", ""))

        return PhaseResult(
            phase="conflict_check",
            status="ok",
            elapsed_ms=elapsed,
            data={"verdict": str(verdict)},
        )
    except Exception as e:
        return PhaseResult(
            phase="conflict_check",
            status="error",
            elapsed_ms=(time.time() - t0) * 1000,
            error=str(e),
        )


# ═══════════════════════════════════════════════════════════════
# Pipeline Runner
# ═══════════════════════════════════════════════════════════════

def run_pipeline(query: str, force_intent: Optional[str] = None) -> PipelineResult:
    """执行完整检索管线。

    Args:
        query: 用户查询 (如 "检索珠星三块鱼相关文献")
        force_intent: 可选，强制意图 ("search" | "query" | "auto")

    Returns:
        PipelineResult with full trace
    """
    t_total = time.time()

    result = PipelineResult(query=query)
    cpm = _get_checkpoint(query)

    # ── Phase 0: Parse intent ──
    if force_intent:
        intent_map = {"search": Intent.SEARCH_LITERATURE, "query": Intent.QUERY, "auto": Intent.AUTO}
        intent = intent_map.get(force_intent, Intent.AUTO)
        species = query
    else:
        intent, species = parse_intent(query)

    result.intent = intent
    result.species_name = species
    result.phases.append(PhaseResult(phase="parse_intent", data={"intent": intent.value, "species": species}))

    # ── Try checkpoint restore for SEARCH_LITERATURE ──
    if intent == Intent.SEARCH_LITERATURE and cpm.has_checkpoint("phase_3_conflict"):
        # Pipeline was previously completed — restore from final state
        saved = cpm.restore("phase_3_conflict")
        if saved:
            result.paper_count = saved.get("paper_count", 0)
            result.papers = saved.get("papers", [])
            result.conflict_verdict = saved.get("verdict", "")
            result.total_elapsed_ms = (time.time() - t_total) * 1000
            result.phases.append(PhaseResult(phase="checkpoint_restore", data={"from": "full_pipeline"}))
            return result

    # ── Phase 1: KB lookup (always) ──
    kb_restored = False
    if cpm.has_checkpoint("phase_1_kb"):
        saved_kb = cpm.restore("phase_1_kb")
        if saved_kb:
            kb = PhaseResult(
                phase="kb_lookup",
                status="ok",
                data=saved_kb
            )
            kb_restored = True

    if not kb_restored:
        kb = phase_kb_lookup(species)
        cpm.save("phase_1_kb", kb.data)

    result.phases.append(kb)
    result.kb_hit = kb.data.get("hit", False)

    if result.kb_hit:
        kb_data = kb.data
        result.species_name = kb_data.get("chinese_name", species)
        result.kb_summary = (
            f"{kb_data.get('scientific_name','?')} / "
            f"{kb_data.get('family','?')} / "
            f"{kb_data.get('ecology','?')}"
        )
    else:
        kb_data = {"scientific_name": species}

    # ── Branch: SEARCH_LITERATURE → full pipeline ──
    if intent == Intent.SEARCH_LITERATURE:
        # Phase 2: cognitive search
        cog_restored = False
        if cpm.has_checkpoint("phase_2_cognitive"):
            saved_cog = cpm.restore("phase_2_cognitive")
            if saved_cog:
                cog = PhaseResult(
                    phase="cognitive_search",
                    status=saved_cog.get("status", "restored"),
                    data=saved_cog.get("data", {}),
                )
                cog_restored = True

        if not cog_restored:
            cog = phase_cognitive_search(species, kb_data)
            cpm.save("phase_2_cognitive", {
                "status": cog.status,
                "data": cog.data,
                "query": species,
            })

        result.phases.append(cog)
        papers = cog.data.get("papers", [])
        result.paper_count = len(papers)
        result.papers = papers

        # Phase 3: credibility scoring
        if papers:
            cred_restored = False
            if cpm.has_checkpoint("phase_3_credibility"):
                saved_cred = cpm.restore("phase_3_credibility")
                if saved_cred:
                    cred = PhaseResult(
                        phase="credibility_scoring", status="ok",
                        data=saved_cred
                    )
                    cred_restored = True

            if not cred_restored:
                cred = phase_score_credibility(papers)
                cpm.save("phase_3_credibility", cred.data)

            result.phases.append(cred)
            result.credibility_scores = cred.data.get("scores", [])

        # Phase 4: conflict check
        conflict = phase_check_conflicts(species, papers)
        result.phases.append(conflict)
        result.conflict_verdict = conflict.data.get("verdict", "")

        # Final checkpoint
        cpm.save("phase_3_conflict", {
            "paper_count": result.paper_count,
            "papers": result.papers,
            "verdict": result.conflict_verdict,
        })

    elif intent == Intent.QUERY:
        # KB-only — just return what we have
        pass

    else:  # AUTO
        # KB hit → return KB data (caller does ask_choice)
        # KB miss → auto fallthrough to search
        if not result.kb_hit:
            cog = phase_cognitive_search(species, kb_data)
            result.phases.append(cog)
            papers = cog.data.get("papers", [])
            result.paper_count = len(papers)
            result.papers = papers

    result.total_elapsed_ms = (time.time() - t_total) * 1000
    return result


# ═══════════════════════════════════════════════════════════════
# Test Suite
# ═══════════════════════════════════════════════════════════════

TEST_CASES = [
    # (name, query, force_intent, expected_intent, expect_kb_hit, min_papers)
    ("TC01: 明确检索中文", "检索珠星三块鱼相关文献", None, Intent.SEARCH_LITERATURE, True, 0),
    ("TC02: 明确检索(简短)", "搜珠星三块鱼文献", None, Intent.SEARCH_LITERATURE, True, 0),
    ("TC03: 查基本信息", "珠星三块鱼是什么", None, Intent.QUERY, True, 0),
    ("TC04: 不明确意图", "珠星三块鱼", None, Intent.AUTO, True, 0),
    ("TC05: 学名检索", "Tribolodon brandti", "search", Intent.SEARCH_LITERATURE, True, 0),
    ("TC06: 冷启动(未知物种)", "Xyzzyx unknownus", "search", Intent.SEARCH_LITERATURE, False, 0),
    ("TC07: 强制搜索(中文)", "翘嘴鲌", "search", Intent.SEARCH_LITERATURE, True, 0),
    ("TC08: 别名检索", "东北三块鱼", None, Intent.AUTO, True, 0),
]


def run_tests() -> int:
    """运行测试集。返回失败数。"""
    passed = 0
    failed = 0

    print("=" * 70)
    print("  物种文献检索管线 — 测试集")
    print("=" * 70)

    for tc in TEST_CASES:
        name, query, force_intent, expected_intent, expect_kb, min_papers = tc
        print(f"\n{'─' * 60}")
        print(f"  {name}")
        print(f"  输入: {query}")
        if force_intent:
            print(f"  强制意图: {force_intent}")

        result = run_pipeline(query, force_intent=force_intent)

        errors = []
        # Check intent
        if expected_intent and result.intent != expected_intent:
            errors.append(f"意图错误: expected={expected_intent.value} got={result.intent.value}")
        # Check KB hit
        if expect_kb and not result.kb_hit:
            errors.append(f"KB应命中但未命中")
        if not expect_kb and result.kb_hit:
            errors.append(f"KB不应命中但却命中了")

        # Only check paper count for SEARCH_LITERATURE intent
        if result.intent == Intent.SEARCH_LITERATURE:
            if result.paper_count < min_papers:
                errors.append(f"文献数不足: got={result.paper_count} need>={min_papers}")
            # Check that cognitive_search phase exists
            has_cog = any(p.phase == "cognitive_search" for p in result.phases)
            if not has_cog:
                errors.append(f"缺少 cognitive_search 阶段")

        # Check QUERY intent should NOT trigger search
        if result.intent == Intent.QUERY:
            has_cog = any(p.phase == "cognitive_search" for p in result.phases)
            if has_cog:
                errors.append(f"QUERY意图不应触发cognitive搜索")

        # Print result
        if errors:
            print(f"  ✗ FAIL: {'; '.join(errors)}")
            failed += 1
        else:
            print(f"  ✓ PASS [{result.intent.value}] KB={'hit' if result.kb_hit else 'miss'} papers={result.paper_count} {result.total_elapsed_ms:.0f}ms")
            passed += 1

        # Print phase trace
        for p in result.phases:
            icon = "✓" if p.status == "ok" else ("⚠" if p.status in ("miss", "empty", "skipped") else "✗")
            extra = ""
            if p.phase == "cognitive_search":
                mode = p.data.get("search_mode", "?")
                extra = f" [{mode}]"
            print(f"    {icon} {p.phase:20s} [{p.status}] {p.elapsed_ms:.0f}ms{extra}")

        # For SEARCH_LITERATURE, show papers
        if result.intent == Intent.SEARCH_LITERATURE and result.papers:
            for i, p in enumerate(result.papers[:3]):
                title = p.get("title", str(p)) if isinstance(p, dict) else str(p)
                print(f"       📄 [{i+1}] {title[:70]}")

        if result.conflict_verdict:
            print(f"       ⚖️  {result.conflict_verdict[:80]}")

    print(f"\n{'=' * 70}")
    print(f"  结果: {passed} passed, {failed} failed, {len(TEST_CASES)} total")
    print(f"{'=' * 70}")
    return failed


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--test" in sys.argv:
        exit_code = run_tests()
        sys.exit(exit_code)

    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/pipeline_search_species.py <查询>")
        print("  python scripts/pipeline_search_species.py <查询> --intent search|query|auto")
        print("  python scripts/pipeline_search_species.py --test")
        print()
        print("示例:")
        print('  python scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"')
        print('  python scripts/pipeline_search_species.py "珠星三块鱼" --intent search')
        sys.exit(1)

    query = sys.argv[1]
    force = None
    if "--intent" in sys.argv:
        idx = sys.argv.index("--intent")
        force = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

    result = run_pipeline(query, force_intent=force)
    print(result.summary())
    print()

    # Show phases
    for p in result.phases:
        print(f"  [{p.status:7s}] {p.phase:20s} {p.elapsed_ms:.0f}ms")
        if p.error:
            print(f"         error: {p.error}")

    if result.papers:
        print(f"\n  文献 ({len(result.papers)} 篇):")
        for i, paper in enumerate(result.papers[:5]):
            if isinstance(paper, dict):
                title = paper.get("title", str(paper))
                year = paper.get("year", "?")
                source = paper.get("source", "?")
                print(f"  [{i+1}] ({year}) {title[:70]}")
                print(f"       source={source}")
