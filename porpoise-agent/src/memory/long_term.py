"""
长期记忆 (Long-term Memory)
─────────────────────────────
借助向量数据库 (ChromaDB) 将历史交互、领域知识库转化为高维向量存储。
当需要时，通过余弦相似度召回相关信息，实现 RAG (Retrieval-Augmented Generation)。

存储架构:
- ChromaDB: 语义搜索 (文献、观测、笔记)
- 可选 Neo4j: 结构化知识图谱 (实体关系)
- 可选 SQLite: 结构化元数据索引

记忆演化函数 (MDP 形式化):
    M_lt+1 = Φ_lt(M_lt, O_t, A_t)
    其中 Φ_lt 将重要交互持久化到长期存储
"""

import logging
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ── 数据类型 ────────────────────────────────────────────────

@dataclass
class LongTermDocument:
    """长期记忆文档"""
    id: str
    content: str
    collection: str                     # literature / observations / notes / reports
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list[float]] = None
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0


@dataclass
class SearchResult:
    """检索结果"""
    document: LongTermDocument
    score: float                        # 相似度分数 (0-1)
    distance: float                     # 向量距离


# ── ChromaDB 后端 ──────────────────────────────────────────

class ChromaBackend:
    """
    ChromaDB 向量存储后端

    封装 ChromaDB 的持久化和查询操作。
    如果 ChromaDB 不可用，降级为内存字典 + 简单 TF-IDF。
    """

    def __init__(self, persist_dir: str = "./data/chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collections: dict[str, Any] = {}
        self._fallback: dict[str, list[dict]] = {}  # 降级存储
        self._chroma_available = False

        self._init_chroma()

    def _init_chroma(self):
        """初始化 ChromaDB 连接"""
        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )
            self._chroma_available = True
            logger.info(f"ChromaDB initialized at {self.persist_dir}")
        except ImportError:
            logger.warning("ChromaDB not installed — using in-memory fallback")
            self._chroma_available = False
        except Exception as e:
            logger.warning(f"ChromaDB init failed ({e}) — using in-memory fallback")
            self._chroma_available = False

    def get_or_create_collection(self, name: str) -> Any:
        """获取或创建 collection"""
        full_name = f"porpoise_{name}"

        if self._chroma_available and self._client:
            try:
                # 检查是否已缓存
                if full_name in self._collections:
                    return self._collections[full_name]

                # 尝试获取已存在的
                try:
                    coll = self._client.get_collection(full_name)
                except Exception:
                    coll = self._client.create_collection(full_name)

                self._collections[full_name] = coll
                return coll
            except Exception as e:
                logger.error(f"ChromaDB collection error: {e}")

        # Fallback
        if full_name not in self._fallback:
            self._fallback[full_name] = []
        return self._fallback[full_name]

    def add(
        self,
        collection: str,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None,
    ):
        """向 collection 添加文档"""
        coll = self.get_or_create_collection(collection)

        if self._chroma_available and hasattr(coll, 'add'):
            try:
                coll.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids or [f"doc_{int(time.time()*1000)}_{i}" for i in range(len(documents))],
                )
                logger.debug(f"Added {len(documents)} docs to {collection}")
                return
            except Exception as e:
                logger.error(f"ChromaDB add failed: {e}")

        # Fallback: 内存存储
        if isinstance(coll, list):
            for i, doc in enumerate(documents):
                coll.append({
                    "id": ids[i] if ids else f"doc_{len(coll)}",
                    "document": doc,
                    "metadata": metadatas[i] if metadatas else {},
                })

    def query(
        self,
        collection: str,
        query_texts: list[str],
        n_results: int = 5,
    ) -> dict:
        """查询 collection"""
        coll = self.get_or_create_collection(collection)

        if self._chroma_available and hasattr(coll, 'query'):
            try:
                return coll.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"],
                )
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}")

        # Fallback: 简单关键词匹配
        if isinstance(coll, list):
            results = []
            for query in query_texts:
                query_lower = query.lower()
                scored = []
                for doc in coll:
                    doc_text = doc.get("document", "").lower()
                    # 简单 TF 分数
                    score = sum(1 for word in query_lower.split() if word in doc_text)
                    scored.append((score, doc))
                scored.sort(key=lambda x: x[0], reverse=True)
                top = scored[:n_results]
                results.append({
                    "documents": [[d.get("document", "") for _, d in top]],
                    "metadatas": [[d.get("metadata", {}) for _, d in top]],
                    "distances": [[1.0 / max(s, 1) for s, _ in top]],
                })
            return self._merge_results(results)

        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def _merge_results(self, results: list[dict]) -> dict:
        """合并多个查询结果"""
        merged = {"documents": [], "metadatas": [], "distances": []}
        for r in results:
            merged["documents"].extend(r.get("documents", [[]]))
            merged["metadatas"].extend(r.get("metadatas", [[]]))
            merged["distances"].extend(r.get("distances", [[]]))
        return merged

    def delete_collection(self, name: str):
        """删除 collection"""
        full_name = f"porpoise_{name}"
        if self._chroma_available and self._client:
            try:
                self._client.delete_collection(full_name)
            except Exception:
                pass
        self._collections.pop(full_name, None)
        self._fallback.pop(full_name, None)


# ── 长期记忆管理器 ─────────────────────────────────────────

