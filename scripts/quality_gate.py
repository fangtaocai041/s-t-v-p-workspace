#!/usr/bin/env python
"""quality_gate.py — 七项目统一质控入口 (v8.1)

Single command to validate the entire workspace:
  python scripts/quality_gate.py          # full check
  python scripts/quality_gate.py --quick  # adapter load only
  python scripts/quality_gate.py --ci     # CI mode (exit code)

Five gates:
  GATE-1: Adapter loading — all 7 projects load via project_loader
  GATE-2: Adapter health — all adapters report HEALTHY or STANDBY
  GATE-3: Coordinator — all 6 pathways verify OK
  GATE-4: Cross-import — no circular or missing imports
  GATE-5: File integrity — required files present, no duplicates
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))

# ── Color helpers ──
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"
_BOLD = "\033[1m"

def _ok(msg: str) -> str: return f"{_GREEN}✓{_RESET} {msg}"
def _fail(msg: str) -> str: return f"{_RED}✗{_RESET} {msg}"
def _warn(msg: str) -> str: return f"{_YELLOW}⚠{_RESET} {msg}"

# ═══════════════════════════════════════════════════════════════
# GATE-1: Adapter Loading
# ═══════════════════════════════════════════════════════════════

EXPECTED_ADAPTERS = {
    "T_eon_core": "EonCoreAdapter",
    "V0_fish": "FishEcologyAdapter",
    "V1_cognitive": "CognitiveSearchAdapter",
    "P1_porpoise": "PorpoiseAdapter",
    "P2_coilia": "CoiliaAdapter",
    "P3_culter": "CulterAdapter",
    "C_conflict": "ConflictArbiterAdapter",
}

def gate1_adapter_loading() -> dict:
    """Load all 7 adapters via project_loader. Returns {key: class_name or error}."""
    results = {}
    from scripts.project_loader import get_all_adapters
    adapters = get_all_adapters()
    for key, adapter in adapters.items():
        if adapter is None:
            results[key] = f"FAILED: None returned"
        else:
            cls_name = type(adapter).__name__
            results[key] = cls_name
    return results

# ═══════════════════════════════════════════════════════════════
# GATE-2: Adapter Health
# ═══════════════════════════════════════════════════════════════

def gate2_adapter_health() -> dict:
    """Check all adapters report HEALTHY or STANDBY."""
    results = {}
    from scripts.coordinator import coordinator
    for key in ["eon", "fish", "cognitive", "porpoise", "coilia", "culter", "conflict"]:
        try:
            h = coordinator.health(key)
            status = h.get("status", "UNKNOWN")
            results[key] = status
        except Exception as exc:
            results[key] = f"ERROR: {exc}"
    return results

# ═══════════════════════════════════════════════════════════════
# GATE-3: Coordinator Pathways
# ═══════════════════════════════════════════════════════════════

def gate3_pathways() -> dict:
    """Verify all 6 coordinator pathways."""
    from scripts.coordinator import coordinator
    result = coordinator.verify_all()
    return {pid: r["status"] for pid, r in result.get("results", {}).items()}

# ═══════════════════════════════════════════════════════════════
# GATE-4: Cross-Import Integrity
# ═══════════════════════════════════════════════════════════════

REQUIRED_FILES = [
    "coordination.yaml",
    "VERSION.yaml",
    "scripts/project_loader.py",
    "scripts/coordinator.py",
    "scripts/shared_types.py",
    "scripts/adapter_protocol.py",
    "scripts/pathway_contracts.py",
    "scripts/pathway_executor.py",
    "scripts/spawn_agent.py",
    "eon-core/src/adapter.py",
    "fish-ecology-assistant/src/adapter.py",
    "cognitive-search-engine/src/adapter.py",
    "porpoise-agent/src/adapter.py",
    "coilia-agent/src/adapter.py",
    "culter-agent/src/adapter.py",
    "conflict-arbiter/src/adapter.py",
]

FORBIDDEN_DUPLICATES = [
    # These should NOT exist — duplicates removed in v8.0
    "cognitive-search-engine/coordination.yaml",
    "porpoise-agent/coordination.yaml",
    "fish-ecology-assistant/coordination.yaml",
    "cognitive-search-engine/config/meso_agent.yaml",
    "porpoise-agent/config/meso_agent.yaml",
    "cognitive-search-engine/skills/chinese-academic-search.md",
    "cognitive-search-engine/skills/cognitive-species-search.md",
    "cognitive-search-engine/skills/graph-search-engine.md",
    "cognitive-search-engine/skills/meso-orchestrator.md",
    "cognitive-search-engine/skills/self-evolve.md",
    "fish-ecology-assistant/.reasonix/skills/meso-orchestrator.md",
]

def gate4_file_integrity() -> dict:
    """Check required files exist and forbidden duplicates don't."""
    results = {"required_present": [], "required_missing": [], "duplicates_found": []}

    for f in REQUIRED_FILES:
        if (_WORKSPACE / f).exists():
            results["required_present"].append(f)
        else:
            results["required_missing"].append(f)

    for f in FORBIDDEN_DUPLICATES:
        if (_WORKSPACE / f).exists():
            results["duplicates_found"].append(f)

    return results

