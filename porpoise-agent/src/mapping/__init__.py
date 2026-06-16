"""
逻辑映射与转换层 (Mapping & Translation Layer)
───────────────────────────────────────────────
跨越"语义空间"与"代码/系统空间"的桥梁。

组件:
- Router: 意图对齐与路由 (Intent → Tool/Agent mapping)
- Serializer: 工程语言化 (NL → Python/SQL/JSON/HTTP)
- Validator: 输出校验 (语法/安全/Schema)
"""

from src.mapping.router import (
    IntentRouter,
    Route,
    RouteTarget,
    RouteResult,
)
from src.mapping.serializer import (
    EngineeringSerializer,
    SerializedFormat,
    SerializedOutput,
    serialize_to_tool_call,
    nl_to_python,
)
from src.mapping.validator import (
    OutputValidator,
    ValidationStatus,
    ValidationIssue,
    ValidationResult,
)

__all__ = [
    # Router
    "IntentRouter",
    "Route",
    "RouteTarget",
    "RouteResult",
    # Serializer
    "EngineeringSerializer",
    "SerializedFormat",
    "SerializedOutput",
    "serialize_to_tool_call",
    "nl_to_python",
    # Validator
    "OutputValidator",
    "ValidationStatus",
    "ValidationIssue",
    "ValidationResult",
]
