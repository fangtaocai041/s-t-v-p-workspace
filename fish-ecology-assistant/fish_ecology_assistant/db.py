"""
fish-ecology-assistant SQLite 知识库层

替代 YAML 文件扫描，提供:
  - 30 物种的结构化存储
  - 全文搜索（学名/中文名/别名/文献标题）
  - 知识回补写回 API
  - 与现有 orchestrator 兼容的接口

用法:
    from fish_ecology_assistant.db import KnowledgeDB
    db = KnowledgeDB()
    db.init_from_yaml()           # 从 YAML 迁移
    species = db.lookup("鳤")      # 查询
    db.add_literature("ochetobius_elongatus", {...})  # 写回
"""

from __future__ import annotations

import sqlite3
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "config" / "knowledge_base" / "species"
DB_PATH = ROOT / "data" / "species.db"


class KnowledgeDB:
    """SQLite 知识库 — 兼容现有 KbFirstResult 接口"""

    def __init__(self, db_path: str | Path = DB_PATH):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
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

    # ── YAML → SQLite 迁移 ──

    def init_from_yaml(self) -> int:
        """从 config/knowledge_base/species/*.md 迁移到 SQLite"""
        count = 0
        for md_file in sorted(KB_DIR.glob("*.md")):
            try:
                frontmatter, _ = self._parse_markdown(md_file)
                if not frontmatter:
                    continue
                self._insert_species(frontmatter)
                count += 1
            except Exception as e:
                print(f"  ⚠️ {md_file.name}: {e}")
        print(f"✅ 已迁移 {count} 个物种到 SQLite")
        return count

    def _parse_markdown(self, path: Path) -> tuple[dict, str]:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        return yaml.safe_load(parts[1]) or {}, parts[2].strip()

    def _insert_species(self, fm: dict):
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
        d = dict(row)
        d["aliases"] = [r[0] for r in self.conn.execute(
            "SELECT alias FROM aliases WHERE species_id=?", (d["id"],)
        ).fetchall()]
        d["literature_count"] = self.conn.execute(
            "SELECT COUNT(*) FROM literature WHERE species_id=?", (d["id"],)
        ).fetchone()[0]
        return d

    def close(self):
        self.conn.close()


# ── 单例 ──
_instance: Optional[KnowledgeDB] = None

def get_db() -> KnowledgeDB:
    global _instance
    if _instance is None:
        _instance = KnowledgeDB()
    return _instance
