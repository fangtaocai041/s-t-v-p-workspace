#!/usr/bin/env python3
"""
统一搜索引擎调度器 — 11 引擎矩阵

基于 coordination.yaml 的 search_engine_registry，将文献搜索请求
自动分发到全部 11 个引擎，按优先级 fan-out 并行执行。

引擎矩阵:
  学术: scholar(OpenAlex+Crossref) / article(EuropePMC) / scholarly(GS) / ncbi(PubMed)
  中文: baidu_scholar(百度学术) / cnki(知网) / wanfang(万方) / cas(中科院)
  深度: tavily(AI搜索) / exa(语义搜索)
  保底: web_search(内置通用)

用法:
  from scripts.search_dispatcher import SearchDispatcher
  sd = SearchDispatcher()
  results = sd.search("刀鲚洄游", category="all")
  results = sd.search("Coilia nasus", category="academic")
  results = sd.search("江豚种群", category="chinese")
"""

from __future__ import annotations

import concurrent.futures
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent


class EngineCategory(str, Enum):
    ACADEMIC = "academic"
    CHINESE = "chinese_academic"
    SEMANTIC = "semantic"
    BUILTIN = "builtin"


class EngineGroup(str, Enum):
    QUICK = "quick"         # 3 引擎快速验证
    STANDARD = "standard"   # 5 引擎标准搜索
    FULL = "full"           # 8 引擎全量搜索
    CHINESE = "chinese"     # 4 引擎中文搜索
    ALL = "all"             # 11 引擎全部


@dataclass
class EngineSpec:
    """搜索引擎规格"""
    name: str
    category: EngineCategory
    priority: int          # 1=最高
    mcp_tool: str          # MCP 工具名
    strategy: str = ""     # site: 策略 (中文引擎)
    language: str = "en"
    description: str = ""


@dataclass
class EngineResult:
    engine: str
    query: str
    status: str = "pending"
    papers: List[Dict] = field(default_factory=list)
    error: str = ""
    elapsed_ms: float = 0.0
    priority: int = 5


@dataclass
class SearchReport:
    query: str
    total_papers: int
    engines_used: int
    engines_failed: int
    results: List[EngineResult]
    elapsed_total_ms: float


# ── 11 引擎注册表 ──

ENGINE_REGISTRY: Dict[str, EngineSpec] = {
    # ─ 学术引擎 (Priority 1-3) ─
    "scholar": EngineSpec(
        name="scholar", category=EngineCategory.ACADEMIC, priority=1,
        mcp_tool="scholar_search_literature_graph",
        description="OpenAlex + Crossref + Semantic Scholar 三源融合",
    ),
    "ncbi": EngineSpec(
        name="ncbi", category=EngineCategory.ACADEMIC, priority=1,
        mcp_tool="ncbi_ncbi_esearch",
        description="PubMed 生物医学文献 (NCBI E-utilities)",
    ),
    "article": EngineSpec(
        name="article", category=EngineCategory.ACADEMIC, priority=2,
        mcp_tool="article_search_literature",
        description="Europe PMC 全文 + 元数据",
    ),
    "scholarly": EngineSpec(
        name="scholarly", category=EngineCategory.ACADEMIC, priority=2,
        mcp_tool="scholar_search_google_scholar_key_words",
        description="Google Scholar 传统关键词搜索",
    ),
    # ─ 中文学术 (Priority 4-6) ─
    "baidu_scholar": EngineSpec(
        name="baidu_scholar", category=EngineCategory.CHINESE, priority=4,
        mcp_tool="web_search", strategy="site:xueshu.baidu.com",
        language="zh", description="百度学术",
    ),
    "cnki": EngineSpec(
        name="cnki", category=EngineCategory.CHINESE, priority=4,
        mcp_tool="web_search", strategy="site:cnki.net OR site:navi.cnki.net",
        language="zh", description="中国知网",
    ),
    "wanfang": EngineSpec(
        name="wanfang", category=EngineCategory.CHINESE, priority=5,
        mcp_tool="web_search", strategy="site:wanfangdata.com.cn",
        language="zh", description="万方数据",
    ),
    "cas": EngineSpec(
        name="cas", category=EngineCategory.CHINESE, priority=5,
        mcp_tool="web_search", strategy="site:cas.cn OR site:ihb.ac.cn OR site:ioz.ac.cn",
        language="zh", description="中科院系统",
    ),
    # ─ AI 深度搜索 (Priority 7) ─
    "tavily": EngineSpec(
        name="tavily", category=EngineCategory.SEMANTIC, priority=7,
        mcp_tool="tavily_tavily_search",
        description="Tavily AI 深度搜索",
    ),
    "exa": EngineSpec(
        name="exa", category=EngineCategory.SEMANTIC, priority=7,
        mcp_tool="exa_web_search_exa",
        description="Exa 语义向量搜索",
    ),
    # ─ 保底 (Priority 9) ─
    "web_search": EngineSpec(
        name="web_search", category=EngineCategory.BUILTIN, priority=9,
        mcp_tool="web_search",
        description="Reasonix 内置通用搜索",
    ),
}

