"""
工具与执行层 (Tool & Execution Layer)
──────────────────────────────────────
Agent 干涉外部环境并获取客观真实数据的物理或虚拟环境。

组件:
- Sandbox: 沙盒执行器 (隔离运行代码 + 捕获输出)
- ToolRegistry: 工具注册中心 (注册/发现/调用)
- APIClient: 外部 API 封装 (PubMed/CrossRef/Semantic Scholar/NCBI)
"""

from src.execution.sandbox import (
    SandboxExecutor,
    SandboxConfig,
    SandboxResult,
    execute_python,
    execute_safe,
)
from src.execution.tool_registry import (
    ToolRegistry,
    ToolSpec,
    ToolCall,
    tool,
    tools,
)
from src.execution.api import (
    APIClient,
    APIResult,
    api_client,
)

__all__ = [
    # Sandbox
    "SandboxExecutor",
    "SandboxConfig",
    "SandboxResult",
    "execute_python",
    "execute_safe",
    # Tool Registry
    "ToolRegistry",
    "ToolSpec",
    "ToolCall",
    "tool",
    "tools",
    # API
    "APIClient",
    "APIResult",
    "api_client",
]
