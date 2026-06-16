"""
记忆协调器 (Memory Manager)
─────────────────────────────
统一管理短期记忆和长期记忆，提供单一读写接口。

对应 MDP 中的记忆演化函数:
    M_t+1 = Φ(M_t, O_t, A_t)

其中:
    M_t = (STM_t, LTM_t)        # 短期 + 长期记忆
    O_t = 当前观察
    A_t = 当前动作

演化逻辑:
    1. 所有交互先写入 STM
    2. 高优先级 / 标记持久化的内容异步写入 LTM
    3. 查询时: 先查 STM → 不足时查 LTM (RAG)
    4. 上下文窗口超限时: STM 压缩 → 低优先级冲入 LTM
"""

import logging
from typing import Any, Optional

from src.memory.short_term import (
    ShortTermMemory,
    MemoryItem,
    MemoryPriority,
)
from src.memory.long_term import (
    LongTermMemory,
    SearchResult,
)

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    记忆协调器 — 统一的记忆读写接口

    架构:
        ┌─────────────────────────────┐
        │       MemoryManager         │
        │  ┌─────────┐  ┌──────────┐  │
        │  │   STM   │  │   LTM    │  │
        │  │ (快速)  │  │ (持久)   │  │
        │  └────┬────┘  └────┬─────┘  │
        │       └──────┬──────┘        │
        │         同步 / 冲入          │
        └─────────────────────────────┘

    用法:
        mm = MemoryManager(max_stm_tokens=8000, persist_dir="./data/chroma_db")
        mm.remember("用户: 搜索江豚文献", priority=MemoryPriority.HIGH)
        context = mm.recall("江豚被动声学监测")
        mm.persist("literature", "论文摘要...", metadata={"year": 2024})
    """

    def __init__(
        self,
        max_stm_tokens: int = 8000,
        persist_dir: str = "./data/chroma_db",
        auto_persist_threshold: MemoryPriority = MemoryPriority.HIGH,
    ):
        self.stm = ShortTermMemory(max_tokens=max_stm_tokens)
        self.ltm = LongTermMemory(persist_dir=persist_dir)
        self.auto_persist_threshold = auto_persist_threshold

        logger.info(
            f"MemoryManager initialized (STM={max_stm_tokens}t, "
            f"LTM={persist_dir})"
        )

        # 初始化时自动加载领域知识库到 LTM
        self._load_knowledge_bases(persist_dir)

    # ── 写入 ──────────────────────────────────────────

    def remember(
        self,
        content: str,
        role: str = "system",
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        metadata: Optional[dict] = None,
        persist: bool = False,
    ):
        """
        记忆: 将信息写入短期记忆

        Args:
            content: 内容
            role: 角色
            priority: 优先级
            metadata: 元数据
            persist: 是否同时持久化到 LTM
        """
        # Convert int to enum if needed
        if isinstance(priority, int):
            priority = MemoryPriority(priority)

        self.stm.add(content, role=role, priority=priority, metadata=metadata)

        # 自动持久化高优先级内容
        if persist or priority.value >= self.auto_persist_threshold.value:
            self.ltm.add(
                collection="interactions",
                content=content,
                metadata={
                    "role": role,
                    "priority": priority.name,
                    **(metadata or {}),
                },
            )

    def persist(
        self,
        collection: str,
        content: str,
        metadata: Optional[dict] = None,
        doc_id: Optional[str] = None,
    ):
        """
        持久化: 将内容直接写入长期记忆

        Args:
            collection: 集合 (literature/observations/notes/reports)
            content: 文档内容
            metadata: 元数据
            doc_id: 文档 ID
        """
        self.ltm.add(collection, content, metadata=metadata, doc_id=doc_id)

    def memorize_step(
        self,
        observation: dict,
        action: Optional[dict] = None,
        reflection: Optional[str] = None,
    ):
        """
        记录一次执行步骤 (用于记忆演化 Φ)

        同时写入 STM 和 LTM (执行日志)

        Args:
            observation: 观察结果
            action: 执行的动作
            reflection: 反思内容
        """
        import json

        step_record = json.dumps(
            {
                "observation": observation,
                "action": action,
                "reflection": reflection,
            },
            ensure_ascii=False,
            default=str,
        )

        # STM: 记录最近步骤
        self.stm.add(
            step_record[:500],  # STM 中截取前 500 字符
            role="tool",
            priority=MemoryPriority.MEDIUM,
        )

        # LTM: 完整记录
        self.ltm.add(
            collection="execution_log",
            content=step_record,
            metadata={
                "action_name": action.get("name", "") if action else "",
                "has_error": bool(observation.get("error")),
            },
        )

    # ── 读取 ──────────────────────────────────────────

    def recall(
        self,
        query: str,
        include_stm: bool = True,
        include_ltm: bool = True,
        max_stm_items: int = 5,
        max_ltm_results: int = 3,
    ) -> dict[str, Any]:
        """
        回忆: 从记忆中检索相关信息

        策略: STM 优先 (最近) + LTM 补充 (RAG)

        Args:
            query: 查询
            include_stm: 是否查短期记忆
            include_ltm: 是否查长期记忆
            max_stm_items: STM 最大返回条目
            max_ltm_results: LTM 最大返回结果

        Returns:
            dict: {"stm_results": [...], "ltm_results": [...], "combined": "..."}
        """
        result: dict[str, Any] = {"stm_results": [], "ltm_results": [], "combined": ""}

        # STM 检索 (按优先级 + 相关性)
        if include_stm:
            stm_items = self.stm.get_recent(max_stm_items)
            result["stm_results"] = [
                {"content": item.content[:300], "role": item.role, "priority": item.priority.name}
                for item in stm_items
            ]

        # LTM 检索 (语义搜索)
        if include_ltm:
            ltm_results = self.ltm.search(
                "interactions", query, top_k=max_ltm_results
            )
            result["ltm_results"] = [
                {"content": r.document.content[:300], "score": r.score}
                for r in ltm_results
            ]

        # 合并上下文
        parts = []
        if result["stm_results"]:
            parts.append("## Short-term (recent)")
            for r in result["stm_results"]:
                parts.append(f"- [{r['role']}] {r['content']}")
        if result["ltm_results"]:
            parts.append("## Long-term (retrieved)")
            for r in result["ltm_results"]:
                parts.append(f"- (score: {r['score']:.2f}) {r['content']}")

        result["combined"] = "\n\n".join(parts)
        return result

    def get_context_for_llm(
        self,
        query: str,
        max_tokens: int = 4000,
    ) -> str:
        """
        获取 LLM 上下文 — 合并 STM + LTM RAG

        这是主要的对外接口: 在每次 LLM 调用前获取相关上下文。
        """
        parts = []

        # RAG 上下文 (LTM)
        rag = self.ltm.get_rag_context(query, max_tokens=max_tokens // 2)
        if rag and "No relevant knowledge" not in rag:
            parts.append(rag)

        # 最近对话 (STM)
        stm_context = self.stm.get_context(max_tokens=max_tokens // 2)
        if stm_context:
            parts.append(stm_context)

        return "\n\n---\n\n".join(parts)

    # ── 维护 ──────────────────────────────────────────

    def flush(self):
        """
        冲入: 将 STM 中所有内容持久化到 LTM

        用于会话结束或检查点。
        """
        for item in self.stm.items:
            if item.priority.value >= MemoryPriority.MEDIUM.value:
                self.ltm.add(
                    collection="interactions",
                    content=item.content,
                    metadata={"role": item.role, "priority": item.priority.name},
                )
        logger.info(f"Flushed {len(self.stm.items)} STM items → LTM")

    def clear(self, what: str = "all"):
        """
        清除记忆

        Args:
            what: "stm" | "ltm" | "all"
        """
        if what in ("stm", "all"):
            self.stm.clear()
        if what in ("ltm", "all"):
            for coll in ["literature", "observations", "notes", "reports", "interactions", "execution_log"]:
                self.ltm.clear_collection(coll)
        logger.info(f"Memory cleared: {what}")

    def _load_knowledge_bases(self, persist_dir: str):
        """
        启动时加载领域知识库到长期记忆。

        扫描 data/knowledge_base/ 下的 .md 文件，
        按节段拆分后存入 LTM (collection="knowledge_base")。
        """
        try:
            from pathlib import Path
            kb_dir = Path("data/knowledge_base")
            if not kb_dir.exists():
                return

            for kb_file in kb_dir.glob("*.md"):
                content = kb_file.read_text(encoding="utf-8")
                # 按 ## 标题拆分为独立文档块
                sections = content.split("\n## ")
                for i, section in enumerate(sections):
                    title = section.split("\n")[0].strip("# ")[:80] if section.strip() else kb_file.stem
                    doc_id = f"kb_{kb_file.stem}_{i}"
                    self.ltm.add(
                        collection="knowledge_base",
                        content=section[:2000],
                        metadata={
                            "source": str(kb_file),
                            "title": title,
                            "doc_id": doc_id,
                        },
                        doc_id=doc_id,
                    )
            logger.info(f"Loaded {len(list(kb_dir.glob('*.md')))} knowledge base files into LTM")
        except Exception as e:
            logger.debug(f"Knowledge base loading skipped: {e}")

    def stats(self) -> dict:
        """记忆统计"""
        return {
            "stm": self.stm.stats(),
            "ltm": self.ltm.stats(),
        }