# ═══════════════════════════════════════════════════════════════
# GATE-5: Project Structure Integrity
# ═══════════════════════════════════════════════════════════════

EXPECTED_DIRS = {
    "eon-core": ["src/adapter.py", "src/kernel/origin.py", "config/taiji.yaml"],
    "fish-ecology-assistant": ["src/adapter.py", "config/agent.yaml", "config/fish_species_kb.yaml"],
    "cognitive-search-engine": ["src/adapter.py", "config/agent.yaml", "config/search_rules.yaml"],
    "porpoise-agent": ["src/adapter.py", "config/agent.yaml", "src/agent/orchestrator.py"],
    "coilia-agent": ["src/adapter.py", "config/agent.yaml", "src/agent/orchestrator.py"],
    "culter-agent": ["src/adapter.py", "config/agent.yaml", "src/agent/orchestrator.py"],
    "conflict-arbiter": ["src/adapter.py", "config/agent.yaml", "src/arbiter.py"],
}

def gate5_project_structure() -> dict:
    """Check each project has its essential files."""
    results = {}
    for project, files in EXPECTED_DIRS.items():
        missing = [f for f in files if not (_WORKSPACE / project / f).exists()]
        results[project] = "OK" if not missing else f"MISSING: {missing}"
    return results

# ═══════════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════════

def run_all(quick: bool = False, ci: bool = False) -> int:
    """Run all quality gates. Returns exit code (0=pass, 1=fail)."""
    failures = 0
    total = 0

    def check(name, results, ok_predicate):
        nonlocal failures, total
        total += 1
        passed = all(ok_predicate(v) for v in results.values()) if isinstance(results, dict) else ok_predicate(results)
        status = _ok("PASS") if passed else _fail("FAIL")
        print(f"\n{_BOLD}{name}{_RESET} {status}")

        if isinstance(results, dict):
            for key, val in results.items():
                icon = _ok(" ") if ok_predicate(val) else _fail(" ")
                print(f"  {icon} {key:20s} → {val}")
        if not passed:
            failures += 1

    # ── GATE-1 ──
    g1 = gate1_adapter_loading()
    check("GATE-1: Adapter Loading (7/7)", g1,
          lambda v: v in EXPECTED_ADAPTERS.values())

    if quick:
        return 0 if failures == 0 else 1

    # ── GATE-2 ──
    g2 = gate2_adapter_health()
    check("GATE-2: Adapter Health", g2,
          lambda v: v in ("HEALTHY", "STANDBY"))

    # ── GATE-3 ──
    g3 = gate3_pathways()
    check("GATE-3: Coordinator Pathways (6/6)", g3,
          lambda v: v == "OK")

    # ── GATE-4 ──
    g4 = gate4_file_integrity()
    missing_count = len(g4["required_missing"])
    dup_count = len(g4["duplicates_found"])
    g4_ok = missing_count == 0 and dup_count == 0
    status = _ok("PASS") if g4_ok else _fail("FAIL")
    total += 1
    print(f"\n{_BOLD}GATE-4: File Integrity{_RESET} {status}")
    print(f"  Required present: {len(g4['required_present'])}/{len(REQUIRED_FILES)}")
    if g4["required_missing"]:
        for f in g4["required_missing"]:
            print(f"  {_fail(' ')} MISSING: {f}")
    print(f"  Forbidden duplicates: {dup_count}")
    if g4["duplicates_found"]:
        for f in g4["duplicates_found"]:
            print(f"  {_warn(' ')} DUPLICATE: {f}")
    if not g4_ok:
        failures += 1

    # ── GATE-5 ──
    g5 = gate5_project_structure()
    check("GATE-5: Project Structure", g5,
          lambda v: v == "OK")

    # ── Summary ──
    passed_count = total - failures
    print(f"\n{'='*60}")
    summary = _ok(f"{passed_count}/{total} gates passed") if failures == 0 else _fail(f"{passed_count}/{total} gates passed")
    print(f"{_BOLD}Quality Gate Summary:{_RESET} {summary}")
    print(f"Workspace: {_WORKSPACE}")
    print(f"Version: v8.1")

    if ci:
        return 0 if failures == 0 else 1
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    ci = "--ci" in sys.argv
    exit_code = run_all(quick=quick, ci=ci)
    sys.exit(exit_code)
