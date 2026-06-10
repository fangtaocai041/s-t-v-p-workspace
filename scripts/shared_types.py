# 🚫 重定向至权威版本: eon-core/scripts/shared_types.py
# 只有 eon-core 版本是权威的
import sys as _sys
from pathlib import Path as _Path
_EON = str(_Path(__file__).resolve().parent.parent / "eon-core" / "scripts")
if _EON not in _sys.path:
    _sys.path.insert(0, _EON)

from shared_types import (  # noqa: F401
    VerificationStatus, ContradictionType,
)