class LongTermMemory:
    """
    长期记忆 — 向量检索 + RAG

    支持 Collection:
    - literature: 科学论文和摘要
    - observations: 野外观察和 PAM 检测
    - notes: 研究笔记和假设
    - reports: 生成的报告和摘要
    - execution_log: 执行日志

    用法:
        ltm = LongTermMemory()
        ltm.add("literature", "江豚在长江中下游的分布...", metadata={"year": 2024})
        results = ltm.search("literature", "江豚分布", top_k=5)
        context = ltm.get_rag_context("江豚栖息地退化", max_tokens=2000)
    """

    def __init__(self, persist_dir: str = "./data/chroma_db"):
        self.backend = ChromaBackend(persist_dir)
        self._document_cache: dict[str, LongTermDocument] = {}
        logger.info(f"LongTermMemory initialized at {persist_dir}")

    def add(
        self,
        collection: str,
        content: str,
        metadata: Optional[dict] = None,
        doc_id: Optional[str] = None,
    ):
        """
        添加文档到长期记忆

        Args:
            collection: 集合名称
            content: 文档内容
            metadata: 元数据 (如 year, authors, doi)
            doc_id: 文档 ID (自动生成)
        """
        doc_id = doc_id or f"doc_{collection}_{int(time.time()*1000)}_{len(self._document_cache)}"

        doc = LongTermDocument(
            id=doc_id,
            content=content,
            collection=collection,
            metadata=metadata or {},
        )
        self._document_cache[doc_id] = doc

        self.backend.add(
            collection=collection,
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id],
        )
        logger.debug(f"LTM add: {doc_id} → {collection} ({len(content)} chars)")

    def add_batch(
        self,
        collection: str,
        documents: list[dict],  # [{"content": ..., "metadata": ...}]
    ):
        """批量添加文档"""
        contents = [d["content"] for d in documents]
        metadatas = [d.get("metadata", {}) for d in documents]
        ids = [
            f"doc_{collection}_{int(time.time()*1000)}_{i}"
            for i in range(len(documents))
        ]
        self.backend.add(collection, contents, metadatas, ids)
        logger.info(f"LTM batch add: {len(documents)} docs → {collection}")

    def search(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        语义搜索

        Args:
            collection: 集合名称
            query: 查询文本
            top_k: 返回结果数

        Returns:
            list[SearchResult]: 按相似度排序的结果
        """
        raw = self.backend.query(collection, [query], n_results=top_k)

        results = []
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        for i, doc_text in enumerate(docs):
            if not doc_text:
                continue
            dist = dists[i] if i < len(dists) else 1.0
            score = 1.0 / (1.0 + dist)  # 距离 → 相似度

            doc = LongTermDocument(
                id=f"result_{i}",
                content=doc_text,
                collection=collection,
                metadata=metas[i] if i < len(metas) else {},
            )
            results.append(SearchResult(document=doc, score=score, distance=dist))

        logger.debug(f"LTM search '{query[:50]}' → {len(results)} results")
        return results

    def get_rag_context(
        self,
        query: str,
        collections: Optional[list[str]] = None,
        max_tokens: int = 2000,
        top_k_per_collection: int = 3,
    ) -> str:
        """
        获取 RAG 上下文 — 为 LLM 注入相关领域知识

        Args:
            query: 用户查询
            collections: 搜索的集合 (默认全部)
            max_tokens: 最大返回 token 数
            top_k_per_collection: 每个集合的最大结果数

        Returns:
            str: 格式化的上下文文本
        """
        if collections is None:
            collections = ["literature", "observations", "notes", "reports"]

        all_results: list[SearchResult] = []
        for coll in collections:
            try:
                results = self.search(coll, query, top_k=top_k_per_collection)
                all_results.extend(results)
            except Exception as e:
                logger.debug(f"Search {coll} failed: {e}")

        # 按相似度排序
        all_results.sort(key=lambda r: r.score, reverse=True)

        # 组装上下文
        lines = ["## Relevant Knowledge (RAG)", ""]
        char_budget = max_tokens * 4  # 粗略: 1 token ≈ 4 chars
        used = 0

        for i, result in enumerate(all_results):
            snippet = result.document.content[:300]
            source = result.document.collection
            score_label = (
                "🟢" if result.score > 0.8 else
                "🟡" if result.score > 0.5 else "🔴"
            )

            entry = (
                f"### [{source}] {score_label} (similarity: {result.score:.2f})\n"
                f"{snippet}\n"
            )
            if used + len(entry) > char_budget:
                break
            lines.append(entry)
            used += len(entry)

        if not all_results:
            lines.append("*(No relevant knowledge found in long-term memory)*")

        return "\n".join(lines)

    def delete_document(self, collection: str, doc_id: str):
        """删除文档"""
        # ChromaDB 的删除有限，这里记录警告
        logger.warning(
            f"Document deletion: {doc_id} from {collection} — "
            f"ChromaDB delete requires full implementation"
        )
        self._document_cache.pop(doc_id, None)

    def clear_collection(self, collection: str):
        """清空集合"""
        self.backend.delete_collection(collection)
        # 清除缓存中属于该集合的文档
        to_remove = [
            did for did, doc in self._document_cache.items()
            if doc.collection == collection
        ]
        for did in to_remove:
            del self._document_cache[did]
        logger.info(f"Cleared collection: {collection}")

    def stats(self) -> dict:
        """记忆统计"""
        return {
            "cached_documents": len(self._document_cache),
            "by_collection": {
                coll: sum(1 for d in self._document_cache.values() if d.collection == coll)
                for coll in set(d.collection for d in self._document_cache.values())
            } if self._document_cache else {},
            "chroma_available": self.backend._chroma_available,
        }
