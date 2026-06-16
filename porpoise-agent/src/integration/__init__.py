"""
集成模块 (Integration Layer)
─────────────────────────────
将外部工具桥接到 Porpoise Agent 五层架构中。

组件:
- CognitiveSearchAdapter: cognitive-search-engine (v5.0 Hub-and-Spoke)
- ZoteroAdapter: Zotero SQLite 本地文献库
- ObsidianAdapter: Obsidian Vault 知识库
- KnowledgeGraph: 江豚研究动态知识图谱 (图引擎)
"""

from src.integration.cognitive_search_adapter import (
    CognitiveSearchAdapter,
    is_species_query,
    get_adapter,
)
from src.integration.zotero_adapter import ZoteroAdapter, get_zotero
from src.integration.obsidian_adapter import ObsidianAdapter, get_obsidian
from src.integration.knowledge_graph import KnowledgeGraph, get_graph

__all__ = [
    "CognitiveSearchAdapter",
    "is_species_query",
    "get_adapter",
    "ZoteroAdapter",
    "get_zotero",
    "ObsidianAdapter",
    "get_obsidian",
    "KnowledgeGraph",
    "get_graph",
]
