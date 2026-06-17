"""
fishkb Variants — 物种拼写变体加载

从 species_variants.yaml 加载预计算的拼写变体，
解决学术出版中物种名拼写错误的搜索盲区。

Usage:
    from fishkb.variants import SpeciesVariants
    sv = SpeciesVariants()
    variants = sv.get_variants("Ochetobius_elongatus")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_VARIANTS_YAML = Path(__file__).resolve().parent.parent / "config" / "species_variants.yaml"


class SpeciesVariants:
    """物种拼写变体注册表"""

    def __init__(self, yaml_path: str | Path | None = None):
        yaml_path = Path(yaml_path) if yaml_path else _VARIANTS_YAML
        self._data: Dict[str, Any] = {}
        if yaml_path.is_file():
            self._data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}

    @property
    def species_ids(self) -> List[str]:
        """返回所有注册的物种 ID 列表"""
        return list(self._data.get("species", {}).keys())

    def get_variants(self, species_id: str) -> Optional[Dict[str, Any]]:
        """获取某个物种的变体信息。

        Returns:
            {
                "genus": "...",
                "species": "...",
                "chinese_name": "...",
                "chinese_aliases": [...],
                "known_misspellings": [...],
                "target_journals": [...],
            }
            若未找到则返回 None。
        """
        return self._data.get("species", {}).get(species_id)

    def get_all_misspellings(self, species_id: str) -> List[str]:
        """获取某个物种的所有已知拼写错误"""
        entry = self.get_variants(species_id)
        if entry:
            return entry.get("known_misspellings", [])
        return []

    def get_target_journals(self, species_id: str) -> List[str]:
        """获取某个物种的目标期刊列表"""
        entry = self.get_variants(species_id)
        if entry:
            return entry.get("target_journals", [])
        return []

    def find_by_scientific(self, scientific: str) -> Optional[Dict[str, Any]]:
        """根据学名查找物种变体（部分匹配）"""
        scientific_lower = scientific.lower().replace(" ", "_")
        for sid, entry in self._data.get("species", {}).items():
            full = f"{entry.get('genus', '')}_{entry.get('species', '')}".lower()
            if scientific_lower == full or scientific_lower in full or full in scientific_lower:
                return entry
            # Also check misspellings
            for ms in entry.get("known_misspellings", []):
                ms_clean = ms.lower().split()[0] + "_" + ms.lower().split()[1] if len(ms.split()) >= 2 else ms.lower()
                if scientific_lower == ms_clean:
                    return entry
        return None


# ── 单例 ──
_variants_instance: Optional[SpeciesVariants] = None


def get_variants(yaml_path: str | Path | None = None) -> SpeciesVariants:
    """获取 SpeciesVariants 单例。"""
    global _variants_instance
    if _variants_instance is None:
        _variants_instance = SpeciesVariants(yaml_path)
    return _variants_instance
