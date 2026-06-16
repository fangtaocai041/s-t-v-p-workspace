"""
认知搜索引擎适配器 (Cognitive Search Adapter)
──────────────────────────────────────────────
将 cognitive-search-engine (v5.0 Hub-and-Spoke) 桥接到 Porpoise Agent。

封装:
- ParallelSearch: 多 query 并行搜索 + DOI 去重
- generate_variants: OCR 拼写变体自动生成
- build_search_queries: 完整的 Layer 0-4 query 构建

降级策略:
- cognitive-search-engine 不可用时 → 使用 Porpoise 内置的简化搜索
- 单个 provider 失败 → 其他 provider 继续

用法:
    from src.integration.cognitive_search_adapter import CognitiveSearchAdapter

    adapter = CognitiveSearchAdapter()
    papers = adapter.search("Neophocaena asiaeorientalis", chinese_name="江豚")
    # → [{"title": "...", "doi": "...", ...}, ...]
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── 定位 cognitive-search-engine ─────────────────────────────

# Try multiple paths to locate cognitive-search-engine:
#   1. D:/Reasonix/cognitive-search-engine (sibling to canonical porpoise-agent)
#   2. ../cognitive-search-engine relative to this project
#   3. Environment variable COGNITIVE_SEARCH_ENGINE_PATH
#   4. sys.path fallback
_COGNITIVE_SEARCH_PATHS = [
    Path("D:/Reasonix/cognitive-search-engine"),
    Path(__file__).resolve().parent.parent.parent.parent / "cognitive-search-engine",
    Path(__file__).resolve().parent.parent.parent.parent.parent / "cognitive-search-engine",
]

import os as _os
_env_path = _os.getenv("COGNITIVE_SEARCH_ENGINE_PATH", "")
if _env_path:
    _COGNITIVE_SEARCH_PATHS.insert(0, Path(_env_path))

_COGNITIVE_SEARCH_PATH = None
for _p in _COGNITIVE_SEARCH_PATHS:
    if (_p / "src" / "parallel_search.py").exists():
        _COGNITIVE_SEARCH_PATH = _p
        break

if _COGNITIVE_SEARCH_PATH is None:
    _COGNITIVE_SEARCH_PATH = _COGNITIVE_SEARCH_PATHS[0]  # fallback for error message
_COGNITIVE_SEARCH_AVAILABLE = False

_parallel_search = None
_generate_variants = None
_build_search_queries = None
_CognitiveAgent = None  # full search_rules.yaml pipeline


def _try_import_cognitive_search():
    """尝试导入 cognitive-search-engine。失败则标记不可用。"""
    global _COGNITIVE_SEARCH_AVAILABLE, _parallel_search, _generate_variants, _build_search_queries
    global _CognitiveAgent

    if _COGNITIVE_SEARCH_AVAILABLE:
        return True

    if _COGNITIVE_SEARCH_PATH is None:
        return False

    try:
        import importlib.util
        import sys as _sys

        def _load_module(file_name: str, module_name: str):
            """Load a .py file as a named module into sys.modules."""
            fpath = _COGNITIVE_SEARCH_PATH / "src" / file_name
            spec = importlib.util.spec_from_file_location(module_name, str(fpath))
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load {fpath}")
            mod = importlib.util.module_from_spec(spec)
            # Register in sys.modules BEFORE execution (allows cross-imports)
            _sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            return mod

        # 1. Load dependencies first (agent_core imports these)
        _load_module("world_model.py", "src.world_model")
        _load_module("memory_layer.py", "src.memory_layer")

        # 2. Load parallel_search
        ps_module = _load_module("parallel_search.py", "cognitive_search.parallel_search")

        # 3. Load variant_generator
        vg_module = _load_module("variant_generator.py", "cognitive_search.variant_generator")

        # 4. Load agent_core (CognitiveAgent — full search_rules.yaml pipeline)
        try:
            ac_module = _load_module("agent_core.py", "src.agent_core")
            _CognitiveAgent = getattr(ac_module, "CognitiveAgent", None)
        except Exception as e:
            logger.debug(f"CognitiveAgent load skipped: {e}")
            _CognitiveAgent = None

        _parallel_search = ps_module.ParallelSearch
        _generate_variants = vg_module.generate_variants
        _build_search_queries = ps_module.build_search_queries
        _COGNITIVE_SEARCH_AVAILABLE = True
        logger.info(f"cognitive-search-engine loaded from {_COGNITIVE_SEARCH_PATH}"
                     f" (CognitiveAgent={'available' if _CognitiveAgent else 'unavailable'})")
        return True

    except Exception as e:
        logger.warning(f"cognitive-search-engine not available: {e}")
        _COGNITIVE_SEARCH_AVAILABLE = False
        return False


# ══════════════════════════════════════════════════════════════
# Adapter
# ══════════════════════════════════════════════════════════════

class CognitiveSearchAdapter:
    """
    认知搜索引擎适配器

    桥接 Porpoise Agent ←→ cognitive-search-engine

    两种管线:
    - fast (默认):     ParallelSearch 多 query 并行 → DOI 去重
    - full_pipeline:   CognitiveAgent.search() → search_rules.yaml 完整管线
                        (BDI 相位选择 + 引用图遍历 + review mining + OCR 变体
                         + 自适应停止条件 + D₃ 世界模型预测)

    用法:
        adapter = CognitiveSearchAdapter()
        # 快速搜索
        papers = adapter.search("Neophocaena asiaeorientalis", genus="Neophocaena",
                                 species="asiaeorientalis", chinese_name="江豚")
        # 完整管线
        result = adapter.search("Neophocaena asiaeorientalis", genus="Neophocaena",
                                 species="asiaeorientalis", chinese_name="江豚",
                                 full_pipeline=True)
    """

    def __init__(self, max_results: int = 20, max_workers: int = 4):
        self.max_results = max_results
        self.max_workers = max_workers
        self._available = _try_import_cognitive_search()
        self._searcher: Optional[Any] = None
        self._cognitive_agent: Optional[Any] = None

        if self._available:
            self._searcher = _parallel_search(
                mode="http",
                max_workers=max_workers,
            )
            if _CognitiveAgent is not None:
                self._cognitive_agent = _CognitiveAgent(mode="http")
            logger.info(
                f"CognitiveSearchAdapter ready"
                f" (full_pipeline={'available' if self._cognitive_agent else 'unavailable'})"
            )

    @property
    def available(self) -> bool:
        return self._available and self._searcher is not None

    @property
    def full_pipeline_available(self) -> bool:
        return self._cognitive_agent is not None

    def search(
        self,
        query: str,
        *,
        genus: str = "",
        species: str = "",
        chinese_name: str = "",
        keywords: Optional[list[str]] = None,
        max_per_query: int = 10,
        full_pipeline: bool = False,
    ) -> list[dict]:
        """
        执行认知搜索

        Args:
            query: 搜索查询
            genus: 属名 (物种模式)
            species: 种名 (物种模式)
            chinese_name: 中文名
            keywords: 生态关键词
            max_per_query: 每 query 最大结果数 (仅 fast 模式)
            full_pipeline: True → 走 search_rules.yaml 完整管线

        Returns:
            list[dict]: 论文列表
        """
        if not self.available:
            logger.debug("cognitive-search-engine unavailable — use fallback")
            return []

        try:
            # ── 完整管线: CognitiveAgent.search() ──
            if full_pipeline and genus and species:
                return self._search_full_pipeline(
                    genus, species, chinese_name, keywords
                )

            # ── 物种模式 (fast) ──
            if genus and species:
                return self._search_species(
                    genus, species, chinese_name, keywords, max_per_query
                )

            # ── 通用模式 ──
            queries = [query]
            if chinese_name:
                queries.append(chinese_name)
                queries.append(f"{chinese_name} {query}")

            return self._search_generic(queries, max_per_query)

        except Exception as e:
            logger.error(f"CognitiveSearchAdapter.search failed: {e}")
            return []

    def _search_full_pipeline(
        self,
        genus: str,
        species: str,
        chinese_name: str = "",
        keywords: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        完整管线: CognitiveAgent.search()

        走 search_rules.yaml 定义的全部相位:
          multi_engine_parallel → exact_search → review_mining
          → citation_traversal → variant_search → journal_scan
          → dedup_merge

        BDI ReAct 循环控制:
          Think → Act → Observe → Reflect
          自适应停止: 满意即止 / 收益递减 / token 预算 / 连续零产出
        """
        if not self._cognitive_agent:
            logger.warning("CognitiveAgent not available — falling back to fast search")
            return self._search_species(genus, species, chinese_name, keywords)

        species_id = f"{genus}_{species}"
        logger.info(f"Full pipeline search: {species_id} ({chinese_name})")

        # 调用 CognitiveAgent.search() — 完整的 ReAct 循环
        result = self._cognitive_agent.search(
            species_id=species_id,
            genus=genus,
            species=species,
            chinese_name=chinese_name,
        )

        papers_raw = result.get("papers", [])
        logger.info(
            f"Full pipeline: {len(papers_raw)} papers, "
            f"{result.get('tokens_spent', 0)} tokens, "
            f"phases: {result.get('phases_executed', [])}, "
            f"stop: {result.get('stop_reason', 'unknown')}"
        )

        # 标准化 Paper dataclass → dict
        standardized = []
        for p in papers_raw:
            if hasattr(p, '__dataclass_fields__'):
                # cognitive-search-engine Paper dataclass
                std_paper = {
                    "title": getattr(p, "title", ""),
                    "doi": getattr(p, "doi", ""),
                    "year": getattr(p, "year", None),
                    "journal": getattr(p, "journal", ""),
                    "authors": getattr(p, "authors", []),
                    "abstract": getattr(p, "abstract", ""),
                    "source": getattr(p, "source", "full_pipeline"),
                    "citations": getattr(p, "citations", 0),
                    "trust": getattr(p, "trust", "pending"),
                    "trust_score": getattr(p, "trust_score", 50),
                    "pmid": getattr(p, "pmid", None),
                    "note": getattr(p, "note", ""),
                    "_raw": p,
                }
            elif isinstance(p, dict):
                std_paper = {
                    "title": p.get("title", ""),
                    "doi": p.get("doi", ""),
                    "year": p.get("year"),
                    "journal": p.get("journal", ""),
                    "authors": p.get("authors", []),
                    "abstract": p.get("abstract", ""),
                    "source": p.get("source", "full_pipeline"),
                    "citations": p.get("citations", 0),
                    "_raw": p,
                }
            else:
                std_paper = {"title": str(p)[:100], "source": "full_pipeline", "_raw": p}
            standardized.append(std_paper)

        return standardized

    def _search_species(
        self,
        genus: str,
        species: str,
        chinese_name: str = "",
        keywords: Optional[list[str]] = None,
        max_per_query: int = 10,
    ) -> list[dict]:
        """
        物种模式: OCR 变体 + 多 query 并行

        流程:
        1. 生成 OCR 变体
        2. 构建完整 query 集 (精确名 + 变体 + 中文 + 生态关键词)
        3. 并行搜索所有 query
        4. DOI 去重
        """
        # Step 1: OCR 变体
        variants: list[str] = []
        if _generate_variants:
            try:
                variants = _generate_variants(genus, species, max_variants=15)
                logger.debug(f"Generated {len(variants)} OCR variants for {genus} {species}")
            except Exception as e:
                logger.debug(f"Variant generation failed: {e}")

        # Step 2: 构建 query 集
        if _build_search_queries:
            queries = _build_search_queries(
                genus=genus,
                species=species,
                chinese_name=chinese_name,
                variants=variants,
                keywords=keywords or [],
            )
        else:
            # fallback query 构建
            full_name = f"{genus} {species}"
            queries = [full_name]
            if chinese_name:
                queries.append(chinese_name)
            for v in variants[:10]:
                queries.append(v)
            for kw in (keywords or [])[:3]:
                queries.append(f"{full_name} {kw}")

        logger.info(f"Species search: {genus} {species} → {len(queries)} queries "
                     f"(incl. {len(variants)} OCR variants)")

        # Step 3: 并行搜索
        return self._search_generic(queries, max_per_query)

    def _search_generic(
        self,
        queries: list[str],
        max_per_query: int = 10,
    ) -> list[dict]:
        """通用模式: 直接并行搜索 + DOI 去重"""
        if not self._searcher:
            return []

        stats = self._searcher.search_all(
            queries,
            max_per_query=max_per_query,
            dedup=True,
        )

        papers = stats.new_papers

        # 标准化字段名
        standardized = []
        for p in papers:
            std_paper = {
                "title": p.get("title", ""),
                "doi": p.get("doi", ""),
                "year": p.get("year"),
                "journal": p.get("journal", ""),
                "authors": p.get("authors", []),
                "abstract": p.get("abstract", ""),
                "source": p.get("_source", p.get("source", "unknown")),
                "citations": p.get("citations", p.get("cited_by_count", 0)),
                "_raw": p,
            }
            standardized.append(std_paper)

        logger.info(
            f"Search: {len(queries)} queries → "
            f"{stats.total_raw} raw → {len(standardized)} unique "
            f"(deduped {stats.deduped})"
        )

        return standardized

    def generate_variants(self, genus: str, species: str) -> list[str]:
        """生成 OCR 拼写变体 (公开给 LiteratureAgent 使用)"""
        if not self.available:
            return []

        if _generate_variants:
            try:
                return _generate_variants(genus, species, max_variants=20)
            except Exception:
                return []
        return []

    def close(self):
        if self._searcher:
            try:
                self._searcher.close()
            except Exception:
                pass


# ── 便捷函数 ──────────────────────────────────────────────────

def is_species_query(query: str) -> bool:
    """
    检测查询是否为物种搜索 (非通用关键词)。

    启发式:
    - 包含拉丁学名模式 (大写字母开头 + 小写字母)
    - 包含中文物种名

    Returns:
        bool: 是否可能为物种查询
    """
    import re

    # 拉丁学名模式: 大写字母开头 + 空格 + 小写字母 (如 "Neophocaena asiaeorientalis")
    if re.search(r'\b[A-Z][a-z]+\s+[a-z]+\b', query):
        return True

    # 包含已知物种指示词
    species_indicators = [
        "江豚", "白鱀豚", "中华白海豚",
        "porpoise", "dolphin", "whale",
        "cetacean", "phocoena", "neophocaena",
    ]
    query_lower = query.lower()
    return any(indicator.lower() in query_lower for indicator in species_indicators)


# ── 全局实例 ──────────────────────────────────────────────────

_adapter: Optional[CognitiveSearchAdapter] = None


def get_adapter() -> CognitiveSearchAdapter:
    """获取全局适配器实例 (懒加载)"""
    global _adapter
    if _adapter is None:
        _adapter = CognitiveSearchAdapter()
    return _adapter
