"""shared_types — 跨项目共享类型 (workspace root)

All 5 projects import from here via `from scripts.shared_types import ...`.
Canonical single source of truth for cross-project enums and dataclasses.

Previously duplicated across:
  - eon-core/src/orchestrator_base.py
  - porpoise-agent/src/agent/orchestrator.py
  - coilia-agent/src/agent/orchestrator.py (set to None)

Usage:
  from scripts.shared_types import VerificationStatus, ContradictionType
"""

from __future__ import annotations

from enum import Enum


# ═══════════════════════════════════════════════════════
# VerificationStatus — 跨项目验证状态
# ═══════════════════════════════════════════════════════

class VerificationStatus(str, Enum):
    """Claim verification status — controls output gate.

    verified:      >=2 independent sources → allowed in output
    pending:       logical inference only → allowed with warning
    hypothesis:    plausible but lacks direct evidence → allowed with flag
    unverified:    cannot be verified → blocked from output
    unverifiable:  no source or verification path → blocked (alias for unverified)
    """
    VERIFIED = "verified"
    PENDING = "pending"
    HYPOTHESIS = "hypothesis"
    UNVERIFIED = "unverified"
    UNVERIFIABLE = "unverifiable"  # legacy alias from eon-core


# ═══════════════════════════════════════════════════════
# ContradictionType — 矛盾类型
# ═══════════════════════════════════════════════════════

class ContradictionType(str, Enum):
    """矛盾分析类型 — drives resource allocation strategy.

    antagonistic:     必须解决的对立矛盾 (2.5x budget)
    non_antagonistic: 可调和矛盾 (1.5x budget)
    structural:       结构性矛盾 (phasic approach)
    phasic:           阶段性矛盾 (stage-gated)
    """
    ANTAGONISTIC = "antagonistic"
    NON_ANTAGONISTIC = "non_antagonistic"
    STRUCTURAL = "structural"
    PHASIC = "phasic"
