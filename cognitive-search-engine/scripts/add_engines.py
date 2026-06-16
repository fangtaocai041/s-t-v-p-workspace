"""Add 7 new search providers to parallel_search.py + update unified_search.py registries."""
import re

# ─── 1. Read parallel_search.py ───
with open('cognitive-search-engine/src/parallel_search.py', 'r', encoding='utf-8') as f:
    ps_text = f.read()

# ─── 2. Add new provider functions BEFORE "_CN_PROVIDERS" registry ───
new_providers_code = """

# ═══════════════════════════════════════════════════════════════
# Provider: Baidu Scholar (中文)
# ═══════════════════════════════════════════════════════════════

def _search_baidu_scholar(chinese_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
    \"\"\"Search Baidu Scholar for Chinese academic papers.

    Uses xueshu.baidu.com search with site scraping.
    \"\"\"
    papers: List[Dict[str, Any]] = []
    if not chinese_name:
        return papers
    try:
        safe_q = urllib.parse.quote(chinese_name)
        url = f"https://xueshu.baidu.com/s?wd={safe_q}&rsv_bp=0&tn=SE_baiduxueshu_c1g0"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract paper entries
        entries = re.findall(
            r'<div class="result[^"]*"(.*?)</div>\\s*</div>\\s*</div>\\s*<div class="pager"',
            html, re.DOTALL
        ) or re.findall(r'<div class="sc_content"[^>]*>(.*?)</div>\\s*<!--/sc_content-->', html, re.DOTALL)
        
        if not entries:
            entries = re.findall(r'<h3[^>]*class="t"[^>]*>(.*?)</h3>', html, re.DOTALL)[:max_results]

        for i, entry in enumerate(entries[:max_results]):
            title_m = re.search(r'<a[^>]*>(.*?)</a>', entry, re.DOTALL)
            title = re.sub(r'<.*?>', '', title_m.group(1)).strip() if title_m else ""
            if not title:
                title_m2 = re.search(r'class="t"[^>]*>(.*?)</a>', entry, re.DOTALL)
                title = re.sub(r'<.*?>', '', title_m2.group(1)).strip() if title_m2 else ""

            paper = {
                "doi": "",
                "title": title,
                "authors": [],
                "year": "",
                "journal": "",
                "abstract": "",
                "source": "baidu_scholar",
                "pmid": "", "pmcid": "",
                "url": "",
                "credibility_score": 35,
                "_channel": "CN",
            }
            papers.append(paper)
    except Exception as e:
        logger.debug(f"Baidu Scholar search failed: {e}")
    return papers


# ═══════════════════════════════════════════════════════════════
# Provider: Wanfang Data (中文)
# ═══════════════════════════════════════════════════════════════

def _search_wanfang_web(chinese_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
    \"\"\"Search Wanfang Data via web interface for Chinese papers.\"\"\"
    papers: List[Dict[str, Any]] = []
    if not chinese_name:
        return papers
    try:
        safe_q = urllib.parse.quote(chinese_name)
        url = f"https://s.wanfangdata.com.cn/paper?q={safe_q}&p=1&ps={max_results}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            text = resp.read().decode("utf-8", errors="replace")

        # Extract paper titles and metadata
        titles = re.findall(r'<a[^>]*class="title"[^>]*>(.*?)</a>', text, re.DOTALL)[:max_results]
        for title_html in titles:
            title = re.sub(r'<.*?>', '', title_html).strip()
            if not title:
                continue
            paper = {
                "doi": "",
                "title": title,
                "authors": [],
                "year": "",
                "journal": "",
                "abstract": "",
                "source": "wanfang_web",
                "pmid": "", "pmcid": "",
                "url": "",
                "credibility_score": 35,
                "_channel": "CN",
            }
            papers.append(paper)
    except Exception as e:
        logger.debug(f"Wanfang web search failed: {e}")
    return papers


# ═══════════════════════════════════════════════════════════════
# Provider: CrossRef Direct API
# ═══════════════════════════════════════════════════════════════

def _search_crossref_direct(query: str, max_results: int = 15) -> List[Dict[str, Any]]:
    \"\"\"Search CrossRef REST API directly (free, no key needed).

    More flexible than the MCP article-mcp, with email-based polite pool.
    \"\"\"
    papers: List[Dict[str, Any]] = []
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "rows": min(max_results, 30),
            "sort": "relevance",
            "order": "desc",
            "mailto": "fangtaocai041@gmail.com",  # polite pool
        })
        url = f"https://api.crossref.org/works?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "ReasonixCognitiveSearch/5.8 (fangtaocai041@gmail.com)",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("message", {}).get("items", [])
        for item in items[:max_results]:
            title = (item.get("title") or [""])[0]
            if not title:
                continue
            authors = []
            for a in item.get("author", []):
                given = a.get("given", "")
                family = a.get("family", "")
                authors.append(f"{given} {family}".strip())
            doi = item.get("DOI", "")
            year = ""
            if item.get("published-print"):
                year = str(item["published-print"].get("date-parts", [[None]])[0][0] or "")
            elif item.get("published-online"):
                year = str(item["published-online"].get("date-parts", [[None]])[0][0] or "")
            journal = (item.get("container-title") or [""])[0]

            papers.append({
                "doi": doi,
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": "",
                "source": "crossref_direct",
                "pmid": "", "pmcid": "",
                "url": f"https://doi.org/{doi}" if doi else "",
                "credibility_score": 60,
            })
    except Exception as e:
        logger.debug(f"CrossRef direct search failed: {e}")
    return papers


# ═══════════════════════════════════════════════════════════════
# Provider: Semantic Scholar API
# ═══════════════════════════════════════════════════════════════

def _search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    \"\"\"Search Semantic Scholar API (free, no key for basic).\"\"\"
    papers: List[Dict[str, Any]] = []
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "limit": min(max_results, 50),
            "fields": "title,authors,year,journal,externalIds,abstract,url",
        })
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "ReasonixCognitiveSearch/5.8 (fangtaocai041@gmail.com)",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for p in data.get("data", [])[:max_results]:
            title = p.get("title", "")
            if not title:
                continue
            authors = [a.get("name", "") for a in p.get("authors", []) if a.get("name")]
            year = str(p.get("year", ""))
            journal = (p.get("journal", {}) or {}).get("name", "")
            ext_ids = p.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI", "")
            pmid = ext_ids.get("PubMed", "")

            papers.append({
                "doi": doi,
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": p.get("abstract", ""),
                "source": "semantic_scholar",
                "pmid": pmid,
                "pmcid": "",
                "url": p.get("url", f"https://doi.org/{doi}" if doi else ""),
                "credibility_score": 65,
            })
    except Exception as e:
        logger.debug(f"Semantic Scholar search failed: {e}")
    return papers


# ═══════════════════════════════════════════════════════════════
# Provider: bioRxiv / medRxiv (预印本)
# ═══════════════════════════════════════════════════════════════

def _search_biorxiv_medrxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    \"\"\"Search bioRxiv/medRxiv API for preprints.\"\"\"
    papers: List[Dict[str, Any]] = []
    try:
        for server in ["biorxiv", "medrxiv"]:
            params = urllib.parse.urlencode({"q": query})
            url = f"https://api.biorxiv.org/details/{server}/2020-01-01/2030-12-31/0/{max_results}?{params}"
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "ReasonixCognitiveSearch/5.8",
                })
                with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("collection", [])[:max_results]:
                    title = item.get("title", "")
                    if not title or query.lower() not in title.lower():
                        continue
                    papers.append({
                        "doi": item.get("doi", ""),
                        "title": title,
                        "authors": [item.get("author", "")],
                        "year": str(item.get("date", "")[:4]),
                        "journal": f"{server} preprint",
                        "abstract": item.get("abstract", ""),
                        "source": server,
                        "pmid": "", "pmcid": "",
                        "url": f"https://doi.org/{item.get('doi', '')}" if item.get('doi') else "",
                        "credibility_score": 40,
                    })
            except Exception:
                continue
    except Exception as e:
        logger.debug(f"bioRxiv/medRxiv search failed: {e}")
    return papers


# ═══════════════════════════════════════════════════════════════
# Provider: ResearchGate (web scrape)
# ═══════════════════════════════════════════════════════════════

def _search_researchgate(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    \"\"\"Search ResearchGate via public web search.

    ResearchGate has no public API, so uses Bing site: search as fallback.
    \"\"\"
    papers: List[Dict[str, Any]] = []
    try:
        safe_q = urllib.parse.quote(f"{query} site:researchgate.net/publication")
        bing_url = (
            "https://www.bing.com/search?"
            + urllib.parse.urlencode({"q": f"{query} researchgate publication", "count": max_results})
        )
        req = urllib.request.Request(bing_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        snippets = re.findall(r'<li class="b_algo"(.*?)</li>', html, re.DOTALL)
        for sn in snippets[:max_results]:
            title_m = re.search(r'<h2>.*?<a[^>]*>(.*?)</a>', sn, re.DOTALL)
            title = re.sub(r'<.*?>', '', title_m.group(1)).strip() if title_m else ""
            if not title:
                continue
            papers.append({
                "doi": "",
                "title": title,
                "authors": [],
                "year": "",
                "journal": "",
                "abstract": "",
                "source": "researchgate",
                "pmid": "", "pmcid": "",
                "url": "",
                "credibility_score": 30,
            })
    except Exception as e:
        logger.debug(f"ResearchGate search failed: {e}")
    return papers
"""

