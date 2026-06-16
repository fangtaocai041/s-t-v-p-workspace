"""FishEcologyOrchestrator — 统一入口 API

三角核心 S/V0 知识供给层的主入口。提供:
  - kb_first_lookup(): 知识库优先查询
  - search_species(): 统一物种搜索
  - delegate_to(): 跨项目委托

三角核心:
  fish-ecology-assistant (S/V0 知识供给)
  cognitive-search-engine (V/V1 搜索验证)
  eon-core (Coordinator 协调器)

Usage:
    from src.orchestrator import FishEcologyOrchestrator
    orch = FishEcologyOrchestrator()
    result = orch.search_species("珠星三块鱼")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# 涌现检测集成
try:
    import sys as _sys
    _infra = str(Path(__file__).resolve().parent.parent.parent / "infrastructure")
    if _infra not in _sys.path:
        _sys.path.insert(0, _infra)
    from unified_emergence import EmergenceMonitor, DimensionalLevel
    _EMERGENCE_AVAILABLE = True
except ImportError:
    _EMERGENCE_AVAILABLE = False

from .shared import JOURNAL_WHITELIST, build_search_queries, generate_ocr_variants

logger = logging.getLogger(__name__)


@dataclass
class KbFirstResult:
    """Result from kb_first_lookup() — pure knowledge base query.

    This is the Stage 1 (KB-first) result. The caller should present
    summary_text to the user and ask: stay in KB or continue to
    cognitive-search-engine full search?
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
    distribution: Dict[str, Any] = field(default_factory=dict)  # {continents, countries, basins}
    category: str = ""                   # KB category (dominant/diadromous/protected/endangered)
    matched_by_alias: bool = False       # True if matched via alias, not primary name
    all_candidates: List[Dict[str, Any]] = field(default_factory=list)  # All fuzzy matches
    summary_text: str = ""              # Human-readable summary for user presentation
    search_recommendation: str = ""     # "stay_in_kb" | "continue_to_c" | "not_found"
    raw_species_data: Dict[str, Any] = field(default_factory=dict)  # Full KB entry


