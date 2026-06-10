"""project_loader — 七项目统一 DirectLoader.

Replaces scattered spec_from_file_location calls across meso-cosmos,
porpoise, and coilia with a single, version-aware loading interface.

Usage:
  from scripts.project_loader import get_cognitive, get_porpoise, get_coilia, get_fish, get_eon

  cog = get_cognitive()    # → CognitiveSearchAdapter
  por = get_porpoise()     # → PorpoiseAdapter
  coi = get_coilia()       # → CoiliaAdapter
  fish = get_fish()        # → FishEcologyAdapter
  eon = get_eon()          # → EonCoreAdapter

Design:
  - Single importlib cache per project (module loaded once, reused)
  - Absolute path resolution from workspace root
  - Each project exposes get_adapter() → IProjectAdapter
  - Fallback to stub if project not found
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# Workspace root resolution
# ═══════════════════════════════════════════════════════════════

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Ensure workspace root is on sys.path so adapters can import
# shared modules like scripts.adapter_protocol
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))


def _resolve_project(project_name: str) -> Optional[Path]:
    """Resolve absolute path to a sibling project directory.

    IF project directory exists at workspace root THEN return Path.
    ELSE return None.
    """
    path = _WORKSPACE_ROOT / project_name
    if path.is_dir():
        return path
    return None


# ═══════════════════════════════════════════════════════════════
# IProjectAdapter — imported from shared protocol module
# ═══════════════════════════════════════════════════════════════

from scripts.adapter_protocol import IProjectAdapter


# ═══════════════════════════════════════════════════════════════
# DirectLoader engine (cached)
# ═══════════════════════════════════════════════════════════════

# Module-level cache: {project_name: adapter_instance}
_cache: Dict[str, IProjectAdapter] = {}


def _load_adapter(project_name: str, adapter_rel_path: str, class_name: str) -> Optional[IProjectAdapter]:
    """Generic DirectLoader: load adapter class from project, instantiate, cache.

    Args:
      project_name: e.g. "cognitive-search-engine"
      adapter_rel_path: e.g. "src/adapter.py"
      class_name: e.g. "CognitiveSearchAdapter"

    Returns: IProjectAdapter instance or None if project/class not found.
    """
    if project_name in _cache:
        return _cache[project_name]

    project_root = _resolve_project(project_name)
    if project_root is None:
        logger.warning(f"Project {project_name} not found at {_WORKSPACE_ROOT}")
        return None

    adapter_file = project_root / adapter_rel_path
    if not adapter_file.is_file():
        logger.warning(f"Adapter not found: {adapter_file}")
        return None

    # Ensure project root is on sys.path (first) for internal imports
    proj_str = str(project_root)
    if proj_str in sys.path:
        sys.path.remove(proj_str)
    sys.path.insert(0, proj_str)

    try:
        # Use "src.adapter" as module name so relative imports
        # (from .orchestrator) resolve correctly against the src/ package.
        module_name = "src.adapter"
        spec = importlib.util.spec_from_file_location(module_name, str(adapter_file))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        adapter_cls = getattr(mod, class_name, None)
        if adapter_cls is None:
            # Try get_adapter() factory function
            factory = getattr(mod, "get_adapter", None)
            if factory:
                adapter = factory()
                _cache[project_name] = adapter
                return adapter
            logger.warning(f"Class {class_name} not found in {adapter_file}")
            return None

        adapter = adapter_cls()
        _cache[project_name] = adapter
        return adapter
    except Exception as exc:
        logger.warning(f"Failed to load {project_name} adapter: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════
# Public API: get_<project>() functions
# ═══════════════════════════════════════════════════════════════


def get_cognitive() -> Optional[IProjectAdapter]:
    """Load cognitive-search-engine (V1 — 验证引擎).

    Adapter: cognitive-search-engine/src/adapter.py → CognitiveSearchAdapter
    Falls back to meso_agent.MesoAgent if adapter.py not found.
    """
    adapter = _load_adapter("cognitive-search-engine", "src/adapter.py", "CognitiveSearchAdapter")
    if adapter is not None:
        return adapter

    # Fallback: load meso_agent directly
    return _load_adapter("cognitive-search-engine", "src/meso_agent.py", "MesoAgent")


def get_porpoise() -> Optional[IProjectAdapter]:
    """Load porpoise-agent (P₁ — 江豚领域专研, 衍生自三角).

    Adapter: porpoise-agent/src/adapter.py → PorpoiseAdapter
    """
    return _load_adapter("porpoise-agent", "src/adapter.py", "PorpoiseAdapter")


def get_coilia() -> Optional[IProjectAdapter]:
    """Load coilia-agent (P₂ — 刀鲚领域专研, 衍生自三角).

    Adapter: coilia-agent/src/adapter.py → CoiliaAdapter
    """
    return _load_adapter("coilia-agent", "src/adapter.py", "CoiliaAdapter")


def get_culter() -> Optional[IProjectAdapter]:
    """Load culter-agent (P₃ — 鲌类领域专研, 衍生自三角).

    Adapter: culter-agent/src/adapter.py → CulterAdapter
    """
    return _load_adapter("culter-agent", "src/adapter.py", "CulterAdapter")


def get_fish() -> Optional[IProjectAdapter]:
    """Load fish-ecology-assistant (V0 — 知识供给).

    Adapter: fish-ecology-assistant/src/adapter.py → FishEcologyAdapter
    """
    return _load_adapter("fish-ecology-assistant", "src/adapter.py", "FishEcologyAdapter")


def get_eon() -> Optional[IProjectAdapter]:
    """Load eon-core (三角·协调内核).

    Adapter: eon-core/src/adapter.py → EonCoreAdapter
    """
    return _load_adapter("eon-core", "src/adapter.py", "EonCoreAdapter")


def get_conflict() -> Optional[IProjectAdapter]:
    """Load conflict-arbiter (V4 — 冲突仲裁, 火 🟥).

    Adapter: conflict-arbiter/src/adapter.py → ConflictArbiterAdapter
    """
    return _load_adapter("conflict-arbiter", "src/adapter.py", "ConflictArbiterAdapter")


def get_all_adapters() -> Dict[str, Optional[IProjectAdapter]]:
    """Load all 7 adapters at once."""
    return {
        "T_eon_core": get_eon(),
        "V0_fish": get_fish(),
        "V1_cognitive": get_cognitive(),
        "P1_porpoise": get_porpoise(),
        "P2_coilia": get_coilia(),
        "P3_culter": get_culter(),
        "C_conflict": get_conflict(),
    }


def clear_cache() -> None:
    """Clear the module cache (for testing/reload)."""
    _cache.clear()