# Insert before _CN_PROVIDERS
insert_point = ps_text.find("# Provider registry\n_PROVIDERS: Dict")
ps_text = ps_text[:insert_point] + new_providers_code + ps_text[insert_point:]

# Update _PROVIDERS to add new international providers
old_providers = """_PROVIDERS: Dict[str, Tuple[Callable, int]] = {
    "pubmed": (_search_pubmed, 10),
    "europe_pmc": (_search_europe_pmc, 20),
    "crossref": (_search_crossref, 20),
    "openalex": (_search_openalex, 20),
    "arxiv": (_search_arxiv, 10),
}"""

new_providers = """_PROVIDERS: Dict[str, Tuple[Callable, int]] = {
    "pubmed": (_search_pubmed, 10),
    "europe_pmc": (_search_europe_pmc, 20),
    "crossref": (_search_crossref, 20),
    "openalex": (_search_openalex, 20),
    "arxiv": (_search_arxiv, 10),
    "crossref_direct": (_search_crossref_direct, 15),
    "semantic_scholar": (_search_semantic_scholar, 10),
    "biorxiv_medrxiv": (_search_biorxiv_medrxiv, 10),
    "researchgate": (_search_researchgate, 10),
}"""

ps_text = ps_text.replace(old_providers, new_providers)

