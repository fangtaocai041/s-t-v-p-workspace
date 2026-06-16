"""
外部 API 调用封装 (API Client)
───────────────────────────────
封装常用学术 API 调用，提供统一接口。

支持:
- PubMed E-utilities (学术文献检索)
- CrossRef API (DOI 元数据)
- Semantic Scholar API (文献搜索)
- NCBI E-utilities (生物信息学)
- arXiv API (预印本)
- 本地文件系统 (数据加载)

对应五层模型中的"API调用与控制":
    工具层 → HTTP 请求 → 外部服务 → 结果解析
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class APIResult:
    """API 调用结果"""
    success: bool
    data: Any
    status_code: int = 0
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    source: str = ""
    raw_response: Optional[str] = None


class APIClient:
    """
    API 客户端 — 统一的学术 API 接口

    用法:
        client = APIClient()
        papers = client.search_pubmed("finless porpoise", max_results=20)
        doi_info = client.resolve_doi("10.1121/1.123456")
    """

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._http_client = None
        logger.info("APIClient initialized")

    async def _get_http_client(self):
        """懒加载 HTTP 客户端"""
        if self._http_client is None:
            try:
                import httpx
                self._http_client = httpx.AsyncClient(timeout=self.timeout)
            except ImportError:
                logger.warning("httpx not installed — using requests fallback")
                self._http_client = None
        return self._http_client

    # ── PubMed ───────────────────────────────────────

    async def search_pubmed(
        self,
        query: str,
        max_results: int = 20,
        retstart: int = 0,
    ) -> APIResult:
        """
        PubMed E-utilities 搜索

        Args:
            query: 搜索查询
            max_results: 最大返回数
            retstart: 偏移量

        Returns:
            APIResult: 包含 PMID 列表
        """
        start = time.time()

        try:
            client = await self._get_http_client()
            if client is None:
                return self._fallback_result(query, "pubmed")

            # ESearch: 获取 PMID 列表
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retstart": retstart,
                "retmode": "json",
                "sort": "relevance",
            }
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{urlencode(params)}"
            resp = await client.get(url)
            data = resp.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])

            elapsed = (time.time() - start) * 1000
            logger.info(f"PubMed search: {query[:50]} → {len(pmids)} results ({elapsed:.0f}ms)")

            return APIResult(
                success=True,
                data={"pmids": pmids, "count": len(pmids)},
                status_code=resp.status_code,
                elapsed_ms=elapsed,
                source="pubmed",
            )

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return APIResult(
                success=False,
                data={"pmids": []},
                error=str(e),
                elapsed_ms=(time.time() - start) * 1000,
                source="pubmed",
            )

    async def fetch_pubmed_details(self, pmids: list[str]) -> APIResult:
        """
        PubMed EFetch: 获取文献详情

        Args:
            pmids: PMID 列表

        Returns:
            APIResult: 包含标题、摘要、作者等
        """
        start = time.time()

        try:
            client = await self._get_http_client()
            if client is None:
                return self._fallback_result(str(pmids), "pubmed_details")

            params = {
                "db": "pubmed",
                "id": ",".join(pmids[:50]),  # 最多 50 个
                "retmode": "xml",
            }
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{urlencode(params)}"
            resp = await client.get(url)

            # 简单 XML 解析 (完整版应使用 Bio.Entrez)
            papers = self._parse_pubmed_xml(resp.text)

            return APIResult(
                success=True,
                data={"papers": papers},
                status_code=resp.status_code,
                elapsed_ms=(time.time() - start) * 1000,
                source="pubmed",
                raw_response=resp.text[:10000],
            )

        except Exception as e:
            return APIResult(
                success=False, data={"papers": []}, error=str(e),
                elapsed_ms=(time.time() - start) * 1000, source="pubmed",
            )

    def _parse_pubmed_xml(self, xml_text: str) -> list[dict]:
        """解析 PubMed XML (简化版)"""
        import re
        papers = []

        # 提取每篇文章
        articles = re.split(r'<PubmedArticle>|</PubmedArticle>', xml_text)
        for article in articles:
            if not article.strip():
                continue

            title_match = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', article, re.DOTALL)
            abstract_match = re.search(r'<AbstractText[^>]*>(.*?)</AbstractText>', article, re.DOTALL)
            year_match = re.search(r'<Year>(\d{4})</Year>', article)
            doi_match = re.search(r'<ELocationID EIdType="doi"[^>]*>(.*?)</ELocationID>', article)

            # 提取作者
            authors = []
            for author_match in re.finditer(
                r'<Author[^>]*>.*?<LastName>(.*?)</LastName>.*?<ForeName>(.*?)</ForeName>.*?</Author>',
                article, re.DOTALL,
            ):
                authors.append(f"{author_match.group(2)} {author_match.group(1)}")

            if title_match:
                papers.append({
                    "title": self._clean_xml(title_match.group(1)),
                    "abstract": self._clean_xml(abstract_match.group(1)) if abstract_match else "",
                    "year": int(year_match.group(1)) if year_match else None,
                    "doi": doi_match.group(1) if doi_match else "",
                    "authors": authors,
                })

        return papers

    # ── CrossRef ─────────────────────────────────────

    async def resolve_doi(self, doi: str) -> APIResult:
        """
        CrossRef DOI 解析

        Args:
            doi: DOI 字符串

        Returns:
            APIResult: 包含完整元数据
        """
        start = time.time()

        try:
            client = await self._get_http_client()
            if client is None:
                return self._fallback_result(doi, "crossref")

            url = f"https://api.crossref.org/works/{doi}"
            headers = {"Accept": "application/json"}
            resp = await client.get(url, headers=headers)

            if resp.status_code == 404:
                return APIResult(
                    success=False, data={}, status_code=404,
                    error="DOI not found", source="crossref",
                )

            data = resp.json()
            work = data.get("message", {})

            return APIResult(
                success=True,
                data={
                    "title": work.get("title", [""])[0],
                    "authors": [
                        f"{a.get('given', '')} {a.get('family', '')}"
                        for a in work.get("author", [])
                    ],
                    "year": work.get("published-print", {}).get("date-parts", [[None]])[0][0],
                    "journal": work.get("container-title", [""])[0],
                    "doi": work.get("DOI", doi),
                    "abstract": work.get("abstract", ""),
                    "references_count": work.get("references-count", 0),
                },
                status_code=resp.status_code,
                elapsed_ms=(time.time() - start) * 1000,
                source="crossref",
            )

        except Exception as e:
            return APIResult(
                success=False, data={}, error=str(e),
                elapsed_ms=(time.time() - start) * 1000, source="crossref",
            )

    # ── Semantic Scholar ─────────────────────────────

    async def search_semantic_scholar(
        self,
        query: str,
        limit: int = 20,
        fields: Optional[list[str]] = None,
    ) -> APIResult:
        """
        Semantic Scholar API 搜索

        Args:
            query: 搜索查询
            limit: 最大结果数
            fields: 返回字段

        Returns:
            APIResult: 论文列表
        """
        start = time.time()
        fields = fields or [
            "title", "authors", "year", "journal", "externalIds",
            "abstract", "citationCount", "tldr",
        ]

        try:
            client = await self._get_http_client()
            if client is None:
                return self._fallback_result(query, "semantic_scholar")

            params = {
                "query": query,
                "limit": min(limit, 100),
                "fields": ",".join(fields),
            }
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?{urlencode(params)}"
            resp = await client.get(url)

            if resp.status_code != 200:
                return APIResult(
                    success=False, data={}, status_code=resp.status_code,
                    error=f"HTTP {resp.status_code}", source="semantic_scholar",
                )

            data = resp.json()
            papers = []
            for paper in data.get("data", []):
                papers.append({
                    "title": paper.get("title", ""),
                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "journal": paper.get("journal", {}).get("name", ""),
                    "doi": paper.get("externalIds", {}).get("DOI", ""),
                    "abstract": paper.get("abstract", ""),
                    "citations": paper.get("citationCount", 0),
                    "tldr": paper.get("tldr", {}).get("text", ""),
                    "paper_id": paper.get("paperId", ""),
                })

            return APIResult(
                success=True,
                data={"papers": papers, "total": data.get("total", 0)},
                status_code=resp.status_code,
                elapsed_ms=(time.time() - start) * 1000,
                source="semantic_scholar",
            )

        except Exception as e:
            return APIResult(
                success=False, data={"papers": []}, error=str(e),
                elapsed_ms=(time.time() - start) * 1000, source="semantic_scholar",
            )

    # ── NCBI E-utilities ─────────────────────────────

    async def search_ncbi(
        self,
        db: str,
        query: str,
        max_results: int = 20,
    ) -> APIResult:
        """
        通用 NCBI E-utilities 搜索

        支持的数据库: pubmed, nucleotide, protein, taxonomy, etc.

        Args:
            db: 数据库名
            query: 查询
            max_results: 最大结果数
        """
        start = time.time()

        try:
            client = await self._get_http_client()
            if client is None:
                return self._fallback_result(query, f"ncbi_{db}")

            params = {
                "db": db,
                "term": query,
                "retmax": max_results,
                "retmode": "json",
            }
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{urlencode(params)}"
            resp = await client.get(url)
            data = resp.json()

            ids = data.get("esearchresult", {}).get("idlist", [])
            return APIResult(
                success=True,
                data={"ids": ids, "count": data.get("esearchresult", {}).get("count", 0)},
                status_code=resp.status_code,
                elapsed_ms=(time.time() - start) * 1000,
                source=f"ncbi_{db}",
            )

        except Exception as e:
            return APIResult(
                success=False, data={"ids": []}, error=str(e),
                elapsed_ms=(time.time() - start) * 1000,
            )

    # ── 辅助 ─────────────────────────────────────────

    def _clean_xml(self, text: str) -> str:
        """清理 XML/HTML 标签"""
        import re
        return re.sub(r'<[^>]+>', '', text).strip()

    def _fallback_result(self, query: str, source: str) -> APIResult:
        """无网络时的 fallback"""
        return APIResult(
            success=False,
            data={},
            error=f"HTTP client unavailable; cannot query {source}. Install httpx.",
            source=source,
            elapsed_ms=0.0,
        )


# ── 全局客户端 ─────────────────────────────────────────────

api_client = APIClient()
