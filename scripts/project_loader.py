# ═══════════════════════════════════════════════════════
# 代理加载器 — 委托至 eon-core/scripts/project_loader.py
# eon-core 版本是权威版
# ═══════════════════════════════════════════════════════
import sys
from pathlib import Path

_EON_SCRIPTS = str(Path(__file__).resolve().parent.parent / "eon-core" / "scripts")
if _EON_SCRIPTS not in sys.path:
    sys.path.insert(0, _EON_SCRIPTS)

# 直接从 eon-core 导入，避免重定向器自引用
import importlib.util as _import_util

_eon_path = str(Path(__file__).resolve().parent.parent / "eon-core" / "scripts" / "project_loader.py")
_spec = _import_util.spec_from_file_location("eon_project_loader", _eon_path)
_eon_mod = _import_util.module_from_spec(_spec)
_spec.loader.exec_module(_eon_mod)
get_fish = _eon_mod.get_fish
get_cognitive = _eon_mod.get_cognitive
get_porpoise = _eon_mod.get_porpoise
get_coilia = _eon_mod.get_coilia
get_culter = _eon_mod.get_culter
get_conflict = _eon_mod.get_conflict
load_all = _eon_mod.load_all

__all__ = [
    "get_fish",
    "get_cognitive",
    "get_porpoise",
    "get_coilia",
    "get_culter",
    "get_conflict",
    "load_all",
]