# Update _CN_PROVIDERS
old_cn = """_CN_PROVIDERS: Dict[str, Tuple[Callable, int]] = {
    "cnki_web": (_search_cnki_web, 10),
}"""

new_cn = """_CN_PROVIDERS: Dict[str, Tuple[Callable, int]] = {
    "cnki_web": (_search_cnki_web, 10),
    "baidu_scholar": (_search_baidu_scholar, 10),
    "wanfang_web": (_search_wanfang_web, 10),
}"""

ps_text = ps_text.replace(old_cn, new_cn)

with open('cognitive-search-engine/src/parallel_search.py', 'w', encoding='utf-8') as f:
    f.write(ps_text)
print("✅ parallel_search.py: 新增 7 个 provider + 更新注册表")

# ─── 3. Update unified_search.py ENGINE_REGISTRY ───
with open('cognitive-search-engine/src/unified_search.py', 'r', encoding='utf-8') as f:
    us_text = f.read()

old_registry = """ENGINE_REGISTRY = {
    # 学术搜索 (Priority 1-3)
    "scholar_graph":    {"tool": "scholar_search_literature_graph", "category": "academic", "priority": 1},
    "scholar_keywords": {"tool": "scholar_search_google_scholar_key_words", "category": "academic", "priority": 1},
    "scholar_advanced": {"tool": "scholar_search_google_scholar_advanced", "category": "academic", "priority": 2},
    "ncbi_esearch":     {"tool": "ncbi_ncbi_esearch", "category": "academic", "priority": 1},
    "crossref_article": {"tool": "article_search_literature", "category": "academic", "priority": 2},
    "scholarly_multi":  {"tool": "scholarly_research_search", "category": "academic", "priority": 3},
    # 语义/深度搜索 (Priority 4-5)
    "tavily_search":    {"tool": "tavily_tavily_search", "category": "semantic", "priority": 4},
    "tavily_research":  {"tool": "tavily_tavily_research", "category": "semantic", "priority": 5},
    "exa_search":       {"tool": "exa_web_search_exa", "category": "semantic", "priority": 4},
    # 内置搜索 (Priority 6)
    "web_search":       {"tool": "web_search", "category": "web", "priority": 6},
    # 引用/关系 (Priority 7)
    "references":       {"tool": "article_get_references", "category": "graph", "priority": 7},
    "relations":        {"tool": "article_get_literature_relations", "category": "graph", "priority": 7},
}"""

