"""FishEcologyAdapter — fish-ecology-assistant (三角核心·知识供给).

核心专精: lookup_species(name: str) → SpeciesProfile
    长江 443 种鱼类知识库查询 + 可信度评分
    通路: P1(fish→cognitive) P2(cognitive→fish)

Exposes fish ecology knowledge supply as a Python-callable interface.
Uses FishEcologyOrchestrator when available, falls back to direct
species DB + config loading for minimal viable operation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import shared adapter protocol (workspace root on sys.path)
try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object  # fallback for standalone usage


class FishEcologyAdapter(IProjectAdapter):
    """Adapter for fish-ecology-assistant (V0 — 知识供给层).

    Two-tier operation:
      Tier 1: FishEcologyOrchestrator (full pipeline via Reasonix skills)
      Tier 2: Direct species DB lookup (minimal viable fallback)
    """

    project_name = "fish-ecology-assistant"

    # Credibility scoring journal whitelist
    JOURNAL_WHITELIST: Dict[str, int] = {
        "水生生物学报": 25, "中国水产科学": 25, "水产学报": 25,
        "生物多样性": 25, "湖泊科学": 25, "生态学报": 25,
        "Scientific Reports": 30, "PLOS ONE": 30, "Gene": 30,
    }

    def __init__(self) -> None:
        self._orchestrator: Any = None
        self._species_db: Dict[str, Any] = {}
        self._init()

    def _init(self) -> None:
        """Try orchestrator first, fall back to direct config load."""
        try:
            from .orchestrator import FishEcologyOrchestrator
            self._orchestrator = FishEcologyOrchestrator()
        except ImportError:
            self._load_species_db()

    def _load_species_db(self) -> None:
        """Direct load of species knowledge base."""
        try:
            import yaml
            cfg = Path(__file__).resolve().parent.parent / "config" / "fish_species_kb.yaml"
            if not cfg.is_file():
                cfg = Path(__file__).resolve().parent.parent / "config" / "yangtze_fish_species.yaml"
            if cfg.is_file():
                self._species_db = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        except Exception:
            pass

    # ── IProjectAdapter interface ──

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute a fish ecology search.

        Tier 1: Full orchestrator pipeline (DELEGATE protocol).
        Tier 2: Species DB lookup + search query generation.
        """
        if self._orchestrator:
            # Remove already-extracted keys to avoid double-pass in **kwargs
            _clean = {k: v for k, v in kwargs.items()
                      if k not in ("species", "chinese_name")}
            return self._orchestrator.delegate_search(
                kwargs.get("species", query),
                kwargs.get("chinese_name", ""),
                **_clean,
            )

        # Tier 2: Direct species lookup
        species_name = kwargs.get("species", query)
        species_key = species_name.replace(" ", "_").lower()
        species_data = self._species_db.get(species_key, {})
        chinese_name = kwargs.get("chinese_name", species_data.get("chinese_name", ""))

        return {
            "status": "ok",
            "tier": "direct_db",
            "scientific_name": species_name,
            "chinese_name": chinese_name,
            "known_species": bool(species_data),
            "species_data": species_data,
            "search_queries": self._build_queries(species_name, chinese_name),
            "ocr_variants": self._ocr_variants(species_name),
            "sources": ["pubmed", "crossref", "openalex", "cnki", "cscd", "wanfang"],
        }

    def health(self) -> Dict[str, Any]:
        if self._orchestrator:
            return self._orchestrator.health()
        return {
            "project": self.project_name,
            "status": "HEALTHY" if self._species_db else "DEGRADED",
            "tier": "direct_db" if not self._orchestrator else "orchestrator",
            "species_db_size": len(self._species_db),
        }

    def info(self) -> Dict[str, Any]:
        if self._orchestrator:
            return self._orchestrator.info()
        return {
            "project": self.project_name,
            "role": "三角核心·知识供给",
            "capabilities": ["species_knowledge_base", "credibility_scoring",
                           "ocr_variant_generation", "multi_engine_search"],
        }

    # ── P2 通路: 可信度评分 (落地 pathway_contracts.py 合约) ──

    def score_credibility(self, papers: List[dict]) -> List[dict]:
        """Score paper credibility using journal whitelist + identifier presence.

        P2 pathway target_call:
          FishEcologyAdapter.score_credibility(papers: List[dict]) → List[dict]

        INPUT: papers from cognitive-search-engine search results.
        OUTPUT: papers with credibility_score [0-100] + flag added.

        Rules:
          - credibility_score = 50 (baseline)
          - +30 IF journal IN SCI/SSCI
          - +25 IF journal IN 北大核心/CSCD
          - +10 IF has DOI
          - +10 IF has PMID
          - -30 IF preprint without peer review
          - IF score >= 80 THEN flag = '🟢'
          - IF score >= 60 THEN flag = '🟡'
          - ELSE flag = '🟠'
        """
        scored: List[dict] = []
        for paper in papers:
            score = 50  # baseline
            journal = (paper.get("journal") or "").lower()
            # Journal whitelist boost
            for jname, bonus in self.JOURNAL_WHITELIST.items():
                if jname.lower() in journal:
                    score += bonus
                    break
            # Identifier boost
            if paper.get("doi"):
                score += 10
            if paper.get("pmid"):
                score += 10
            # Preprint penalty
            preprint_indicators = ["biorxiv", "research square", "preprint", "ssrn"]
            if any(ind in journal for ind in preprint_indicators):
                score -= 30
            # Clamp
            score = max(0, min(100, score))
            paper["credibility_score"] = score
            paper["flag"] = "🟢 高可信度" if score >= 80 else (
                "🟡 中可信度" if score >= 60 else "🟠 需交叉验证"
            )
            scored.append(paper)
        return scored

    # ── P7 通路: 分类变更回写 (落地 pathway_contracts.py 合约) ──

    def update_taxonomy(
        self,
        species_name: str,
        discrepancy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """P7 pathway target_call: 接收 c项目检测到的分类不一致，写回 f知识库。

        FishEcologyAdapter.update_taxonomy(species_name, discrepancy) → dict

        INPUT:
          species_name: 规范学名 (e.g. "Pseudaspius hakonensis")
          discrepancy: detect_taxonomy_discrepancy() 的返回值
            {
              field: "family",
              c_project_value: "Leuciscidae",
              f_project_value: "Cyprinidae",
              note: "...",
              evidence: [...],
              action_required: True,
            }

        OUTPUT:
          {"status": "ok", "updated": True/False, "field": "taxonomy_log"}

        BEHAVIOR:
          IF fish_species_kb.yaml 中有该物种条目:
            THEN 追加 taxonomy_log 条目 (去重: 相同 note 不重复)
          ELSE:
            创建新条目 (skeleton + taxonomy_log)
        """
        import yaml
        import datetime
        from pathlib import Path

        kb_path = Path(__file__).resolve().parent.parent / "config" / "fish_species_kb.yaml"
        if not kb_path.is_file():
            # Try alternative name
            kb_path = Path(__file__).resolve().parent.parent / "config" / "yangtze_fish_species.yaml"
        if not kb_path.is_file():
            return {"status": "error", "error": "fish_species_kb.yaml not found"}

        species_key = species_name.replace(" ", "_").lower()

        with open(kb_path, encoding="utf-8") as f:
            kb = yaml.safe_load(f) or {}

        species_list = kb.get("species", [])
        if not isinstance(species_list, list):
            species_list = []

        # 查找或创建条目
        target = None
        for s in species_list:
            sid = s.get("id", "").lower()
            s_sci = s.get("scientific", "").lower().replace(" ", "_")
            if species_key in sid or species_key in s_sci:
                target = s
                break

        if target is None:
            # 创建新条目
            target = {
                "id": species_name.replace(" ", "_"),
                "scientific": species_name,
                "chinese_name": "",
                "family": discrepancy.get("c_project_value", ""),
                "taxonomy_log": [],
            }
            species_list.append(target)

        # 追加 taxonomy_log (去重)
        log_entries = target.get("taxonomy_log", [])
        if not isinstance(log_entries, list):
            log_entries = []

        new_entry = {
            "detected_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "field": discrepancy.get("field", "family"),
            "c_project_value": discrepancy.get("c_project_value", ""),
            "f_project_value": discrepancy.get("f_project_value", ""),
            "note": discrepancy.get("note", ""),
            "evidence": discrepancy.get("evidence", []),
            "source": "P7_taxonomy_feedback (auto-detected by cognitive-search-engine)",
        }

        # 去重: 相同 note 不重复
        existing_notes = {e.get("note", "") for e in log_entries}
        if new_entry["note"] not in existing_notes:
            log_entries.append(new_entry)
            target["taxonomy_log"] = log_entries

            # 如果 c_project_value 与 f_project_value 不同，更新 family 字段
            if new_entry["field"] == "family" and target.get("family") != discrepancy.get("c_project_value"):
                target["family"] = discrepancy.get("c_project_value", target.get("family", ""))

            # 写回 YAML
            try:
                with open(kb_path, "w", encoding="utf-8") as f:
                    yaml.dump(kb, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                return {
                    "status": "ok",
                    "updated": True,
                    "species": species_name,
                    "field": "taxonomy_log",
                    "entry": new_entry["note"],
                }
            except Exception as e:
                return {"status": "error", "error": f"Write failed: {e}"}

        return {
            "status": "ok",
            "updated": False,
            "species": species_name,
            "reason": "duplicate — same note already exists in taxonomy_log",
        }

    # ── Helpers ──

    def _build_queries(self, scientific: str, chinese: str) -> List[str]:
        queries = [scientific]
        if chinese:
            queries.append(chinese)
        for direction in ["genetic", "morphology", "ecology", "survey"]:
            queries.append(f"{scientific} {direction}")
        return queries

    def _ocr_variants(self, name: str) -> List[str]:
        variants = set()
        confusable = {"u": ["b"], "b": ["u"], "i": ["l", "e"], "l": ["i"]}
        for i, ch in enumerate(name):
            if ch.lower() in confusable:
                for sub in confusable[ch.lower()]:
                    variants.add(name[:i] + sub + name[i + 1:])
        for n in range(1, min(4, len(name))):
            variants.add(name[:-n])
        return list(variants)[:15]


def get_adapter() -> FishEcologyAdapter:
    return FishEcologyAdapter()