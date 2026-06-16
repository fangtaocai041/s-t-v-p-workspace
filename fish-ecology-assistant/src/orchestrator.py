"""FishEcologyOrchestrator — Python orchestrator for fish-ecology-assistant.

Bridges the gap between the Reasonix skill-based pipeline (28 markdown skills,
5-stage Plan→Search→Analyze→Write→Review) and programmatic cross-project access.

This is NOT a replacement for the Reasonix skill system — it's a lightweight
Python wrapper that:
  1. Loads species knowledge base (yangtze_fish_species.yaml)
  2. Generates DELEGATE protocol messages for Reasonix skill dispatch
  3. Provides structured data access for other projects via adapter.py
  4. Validates queries against known species/configurations

Usage:
    from src.orchestrator import FishEcologyOrchestrator
    orch = FishEcologyOrchestrator()
    result = orch.delegate_search("Ochetobius elongatus", chinese_name="鳤")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FishEcologyOrchestrator:
    """Lightweight Python orchestrator for fish-ecology knowledge supply.

    Loads configs at init, provides structured access to species data,
    and generates Reasonix DELEGATE protocol messages for skill dispatch.
    """

    # Pipeline stages (from research-orchestrator.md)
    STAGES = ["Plan", "Search", "Analyze", "Write", "Review"]

    # Credibility scoring journal whitelist (from v5.0 rules)
    JOURNAL_WHITELIST: Dict[str, int] = {
        "水生生物学报": 25, "中国水产科学": 25, "水产学报": 25,
        "生物多样性": 25, "湖泊科学": 25, "南方水产科学": 25,
        "生态科学": 20, "生态学报": 25,
        "Scientific Data": 30, "Scientific Reports": 30, "Animals": 30,
        "Gene": 30, "Mitochondrial DNA": 30, "Conserv Genet Resour": 30,
        "PLOS ONE": 30,
    }

    def __init__(self) -> None:
        self._project_root = Path(__file__).resolve().parent.parent
        self._agent_config: Dict[str, Any] = {}
        self._species_db: Dict[str, Any] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load agent.yaml and yangtze_fish_species.yaml."""
        try:
            import yaml
            agent_cfg = self._project_root / "config" / "agent.yaml"
            if agent_cfg.is_file():
                self._agent_config = yaml.safe_load(agent_cfg.read_text(encoding="utf-8")) or {}

            species_cfg = self._project_root / "config" / "yangtze_fish_species.yaml"
            if species_cfg.is_file():
                self._species_db = yaml.safe_load(species_cfg.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning(f"Config load failed: {exc}")

    # ── Public API ──

    def delegate_search(
        self, scientific_name: str, chinese_name: str = "", **kwargs
    ) -> Dict[str, Any]:
        """Generate a DELEGATE protocol message for Reasonix research-orchestrator.

        This is the primary interface for cross-project access.
        Other projects call this → gets a DELEGATE message → Reasonix executes the pipeline.

        Returns: {status, delegate_message, species_info, search_queries, ...}
        """
        species_key = scientific_name.replace(" ", "_").lower()
        species_data = self._species_db.get(species_key, {})

        return {
            "status": "ok",
            "protocol": "DELEGATE",
            "target": "fish-ecology-assistant",
            "skill": "research-orchestrator",
            "scientific_name": scientific_name,
            "chinese_name": chinese_name or species_data.get("chinese_name", ""),
            "known_species": bool(species_data),
            "species_data": species_data,
            "pipeline": self.STAGES,
            "search_queries": self._build_search_queries(scientific_name, chinese_name),
            "ocr_variants": self._generate_ocr_variants(scientific_name),
            "max_revision_rounds": 3,
        }

    def lookup_species(self, scientific_name: str) -> Dict[str, Any]:
        """Look up a species in the knowledge base.

        Returns species metadata if found, empty dict if not.
        """
        species_key = scientific_name.replace(" ", "_").lower()
        return dict(self._species_db.get(species_key, {}))

    def list_species(self, family: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """List species in the knowledge base, optionally filtered by family.

        IF family provided THEN filter by family name.
        """
        results = []
        for key, data in self._species_db.items():
            if isinstance(data, dict):
                if family and data.get("family", "") != family:
                    continue
                results.append({"species_id": key, **data})
                if len(results) >= limit:
                    break
        return results

    def score_credibility(self, journal: str, has_doi: bool = False,
                          has_pmid: bool = False, is_preprint: bool = False) -> int:
        """Compute credibility score [0-100] for a paper.

        credibility_score = 50 (baseline)
          + journal_whitelist_bonus
          + 10 IF has_doi
          + 10 IF has_pmid
          - 30 IF is_preprint
        """
        score = 50
        for jname, bonus in self.JOURNAL_WHITELIST.items():
            if jname in journal:
                score += bonus
                break
        if has_doi:
            score += 10
        if has_pmid:
            score += 10
        if is_preprint:
            score -= 30
        return max(0, min(100, score))

    def health(self) -> Dict[str, Any]:
        """Health check."""
        return {
            "project": "fish-ecology-assistant",
            "status": "HEALTHY" if self._agent_config else "DEGRADED",
            "config_loaded": bool(self._agent_config),
            "species_db_size": len(self._species_db),
            "pipeline_stages": self.STAGES,
        }

    def info(self) -> Dict[str, Any]:
        """Version + capabilities."""
        return {
            "project": "fish-ecology-assistant",
            "version": self._agent_config.get("agent", {}).get("version", "unknown"),
            "role": "V0_SupplyVertex (S-State)",
            "pipeline": "5-stage: Plan → Search → Analyze → Write → Review",
            "skill_count": 28,
            "sub_agents": 13,
            "capabilities": [
                "species_knowledge_base",
                "credibility_scoring",
                "ocr_variant_generation",
                "delegate_protocol",
                "chinese_academic_sources",
                "multi_engine_search",
            ],
        }

    # ── Internal ──

    def _build_search_queries(self, scientific_name: str, chinese_name: str) -> List[str]:
        """Build search queries for a species across disciplines."""
        queries = [scientific_name]
        if chinese_name:
            queries.append(chinese_name)
        # Per-discipline queries
        for direction in ["genetic", "morphology", "ecology", "survey"]:
            if direction == "genetic":
                queries.append(f"{scientific_name} genetic diversity population mitochondrial microsatellite")
            elif direction == "morphology":
                queries.append(f"{scientific_name} morphology phenotype shape geometric")
            elif direction == "ecology":
                queries.append(f"{scientific_name} diet feeding habitat reproduction growth")
            elif direction == "survey":
                queries.append(f"{scientific_name} survey diversity community resource")
        return queries

    def _generate_ocr_variants(self, name: str) -> List[str]:
        """Generate OCR error variants for a scientific name."""
        variants = set()
        confusable = {"u": ["b"], "b": ["u"], "i": ["l", "e"], "l": ["i"],
                       "n": ["m"], "m": ["n"]}
        for i, ch in enumerate(name):
            if ch.lower() in confusable:
                for sub in confusable[ch.lower()]:
                    variants.add(name[:i] + sub + name[i + 1:])
        for i in range(len(name)):
            variants.add(name[:i] + name[i + 1:])
        for n in range(1, min(4, len(name))):
            variants.add(name[:-n])
        return list(variants)[:20]


def get_orchestrator() -> FishEcologyOrchestrator:
    """Factory function."""
    return FishEcologyOrchestrator()
