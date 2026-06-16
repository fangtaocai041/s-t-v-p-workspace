"""
短期记忆 (Short-term Memory)
─────────────────────────────
依赖 LLM 上下文窗口 (Context Window)，记录当前对话轮次中的
临时信息和即时状态。

核心机制:
- 上下文窗口管理: 滑动窗口 + 令牌预算
- 摘要压缩: 当上下文接近窗口上限时，自动压缩旧内容
- 优先级队列: 重要信息保留更久
- 遗忘曲线: 模拟人类记忆衰减

记忆演化函数 (MDP 形式化):
    M_st+1 = Φ_st(M_st, O_t, A_t)
    其中 Φ_st 是短期记忆更新函数
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryPriority(int, Enum):
    """记忆优先级"""
    CRITICAL = 5    # 系统指令、安全约束
    HIGH = 4        # 用户目标、关键结果
    MEDIUM = 3      # 工具调用结果
    LOW = 2         # 中间推理
    TRANSIENT = 1   # 临时/可丢弃


@dataclass
class MemoryItem:
    """
    短期记忆条目

    每个条目有:
    - 内容
    - 优先级 (决定保留时间)
    - 时间戳 (用于遗忘曲线)
    - 令牌数估算
    """
    content: str
    role: str = "system"               # system / user / assistant / tool
    priority: MemoryPriority = MemoryPriority.MEDIUM
    timestamp: float = field(default_factory=time.time)
    token_estimate: int = 0            # 估算 token 数
    metadata: dict = field(default_factory=dict)

    def age_seconds(self) -> float:
        """计算条目年龄 (秒)"""
        return time.time() - self.timestamp

    def effective_priority(self) -> float:
        """
        计算有效优先级 (随时间衰减)

        类似 Ebbinghaus 遗忘曲线:
            effective = priority * e^(-λ * age)
        λ 是衰减率
        """
        decay_rate = 0.0001  # 衰减率 (可配置)
        age = self.age_seconds()
        decay = 2.71828 ** (-decay_rate * age)
        return self.priority.value * decay


class ShortTermMemory:
    """
    短期记忆 — 上下文窗口管理器

    约束:
    - max_tokens: 总令牌预算 (默认 8000, 留给模型响应空间)
    - 超过 80% 时触发压缩
    - 低于阈值的条目被压缩为摘要

    用法:
        stm = ShortTermMemory(max_tokens=8000)
        stm.add("用户提问: ...", role="user", priority=MemoryPriority.HIGH)
        stm.add("工具结果: ...", role="tool", priority=MemoryPriority.MEDIUM)
        context = stm.get_context()  # 获取当前窗口内容
    """

    def __init__(
        self,
        max_tokens: int = 8000,
        compression_threshold: float = 0.8,
        decay_rate: float = 0.0001,
    ):
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        self.decay_rate = decay_rate

        self.items: list[MemoryItem] = []
        self._compressed_summary: str = ""
        self._token_count: int = 0

        logger.info(
            f"ShortTermMemory initialized (max_tokens={max_tokens}, "
            f"threshold={compression_threshold})"
        )

    def add(
        self,
        content: str,
        role: str = "system",
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        metadata: Optional[dict] = None,
    ):
        """
        添加记忆条目

        Args:
            content: 条目内容
            role: 角色 (system/user/assistant/tool)
            priority: 优先级
            metadata: 附加元数据
        """
        token_estimate = self._estimate_tokens(content)
        # Convert int to enum if needed
        if isinstance(priority, int):
            priority = MemoryPriority(priority)
        item = MemoryItem(
            content=content,
            role=role,
            priority=priority,
            token_estimate=token_estimate,
            metadata=metadata or {},
        )
        self.items.append(item)
        self._token_count += token_estimate

        logger.debug(
            f"Memory added: {role} [{priority.name}] "
            f"~{token_estimate}t ({self._token_count}/{self.max_tokens}t total)"
        )

        # 检查是否需要压缩
        if self._token_count > self.max_tokens * self.compression_threshold:
            self._compress()

    def get_context(
        self,
        max_tokens: Optional[int] = None,
        include_compressed: bool = True,
    ) -> str:
        """
        获取当前上下文窗口内容

        Args:
            max_tokens: 输出最大 token 数 (默认全部)
            include_compressed: 是否包含压缩摘要

        Returns:
            str: 格式化的上下文文本
        """
        limit = max_tokens or self.max_tokens
        parts: list[str] = []

        # 压缩摘要放在最前面
        if include_compressed and self._compressed_summary:
            parts.append(f"[Compressed Context]\n{self._compressed_summary}\n")

        # 按优先级排序 (关键信息在前)
        sorted_items = sorted(
            self.items,
            key=lambda i: i.effective_priority(),
            reverse=True,
        )

        token_budget = limit - self._estimate_tokens(self._compressed_summary)
        used_tokens = 0

        for item in sorted_items:
            if used_tokens + item.token_estimate > token_budget:
                break
            prefix = {"user": "User", "assistant": "Agent", "tool": "Tool", "system": "System"}
            role_label = prefix.get(item.role, item.role)
            parts.append(f"[{role_label}] {item.content}")
            used_tokens += item.token_estimate

        return "\n\n".join(parts)

    def get_recent(self, n: int = 5) -> list[MemoryItem]:
        """获取最近 n 条记忆"""
        return self.items[-n:]

    def get_by_priority(self, min_priority: MemoryPriority) -> list[MemoryItem]:
        """按优先级筛选"""
        return [i for i in self.items if i.priority.value >= min_priority.value]

    def clear(self):
        """清空短期记忆"""
        self.items.clear()
        self._compressed_summary = ""
        self._token_count = 0
        logger.info("ShortTermMemory cleared")

    def _compress(self):
        """
        压缩低优先级旧条目为摘要

        策略:
        1. 找出所有 TRANSIENT + LOW 优先级的条目
        2. 将其中最旧的 50% 压缩为摘要
        3. 从 items 中移除被压缩的条目
        """
        # 可压缩的条目
        compressible = [
            i for i in self.items
            if i.priority <= MemoryPriority.LOW
        ]
        if len(compressible) < 3:
            return

        # 取最旧的一半
        compressible.sort(key=lambda i: i.timestamp)
        to_compress = compressible[: len(compressible) // 2]

        # 生成摘要
        summary_parts = []
        for item in to_compress:
            # 截取每条内容的前 100 字符
            snippet = item.content[:100].replace("\n", " ")
            summary_parts.append(f"- {snippet}...")

        new_summary = "Earlier context:\n" + "\n".join(summary_parts)

        # 更新压缩摘要
        if self._compressed_summary:
            self._compressed_summary += "\n" + new_summary
        else:
            self._compressed_summary = new_summary

        # 移除被压缩的条目
        compressed_ids = {id(i) for i in to_compress}
        freed_tokens = sum(i.token_estimate for i in to_compress)
        self.items = [i for i in self.items if id(i) not in compressed_ids]
        self._token_count -= freed_tokens

        logger.info(
            f"Compressed {len(to_compress)} items → "
            f"freed ~{freed_tokens}t (now {self._token_count}/{self.max_tokens}t)"
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        估算 token 数

        粗略估算: 英文 ~1.3 token/词, 中文 ~2 token/字
        更精确的估算应使用 tiktoken。
        """
        if not text:
            return 0

        # 统计中文字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        # 统计英文单词
        english_words = len(text.split()) - chinese_chars // 2  # 粗略调整

        return int(chinese_chars * 2.0 + english_words * 1.3)

    def stats(self) -> dict:
        """记忆状态统计"""
        return {
            "n_items": len(self.items),
            "token_count": self._token_count,
            "max_tokens": self.max_tokens,
            "usage_pct": self._token_count / max(self.max_tokens, 1) * 100,
            "has_compressed": bool(self._compressed_summary),
            "priority_distribution": {
                p.name: sum(1 for i in self.items if i.priority == p)
                for p in MemoryPriority
            },
        }
