# ═══════════════════════════════════════════════════════
# 代理加载器 — 委托至 eon-core/scripts/project_loader.py
# eon-core 版本是权威版
# ═══════════════════════════════════════════════════════
import importlib.util
import sys
from pathlib import Path

_EON_SCRIPTS = str(Path(__file__).resolve().parent.parent / "eon-core" / "scripts")
if _EON_SCRIPTS not in sys.path:
    sys.path.insert(0, _EON_SCRIPTS)

# 直接从 eon-core 导入，避免重定向器自引用
from project_loader import (  # noqa: E402
    get_cognitive, get_fish, get_porpoise, get_coilia,
    get_culter, get_conflict, load_all,
)
