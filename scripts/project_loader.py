# ═══════════════════════════════════════════════════════
# 代理加载器 — 委托至 eon-core/scripts/project_loader.py
# eon-core 版本是权威版
# ═══════════════════════════════════════════════════════
import importlib.util
import sys
from pathlib import Path

_EON_LOADER = str(Path(__file__).resolve().parent.parent / "eon-core" / "scripts" / "project_loader.py")

_spec = importlib.util.spec_from_file_location("_eon_project_loader", _EON_LOADER)
if _spec and _spec.loader:
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["_eon_project_loader"] = _mod
    _spec.loader.exec_module(_mod)

    # Re-export all public names
    _EXPORTS = [
        "get_cognitive", "get_fish", "get_porpoise", "get_coilia",
        "get_culter", "get_conflict", "get_culter_orchestrator",
    ]
    for _name in _EXPORTS:
        if hasattr(_mod, _name):
            globals()[_name] = getattr(_mod, _name)

    __all__ = [n for n in _EXPORTS if n in globals()]
else:
    raise ImportError("Cannot load eon-core/scripts/project_loader.py")
