"""
fishkb SQLite 知识库层

提供:
  - 物种的结构化存储 (SQLite + FTS5)
  - 全文搜索（学名/中文名/别名/文献标题）
  - 知识回补写回 API
  - 从 YAML/ Markdown 配置初始化

Extracted from fish-ecology-assistant/fish_ecology_assistant/db.py.

Usage:
    from fishkb.db import KnowledgeDB
    db = KnowledgeDB()
    db.init_from_yaml()           # 从 YAML 迁移
    species = db.lookup("鳤")      # 查询
    db.add_literature("ochetobius_elongatus", {...})  # 写回
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def _default_db_path() -> Path:
    """默认数据库路径: fishkb 包同级的 data/species.db"""
    return Path(__file__).resolve().parent.parent / "data" / "species.db"


def _default_kb_dir() -> Path:
    """默认知识库 Markdown 目录"""
    return Path(__file__).resolve().parent.parent / "config" / "knowledge_base" / "species"


class KnowledgeDB:
    """SQLite 知识库 — 兼容 KbFirstResult 接口"""

    def __init__(self, db_path: str | Path | None = None):
        db_path = Path(db_path) if db_path else _default_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS species (
                id TEXT PRIMARY KEY,
                scientific TEXT NOT NULL,
                chinese TEXT NOT NULL,
                family TEXT DEFAULT '',
                conservation TEXT DEFAULT '',
                status TEXT DEFAULT '',
                last_updated TEXT DEFAULT '',
                basins TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (species_id) REFERENCES species(id)
            );

            CREATE TABLE IF NOT EXISTS literature (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species_id TEXT NOT NULL,
                doi TEXT DEFAULT '',
                title TEXT NOT NULL,
                year INTEGER DEFAULT 0,
                journal TEXT DEFAULT '',
                authors TEXT DEFAULT '',
                category TEXT DEFAULT '',
                abstract TEXT DEFAULT '',
                added_at TEXT DEFAULT '',
                FOREIGN KEY (species_id) REFERENCES species(id)
            );

            CREATE INDEX IF NOT EXISTS idx_species_chinese ON species(chinese);
            CREATE INDEX IF NOT EXISTS idx_species_scientific ON species(scientific);
            CREATE INDEX IF NOT EXISTS idx_lit_species ON literature(species_id);
            CREATE INDEX IF NOT EXISTS idx_lit_title ON literature(title);
            CREATE VIRTUAL TABLE IF NOT EXISTS species_fts USING fts5(
                scientific, chinese, family, basins, content='species', content_rowid='rowid'
            );
        """)

    # ── 初始化 ──

    def init_from_yaml(self, kb_dir: str | Path | None = None) -> int:
        """从 Markdown 知识库文件迁移到 SQLite。

        Args:
            kb_dir: 包含 *.md 物种配置文件的目录。
                    默认: fishkb包同级的 config/knowledge_base/species/
        """
        kb_dir = Path(kb_dir) if kb_dir else _default_kb_dir()
        count = 0
        if not kb_dir.is_dir():
            return count
        for md_file in sorted(kb_dir.glob("*.md")):
            try:
                frontmatter, _ = self._parse_markdown(md_file)
                if not frontmatter:
                    continue
                self._insert_species(frontmatter)
                count += 1
            except Exception as e:
                print(f"  ⚠️ {md_file.name}: {e}")
        print(f"✅ 已迁移 {count} 个物种到 SQLite")
        self.conn.commit()
        return count

    def init_from_index(self,
                        index_path: str | Path,
                        profiles_dir: str | Path | None = None) -> int:
        """从 fish_species_index.yaml + Markdown 配置目录初始化。

        Args:
            index_path: fish_species_index.yaml 路径
            profiles_dir: Markdown 配置目录，默认从 index_path 的 config/knowledge_base/species 推断
        """
        index_path = Path(index_path)
        if profiles_dir:
            profiles_dir = Path(profiles_dir)
        else:
            profiles_dir = index_path.parent / "knowledge_base" / "species"

        index_data = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
        species_list = index_data.get("species", [])
        count = 0

        for entry in species_list:
            sid = entry["id"]
            species_data: Dict[str, Any] = {"id": sid}
            for k in ["name", "scientific", "family"]:
                if k in entry:
                    species_data[k] = entry[k]
            # Load detailed profile from .md file
            profile_path = profiles_dir / f"{sid}.md"
            if profile_path.is_file():
                fm, body = self._parse_markdown(profile_path)
                if fm:
                    species_data.update(fm)
            if "basins" not in species_data and entry.get("basins"):
                species_data["basins"] = entry["basins"]

            self._insert_species(species_data)
            count += 1

        print(f"✅ 已从索引迁移 {count} 个物种到 SQLite")
        self.conn.commit()
        return count

    def _parse_markdown(self, path: Path) -> tuple[dict, str]:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        return yaml.safe_load(parts[1]) or {}, parts[2].strip()

    def _insert_species(self, fm: dict) -> None:
        sid = fm.get("id", "")
        self.conn.execute(
            """INSERT OR REPLACE INTO species(id, scientific, chinese, family, conservation, status, last_updated, basins)
               VALUES(?,?,?,?,?,?,?,?)""",
            (sid, fm.get("scientific", ""), fm.get("name", ""),
             fm.get("family", ""), fm.get("conservation", ""),
             fm.get("status", ""), fm.get("last_updated", ""),
             ",".join(fm.get("basins", [])))
        )
        # Aliases
        for alias in fm.get("aliases", []):
            self.conn.execute("INSERT INTO aliases(species_id, alias) VALUES(?,?)", (sid, alias))
        # Literature
        for lit in fm.get("literature", []):
            self.conn.execute(
                """INSERT INTO literature(species_id, doi, title, year, journal, authors, category, added_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (sid, lit.get("doi", ""), lit.get("title", ""),
                 lit.get("year", 0), lit.get("journal", ""),
                 ",".join(lit.get("authors", [])), lit.get("category", ""),
                 datetime.now(timezone.utc).strftime("%Y-%m-%d"))
            )

    # ── 查询 API ──

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        """查询物种（精确匹配学名/中文名/别名）"""
        row = self.conn.execute(
            "SELECT * FROM species WHERE scientific=? OR chinese=? OR id=?",
            (query, query, query)
        ).fetchone()
        if row:
            return self._row_to_dict(row)
        # 别名匹配
        alias_row = self.conn.execute(
            "SELECT s.* FROM species s JOIN aliases a ON s.id=a.species_id WHERE a.alias=?",
            (query,)
        ).fetchone()
        if alias_row:
            return self._row_to_dict(alias_row)
        return None

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """全文搜索物种"""
        rows = self.conn.execute(
            "SELECT * FROM species_fts WHERE species_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
        if not rows:
            # Fallback: LIKE search
            like = f"%{query}%"
            rows = self.conn.execute(
                "SELECT * FROM species WHERE scientific LIKE ? OR chinese LIKE ? LIMIT ?",
                (like, like, limit)
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_literature(self, species_id: str) -> List[Dict[str, Any]]:
        """获取物种的文献列表"""
        rows = self.conn.execute(
            "SELECT * FROM literature WHERE species_id=? ORDER BY year DESC",
            (species_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def add_literature(self, species_id: str, paper: dict) -> int:
        """添加文献（知识回补写回）"""
        cur = self.conn.execute(
            """INSERT INTO literature(species_id, doi, title, year, journal, authors, category, added_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (species_id, paper.get("doi", ""), paper.get("title", ""),
             paper.get("year", 0), paper.get("journal", ""),
             ",".join(paper.get("authors", [])), paper.get("category", ""),
             datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        return cur.lastrowid

    def list_all(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM species ORDER BY chinese").fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]

    def _row_to_dict(self, row) -> Dict[str, Any]:
        d: Dict[str, Any] = dict(row)
        d["aliases"] = [r[0] for r in self.conn.execute(
            "SELECT alias FROM aliases WHERE species_id=?", (d["id"],)
        ).fetchall()]
        d["literature_count"] = self.conn.execute(
            "SELECT COUNT(*) FROM literature WHERE species_id=?", (d["id"],)
        ).fetchone()[0]
        return d

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ── 单例 ──
_instance: Optional[KnowledgeDB] = None


def get_db(db_path: str | Path | None = None) -> KnowledgeDB:
    """获取 KnowledgeDB 单例。"""
    global _instance
    if _instance is None:
        _instance = KnowledgeDB(db_path)
    return _instance
