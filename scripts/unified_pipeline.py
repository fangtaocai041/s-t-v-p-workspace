#!/usr/bin/env python3
"""
unified_pipeline.py — 八项目统一执行链 v1.0
============================================

端到端物种研究管道: S(knowledge) → V(verify) → P₁P₂P₃(domain) → C(arbitrate) → score

用法:
  python scripts/unified_pipeline.py "鳤" --species "Ochetobius elongatus"
  python scripts/unified_pipeline.py "刀鲚" --species "Coilia nasus" --verbose
  python scripts/unified_pipeline.py --list  # 列出支持的物种

每次执行记录 trace_id 用于追踪。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))


# ── 数据结构 ──

@dataclass
class StageResult:
    project: str
    status: str  # completed | skipped | failed
    duration_ms: float = 0.0
    summary: str = ""
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    query: str
    species: str
    trace_id: str
    timestamp: str
    stages: Dict[str, StageResult] = field(default_factory=dict)
    total_duration_ms: float = 0.0

    @property
    def completed(self) -> int:
        return sum(1 for s in self.stages.values() if s.status == "completed")

    @property
    def failed(self) -> int:
        return sum(1 for s in self.stages.values() if s.status == "failed")

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "species": self.species,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "stages": {k: asdict(v) for k, v in self.stages.items()},
            "completed": self.completed,
            "failed": self.failed,
            "total_duration_ms": round(self.total_duration_ms, 1),
        }


# ── 管道执行 ──

class UnifiedPipeline:
    """八项目统一执行管道.

    执行顺序:
      S (fish-ecology-assistant) → 知识库查询
      V (cognitive-search-engine) → 文献验证
      P₁ (porpoise-agent) → 江豚专研
      P₂ (coilia-agent) → 鲚属专研
      P₃ (culter-agent) → 鲌类专研
      C (conflict-arbiter) → 保护等级仲裁
      score → 综合可信度评分
    """

    def __init__(self):
        self.trace_id = uuid.uuid4().hex

    def run(self, query: str, species: str = "", verbose: bool = False) -> PipelineResult:
        t0 = time.time()
        result = PipelineResult(
            query=query,
            species=species or query,
            trace_id=self.trace_id,
            timestamp=datetime.now().isoformat(),
        )

        # Load all adapters
        if verbose:
            print(f"[{self.trace_id[:8]}] Loading adapters...")
        from scripts.project_loader import (
            get_fish, get_cognitive, get_porpoise,
            get_coilia, get_culter, get_conflict,
        )

        adapters = {
            "S_fish": ("fish-ecology-assistant", get_fish()),
            "V_cognitive": ("cognitive-search-engine", get_cognitive()),
            "P1_porpoise": ("porpoise-agent", get_porpoise()),
            "P2_coilia": ("coilia-agent", get_coilia()),
            "P3_culter": ("culter-agent", get_culter()),
            "C_conflict": ("conflict-arbiter", get_conflict()),
        }

        # Execute each stage
        for stage_id, (proj_name, adapter) in adapters.items():
            if adapter is None:
                result.stages[stage_id] = StageResult(
                    project=proj_name, status="skipped",
                    summary="Adapter unavailable",
                )
                continue

            t1 = time.time()
            stage = StageResult(project=proj_name, status="failed")
            try:
                resp = adapter.search(query, species=species or query)
                duration = (time.time() - t1) * 1000
                stage.duration_ms = round(duration, 1)

                if isinstance(resp, dict):
                    status = resp.get("status", "ok")
                    stage.status = "completed" if status in ("ok", "healthy") else "failed"
                    stage.summary = str(resp.get("summary", resp.get("message", "")))
                    stage.data = resp
                else:
                    stage.status = "completed"
                    stage.summary = str(resp)[:200]
            except Exception as e:
                stage.status = "failed"
                stage.error = str(e)[:200]

            result.stages[stage_id] = stage

            if verbose:
                icon = "OK" if stage.status == "completed" else "SKIP" if stage.status == "skipped" else "FAIL"
                print(f"  [{icon}] {stage_id:<14} {proj_name:<22} {stage.duration_ms:8.1f}ms"
                      f"{'  ' + stage.error[:60] if stage.error else ''}")

        result.total_duration_ms = round((time.time() - t0) * 1000, 1)
        return result


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(
        description="八项目统一执行链 — 端到端物种研究管道"
    )
    parser.add_argument("query", nargs="?", default="", help="搜索查询词")
    parser.add_argument("--species", "-s", default="", help="物种学名")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示每个阶段详情")
    parser.add_argument("--json", "-j", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--list", action="store_true", help="列出支持的物种查询示例")
    args = parser.parse_args()

    if args.list:
        examples = [
            ("鳤", "Ochetobius elongatus"),
            ("刀鲚", "Coilia nasus"),
            ("长江江豚", "Neophocaena asiaeorientalis"),
            ("翘嘴鲌", "Culter alburnus"),
            ("珠星三块鱼", "Tribolodon hakonensis"),
        ]
        print("支持查询示例:")
        for q, s in examples:
            print(f"  {q:<12} → {s}")
        return

    if not args.query:
        parser.print_help()
        return

    pipeline = UnifiedPipeline()
    result = pipeline.run(args.query, args.species, verbose=args.verbose or not args.json)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Trace: {result.trace_id}")
        print(f"Query: {result.query}  |  Species: {result.species}")
        print(f"{'='*60}")
        for sid, stage in result.stages.items():
            icons = {"completed": "OK", "skipped": "--", "failed": "FAIL"}
            icon = icons.get(stage.status, "??")
            print(f"  [{icon}] {sid:<14} {stage.duration_ms:8.1f}ms  {stage.summary[:80]}")
            if stage.error:
                print(f"         error: {stage.error[:120]}")
        print(f"{'='*60}")
        print(f"  Completed: {result.completed}/{len(result.stages)}  |  "
              f"Failed: {result.failed}  |  "
              f"Total: {result.total_duration_ms:.0f}ms")


if __name__ == "__main__":
    main()
