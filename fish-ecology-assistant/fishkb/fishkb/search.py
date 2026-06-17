"""
fishkb Species Matcher — KB-First 物种查找与模糊匹配

从 fish-ecology-assistant/src/orchestrator.py 提取核心物种匹配逻辑，
重构为独立的 FishSpeciesMatcher，不依赖 FishEcologyOrchestrator。

提供:
  - kb_first_lookup(): 知识库优先查询，返回 KbFirstResult
  - _match_species(): 精确匹配规则
  - _fuzzy_find_all(): 模糊搜索所有候选

Usage:
    from fishkb.search import FishSpeciesMatcher
    from fishkb.db import KnowledgeDB

    db = KnowledgeDB()
    matcher = FishSpeciesMatcher(db)
    result = matcher.kb_first_lookup(query="鳤")
    print(result.summary_text)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .db import KnowledgeDB


@dataclass
class KbFirstResult:
    """Result from kb_first_lookup() — pure knowledge base query.

    This is the Stage 1 (KB-first) result. The caller should present
    summary_text to the user and ask: stay in KB or continue to
    full search?
    """
    found: bool                          # Whether species exists in KB
    scientific_name: str = ""            # Canonical scientific name from KB
    chinese_name: str = ""              # Chinese name from KB
    aliases: List[str] = field(default_factory=list)  # Known aliases
    synonyms: List[str] = field(default_factory=list)  # Taxonomic synonyms
    family: str = ""                     # Family (e.g. "鲤科")
    order: str = ""                      # Order (e.g. "鲤形目")
    conservation: str = ""               # IUCN / protection level
    ecology: str = ""                    # Ecology notes
    max_length_cm: str = ""             # Max recorded length
    economic_value: str = ""            # Economic importance
    distribution: Dict[str, Any] = field(default_factory=dict)
    category: str = ""                   # KB category
    matched_by_alias: bool = False
    matched_by_synonym: str = ""
    all_candidates: List[Dict[str, Any]] = field(default_factory=list)
    summary_text: str = ""
    search_recommendation: str = ""     # "stay_in_kb" | "continue_to_c" | "not_found"
    raw_species_data: Dict[str, Any] = field(default_factory=dict)


class FishSpeciesMatcher:
    """物种匹配器 — 基于 KnowledgeDB 的 KB-first 查询。

    精确匹配规则:
      1. query == 学名 (大小写不敏感) → 优先
      2. query == 中文名 → 精确
      3. chinese 参数 == 中文名 → 跨项目调用
      4. 学名字串匹配 → 支持部分拉丁名查询如 "Ochetobius"

    模糊匹配:
      - 属名匹配 +40
      - 学名字串匹配 +30
      - 中文名精确匹配 +60
      - 中文字符交集 +20
      - 别名匹配 +50
    """

    def __init__(self, db: KnowledgeDB | None = None):
        """初始化物种匹配器。

        Args:
            db: KnowledgeDB 实例。若为 None，创建默认实例。
        """
        self.db = db or KnowledgeDB()

    @staticmethod
    def _match_species(query: str, chinese: str, s_name: str, c_name: str) -> bool:
        """Check if query matches a species by scientific or Chinese name.

        知识库精确匹配规则:
          1. query == 学名 (大小写不敏感) → 优先
          2. query == 中文名 → 精确
          3. chinese 参数 == 中文名 → 跨项目调用
          4. 学名字串匹配 → 支持部分拉丁名查询如 "Ochetobius"

        ⚠️ 无中文名字串匹配 — 模糊搜索是上层职责
        """
        q = query.strip().lower()
        s = s_name.lower() if s_name else ""
        c = c_name.lower() if c_name else ""

        if s and (q == s or (len(q) >= 3 and q in s)):
            return True
        if c and (q == c):
            return True
        if chinese and c and chinese == c:
            return True
        return False

    def _find_species(self, scientific: str, chinese: str = "") -> Dict[str, Any]:
        """在 KnowledgeDB 中通过精确规则查找物种。

        Matches against: scientific name, Chinese name, aliases, AND synonyms.
        """
        # Try exact lookup first
        if scientific:
            result = self.db.lookup(scientific)
            if result:
                sci_name = result.get("scientific", "")
                cn_name = result.get("chinese", "")
                if self._match_species(scientific, chinese, sci_name, cn_name):
                    return self._enrich_result(result)

        if chinese:
            result = self.db.lookup(chinese)
            if result:
                sci_name = result.get("scientific", "")
                cn_name = result.get("chinese", "")
                if self._match_species(chinese, "", sci_name, cn_name):
                    return self._enrich_result(result)

        # Try all species with fuzzy matching on aliases and synonyms
        all_species = self.db.list_all()
        for item in all_species:
            s_name = item.get("scientific", "")
            c_name = item.get("chinese", "")
            aliases: list = item.get("aliases", []) or []
            synonyms: list = item.get("synonyms", []) or []

            if self._match_species(scientific, chinese, s_name, c_name):
                return self._enrich_result(item)

            # Match against aliases
            for alias in aliases:
                if self._match_species(scientific, chinese, "", alias):
                    item["matched_by_alias"] = True
                    return self._enrich_result(item)

            # Match against synonyms
            for syn in synonyms:
                if self._match_species(scientific, chinese, "", syn):
                    item["matched_by_alias"] = True
                    item["matched_by_synonym"] = syn
                    return self._enrich_result(item)

        return {}

    def _enrich_result(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed fields to a species result dict."""
        return {
            "chinese_name": item.get("chinese", item.get("name", "")),
            "scientific_name": item.get("scientific", ""),
            "aliases": item.get("aliases", []),
            "synonyms": item.get("synonyms", []),
            "family": item.get("family", ""),
            "conservation": item.get("conservation", ""),
            "category": item.get("category", ""),
            "distribution": item.get("distribution", {}),
            **item,
        }

    def _fuzzy_find_all(self, scientific: str, chinese: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search across ALL species entries for near matches."""
        candidates: List[Dict[str, Any]] = []
        species_list = self.db.list_all()
        if not species_list:
            return candidates

        sci_lower = scientific.lower() if scientific else ""
        cn_clean = chinese.strip() if chinese else ""

        for item in species_list:
            s_name = item.get("scientific", "")
            c_name = item.get("chinese", "")
            aliases: list = item.get("aliases", []) or []
            score = 0

            # Score scientific name: substring match
            if sci_lower and s_name:
                sci_genus = sci_lower.split()[0] if sci_lower else ""
                item_genus = s_name.lower().split()[0] if s_name else ""
                if sci_genus and item_genus and sci_genus in item_genus:
                    score += 40
                if sci_lower in s_name.lower() or s_name.lower() in sci_lower:
                    score += 30

            # Score Chinese name
            if cn_clean and c_name:
                if cn_clean == c_name:
                    score += 60
                elif any(char in c_name for char in cn_clean):
                    score += 20

            # Score aliases
            for alias in aliases:
                if cn_clean and alias and cn_clean in alias:
                    score += 50
                    break

            if score > 0:
                candidates.append({
                    "score": score,
                    "scientific": s_name,
                    "chinese": c_name,
                    "aliases": aliases,
                    "family": item.get("family", ""),
                    "category": item.get("category", ""),
                    "distribution": item.get("distribution", {}),
                })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]

    def kb_first_lookup(self,
                        scientific_name: str = "",
                        chinese_name: str = "",
                        query: str = "") -> KbFirstResult:
        """KB-first search — pure knowledge base lookup, NO external API calls.

        This is the FIRST stage of the two-stage search workflow:
          1. kb_first_lookup() → check knowledge base
          2. [ask user: stay in KB or continue?]
          3. IF continue → full external search

        Args:
            scientific_name: Scientific name (e.g. "Tribolodon hakonensis")
            chinese_name: Chinese common name (e.g. "珠星三块鱼")
            query: Generic query string (fallback if specific names not provided)

        Returns:
            KbFirstResult with found=True/False, species data, and human-readable summary.
        """
        # Resolve query
        sci = scientific_name.strip() if scientific_name else query.strip()
        cn = chinese_name.strip() if chinese_name else ""

        # If only query is provided and looks like Chinese, treat as chinese_name
        if not scientific_name and not chinese_name and query:
            if any('\u4e00' <= c <= '\u9fff' for c in query):
                cn = query
                sci = ""
            else:
                sci = query

        # 1. Exact / alias match
        species_data = self._find_species(sci, cn)

        # 2. If no match, try fuzzy
        all_candidates: List[Dict[str, Any]] = []
        if not species_data:
            all_candidates = self._fuzzy_find_all(sci, cn)

        # 3. Build result
        if species_data:
            return self._build_kb_hit_result(species_data)
        else:
            return self._build_kb_miss_result(sci, cn, all_candidates)

    def _build_kb_hit_result(self, species_data: Dict[str, Any]) -> KbFirstResult:
        """Build KbFirstResult for a KB hit."""
        cn_name = species_data.get("chinese_name", species_data.get("chinese", species_data.get("name", "")))
        sci_name = species_data.get("scientific_name", species_data.get("scientific", ""))
        aliases: list = species_data.get("aliases", []) or []
        synonyms: list = species_data.get("synonyms", []) or []
        family = species_data.get("family", "")
        dist: Dict[str, Any] = species_data.get("distribution", {})

        # Build summary
        lines: List[str] = []
        lines.append(f"📚 **知识库已收录**: {cn_name}（*{sci_name}*）")
        if family:
            lines.append(f"- 科属: {family}")
        if species_data.get("order"):
            lines.append(f"- 目: {species_data['order']}")
        if species_data.get("ecology"):
            lines.append(f"- 生态: {species_data['ecology'].strip()}")
        if species_data.get("economic_value"):
            lines.append(f"- 经济价值: {species_data['economic_value']}")
        if species_data.get("max_length_cm"):
            lines.append(f"- 最大体长: {species_data['max_length_cm']} cm")
        if aliases:
            lines.append(f"- 别名: {', '.join(aliases)}")
        if synonyms:
            lines.append(f"- 同义名: {', '.join(synonyms[:5])}")
        if dist:
            basins = dist.get("basins", []) or []
            countries = dist.get("countries", []) or []
            if basins:
                lines.append(f"- 分布流域: {', '.join(basins)}")
            if countries:
                lines.append(f"- 分布国家: {', '.join(countries)}")

        summary = "\n".join(lines)

        # Recommendation
        has_basins = bool(dist.get("basins", []) or species_data.get("basins", []))
        has_ecology = bool(species_data.get("ecology", "") or species_data.get("summary_text", ""))
        has_rich_data = bool(family and (has_basins or has_ecology))
        recommendation = "stay_in_kb" if has_rich_data else "continue_to_c"

        return KbFirstResult(
            found=True,
            scientific_name=sci_name,
            chinese_name=cn_name,
            aliases=aliases,
            synonyms=synonyms,
            family=family,
            order=species_data.get("order", ""),
            conservation=species_data.get("conservation", species_data.get("iucn", "")),
            ecology=species_data.get("ecology", ""),
            max_length_cm=str(species_data.get("max_length_cm", "")),
            economic_value=species_data.get("economic_value", ""),
            distribution=dist,
            category=species_data.get("category", species_data.get("section", "")),
            matched_by_alias=species_data.get("matched_by_alias", False),
            matched_by_synonym=species_data.get("matched_by_synonym", ""),
            summary_text=summary,
            search_recommendation=recommendation,
            raw_species_data=species_data,
        )

    def _build_kb_miss_result(self, sci: str, cn: str,
                               candidates: List[Dict[str, Any]]) -> KbFirstResult:
        """Build KbFirstResult when species NOT found in KB."""
        lines: List[str] = []
        lines.append(f"🔍 **知识库未收录**: {cn or sci}")

        if candidates:
            lines.append(f"\n但找到 {len(candidates)} 个可能的近缘种:")
            for c in candidates[:5]:
                lines.append(
                    f"  - {c['chinese']}（*{c['scientific']}*） "
                    f"[{c.get('family', '')}] 匹配度={c['score']}"
                )
            lines.append("\n💡 可能是名称变体，建议进行全量搜索。")
        else:
            lines.append("知识库中无任何匹配。建议启动全量搜索。")

        summary = "\n".join(lines)

        return KbFirstResult(
            found=False,
            scientific_name=sci,
            chinese_name=cn,
            all_candidates=candidates,
            summary_text=summary,
            search_recommendation="continue_to_c",
        )


# ── 单例 ──
_matcher_instance: Optional[FishSpeciesMatcher] = None


def get_matcher(db: KnowledgeDB | None = None) -> FishSpeciesMatcher:
    """获取 FishSpeciesMatcher 单例。"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = FishSpeciesMatcher(db)
    return _matcher_instance
