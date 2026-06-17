"""Species Registry — 从 config/species/*.yaml 加载鲚属全类群配置.

用法:
    registry = SpeciesRegistry()
    config = registry.get("coilia_nasus")        # → dict
    for sid in registry.list_species():          # → ["coilia_nasus", ...]
        ...
    default = registry.default()                 # → coilia_nasus 配置
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


class SpeciesRegistry:
    """鲚属全类群物种注册表.

    从 config/species/*.yaml 加载所有物种配置。
    """

    _default_species = "coilia_nasus"

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self._species: Dict[str, Dict[str, Any]] = {}
        if config_dir is None:
            # 自动定位: <project>/config/species/
            config_dir = Path(__file__).resolve().parent.parent.parent / "config" / "species"
        self._config_dir = config_dir
        self._load_all()

    def _load_all(self) -> None:
        """加载 config/species/*.yaml."""
        if not self._config_dir.is_dir():
            return

        # 优先 PyYAML，回退到内置简单解析
        if _HAS_YAML:
            self._load_with_yaml()
        else:
            self._load_with_builtin()

    def _load_with_yaml(self) -> None:
        for yaml_path in sorted(self._config_dir.glob("*.yaml")):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                if cfg and "species_id" in cfg:
                    self._species[cfg["species_id"]] = cfg
            except Exception:
                pass

    def _load_with_builtin(self) -> None:
        """内置 YAML 子集解析 (无 PyYAML 时回退).

        支持嵌套结构 (profile, research_themes).
        """
        import re

        for yaml_path in sorted(self._config_dir.glob("*.yaml")):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    cfg = self._parse_simple_yaml(f.read())
                if cfg and "species_id" in cfg:
                    self._species[cfg["species_id"]] = cfg
            except Exception:
                pass

    @staticmethod
    def _parse_simple_yaml(text: str) -> Dict[str, Any]:
        """解析简单 YAML 子集 (无 PyYAML 依赖).

        支持: 标量、字符串列表、单层嵌套映射、嵌套映射内字符串列表。
        """
        import re

        result: Dict[str, Any] = {}
        lines = text.splitlines()
        i = 0

        def _parse_value(val: str) -> Any:
            val = val.strip().strip('"').strip("'")
            if val.isdigit():
                return int(val)
            if val.replace('.', '', 1).replace('-', '', 1).isdigit():
                return float(val)
            return val

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            # 顶级 key: value
            m = re.match(r'^(\w[\w_]*):\s*(.*)', line)
            if m:
                key = m.group(1)
                val_str = m.group(2).strip()

                if val_str:
                    result[key] = _parse_value(val_str)
                    i += 1
                else:
                    # 嵌套块
                    indent = len(line) - len(line.lstrip()) + 2
                    nested, i = SpeciesRegistry._parse_nested_block(lines, i + 1, indent)
                    if nested is not None:
                        result[key] = nested
                    else:
                        i += 1
            else:
                i += 1

        return result

    @staticmethod
    def _parse_nested_block(lines: List[str], start: int, base_indent: int):
        """解析嵌套 YAML 块: 返回 (dict/list, next_line_index)."""
        import re

        result: Dict[str, Any] = {}
        i = start
        current_key: Optional[str] = None
        current_list: List[str] = []

        def _flush_list():
            nonlocal current_key, current_list
            if current_key and current_list:
                result[current_key] = current_list
                current_key = None
                current_list = []

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            line_indent = len(line) - len(line.lstrip())
            if line_indent < base_indent:
                break  # 回到上级

            # 列表项: "- value"
            list_m = re.match(r'^\s+-\s+(.+)', line)
            if list_m:
                _flush_list()
            else:
                # key: value at this level
                m = re.match(r'^\s+(\w[\w_]*):\s*(.*)', line)
                if m:
                    _flush_list()
                    k = m.group(1)
                    v = m.group(2).strip()
                    if v:
                        val = v.strip('"').strip("'")
                        if val.isdigit():
                            result[k] = int(val)
                        elif val.replace('.', '', 1).replace('-', '', 1).isdigit():
                            result[k] = float(val)
                        else:
                            result[k] = val
                    else:
                        # 更深嵌套
                        deeper_indent = line_indent + 2
                        deeper, i = SpeciesRegistry._parse_nested_block(lines, i + 1, deeper_indent)
                        if deeper:
                            result[k] = deeper
                        continue
                else:
                    i += 1
                    continue

            i += 1

        _flush_list()
        return (result if result else None), i

    # ── 公共 API ──

    def get(self, species_id: str) -> Optional[Dict[str, Any]]:
        """获取指定物种的完整配置."""
        return self._species.get(species_id)

    def list_species(self) -> List[str]:
        """列出所有已注册的物种 ID."""
        return sorted(self._species.keys())

    def default(self) -> Dict[str, Any]:
        """返回默认物种配置 (coilia_nasus)."""
        return self._species.get(self._default_species, {})

    def default_id(self) -> str:
        """返回默认物种 ID."""
        return self._default_species

    def __len__(self) -> int:
        return len(self._species)

    def __contains__(self, species_id: str) -> bool:
        return species_id in self._species

    def __repr__(self) -> str:
        return f"SpeciesRegistry({len(self._species)} species: {self.list_species()})"


# ── 模块级单例 ──

_registry: Optional[SpeciesRegistry] = None


def get_registry() -> SpeciesRegistry:
    """获取全局单例 SpeciesRegistry."""
    global _registry
    if _registry is None:
        _registry = SpeciesRegistry()
    return _registry


def reset_registry() -> None:
    """重置全局注册表 (测试用)."""
    global _registry
    _registry = None
