"""
文献分析 Agent (Literature Agent)
───────────────────────────────────
负责文献搜索、筛选、分析和综述。

能力:
- 多源文献检索 (PubMed, CrossRef, Semantic Scholar)
- 相关性筛选
- 关键发现提取
- 引用网络追踪
- 综述草稿生成

功能生态位: 信息获取 + 初步分析
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.cognitive.bdi import Desire
from src.execution.api import api_client

logger = logging.getLogger(__name__)


class LiteratureAgent(BaseAgent):
    """
    文献分析 Agent — 豚类研究文献专家

    负责:
    1. 接收文献搜索请求
    2. 多源并行检索
    3. 相关性与质量评估
    4. 生成结构化文献报告
    """

    def __init__(self, model: str = "deepseek-chat", memory: Any = None):
        super().__init__(name="literature", model=model, memory=memory)

    def _init_desire(self):
        self.bdi.desire = Desire(
            primary_goal="全面、准确地检索和分析豚类研究文献",
            constraints=[
                "覆盖近5年核心文献",
                "中英文文献均纳入",
                "标注每篇文献的方法学局限",
            ],
            quality_thresholds={
                "min_papers": 10,
                "min_high_relevance": 3,
            },
        )

    def _init_tools(self):
        # 文献 Agent 专有工具
        self.tools.register(
            name="search_literature",
            description="Search scientific literature about cetaceans and porpoises",
            parameters={
                "query": {"type": "string"},
                "source": {"type": "string"},
                "limit": {"type": "integer"},
            },
            fn=self._search_literature,
            category="literature",
            fallback="web_search",
        )

    async def handle_message(self, message: Any) -> dict:
        """
        处理文献请求

        输入: Message 对象 (content 为搜索查询)
        输出: {"papers": [...], "synthesis": "..."}
        """
        self._call_count += 1

        # 提取查询
        query = self._extract_query(message)
        logger.info(f"LiteratureAgent[{self.node_id}]: searching '{query[:80]}'")

        try:
            # 更新 BDI — 加载领域知识库
            self.bdi.belief.user_query = query
            self._load_domain_knowledge(query)

            # 多源并行检索
            results = await self._multi_source_search(query)

            # 质量评估
            assessed = self._assess_quality(results)

            # 生成综述
            synthesis = self._generate_synthesis(assessed)

            return {
                "agent": "literature",
                "query": query,
                "papers": assessed,
                "synthesis": synthesis,
                "n_results": len(assessed),
                "sources": ["semantic_scholar", "pubmed"],
            }

        except Exception as e:
            self._error_count += 1
            logger.error(f"LiteratureAgent failed: {e}")
            return {"agent": "literature", "error": str(e), "papers": []}

    def _extract_query(self, message: Any) -> str:
        """提取查询文本"""
        if hasattr(message, 'content'):
            content = message.content
        else:
            content = message

        if isinstance(content, dict):
            return content.get("query", content.get("text", str(content)))
        elif isinstance(content, str):
            return content
        return str(content)

    async def _multi_source_search(self, query: str) -> list[dict]:
        """
        三层检索策略:
          1. Zotero 本地库 (已有 406 条文献, 零 API 调用)
          2. cognitive-search-engine (完整 search_rules.yaml 管线)
          3. Fallback: Semantic Scholar + PubMed
        """
        import asyncio

        # ── L0: Zotero 本地库 ──
        zotero_papers = self._try_zotero_search(query)
        if zotero_papers:
            logger.info(f"Zotero local: {len(zotero_papers)} papers")
            return zotero_papers

        # ── L1: cognitive-search-engine ──
        cognitive_papers = await self._try_cognitive_search(query)
        if cognitive_papers:
            logger.info(f"cognitive-search-engine: {len(cognitive_papers)} papers")
            # 更新知识图谱 + 自动保存到 Obsidian
            self._update_knowledge_graph(cognitive_papers)
            self._auto_save_to_obsidian(cognitive_papers, query)
            return cognitive_papers

        # ── L2: Fallback 简化搜索 ──
        logger.info("Using fallback search (Semantic Scholar + PubMed)")
        results = []

        try:
            ss_result = await api_client.search_semantic_scholar(query, limit=20)
            if ss_result.success:
                for p in ss_result.data.get("papers", []):
                    p["source"] = "semantic_scholar"
                results.extend(ss_result.data.get("papers", []))

        except Exception as e:
            logger.debug(f"Semantic Scholar search failed: {e}")

        try:
            pubmed_result = await api_client.search_pubmed(query, max_results=10)
            if pubmed_result.success and pubmed_result.data.get("pmids"):
                details = await api_client.fetch_pubmed_details(
                    pubmed_result.data["pmids"][:10]
                )
                if details.success:
                    for p in details.data.get("papers", []):
                        p["source"] = "pubmed"
                    results.extend(details.data.get("papers", []))

        except Exception as e:
            logger.debug(f"PubMed search failed: {e}")

        # DOI 去重
        seen_dois = set()
        deduped = []
        for paper in results:
            doi = paper.get("doi", "")
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            deduped.append(paper)

        # Fallback 结果也更新知识图谱 + Obsidian
        if deduped:
            self._update_knowledge_graph(deduped[:5])
            self._auto_save_to_obsidian(deduped[:5], query)

        return deduped

    def _try_zotero_search(self, query: str) -> list[dict]:
        """在 Zotero 本地库中搜索"""
        try:
            from src.integration.zotero_adapter import get_zotero
            zotero = get_zotero()
            if not zotero.available:
                return []
            return zotero.search(query, limit=20)
        except Exception as e:
            logger.debug(f"Zotero search skipped: {e}")
            return []

    def _update_knowledge_graph(self, papers: list[dict]):
        """自动将新论文添加到动态知识图谱"""
        try:
            from src.integration import get_graph
            g = get_graph()
            for paper in papers[:5]:
                title = paper.get("title", "")
                doi = paper.get("doi", "")
                year = paper.get("year", 0)
                journal = paper.get("journal", "")
                authors = paper.get("authors", [])
                if not title:
                    continue
                # 自动检测物种
                species = []
                title_lower = title.lower()
                if "finless porpoise" in title_lower or "neophocaena" in title_lower or "江豚" in title_lower:
                    species.append("长江江豚")
                if "yangtze" in title_lower:
                    species.append("长江江豚")
                g.add_paper(title, doi, year, journal, authors, species)
            logger.debug(f"Knowledge graph updated with {len(papers[:5])} papers")
        except Exception as e:
            logger.debug(f"Knowledge graph update skipped: {e}")

    def _auto_save_to_obsidian(self, papers: list[dict], query: str):
        """自动保存新论文到 Obsidian 文献笔记 (前 3 篇)"""
        try:
            from src.integration.obsidian_adapter import get_obsidian
            obs = get_obsidian()
            if not obs.available:
                return

            # 检测物种标签
            species_tag = ""
            if any(kw in query for kw in ["江豚", "Neophocaena", "finless porpoise"]):
                species_tag = "江豚"
            elif "鳤" in query or "Ochetobius" in query:
                species_tag = "鳤"

            saved = 0
            for paper in papers[:3]:  # 最多保存 3 篇
                title = paper.get("title", "")
                if not title:
                    continue
                # 检查是否已存在
                existing = obs.list_literature_notes()
                safe_title = title[:60].replace("/", "-")
                if any(safe_title[:20] in e for e in existing):
                    continue
                obs.write_literature_note(paper, species_tag=species_tag)
                saved += 1

            if saved:
                logger.info(f"Auto-saved {saved} papers to Obsidian")
        except Exception as e:
            logger.debug(f"Obsidian auto-save skipped: {e}")

    def _load_domain_knowledge(self, query: str):
        """
        加载领域知识库作为 BDI Belief 上下文。

        来源:
        1. data/knowledge_base/porpoise_research_teams.md  — 研究机构/团队/近缘种
        2. Obsidian Vault — 课题组分析文档 (刘凯课题组研究方向/文献分析)
        """
        # 1. 本地知识库
        kb_paths = [
            "data/knowledge_base/porpoise_research_teams.md",
        ]
        for kb_path in kb_paths:
            try:
                from pathlib import Path
                kb = Path(kb_path)
                if kb.exists():
                    content = kb.read_text(encoding="utf-8")
                    self.bdi.belief.relevant_knowledge.append({
                        "source": kb_path,
                        "title": "江豚研究机构与近缘种知识库",
                        "content": content[:3000],
                    })
                    logger.debug(f"Loaded KB: {kb_path} ({len(content)} chars)")
            except Exception as e:
                logger.debug(f"KB load skipped: {kb_path}: {e}")

        # 2. Obsidian Vault — 课题组分析文档
        try:
            from src.integration.obsidian_adapter import get_obsidian
            obs = get_obsidian()
            if obs.available:
                obs_contexts = obs.load_domain_context(max_chars=2000)
                for ctx in obs_contexts:
                    self.bdi.belief.relevant_knowledge.append({
                        "source": ctx["source"],
                        "title": ctx["title"],
                        "content": ctx["content"],
                    })
                logger.debug(f"Loaded {len(obs_contexts)} Obsidian domain docs")
        except Exception as e:
            logger.debug(f"Obsidian domain load skipped: {e}")

    async def _try_cognitive_search(self, query: str) -> list[dict]:
        """
        尝试通过 cognitive-search-engine 搜索。

        检测物种查询 → OCR变体 + 多query并行
        通用查询 → 直接并行搜索
        """
        from src.integration.cognitive_search_adapter import (
            CognitiveSearchAdapter,
            is_species_query,
        )

        adapter = CognitiveSearchAdapter()
        if not adapter.available:
            return []

        try:
            if is_species_query(query):
                # 尝试从 query 中提取属名/种名
                import re
                latin_match = re.search(
                    r'\b([A-Z][a-z]+)\s+([a-z]+(?:\s+[a-z]+)?)\b', query
                )
                if latin_match:
                    genus = latin_match.group(1)
                    species = latin_match.group(2)
                    # 尝试检测中文名
                    chinese = ""
                    chinese_match = re.search(r'[\u4e00-\u9fff]{2,4}(?:江豚|海豚|鲸|豚)', query)
                    if chinese_match:
                        chinese = chinese_match.group(0)
                    # 物种模式: 走完整 search_rules.yaml 管线
                    # (BDI 相位选择 + 引用图遍历 + OCR 变体 + 自适应停止)
                    return adapter.search(
                        query,
                        genus=genus,
                        species=species,
                        chinese_name=chinese,
                        full_pipeline=True,  # ← search_rules.yaml 完整协议
                    )

            # 通用模式: 快速并行搜索
            return adapter.search(query, max_per_query=10)

        except Exception as e:
            logger.warning(f"cognitive-search-engine failed, falling back: {e}")
            return []
        finally:
            adapter.close()

    def _assess_quality(self, papers: list[dict]) -> list[dict]:
        """评估文献质量与相关性"""
        for paper in papers:
            score = 0

            # DOI 存在 = +20
            if paper.get("doi"):
                score += 20

            # 有摘要 = +15
            if paper.get("abstract"):
                score += 15

            # 有引用计数 = +10 (handle string/int)
            citations = paper.get("citations", 0)
            try:
                citations = int(citations)
            except (ValueError, TypeError):
                citations = 0
            if citations > 0:
                score += min(citations, 50) * 0.2

            # 近期 = +10 (handle string/int)
            year = paper.get("year")
            try:
                year = int(year) if year else 0
            except (ValueError, TypeError):
                year = 0
            if year and year >= 2020:
                score += 10
            if year and year >= 2024:
                score += 5

            # 期刊已知 = +5
            known_journals = [
                "JASA", "Marine Mammal Science", "Endangered Species Research",
                "Frontiers in Marine Science", "PLOS ONE", "Scientific Reports",
                "Journal of Mammalogy", "Bioacoustics",
            ]
            journal = paper.get("journal", "")
            if any(kj.lower() in journal.lower() for kj in known_journals):
                score += 5

            paper["quality_score"] = score
            paper["relevance"] = (
                "high" if score >= 40 else
                "medium" if score >= 20 else
                "low"
            )

        # 按质量分排序
        papers.sort(key=lambda p: p.get("quality_score", 0), reverse=True)
        return papers

    def _generate_synthesis(self, papers: list[dict]) -> str:
        """生成文献综述摘要"""
        if not papers:
            return "No relevant literature found."

        n_high = sum(1 for p in papers if p.get("relevance") == "high")
        n_total = len(papers)

        years = [p.get("year") for p in papers if p.get("year")]
        year_range = f"{min(years)}-{max(years)}" if years else "unknown"

        journals = list(set(
            p.get("journal", "") for p in papers if p.get("journal")
        ))[:5]

        return (
            f"Found {n_total} papers ({n_high} high relevance) "
            f"spanning {year_range}. "
            f"Key journals: {', '.join(journals)}."
        )

    def _search_literature(
        self, query: str, source: str = "semantic_scholar", limit: int = 10
    ) -> dict:
        """同步文献搜索 (工具注册用)"""
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 在已有 event loop 中创建 task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._multi_source_search(query)
                )
                papers = future.result(timeout=30)
        else:
            papers = asyncio.run(self._multi_source_search(query))

        return {
            "query": query,
            "source": source,
            "limit": limit,
            "results": papers[:limit],
            "total_found": len(papers),
        }

    def can_handle(self, intent: str) -> bool:
        return intent in (
            "literature_search", "literature_review",
        )
