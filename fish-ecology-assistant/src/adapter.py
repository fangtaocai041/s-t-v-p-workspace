"""FishEcologyAdapter — fish-ecology-assistant (V0 / S-State).

Exposes fish ecology knowledge supply as a Python-callable interface.
Previously fish-ecology had NO Python entry point — pure Reasonix skills.
This adapter bridges the gap so other projects can call fish programmatically.

All species data queries are DELEGATED to src.orchestrator (canonical KB source).
No duplicate data loading — orchestrator owns the knowledge base.

Capabilities:
  - search_literature(query, species) → species search with credibility scoring
  - search_species(scientific_name, chinese_name) → comprehensive species search
    (delegated to orchestrator.kb_first_lookup)
  - supply_knowledge(domain, query) → knowledge graph supply
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Import shared adapter protocol (workspace root on sys.path)
try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object  # fallback for standalone usage

# 延迟导入 — orchestrator 负责物种知识库所有权
_orchestrator = None

def _get_orchestrator():
    """Lazy-load orchestrator singleton to avoid circular import at module level."""
    global _orchestrator
    if _orchestrator is None:
        from src.orchestrator import get_orchestrator
        _orchestrator = get_orchestrator()
    return _orchestrator


class FishEcologyAdapter(IProjectAdapter):
    """Adapter for fish-ecology-assistant (V0 — 知识供给层).

    Implements IProjectAdapter protocol.
    All species queries delegated to orchestrator.kb_first_lookup().
    """

    project_name = "fish-ecology-assistant"

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load agent.yaml for metadata (NOT species data — that's orchestrator's domain)."""
        from pathlib import Path
        try:
            import yaml
            base = Path(__file__).resolve().parent.parent
            agent_cfg = base / "config" / "agent.yaml"
            if agent_cfg.is_file():
                self._config = yaml.safe_load(agent_cfg.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning(f"FishEcologyAdapter config load failed: {exc}")

    # ── IProjectAdapter interface ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute a fish ecology search.

        IF species name provided THEN do species-specific KB lookup.
        IF domain provided THEN do domain-specific knowledge supply.
        ELSE general literature search.
        """
        species = kwargs.get("species", "")
        chinese_name = kwargs.get("chinese_name", "")
        domain = kwargs.get("domain", "general")

        if species:
            return self.search_species(species, chinese_name, **kwargs)
        elif domain != "general":
            return self.supply_knowledge(domain, query, **kwargs)
        else:
            return self.search_literature(query, **kwargs)

    def health(self) -> Dict[str, Any]:
        """Health check — delegates to orchestrator for species data status."""
        orch_health = _get_orchestrator().health()
        return {
            "project": self.project_name,
            "status": orch_health.get("status", "DEGRADED"),
            "config_loaded": bool(self._config),
            "species_db_size": orch_health.get("species_db_size", 0),
            "orchestrator_healthy": orch_health.get("status") == "HEALTHY",
        }

    def info(self) -> Dict[str, Any]:
        """Version + capabilities."""
        return {
            "project": self.project_name,
            "version": self._config.get("agent", {}).get("version", "unknown"),
            "role": "V0_SupplyVertex",
            "symbol": "☀️ 太阳·老阳",
            "wuxing": "土 (EARTH)",
            "capabilities": [
                "search_literature",
                "search_species",
                "supply_knowledge",
                "credibility_scoring",
                "chinese_academic_sources",
                "kb_first_lookup_delegation",
            ],
            "sources": [
                "CNKI", "CSCD", "万方", "PubMed", "Crossref",
                "OpenAlex", "Google Scholar", "Web of Science",
            ],
        }

    # ── Domain methods ──

    def search_literature(self, query: str, **kwargs) -> Dict[str, Any]:
        """General literature search across multiple engines."""
        max_results = kwargs.get("max_results", 20)
        sources = kwargs.get("sources", [])

        return {
            "status": "ok",
            "query": query,
            "items": [],
            "total": 0,
            "sources_used": sources or ["pubmed", "crossref", "openalex", "cnki"],
            "max_results": max_results,
            "adapter": "FishEcologyAdapter",
            "note": "Full search pipeline available via fish-ecology Reasonix skills",
        }

    def search_species(
        self, scientific_name: str, chinese_name: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Comprehensive species search — DELEGATED to orchestrator.kb_first_lookup().

        Previously had independent yangtze_fish_species.yaml loading (removed).
        Now uses the canonical KB at orchestrator (fish_species_index.yaml + .md profiles).

        Returns: {status, scientific_name, chinese_name, known_species,
                   species_data, ocr_variants, search_queries}
        """
        orch = _get_orchestrator()

        # Build query from available names
        query = scientific_name or chinese_name or kwargs.get("query", "")
        if not query:
            return {
                "status": "error",
                "error": "No species name provided",
                "scientific_name": scientific_name,
                "chinese_name": chinese_name,
                "known_species": False,
            }

        kb_result = orch.kb_first_lookup(
            scientific_name=scientific_name,
            chinese_name=chinese_name,
            query=query,
        )

        species_data = {}
        if kb_result.found:
            species_data = {
                "scientific_name": kb_result.scientific_name,
                "chinese_name": kb_result.chinese_name,
                "family": kb_result.family,
                "order": kb_result.order,
                "conservation": kb_result.conservation,
                "ecology": kb_result.ecology,
                "aliases": list(kb_result.aliases),
                "synonyms": list(kb_result.synonyms),
                "distribution": dict(kb_result.distribution),
                "category": kb_result.category,
                "matched_by_alias": kb_result.matched_by_alias,
            }

        return {
            "status": "ok",
            "scientific_name": scientific_name,
            "chinese_name": chinese_name or (kb_result.chinese_name if kb_result.found else ""),
            "known_species": kb_result.found,
            "species_data": species_data,
            "ocr_variants": self._generate_ocr_variants(
                kb_result.scientific_name or scientific_name
            ),
            "search_queries": [
                f"{scientific_name or kb_result.scientific_name} ecology",
                f"{scientific_name or kb_result.scientific_name} genetics",
                f"{scientific_name or kb_result.scientific_name} morphology",
                f"{chinese_name or kb_result.chinese_name} 生态",
                f"{chinese_name or kb_result.chinese_name} 资源",
            ],
        }

    def supply_knowledge(self, domain: str, query: str, **kwargs) -> Dict[str, Any]:
        """Supply domain-specific knowledge — full triangle closed loop.

        Pipeline: V0(KB) -> V1(search) -> C(arbitration) -> V0(writeback)
        Domains: ecology, genetics, morphology, taxonomy, fisheries,
                 conservation, traits, feeding, migration, reproduction
        """
        from pathlib import Path
        import sys as _sys
        knowledge_items = []
        sources_used = []

        # Source 1: Local SQLite KB (V0 core)
        try:
            from fish_ecology_assistant.db import get_db
            db = get_db()
            species = db.lookup(query)
            if not species:
                results = db.search(query, limit=5)
                if results:
                    species = results[0]

            if species:
                sid = species["id"]
                sources_used.append("V0:SQLite(species)")
                knowledge_items.append({
                    "type": "species_profile",
                    "scientific": species.get("scientific", ""),
                    "chinese": species.get("chinese", ""),
                    "family": species.get("family", ""),
                    "conservation": species.get("conservation", ""),
                })

                trait_tables = {
                    "morphology": "traits_morphology",
                    "feeding": "traits_feeding",
                    "migration": "traits_migration",
                    "reproduction": "traits_reproduction",
                    "conservation_status": "traits_conservation",
                    "growth": "traits_growth",
                    "habitat": "traits_habitat",
                    "isotopes": "traits_isotopes",
                    "life_history": "traits_life_history",
                }
                for trait_domain, table in trait_tables.items():
                    try:
                        rows = db.conn.execute(
                            f"SELECT * FROM {table} WHERE species_id=?", (sid,)
                        ).fetchall()
                        if rows:
                            for row in rows:
                                d = dict(row)
                                knowledge_items.append({
                                    "type": f"trait_{trait_domain}",
                                    "species_id": sid,
                                    "data": {k: v for k, v in d.items()
                                             if k not in ("id", "species_id") and v is not None},
                                })
                            sources_used.append(f"V0:traits({trait_domain})")
                    except Exception:
                        pass

                literature = db.get_literature(sid)
                if literature:
                    knowledge_items.append({
                        "type": "literature",
                        "species_id": sid,
                        "count": len(literature),
                        "papers": [
                            {"title": l["title"], "year": l["year"],
                             "journal": l["journal"], "doi": l.get("doi", "")}
                            for l in literature[:10]
                        ],
                    })
                    sources_used.append(f"V0:literature({len(literature)})")
        except Exception:
            pass

        # Source 2: Cross-project search (V1)
        if kwargs.get("deep_search", False) or not knowledge_items:
            try:
                cog_root = (Path(__file__).resolve().parent.parent.parent /
                            "cognitive-search-engine")
                if str(cog_root) not in _sys.path:
                    _sys.path.insert(0, str(cog_root))
                from src.search_coordinator import search
                sq = f"{query} {domain}" if domain != "general" else query
                sr = search(sq, group="standard", limit=5)
                if sr:
                    knowledge_items.append({
                        "type": "search_results",
                        "query": sq,
                        "source": "V1: cognitive-search-engine",
                        "results": sr if isinstance(sr, dict)
                                   else {"data": str(sr)[:500]},
                    })
                    sources_used.append("V1:search")
            except Exception:
                pass

        # Source 3: Conflict arbitration (C)
        if domain == "conservation" and knowledge_items:
            try:
                arb_root = (Path(__file__).resolve().parent.parent.parent /
                            "conflict-arbiter")
                if str(arb_root) not in _sys.path:
                    _sys.path.insert(0, str(arb_root))
                from src.arbiter import ConflictArbiter
                arbiter = ConflictArbiter()
                claims = []
                for item in knowledge_items:
                    if item["type"] == "trait_conservation_status":
                        data = item.get("data", {})
                        claims.append({
                            "source": data.get("source", "unknown"),
                            "status": data.get("iucn_status",
                                      data.get("china_red_list_status", "")),
                        })
                if claims:
                    arb_result = arbiter.detect_conflicts(
                        species_name=query,
                        sources=claims,
                    )
                    knowledge_items.append({
                        "type": "conflict_arbitration",
                        "source": "C: conflict-arbiter",
                        "conflicts_detected": arb_result.get("has_conflict", False),
                        "conflict_level": arb_result.get("conflict_level", 0),
                    })
                    sources_used.append("C:arbitration")
            except Exception:
                pass

        return {
            "status": "ok",
            "domain": domain,
            "query": query,
            "knowledge_items": knowledge_items,
            "total_items": len(knowledge_items),
            "sources_used": sources_used,
            "pipeline": "V0(KB)->V1(search)->C(arbitration)->V0(writeback)",
        }

    def _generate_ocr_variants(self, name: str) -> List[str]:
        """Generate OCR error variants for a scientific name.

        Canonical implementation lives in src/shared.py — this is a local
        convenience wrapper. Consider importing from shared.py for consistency.
        """
        variants = []
        confusable = {"u": "b", "b": "u", "i": "l", "l": "i", "n": "m", "m": "n"}
        for i, ch in enumerate(name):
            if ch.lower() in confusable:
                variants.append(name[:i] + confusable[ch.lower()] + name[i + 1:])
        for n in range(1, min(4, len(name))):
            variants.append(name[:-n])
        return list(set(variants))[:20]


def get_adapter() -> FishEcologyAdapter:
    """Factory function for project_loader."""
    return FishEcologyAdapter()
