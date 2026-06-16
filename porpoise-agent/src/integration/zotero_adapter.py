"""
Zotero 适配器 (Zotero Adapter)
───────────────────────────────
直读 Zotero SQLite 本地数据库，无需 MCP 进程。

能力:
- 查询全部分类 (collections)
- 按分类获取论文列表
- 关键词搜索 (标题/摘要/DOI)
- 获取最新添加的论文
- 导出论文为 dict 格式 (兼容 Porpoise Agent)

数据库路径: D:/ZoteroData/zotero.sqlite (可通过环境变量 ZOTERO_DB_PATH 覆盖)

用法:
    from src.integration.zotero_adapter import ZoteroAdapter
    
    z = ZoteroAdapter()
    papers = z.search("江豚 声学")  # 在本地 406 条文献中搜索
    cols = z.list_collections()     # 列出全部分类
"""

import logging
import sqlite3
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 默认数据库路径
_DEFAULT_ZOTERO_DB = os.getenv("ZOTERO_DB_PATH", "D:/ZoteroData/zotero.sqlite")

# Zotero item type ID → 名称
_ITEM_TYPES = {
    2: "artwork", 3: "attachment", 7: "book", 8: "bookSection",
    11: "conferencePaper", 12: "dataset", 22: "journalArticle",
    24: "magazineArticle", 25: "manuscript", 27: "newspaperArticle",
    28: "note", 31: "preprint", 34: "report", 37: "thesis",
    40: "webpage",
}


