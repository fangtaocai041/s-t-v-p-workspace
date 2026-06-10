"""ConflictArbiterAdapter — conflict-arbiter (冲突仲裁).

核心专精: assess_conflict(sources: list) → ConflictReport
    多源保护推荐冲突检测 + 可信度加权仲裁 + 熔断
    通路: P5(any→conflict) P6(conflict→user)

Usable as a cross-project arbitration layer — any project's output
can be routed here for consistency checking before finalizing a
conservation recommendation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object


class ConflictArbiterAdapter(IProjectAdapter):
    """Adapter for conflict-arbiter (V4 — 冲突仲裁层)."""

    project_name = "conflict-arbiter"

    def __init__(self) -> None:
        self._arbiter: Any = None
        self._init()

    def _init(self) -> None:
        try:
            # Add src/ to sys.path so absolute import works under project_loader
            import sys as _sys
            _src_path = str(Path(__file__).resolve().parent)
            if _src_path not in _sys.path:
                _sys.path.insert(0, _src_path)
            from arbiter import ConflictArbiter
            cfg = Path(__file__).resolve().parent.parent / "config" / "agent.yaml"
            self._arbiter = ConflictArbiter(config_path=cfg if cfg.is_file() else None)
        except Exception as exc:
            logger.warning(f"Arbiter init failed: {exc}")

    # ── IProjectAdapter interface ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute conflict arbitration.

        Args:
            query: Species name or description
            kwargs:
                sources: List of source dicts [{source, protection_level, iucn, ...}]
                claims: List of claim dicts [{claim, source, weight, value}]

        Returns:
            Conflict report with conflict_level, consensus, verdict
        """
        if not self._arbiter:
            return {"status": "error", "error": "Arbiter not initialized"}

        species_name = kwargs.get("species", query)
        sources = kwargs.get("sources", [])
        claims = kwargs.get("claims", [])
        region = kwargs.get("region", "china")

        if sources:
            return self._arbiter.detect_conflicts(species_name, sources, region=region)
        elif claims:
            return self._arbiter.arbitrate(species_name, claims)
        else:
            return {
                "status": "ok",
                "message": "conflict-arbiter ready. Pass sources=[] or claims=[] for arbitration.",
                "species_name": species_name,
            }

    def health(self) -> Dict[str, Any]:
        if self._arbiter:
            return self._arbiter.health()
        return {"project": self.project_name, "status": "DEGRADED"}

    def info(self) -> Dict[str, Any]:
        if self._arbiter:
            return self._arbiter.info()
        return {
            "project": self.project_name,
            "role": "冲突仲裁层",
            "capabilities": ["conflict_detection", "weighted_arbitration", "circuit_breaker"],
        }


def get_adapter() -> ConflictArbiterAdapter:
    return ConflictArbiterAdapter()
