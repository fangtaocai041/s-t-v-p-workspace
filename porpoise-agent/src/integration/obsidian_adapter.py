"""
Obsidian 适配器 (Obsidian Adapter)
───────────────────────────────────
读写 Obsidian Vault 中的 Markdown 笔记。

能力:
- 读取课题组分析文档作为领域知识
- 按模板创建文献笔记到 文献笔记/ 目录
- 列出已有文献笔记
- 搜索笔记内容

Vault 路径: D:/Obsidian Vault (可通过环境变量 OBSIDIAN_VAULT_PATH 覆盖)

用法:
    from src.integration.obsidian_adapter import ObsidianAdapter

    obs = ObsidianAdapter()
    ctx = obs.load_domain_context()  # 加载课题组分析文档
    obs.write_literature_note(paper) # 写入文献笔记
"""

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_DEFAULT_VAULT = os.getenv("OBSIDIAN_VAULT_PATH", "D:/Obsidian Vault")

# 文献笔记模板 (Obsidian Markdown + YAML frontmatter)
_LITERATURE_NOTE_TEMPLATE = """---
title: "{title}"
authors: {authors}
year: {year}
journal: "{journal}"
doi: "{doi}"
source: "{source}"
added: {date}
tags: [literature, {tag_species}]
---

# {title}

## 基本信息

| 字段 | 值 |
|------|-----|
| 作者 | {authors} |
| 年份 | {year} |
| 期刊 | {journal} |
| DOI | [{doi}](https://doi.org/{doi}) |
| 来源 | {source} |

## 摘要

{abstract}

## 关键发现

<!-- TODO: 阅读后填写 -->

## 方法与技术

<!-- TODO: 阅读后填写 -->

## 与课题组关联

<!-- TODO: 分析后填写 -->

## 笔记

<!-- TODO: 阅读后填写 -->
"""


class ObsidianAdapter:
    """Obsidian Vault 读写适配器"""

    def __init__(self, vault_path: str = ""):
        self.vault_path = Path(vault_path or _DEFAULT_VAULT)
        self._available = self.vault_path.exists() and self.vault_path.is_dir()
        if self._available:
            self.notes_dir = self.vault_path / "文献笔记"
            self.notes_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"ObsidianAdapter connected to {self.vault_path}")
        else:
            logger.warning(f"Obsidian vault not found at {self.vault_path}")

    @property
    def available(self) -> bool:
        return self._available

    # ── 读取 ─────────────────────────────────────────

    def read_note(self, relative_path: str) -> str:
        """读取指定笔记"""
        full_path = self.vault_path / relative_path
        if full_path.exists():
            return full_path.read_text(encoding="utf-8")
        return ""

    def load_domain_context(self, max_chars: int = 6000) -> list[dict]:
        """
        加载课题组分析文档作为领域上下文。

        扫描 vault 根目录下的课题组相关 .md 文件，
        返回列表供注入 BDI Belief。
        """
        if not self.available:
            return []

        domain_files = [
            "刘凯研究员课题组研究方向.md",
            "刘凯老师课题组文献分析.md",
            "智能体分工协作指南.md",
        ]

        contexts = []
        for filename in domain_files:
            fpath = self.vault_path / filename
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8")
            # 截取前 max_chars，保留完整段落
            snippet = content[:max_chars]
            contexts.append({
                "source": f"obsidian:{filename}",
                "title": filename.replace(".md", ""),
                "content": snippet,
                "full_length": len(content),
            })
            logger.debug(f"Loaded Obsidian doc: {filename} ({len(content)} chars)")

        return contexts

    def search_notes(self, query: str, limit: int = 10) -> list[dict]:
        """搜索笔记内容"""
        if not self.available:
            return []

        results = []
        query_lower = query.lower()

        for md_file in self.vault_path.rglob("*.md"):
            if ".obsidian" in str(md_file):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                if query_lower in content.lower():
                    # 提取匹配行周围上下文
                    lines = content.split("\n")
                    matches = []
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            matches.append("\n".join(lines[start:end]))
                    if matches:
                        results.append({
                            "path": str(md_file.relative_to(self.vault_path)),
                            "title": md_file.stem,
                            "matches": matches[:3],
                            "size": len(content),
                        })
            except Exception:
                pass

        return results[:limit]

    def list_literature_notes(self) -> list[str]:
        """列出已有文献笔记"""
        if not self.available:
            return []
        return sorted([
            f.stem for f in self.notes_dir.glob("*.md")
        ])

    # ── 写入 ─────────────────────────────────────────

    def write_literature_note(self, paper: dict, species_tag: str = "") -> str:
        """
        按模板创建文献笔记。

        Args:
            paper: 论文 dict (title, authors, year, journal, doi, abstract, source)
            species_tag: 物种标签 (如 "江豚", "鳤")

        Returns:
            创建的文件路径 (相对 vault)
        """
        if not self.available:
            return ""

        title = paper.get("title", "Untitled")
        authors_list = paper.get("authors", [])
        authors_str = ", ".join(authors_list[:5])
        if len(authors_list) > 5:
            authors_str += f" et al. ({len(authors_list)} authors)"

        year = paper.get("year", "")
        journal = paper.get("journal", "")
        doi = paper.get("doi", "")
        abstract = paper.get("abstract", "暂无摘要")
        source = paper.get("source", "unknown")

        # 生成安全文件名
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)[:60]
        filename = f"{year}_{safe_title}.md" if year else f"{safe_title}.md"

        content = _LITERATURE_NOTE_TEMPLATE.format(
            title=title,
            authors=authors_str,
            year=year,
            journal=journal,
            doi=doi,
            source=source,
            abstract=abstract,
            date=datetime.now().strftime("%Y-%m-%d"),
            tag_species=species_tag or "待分类",
        )

        filepath = self.notes_dir / filename
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Obsidian note written: {filename}")

        return str(filepath.relative_to(self.vault_path))

    def append_to_note(self, relative_path: str, content: str):
        """追加内容到已有笔记"""
        full_path = self.vault_path / relative_path
        if full_path.exists():
            with open(full_path, "a", encoding="utf-8") as f:
                f.write("\n" + content)
            logger.debug(f"Appended to {relative_path}")


# ── 全局实例 ────────────────────────────────────────────────

_obsidian: Optional[ObsidianAdapter] = None


def get_obsidian() -> ObsidianAdapter:
    global _obsidian
    if _obsidian is None:
        _obsidian = ObsidianAdapter()
    return _obsidian
