"""
Knowledge Base Loader — 解析 data/knowledge_base/species/*.md 为结构化数据。

格式: 去注释后的缩进型 YAML-like 结构，纯标准库实现，零外部依赖。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeBase:
    """加载并索引 species/ 目录下所有 markdown 知识条目。"""

    def __init__(self, root: Optional[Path] = None) -> None:
        if root is None:
            root = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
        self._root = Path(root)
        self._species: Dict[str, Dict[str, Any]] = {}
        self._load_all()

    # ── Public API ──

    @property
    def species_ids(self) -> List[str]:
        return list(self._species.keys())

    def get_species(self, species_id: str) -> Optional[Dict[str, Any]]:
        return self._species.get(species_id)

    def find_by_scientific(self, name: str) -> Optional[Dict[str, Any]]:
        """按学名查找 (大小写不敏感)。"""
        nl = name.strip().lower()
        for s in self._species.values():
            sci = (s.get("scientific") or "").strip().lower()
            if sci == nl:
                return s
        return None

    def find_by_chinese(self, name: str) -> Optional[Dict[str, Any]]:
        """按中文名查找。"""
        for s in self._species.values():
            cn = s.get("chinese", "")
            cns = s.get("common_names", [])
            if name in cn or name in cns:
                return s
        return None

    # ── Loading ──

    def _load_all(self) -> None:
        species_dir = self._root / "species"
        if not species_dir.is_dir():
            return
        for md_file in sorted(species_dir.glob("*.md")):
            data = self._parse_file(md_file)
            if data:
                sid = data.get("id") or md_file.stem
                self._species[sid] = data

    # ── Parser ──

    def _parse_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """解析单个 .md 文件为嵌套 dict。"""
        lines = path.read_text(encoding="utf-8").splitlines()
        stripped: List[str] = []
        for line in lines:
            # 去除纯注释行 (以 # 开头且行首无缩进)
            if re.match(r'^#[^#]', line) or line.strip() == "#":
                continue
            stripped.append(line)

        parsed = self._parse_lines(stripped)
        if not parsed:
            return None
        # 提取 "species" 块作为主体，其他顶层键合并进去
        if "species" in parsed and isinstance(parsed["species"], dict):
            result = parsed["species"]
            for k, v in parsed.items():
                if k != "species":
                    result[k] = v
            return result
        # 单键解包 (无 species 顶层键时)
        if len(parsed) == 1:
            top_key = next(iter(parsed))
            inner = parsed[top_key]
            if isinstance(inner, dict):
                return inner
        return parsed

    def _parse_lines(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """递归解析缩进行列表。"""
        if not lines:
            return None

        result: Dict[str, Any] = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue

            indent = self._indent(line)
            key, value = self._parse_kv(line)
            if key is None:
                i += 1
                continue

            if value is not None:
                # 标量行
                result[key] = value
                i += 1
            else:
                # 可能是嵌套对象或列表
                child_lines, next_i = self._collect_children(lines, i, indent)
                if not child_lines:
                    result[key] = None
                    i += 1
                    continue

                # 检测是否为列表 (跳过前导空行，取首个非空子行)
                first_non_blank = next((l.strip() for l in child_lines if l.strip()), "")
                if first_non_blank.startswith("- "):
                    result[key] = self._parse_list(child_lines)
                else:
                    parsed = self._parse_lines(child_lines)
                    result[key] = parsed if parsed else {}
                i = next_i

        return result if result else None

    def _parse_list(self, lines: List[str]) -> List[Any]:
        """解析列表行 (每行以 '- ' 开头)。支持纯文本项和 KV 对象项。"""
        items: List[Any] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith("- "):
                rest = stripped[2:].strip()
                child_lines, next_i = self._collect_children(lines, i, self._indent(line))
                # 检查 rest 是否为 key: value 格式
                kv_key, kv_val = self._parse_kv(rest)
                if kv_key is not None:
                    # KV 格式的列表项 → 对象
                    obj: Dict[str, Any] = {}
                    if kv_val is not None:
                        obj[kv_key] = kv_val
                    if child_lines:
                        parsed_children = self._parse_lines(child_lines)
                        if parsed_children:
                            obj.update(parsed_children)
                    items.append(obj if obj else (kv_val if kv_val else rest))
                elif child_lines:
                    parsed = self._parse_lines(child_lines)
                    items.append(parsed if parsed else rest)
                else:
                    items.append(rest)
                i = max(i + 1, next_i)
            else:
                # 多行字符串延续
                items[-1] = items[-1] + " " + stripped if items else stripped
                i += 1
        return items

    def _parse_kv(self, line: str) -> tuple:
        """解析单行 key: value，返回 (key, value_or_None)。"""
        stripped = line.strip()
        # 匹配 key: value 或 key:
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)', stripped)
        if not m:
            return (None, None)
        key = m.group(1)
        rest = m.group(2).strip()
        if not rest:
            return (key, None)
        # 布尔值
        if rest.lower() in ("true", "false"):
            return (key, rest.lower() == "true")
        # null
        if rest.lower() in ("null", "none", "~"):
            return (key, None)
        # 整数
        try:
            return (key, int(rest))
        except ValueError:
            pass
        # 浮点数
        try:
            return (key, float(rest))
        except ValueError:
            pass
        # 字符串 — 去外层引号
        val = rest.strip()
        # JSON 数组: ["a", "b"]
        if val.startswith("[") and val.endswith("]"):
            import json
            try:
                return (key, json.loads(val))
            except (json.JSONDecodeError, ValueError):
                pass
        if (val.startswith('"') and val.endswith('"')) or \
           (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        return (key, val)

    def _indent(self, line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def _collect_children(self, lines: List[str], parent_idx: int, parent_indent: int) -> tuple:
        """收集 parent 的子行 (缩进 > parent_indent)。返回 (child_lines, next_idx)。"""
        children: List[str] = []
        j = parent_idx + 1
        while j < len(lines):
            line = lines[j]
            if not line.strip():
                children.append(line)
                j += 1
                continue
            cur_indent = self._indent(line)
            if cur_indent <= parent_indent:
                break
            children.append(line)
            j += 1
        return children, j


# ── Singleton ──

_kb_instance: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