class FishEcologyOrchestrator:
    """Lightweight Python orchestrator for fish-ecology knowledge supply.

    Loads configs at init, provides structured access to species data,
    and generates Reasonix DELEGATE protocol messages for skill dispatch.
    """

    # Pipeline stages (from research-orchestrator.md)
    STAGES = ["Plan", "Search", "Analyze", "Write", "Review"]

    def __init__(self) -> None:
        self._project_root = Path(__file__).resolve().parent.parent
        self._agent_config: Dict[str, Any] = {}
        self._species_db: Dict[str, Any] = {}
        self._hub = None  # 懒加载 ProjectHub
        self._load_configs()

    def _load_configs(self) -> None:
        """Load configs: try new index+profiles first, fall back to flat YAML."""
        try:
            import yaml

            agent_cfg = self._project_root / "config" / "agent.yaml"
            if agent_cfg.is_file():
                self._agent_config = yaml.safe_load(agent_cfg.read_text(encoding="utf-8")) or {}

            # Try new format: index.yaml + individual .md profiles
            index_cfg = self._project_root / "config" / "fish_species_index.yaml"
            profiles_dir = self._project_root / "config" / "knowledge_base" / "species"

            if index_cfg.is_file() and profiles_dir.is_dir():
                index_data = yaml.safe_load(index_cfg.read_text(encoding="utf-8")) or {}
                species_list = []
                for entry in index_data.get("species", []):
                    sid = entry["id"]
                    species_data = {"id": sid}
                    for k in ["name", "scientific", "family"]:
                        if k in entry:
                            species_data[k] = entry[k]
                    profile_path = profiles_dir / f"{sid}.md"
                    if profile_path.is_file():
                        text = profile_path.read_text(encoding="utf-8")
                        if text.startswith("---"):
                            parts = text.split("---", 2)
                            if len(parts) >= 3:
                                fm = yaml.safe_load(parts[1]) or {}
                                species_data.update(fm)
                    if "basins" not in species_data and entry.get("basins"):
                        species_data["basins"] = entry["basins"]
                    species_list.append(species_data)
                self._species_db = {"species": species_list}
            else:
                # Fallback: flat YAML
                species_cfg = self._project_root / "config" / "fish_species_kb.yaml"
                if species_cfg.is_file():
                    self._species_db = yaml.safe_load(species_cfg.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning(f"Config load failed: {exc}")

    # ──── ProjectHub 集成 ────

    @property
    def hub(self):
        """懒加载 ProjectHub — 三生万物架构中枢。"""
        if self._hub is None:
            from src.project_hub import get_hub
            self._hub = get_hub()
        return self._hub

    def search_species(self, name: str, mode: str = "kb_first",
                       group: str = "full", limit: int = 10) -> Dict[str, Any]:
        """统一物种搜索入口 — 三角闭环: S(知识)→V(验证)→S(写回)。

        这是 FISH-ECOLOGY-ASSISTANT 的核心入口。所有物种检索
        通过此方法进行。三角核心联动: fish(S) 提供知识 →
        cognitive(V) 提供搜索验证 → 结果写回 fish 知识库。

        Args:
            name: 中文名或学名
            mode: "kb_first" | "search_only" | "kb_only"
            group: 搜索引擎组
            limit: 每引擎最大结果数
        """
        return self.hub.search_species(name, mode=mode, group=group, limit=limit)

    def delegate_to(self, subsystem: str, task: str, **kwargs) -> Optional[Dict[str, Any]]:
        """委托任务到衍生项目 — 三角赋能万物。

        Args:
            subsystem: "porpoise" | "coilia" | "conflict"
            task: 任务描述
        """
        return self.hub.delegate_to(subsystem, task, **kwargs)

    @property
    def is_triangle_complete(self) -> bool:
        """三角三元素是否完整? (fish + cognitive + eon-core)"""
        return self.hub.is_triangle_complete()

    @property
    def triangle_status(self) -> Dict[str, Any]:
        """三角核心详细状态。"""
        return self.hub.triangle_status()

    # ──── Public API ────

    def delegate_search(
        self, scientific_name: str, chinese_name: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Cross-project entry point. Returns species data + search hints.

        Searches across: dominant_species, protected_species, and
        individual species entries in the knowledge base.
        """
        species_data = self._find_species(scientific_name, chinese_name)
        cn_name = chinese_name or species_data.get("chinese_name", species_data.get("name", ""))

        # Build result with real species data
        result: Dict[str, Any] = {
            "status": "ok",
            "scientific_name": scientific_name,
            "chinese_name": cn_name,
            "known_species": bool(species_data),
            "species_data": species_data,
            "search_queries": build_search_queries(scientific_name, cn_name),
            "ocr_variants": generate_ocr_variants(scientific_name),
        }

        # IF known species THEN include taxonomy + research hints
        if species_data:
            result.update({
                "family": species_data.get("family", ""),
                "order": species_data.get("order", ""),
                "iucn_status": species_data.get("iucn", ""),
                "habitat": species_data.get("habitat", ""),
                "max_length_cm": species_data.get("max_length_cm", ""),
            })

        # Always include DELEGATE protocol for full pipeline
        result["delegate"] = {
            "protocol": "DELEGATE",
            "target": "fish-ecology-assistant",
            "skill": "research-orchestrator",
            "pipeline": self.STAGES,
            "max_revision_rounds": 3,
        }

        return result

    @staticmethod
    def _match_species(query: str, chinese: str, s_name: str, c_name: str) -> bool:
        """Check if query matches a species by scientific or Chinese name.

        鐭ヨ瘑搴撶簿纭尮閰嶈鍒?(f椤圭洰涓嶅仛妯＄硦):
          1. query == 瀛﹀悕 (澶у皬鍐欎笉鏁忔劅) 鈫?浼樺厛
          2. query == 涓枃鍚?鈫?绮剧‘
          3. chinese 鍙傛暟 == 涓枃鍚?鈫?璺ㄩ」鐩皟鐢?          4.瀛﹀悕瀛愪覆鍖归厤 鈫?鏀寔閮ㄥ垎鎷変竵鍚嶆煡璇㈠ "Ochetobius"

        ⚠️ 鏃犱腑鏂囧悕瀛椾覆鍖归厤 —妯＄硦鎼滅储鏄?c椤圭洰鐨勮亴璐?        """
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
        """Search the flat species list in the knowledge base.

        New multi-basin format: self._species_db["species"] is a list of
        species dicts, each with name/scientific/distribution fields.
        Falls back to old section-based format for backward compat.

        Matches against: scientific name, Chinese name, aliases, AND synonyms.
        """
        # ──── NEW: flat species list ────
        species_list = self._species_db.get("species", [])
        if species_list:
            for item in species_list:
                if not isinstance(item, dict):
                    continue
                s_name = item.get("scientific", "")
                c_name = item.get("name", "")
                aliases = item.get("aliases", []) or []
                synonyms = item.get("synonyms", []) or []
                if self._match_species(scientific, chinese, s_name, c_name):
                    return {
                        "chinese_name": c_name,
                        "scientific_name": s_name,
                        "aliases": aliases,
                        "synonyms": synonyms,
                        "family": item.get("family", ""),
                        "conservation": item.get("conservation", ""),
                        "category": item.get("category", ""),
                        "distribution": item.get("distribution", {}),
                        **item,
                    }
                # Also match against aliases
                for alias in aliases:
                    if self._match_species(scientific, chinese, "", alias):
                        return {
                            "chinese_name": alias,
                            "scientific_name": s_name,
                            "aliases": aliases,
                            "synonyms": synonyms,
                            "family": item.get("family", ""),
                            "conservation": item.get("conservation", ""),
                            "category": item.get("category", ""),
                            "distribution": item.get("distribution", {}),
                            "matched_by_alias": True,
                            **item,
                        }
                # Also match against synonyms (e.g. Tribolodon hakonensis → Tribolodon brandti)
                for syn in synonyms:
                    if self._match_species(scientific, chinese, "", syn):
                        return {
                            "chinese_name": c_name,
                            "scientific_name": s_name,
                            "aliases": aliases,
                            "synonyms": synonyms,
                            "family": item.get("family", ""),
                            "conservation": item.get("conservation", ""),
                            "category": item.get("category", ""),
                            "distribution": item.get("distribution", {}),
                            "matched_by_alias": True,
                            "matched_by_synonym": syn,
                            **item,
                        }
            return {}

        # ──── FALLBACK: old section-based format ────
        for section_key in ["dominant_species", "protected_species", "key_endangered_species_in_graph"]:
            section = self._species_db.get(section_key, []) or []
            if not isinstance(section, list):
                continue
            for item in section:
                if not isinstance(item, dict):
                    continue
                s_name = item.get("scientific", "")
                c_name = item.get("name", "")
                if self._match_species(scientific, chinese, s_name, c_name):
                    return {**item, "chinese_name": c_name, "scientific_name": s_name,
                            "section": section_key}

        return {}

    # ⚠️ lookup_species() and list_species() removed — use kb_first_lookup() instead.
    # ⚠️ score_credibility() moved to adapter.py — use adapter.score_credibility(papers) instead.

    def health(self) -> Dict[str, Any]:
        """Health check — 包含宿主 + 所有子系统状态。"""
        base = {
            "project": "fish-ecology-assistant",
            "status": "HEALTHY" if self._agent_config else "DEGRADED",
            "config_loaded": bool(self._agent_config),
            "species_db_size": len(self._species_db.get("species", [])),
            "pipeline_stages": self.STAGES,
        }
        # 附加子系统健康状态
        try:
            hub_health = self.hub.health_all()
            base["subsystems"] = hub_health.get("subsystems", {})
        except Exception:
            base["subsystems"] = {"error": "hub unavailable"}
        return base

    def info(self) -> Dict[str, Any]:
        """Version + capabilities — 包含子系统清单。"""
        base = {
            "project": "fish-ecology-assistant",
            "version": self._agent_config.get("agent", {}).get("version", "unknown"),
            "role": "宿主容器·知识供给 (V0) — 统一入口",
            "pipeline": "5-stage: Plan 鈫?Search 鈫?Analyze 鈫?Write 鈫?Review",
            "skill_count": 28,
            "sub_agents": 28,
            "capabilities": [
                "species_knowledge_base",
                "credibility_scoring",
                "ocr_variant_generation",
                "delegate_protocol",
                "chinese_academic_sources",
                "multi_engine_search",
                "kb_first_two_stage_search",
                "project_hub_unified_entry",
            ],
        }
        # 附加子系统能力
        try:
            hub_caps = self.hub.capabilities()
            base["subsystems"] = hub_caps.get("subsystems", {})
        except Exception:
            base["subsystems"] = {"error": "hub unavailable"}
        return base

    # ──── KB-First Lookup (Stage 1: knowledge base only) ────

    def kb_first_lookup(self, scientific_name: str = "", chinese_name: str = "",
                        query: str = "") -> KbFirstResult:
        """KB-first search — pure knowledge base lookup, NO external API calls.

        This is the FIRST stage of the two-stage search workflow:
          1. kb_first_lookup() → check f项目 knowledge base
          2. [ask user: stay in KB or continue?]
          3. IF continue → cognitive-search-engine full search

        Args:
            scientific_name: Scientific name (e.g. "Tribolodon hakonensis")
            chinese_name: Chinese common name (e.g. "珠星三块鱼")
            query: Generic query string (fallback if specific names not provided)

        Returns:
            KbFirstResult with found=True/False, species data, and human-readable summary.
        """
        # Resolve query: use scientific + chinese if provided, else fall back to query string
        sci = scientific_name.strip() if scientific_name else query.strip()
        cn = chinese_name.strip() if chinese_name else ""

        # If only query is provided and looks like Chinese, treat as chinese_name
        if not scientific_name and not chinese_name and query:
            if any('\u4e00' <= c <= '\u9fff' for c in query):
                cn = query
                sci = ""
            else:
                sci = query

        # 1. Exact / alias match via existing _find_species
        species_data = self._find_species(sci, cn)

        # 2. If no match, try listing all species and find fuzzy matches
        all_candidates = []
        if not species_data:
            all_candidates = self._fuzzy_find_all(sci, cn, limit=10)

        # 3. Build result
        if species_data:
            return self._build_kb_hit_result(species_data)
        else:
            return self._build_kb_miss_result(sci, cn, all_candidates)

    def _fuzzy_find_all(self, scientific: str, chinese: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search across ALL species entries for near matches."""
        candidates = []
        species_list = self._species_db.get("species", [])
        if not species_list:
            return candidates

        sci_lower = scientific.lower() if scientific else ""
        cn_clean = chinese.strip() if chinese else ""

        for item in species_list:
            if not isinstance(item, dict):
                continue
            s_name = item.get("scientific", "")
            c_name = item.get("name", "")
            aliases = item.get("aliases", []) or []
            score = 0

            # Score scientific name: substring match
            if sci_lower and s_name:
                # Genus match (first word)
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

    def _build_kb_hit_result(self, species_data: Dict[str, Any]) -> KbFirstResult:
        """Build KbFirstResult for a KB hit."""
        cn_name = species_data.get("chinese_name", species_data.get("name", ""))
        sci_name = species_data.get("scientific_name", species_data.get("scientific", ""))
        aliases = species_data.get("aliases", []) or []
        synonyms = species_data.get("synonyms", []) or []
        family = species_data.get("family", "")
        dist = species_data.get("distribution", {})

        # Build summary
        lines = []
        lines.append(f"📚 **f项目知识库已收录**: {cn_name}（*{sci_name}*）")
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

        # Recommendation: if KB has rich data, suggest staying; otherwise suggest c
        has_rich_data = bool(family and (dist or species_data.get("ecology")))
        recommendation = (
            "stay_in_kb" if has_rich_data else "continue_to_c"
        )

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
            summary_text=summary,
            search_recommendation=recommendation,
            raw_species_data=species_data,
        )

    def _build_kb_miss_result(self, sci: str, cn: str,
                               candidates: List[Dict[str, Any]]) -> KbFirstResult:
        """Build KbFirstResult when species NOT found in KB."""
        lines = []
        lines.append(f"🔍 **f项目知识库未收录**: {cn or sci}")

        if candidates:
            lines.append(f"\n但找到 {len(candidates)} 个可能的近缘种:")
            for c in candidates[:5]:
                lines.append(f"  - {c['chinese']}（*{c['scientific']}*） [{c.get('family', '')}] 匹配度={c['score']}")
            lines.append("\n💡 可能是名称变体，建议用 c项目进行全量搜索。")
        else:
            lines.append("知识库中无任何匹配。建议启动 c项目全量搜索。")

        summary = "\n".join(lines)

        # Feed to emergence engine
        if _EMERGENCE_AVAILABLE:
            try:
                mon = EmergenceMonitor()
                mon.record("f_kb_query", 1, DimensionalLevel.D1)
                mon.record("f_kb_found", 0, DimensionalLevel.D1)
                mon.record("f_candidates", len(candidates), DimensionalLevel.D1)
            except Exception:
                pass

        return KbFirstResult(
            found=False,
            scientific_name=sci,
            chinese_name=cn,
            all_candidates=candidates,
            summary_text=summary,
            search_recommendation="continue_to_c",
        )



_orchestrator_instance: Optional[FishEcologyOrchestrator] = None


def get_orchestrator() -> FishEcologyOrchestrator:
    """Factory function — 返回（缓存的）单例。

    同一进程中多次调用返回同一实例。
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = FishEcologyOrchestrator()
    return _orchestrator_instance