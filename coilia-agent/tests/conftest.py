"""conftest — 在 pytest 收集前加 workspace 根到 sys.path。"""
import sys
from pathlib import Path

# Add workspace root so scripts.test_pn_base is importable
_workspace = str(Path(__file__).resolve().parent.parent.parent)
if _workspace not in sys.path:
    sys.path.insert(0, _workspace)
