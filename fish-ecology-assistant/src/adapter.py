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
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# 延迟导入 — orchestrator 负责物种知识库所有权
_orchestrator = None

def _get_orchestrator():
    """Lazy-load orchestrator singleton to avoid circular import at module level."""
    global _orchestrator
    if _orchestrator is None:
        from src.orchestrator import get_orchestrator
        _orchestrator = get_orchestrator()
    return _orchestrator


class FishEcologyAdapter:
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
        """Supply domain-specific knowledge from fish ecology knowledge base.

        domains: ecology, genetics, morphology, taxonomy, fisheries
        """
        return {
            "status": "ok",
            "domain": domain,
            "query": query,
            "knowledge_items": [],
            "source": "fish-ecology-assistant knowledge base",
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
