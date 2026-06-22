"""
workspace/senses — 感受器层 (移植自 san-sheng-wanwu-core)

统一感知协议 + 学科知识图谱 + 搜索缓存。

依赖注入模式: MCP 工具函数在运行时注入。
零外部依赖: domains.py 和 cache.py 仅使用 Python 标准库。

内置感受器 (占位, 在 Reasonix MCP 环境中自动激活):
  Scholar/Cnki/Ncbi/FishBase/Web/Ocr — 通过 MCP 数据通道

学科领域感受器 (内置知识图谱, 无需 MCP):
  domains.py — 12 个学科领域 (数理化生计算机心哲马经文中)

基础设施:
  cache.py — 搜索缓存 (24h TTL LRU)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime

# ── 统一输入/输出协议 ──

@dataclass
class SenseInput:
    """统一的感受器输入格式 (移植自 san-sheng-wanwu-core)。"""
    query: str
    species: Optional[str] = None
    speech_act: str = "assertion"
    max_results: int = 10
    sources: List[str] = field(default_factory=lambda: ["crossref", "openalex", "google_scholar"])
    time_range: Optional[tuple] = None


@dataclass
class SenseOutput:
    """统一的感受器输出格式 — 所有感受器返回此协议。"""
    query: str
    species: Optional[str] = None
    total_found: int = 0
    papers: List[Dict[str, Any]] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# ── 学科知识图谱 ──

from .domains import (
    ALL_DOMAIN_SENSES, ALL_DOMAIN_NAMES,
    create_all_domains, create_domain,
    MathSense, PhysicsSense, ChemistrySense, BiologySense,
    ComputerScienceSense, PsychologySense, PhilosophySense,
    ChinesePhilosophySense, MarxismSense, EconomicsSense,
    LiteratureSense, SciFiSense,
    get_domain_topology, get_domain_neighbors,
)

# ── 搜索缓存 ──

from .cache import SearchCache

# ── 便捷装配 ──

def setup_senses():
    """一键创建所有领域感受器实例 + 搜索缓存。"""
    from .domains import create_all_domains
    domain_list = create_all_domains()
    domain_dict = {d.domain: d for d in domain_list}
    cache = SearchCache()
    return {"domains": domain_dict, "cache": cache, "total_domains": len(domain_dict)}


__all__ = [
    "SenseInput", "SenseOutput",
    "SearchCache",
    # 学科领域
    "MathSense", "PhysicsSense", "ChemistrySense", "BiologySense",
    "ComputerScienceSense", "PsychologySense", "PhilosophySense",
    "ChinesePhilosophySense", "MarxismSense", "EconomicsSense",
    "LiteratureSense", "SciFiSense",
    "ALL_DOMAIN_SENSES", "ALL_DOMAIN_NAMES",
    "create_all_domains", "create_domain",
    "get_domain_topology", "get_domain_neighbors",
    "setup_senses",
]