new_registry = """ENGINE_REGISTRY = {
    # 学术搜索 (Priority 1-3)
    "scholar_graph":    {"tool": "scholar_search_literature_graph", "category": "academic", "priority": 1},
    "scholar_keywords": {"tool": "scholar_search_google_scholar_key_words", "category": "academic", "priority": 1},
    "scholar_advanced": {"tool": "scholar_search_google_scholar_advanced", "category": "academic", "priority": 2},
    "ncbi_esearch":     {"tool": "ncbi_ncbi_esearch", "category": "academic", "priority": 1},
    "crossref_article": {"tool": "article_search_literature", "category": "academic", "priority": 2},
    "crossref_direct":  {"tool": "crossref_direct", "category": "academic", "priority": 2},
    "scholarly_multi":  {"tool": "scholarly_research_search", "category": "academic", "priority": 3},
    "semantic_scholar": {"tool": "semantic_scholar", "category": "academic", "priority": 2},
    # 中文学术搜索 (Priority 2)
    "baidu_scholar":    {"tool": "baidu_scholar", "category": "chinese", "priority": 2},
    "cnki_web":         {"tool": "cnki_web", "category": "chinese", "priority": 2},
    "wanfang_web":      {"tool": "wanfang_web", "category": "chinese", "priority": 3},
    # 预印本 (Priority 3)
    "biorxiv_medrxiv":  {"tool": "biorxiv_medrxiv", "category": "preprint", "priority": 3},
    # 语义/深度搜索 (Priority 4-5)
    "tavily_search":    {"tool": "tavily_tavily_search", "category": "semantic", "priority": 4},
    "tavily_research":  {"tool": "tavily_tavily_research", "category": "semantic", "priority": 5},
    "exa_search":       {"tool": "exa_web_search_exa", "category": "semantic", "priority": 4},
    # 全文/社交搜索 (Priority 5)
    "researchgate":     {"tool": "researchgate", "category": "fulltext", "priority": 5},
    # 内置搜索 (Priority 6)
    "web_search":       {"tool": "web_search", "category": "web", "priority": 6},
    # 引用/关系 (Priority 7)
    "references":       {"tool": "article_get_references", "category": "graph", "priority": 7},
    "relations":        {"tool": "article_get_literature_relations", "category": "graph", "priority": 7},
}"""

us_text = us_text.replace(old_registry, new_registry)

# Update ENGINE_GROUPS
old_groups = """ENGINE_GROUPS = {
    "quick":    ["scholar_graph", "ncbi_esearch", "web_search"],
    "standard": ["scholar_graph", "ncbi_esearch", "crossref_article", "web_search", "tavily_search"],
    "full":     ["scholar_graph", "ncbi_esearch", "crossref_article", "scholarly_multi",
                 "tavily_search", "exa_search", "web_search"],
    "chinese":  ["scholar_graph", "ncbi_esearch", "web_search"]"""

new_groups = """ENGINE_GROUPS = {
    "quick":    ["scholar_graph", "ncbi_esearch", "web_search"],
    "standard": ["scholar_graph", "ncbi_esearch", "crossref_article", "scholarly_multi",
                 "tavily_search", "web_search"],
    "full":     ["scholar_graph", "ncbi_esearch", "crossref_article", "crossref_direct",
                 "scholarly_multi", "semantic_scholar", "tavily_search", "tavily_research",
                 "exa_search", "baidu_scholar", "cnki_web", "wanfang_web",
                 "biorxiv_medrxiv", "researchgate", "web_search"],
    "chinese":  ["scholar_graph", "ncbi_esearch", "baidu_scholar", "cnki_web", "wanfang_web",
                 "crossref_article", "web_search"]"""

us_text = us_text.replace(old_groups, new_groups)

with open('cognitive-search-engine/src/unified_search.py', 'w', encoding='utf-8') as f:
    f.write(us_text)
print("✅ unified_search.py: ENGINE_REGISTRY 19 引擎 + ENGINE_GROUPS 重配")

# ─── 4. Verify ───
print("\n=== 验证 ===")
# Check imports
errs = []
try:
    import ast
    ast.parse(open('cognitive-search-engine/src/parallel_search.py').read())
    print("  ✅ parallel_search.py 语法正确")
except SyntaxError as e:
    errs.append(f"parallel_search.py: {e}")

try:
    ast.parse(open('cognitive-search-engine/src/unified_search.py').read())
    print("  ✅ unified_search.py 语法正确")
except SyntaxError as e:
    errs.append(f"unified_search.py: {e}")

# Check provider count
with open('cognitive-search-engine/src/parallel_search.py') as f:
    txt = f.read()
providers = re.findall(r'"_PROVIDERS.*?_PROVIDERS:.*?\{(.*?)\}', txt, re.DOTALL)
cn_providers = re.findall(r'"_CN_PROVIDERS.*?_CN_PROVIDERS:.*?\{(.*?)\}', txt, re.DOTALL)
if providers:
    count = providers[0].count('"_')
    print(f"  ✅ _PROVIDERS: {count} 个国际源")
if cn_providers:
    count2 = cn_providers[0].count('"_')
    print(f"  ✅ _CN_PROVIDERS: {count2} 个中文源")

# Check registry size
with open('cognitive-search-engine/src/unified_search.py') as f:
    txt = f.read()
registry_entries = txt.count('"tool"')
print(f"  ✅ ENGINE_REGISTRY: {registry_entries} 个引擎注册")

if errs:
    print(f"\n❌ 错误: {errs}")
else:
    print("\n✅ 全部验证通过!")
