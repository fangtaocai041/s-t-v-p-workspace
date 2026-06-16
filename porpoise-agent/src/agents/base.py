"""
Agent 基类 (Base Agent)
────────────────────────
所有专业 Agent 的共同基类。

每个 Agent 具备:
- BDI 状态 (Belief/Desire/Intention)
- 工具集 (受限的工具注册子集)
- 上下文窗口 (短期记忆)
- 消息处理接口 (统一的 handle_message)
- 功能生态位 (Functional Niche): 受限的能力范围
"""

import logging
from typing import Any, Optional

from src.cognitive.bdi import BDICoordinator, Belief, Desire
from src.execution.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Agent 基类

    子类需实现:
    - handle_message(msg) → 处理消息的核心逻辑
    - _init_tools() → 注册本 Agent 专有的工具
    - _init_desire() → 配置 BDI 愿望

    用法:
        class LiteratureAgent(BaseAgent):
            def _init_tools(self):
                self.tools.register("search_literature", ...)
            
            async def handle_message(self, msg):
                return await self.search_and_analyze(msg.content)
    """

    def __init__(
        self,
        name: str = "base",
        model: str = "deepseek-chat",
        memory: Any = None,
    ):
        self.name = name
        self.node_id = name  # 拓扑中的节点 ID (由 Topology 设置)
        self.model = model
        self.memory = memory

        # BDI
        self.bdi = BDICoordinator()
        self._init_desire()

        # 工具 (功能生态位)
        self.tools = ToolRegistry()
        self._init_tools()

        # 统计
        self._call_count = 0
        self._error_count = 0

        logger.info(f"Agent[{self.name}] initialized (model={model})")

    def _init_desire(self):
        """初始化 BDI Desire — 子类覆写"""
        self.bdi.desire = Desire(
            primary_goal=f"Execute {self.name} agent tasks",
            constraints=["Stay within role boundaries"],
        )

    def _init_tools(self):
        """初始化工具集 — 子类覆写"""
        pass

    async def handle_message(self, message: Any) -> Any:
        """
        处理消息 — 子类必须实现

        Args:
            message: Message 对象或 dict/str

        Returns:
            处理结果
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.handle_message() not implemented"
        )

    async def run(self, input_data: Any) -> Any:
        """快捷执行接口"""
        return await self.handle_message(input_data)

    def can_handle(self, intent: str) -> bool:
        """检查是否能处理某意图"""
        return False  # 子类覆写

    def get_capabilities(self) -> list[str]:
        """返回能力列表"""
        return [t.name for t in self.tools.list_tools()]

    def stats(self) -> dict:
        """Agent 统计"""
        return {
            "name": self.name,
            "node_id": self.node_id,
            "calls": self._call_count,
            "errors": self._error_count,
            "tools": len(self.tools.list_tools()),
            "bdi_status": self.bdi.status.value if self.bdi else "N/A",
        }