class ZoteroAdapter:
    """Zotero SQLite 直读适配器"""

    def __init__(self, db_path: str = ""):
        self.db_path = db_path or _DEFAULT_ZOTERO_DB
        self._available = Path(self.db_path).exists()
        if self._available:
            logger.info(f"ZoteroAdapter connected to {self.db_path}")
        else:
            logger.warning(f"Zotero database not found at {self.db_path}")

    @property
    def available(self) -> bool:
        return self._available

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Collections ──────────────────────────────────

    def list_collections(self) -> list[dict]:
        """列出全部分类"""
        if not self.available:
            return []

        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT collectionID, collectionName, parentCollectionID "
                "FROM collections ORDER BY collectionName"
            ).fetchall()
            return [{"id": r["collectionID"], "name": r["collectionName"],
                     "parent_id": r["parentCollectionID"]} for r in rows]
        finally:
            conn.close()

    def get_collection_papers(self, collection_name: str) -> list[dict]:
        """按分类名获取论文"""
        if not self.available:
            return []

        conn = self._connect()
        try:
            rows = conn.execute("""
                SELECT DISTINCT i.itemID, i.key
                FROM items i
                JOIN collectionItems ci ON i.itemID = ci.itemID
                JOIN collections c ON ci.collectionID = c.collectionID
                WHERE c.collectionName = ?
                  AND i.itemTypeID NOT IN (3, 28)  -- exclude attachments, notes
            """, (collection_name,)).fetchall()

            papers = []
            for row in rows:
                paper = self._get_paper_by_id(conn, row["itemID"])
                if paper:
                    paper["zotero_collections"] = [collection_name]
                    papers.append(paper)
            return papers
        finally:
            conn.close()

    # ── Search ───────────────────────────────────────

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        在 Zotero 本地库中搜索。

        搜索范围: 标题、摘要、DOI、期?名

        Args:
            query: 搜索词 (支持中英文)
            limit: 最大返回数

        Returns:
            list[dict]: 匹配的论文
        """
        if not self.available:
            return []

        conn = self._connect()
        try:
            # 搜索标题和摘要
            like_query = f"%{query}%"
            rows = conn.execute("""
                SELECT DISTINCT i.itemID
                FROM items i
                LEFT JOIN itemData id_t ON i.itemID = id_t.itemID AND id_t.fieldID = 1
                LEFT JOIN itemDataValues v_t ON id_t.valueID = v_t.valueID
                LEFT JOIN itemData id_a ON i.itemID = id_a.itemID AND id_a.fieldID = 2
                LEFT JOIN itemDataValues v_a ON id_a.valueID = v_a.valueID
                LEFT JOIN itemData id_d ON i.itemID = id_d.itemID AND id_d.fieldID = 8
                LEFT JOIN itemDataValues v_d ON id_d.valueID = v_d.valueID
                WHERE i.itemTypeID NOT IN (3, 28)
                  AND (
                    v_t.value LIKE ?
                    OR v_a.value LIKE ?
                    OR v_d.value LIKE ?
                  )
                LIMIT ?
            """, (like_query, like_query, like_query, limit)).fetchall()

            papers = []
            for row in rows:
                paper = self._get_paper_by_id(conn, row["itemID"])
                if paper:
                    papers.append(paper)
            return papers
        finally:
            conn.close()

    def search_by_doi(self, doi: str) -> Optional[dict]:
        """按 DOI 精确查找"""
        if not self.available:
            return None

        conn = self._connect()
        try:
            row = conn.execute("""
                SELECT i.itemID
                FROM items i
                JOIN itemData id ON i.itemID = id.itemID AND id.fieldID = 8
                JOIN itemDataValues v ON id.valueID = v.valueID
                WHERE v.value = ?
                LIMIT 1
            """, (doi,)).fetchone()

            if row:
                return self._get_paper_by_id(conn, row["itemID"])
            return None
        finally:
            conn.close()

    def get_recent(self, limit: int = 10) -> list[dict]:
        """获取最近添加的论文"""
        if not self.available:
            return []

        conn = self._connect()
        try:
            rows = conn.execute("""
                SELECT i.itemID
                FROM items i
                WHERE i.itemTypeID NOT IN (3, 28)
                ORDER BY i.dateAdded DESC
                LIMIT ?
            """, (limit,)).fetchall()

            papers = []
            for row in rows:
                paper = self._get_paper_by_id(conn, row["itemID"])
                if paper:
                    papers.append(paper)
            return papers
        finally:
            conn.close()

    # ── Internal ─────────────────────────────────────

    def _get_paper_by_id(self, conn: sqlite3.Connection, item_id: int) -> Optional[dict]:
        """从 itemID 获取完整论文信息"""
        # Get item type
        item_row = conn.execute(
            "SELECT i.itemTypeID, i.key, i.dateAdded FROM items i WHERE i.itemID = ?",
            (item_id,)
        ).fetchone()
        if not item_row:
            return None

        item_type = _ITEM_TYPES.get(item_row["itemTypeID"], "unknown")
        if item_type == "attachment":
            return None

        # Get fields: title(1), abstract(2), date(6), DOI(8), url(10), extra(19)
        fields = conn.execute("""
            SELECT id.fieldID, v.value
            FROM itemData id
            JOIN itemDataValues v ON id.valueID = v.valueID
            WHERE id.itemID = ? AND id.fieldID IN (1, 2, 6, 8, 10, 19)
        """, (item_id,)).fetchall()

        field_map = {f["fieldID"]: f["value"] for f in fields}

        # Get creators (authors)
        creators = conn.execute("""
            SELECT c.firstName, c.lastName, ct.creatorType
            FROM itemCreators ic
            JOIN creators c ON ic.creatorID = c.creatorID
            JOIN creatorTypes ct ON ic.creatorTypeID = ct.creatorTypeID
            WHERE ic.itemID = ?
            ORDER BY ic.orderIndex
        """, (item_id,)).fetchall()

        authors = []
        for cr in creators:
            name = f"{cr['firstName'] or ''} {cr['lastName'] or ''}".strip()
            if name:
                authors.append(name)

        # Get publication info: journal(?), volume, issue, pages
        pub_fields = conn.execute("""
            SELECT id.fieldID, v.value
            FROM itemData id
            JOIN itemDataValues v ON id.valueID = v.valueID
            WHERE id.itemID = ? AND id.fieldID IN (
                SELECT fieldID FROM fieldsCombined
                WHERE fieldName IN ('publicationTitle', 'volume', 'issue', 'pages', 'publisher', 'place')
            )
        """, (item_id,)).fetchall()
        pub_map = {f["fieldID"]: f["value"] for f in pub_fields}

        # Find journal/publication name
        journal = ""
        for fid, fname in conn.execute(
            "SELECT fieldID, fieldName FROM fieldsCombined WHERE fieldName LIKE '%publication%' OR fieldName LIKE '%journal%'"
        ).fetchall():
            if fid in pub_map:
                journal = pub_map[fid]
                break

        # Get tags
        tags = conn.execute("""
            SELECT t.name FROM itemTags it
            JOIN tags t ON it.tagID = t.tagID
            WHERE it.itemID = ?
        """, (item_id,)).fetchall()
        tag_list = [t["name"] for t in tags]

        # Get collections
        collections = conn.execute("""
            SELECT c.collectionName FROM collectionItems ci
            JOIN collections c ON ci.collectionID = c.collectionID
            WHERE ci.itemID = ?
        """, (item_id,)).fetchall()
        col_list = [c["collectionName"] for c in collections]

        # Parse year from date
        year = None
        date_str = field_map.get(6, "")
        if date_str and len(date_str) >= 4:
            try:
                year = int(date_str[:4])
            except ValueError:
                pass

        return {
            "title": field_map.get(1, ""),
            "abstract": field_map.get(2, ""),
            "doi": field_map.get(8, ""),
            "url": field_map.get(10, ""),
            "year": year,
            "date": date_str,
            "authors": authors,
            "journal": journal,
            "item_type": item_type,
            "extra": field_map.get(19, ""),
            "tags": tag_list,
            "zotero_key": item_row["key"],
            "zotero_collections": col_list,
            "source": "zotero_local",
            "citations": 0,  # Zotero 不存储引用计数
        }


# ── 全局实例 ────────────────────────────────────────────────

_zotero: Optional[ZoteroAdapter] = None


def get_zotero() -> ZoteroAdapter:
    global _zotero
    if _zotero is None:
        _zotero = ZoteroAdapter()
    return _zotero