# ─ 引擎组预设 ─
ENGINE_GROUPS: Dict[EngineGroup, List[str]] = {
    EngineGroup.QUICK:    ["scholar", "ncbi", "web_search"],
    EngineGroup.STANDARD: ["scholar", "article", "ncbi", "tavily", "web_search"],
    EngineGroup.FULL:     ["scholar", "article", "ncbi", "scholarly",
                           "baidu_scholar", "cnki", "tavily", "web_search"],
    EngineGroup.CHINESE:  ["baidu_scholar", "cnki", "wanfang", "cas"],
    EngineGroup.ALL:      list(ENGINE_REGISTRY.keys()),
}


class SearchDispatcher:
    """
    统一搜索引擎调度器

    用法:
        sd = SearchDispatcher()
        report = sd.search("刀鲚洄游", group=EngineGroup.FULL)
        print(f"{report.total_papers} papers from {report.engines_used} engines")
    """

    def __init__(self, max_workers: int = 5, timeout_s: float = 30.0):
        self.max_workers = max_workers
        self.timeout_s = timeout_s

    def search(
        self,
        query: str,
        group: EngineGroup = EngineGroup.STANDARD,
        max_results: int = 10,
        progress_callback: Optional[Callable] = None,
    ) -> SearchReport:
        """
        对 query 在指定引擎组中并行搜索。

        Args:
            query: 搜索关键词
            group: 引擎组 (QUICK/STANDARD/FULL/CHINESE/ALL)
            max_results: 每个引擎最大结果数
            progress_callback: 每完成一个引擎回调 (engine_name, status, paper_count)
        """
        engine_names = ENGINE_GROUPS.get(group, ENGINE_GROUPS[EngineGroup.STANDARD])
        engines = [ENGINE_REGISTRY[n] for n in engine_names if n in ENGINE_REGISTRY]
        engines.sort(key=lambda e: e.priority)

        all_results: List[EngineResult] = []
        total_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._search_one, e, query, max_results): e
                for e in engines
            }
            for future in concurrent.futures.as_completed(futures):
                engine = futures[future]
                try:
                    result = future.result(timeout=self.timeout_s)
                except concurrent.futures.TimeoutError:
                    result = EngineResult(
                        engine=engine.name, query=query,
                        status="timeout", error=f">{self.timeout_s}s",
                        priority=engine.priority,
                    )
                except Exception as e:
                    result = EngineResult(
                        engine=engine.name, query=query,
                        status="error", error=str(e)[:100],
                        priority=engine.priority,
                    )
                all_results.append(result)

                if progress_callback:
                    progress_callback(engine.name, result.status, len(result.papers))

        all_results.sort(key=lambda r: r.priority)
        total_papers = sum(len(r.papers) for r in all_results)
        failed = sum(1 for r in all_results if r.status != "ok")

        return SearchReport(
            query=query,
            total_papers=total_papers,
            engines_used=len(all_results) - failed,
            engines_failed=failed,
            results=all_results,
            elapsed_total_ms=(time.perf_counter() - total_start) * 1000,
        )

    def _search_one(self, engine: EngineSpec, query: str, limit: int) -> EngineResult:
        """单个引擎搜索（离线模式 — 记录调用意图）"""
        t0 = time.perf_counter()
        result = EngineResult(engine=engine.name, query=query, priority=engine.priority)

        # 构建实际查询（中文引擎加 site: 策略）
        actual_query = query
        if engine.strategy:
            actual_query = f"{engine.strategy} {query}"

        # 离线模式：记录调用参数，不实际执行 MCP
        result.papers = [{
            "engine": engine.name,
            "mcp_tool": engine.mcp_tool,
            "query": actual_query,
            "language": engine.language,
            "category": engine.category.value,
            "note": f"[离线模式] 在 Reasonix 会话中通过 {engine.mcp_tool} 执行",
        }]
        result.status = "ok"
        result.elapsed_ms = (time.perf_counter() - t0) * 1000
        return result

    def search_online(
        self,
        query: str,
        search_fn: Callable,
        group: EngineGroup = EngineGroup.STANDARD,
        max_results: int = 10,
    ) -> SearchReport:
        """
        在线搜索 — 传入实际搜索函数（在 Reasonix 会话中可用）。

        Args:
            query: 关键词
            search_fn: 搜索函数，签名 (engine_name, actual_query, limit) -> List[dict]
            group: 引擎组
            max_results: 每引擎最大结果
        """
        engine_names = ENGINE_GROUPS.get(group, ENGINE_GROUPS[EngineGroup.STANDARD])
        engines = [ENGINE_REGISTRY[n] for n in engine_names if n in ENGINE_REGISTRY]
        engines.sort(key=lambda e: e.priority)

        all_results: List[EngineResult] = []
        total_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for e in engines:
                actual_query = query
                if e.strategy:
                    actual_query = f"{e.strategy} {query}"
                futures[executor.submit(search_fn, e.name, actual_query, max_results)] = e

            for future in concurrent.futures.as_completed(futures):
                engine = futures[future]
                try:
                    papers = future.result(timeout=self.timeout_s)
                    result = EngineResult(
                        engine=engine.name, query=query,
                        status="ok", papers=papers or [],
                        priority=engine.priority,
                    )
                except Exception as e:
                    result = EngineResult(
                        engine=engine.name, query=query,
                        status="error", error=str(e)[:100],
                        priority=engine.priority,
                    )
                all_results.append(result)

        all_results.sort(key=lambda r: r.priority)
        total_papers = sum(len(r.papers) for r in all_results)
        failed = sum(1 for r in all_results if r.status != "ok")

        return SearchReport(
            query=query,
            total_papers=total_papers,
            engines_used=len(all_results) - failed,
            engines_failed=failed,
            results=all_results,
            elapsed_total_ms=(time.perf_counter() - total_start) * 1000,
        )

    def list_engines(self) -> List[Dict]:
        return [
            {"name": e.name, "category": e.category.value, "priority": e.priority,
             "mcp_tool": e.mcp_tool, "language": e.language, "desc": e.description}
            for e in sorted(ENGINE_REGISTRY.values(), key=lambda x: x.priority)
        ]

    def print_matrix(self):
        """打印引擎矩阵"""
        print(f"\n{'─'*70}")
        print(f"  搜索引擎矩阵 — 11 引擎")
        print(f"{'─'*70}")
        print(f"  {'引擎':15s} {'类型':12s} {'优先级':6s} {'MCP工具':35s}")
        print(f"  {'─'*68}")
        for e in sorted(ENGINE_REGISTRY.values(), key=lambda x: x.priority):
            icon = "🟢" if e.priority <= 3 else "🟡" if e.priority <= 6 else "🔵"
            print(f"  {icon} {e.name:13s} {e.category.value:12s} P{e.priority:<5d} {e.mcp_tool:35s}")
        print(f"\n  引擎组预设:")
        for group, names in ENGINE_GROUPS.items():
            print(f"    {group.value:10s} → {', '.join(names)}")


# ── CLI ──

def main():
    import argparse
    parser = argparse.ArgumentParser(description="搜索引擎调度器")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--group", choices=[g.value for g in EngineGroup], default="standard")
    parser.add_argument("--list", action="store_true", help="列出引擎矩阵")
    args = parser.parse_args()

    sd = SearchDispatcher()

    if args.list:
        sd.print_matrix()
        return

    if args.query:
        group = EngineGroup(args.group)
        report = sd.search(args.query, group=group)
        print(f"\n🔍 \"{args.query}\" ({group.value})")
        print(f"   {report.total_papers} papers from {report.engines_used} engines")
        print(f"   {report.elapsed_total_ms:.0f}ms total")
        for r in report.results:
            icon = "✅" if r.status == "ok" else "❌"
            print(f"   {icon} {r.engine:15s} {len(r.papers):3d} papers  {r.elapsed_ms:.0f}ms")
    else:
        sd.print_matrix()


if __name__ == "__main__":
    main()
