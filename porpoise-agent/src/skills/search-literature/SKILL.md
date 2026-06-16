# Skill: search-literature

## Signature
`search_literature(query: str, sources: list[str] = ["pubmed","crossref","openalex"], max_results: int = 20, year_range: tuple[int,int] = (0,9999)) → list[Paper]`

## Trigger
```python
WHEN intent IN [LITERATURE_SEARCH, LITERATURE_REVIEW]
  OR query MATCHES r"(搜索|检索|找文献|文献|论文|综述|search|find paper|review)"
THEN activate()
```

## Input
```yaml
REQUIRED:
  query: str                          # 研究问题或关键词
OPTIONAL:
  sources: list[str] = ["pubmed","crossref","openalex"]
  max_results: int = 20
  year_from: int = 0
  year_to: int = 9999
```

## Steps
```python
# 1. Task decomposition
sub_queries: list[str] = decompose(query, n=[3,5])

# 2. Keyword expansion
keywords_zh: list[str] = extract_keywords(query, lang="zh")
keywords_en: list[str] = extract_keywords(query, lang="en")
expanded_queries = merge(sub_queries, keywords_zh, keywords_en)

# 3. Parallel search
results: list[SearchResult]
PARALLEL:
    results += pubmed.search(q, limit=max_results)     FOR EACH q IN expanded_queries
    results += crossref.search(q, rows=max_results)    FOR EACH q IN expanded_queries
    results += openalex.search(q, per_page=max_results) FOR EACH q IN expanded_queries

# 4. Relevance filtering
FOR EACH paper IN results:
    paper.relevance = classify(paper.title, paper.abstract)
    # relevance ∈ {high: score≥40, medium: 20≤score<40, low: score<20}
    # score = 20×has_doi + 15×has_abstract + min(citations,50)×0.2 + 10×(year≥2020) + 5×known_journal

# 5. DOI deduplication
papers = deduplicate(results, primary_key="doi", secondary_key="title[:80]")

# 6. Deep analysis (high relevance only)
FOR EACH paper IN papers WHERE paper.relevance == "high":
    paper.key_findings = extract_findings(paper.abstract)
    paper.methods = extract_methods(paper.abstract)
    paper.limitations = detect_limitations(paper.abstract)

# 7. Synthesis
synthesis: str = summarize(papers, max_tokens=500)
gaps: list[str] = identify_gaps(papers, min_papers_per_topic=3)
```

## Decision Points
```python
IF len(filter(papers, relevance="high")) < 5
THEN expand_query_terms(query, step=+2_synonyms)

IF len(papers) > 50
THEN narrow_by_year(papers, year=[max(year_from, current_year-5), year_to])

IF confidence_divergence(papers) > 0.3
THEN flag_for_manual_review(papers)

IF len(papers) >= config.cognitive.react_loop.min_papers_satisfice  # default=8
THEN STOP
```

## Output Schema
```json
{
  "research_question": "string",
  "sub_questions": ["string"],
  "papers": [{
    "title": "string",
    "authors": ["string"],
    "year": 2024,
    "journal": "string",
    "doi": "string",
    "relevance": "high|medium|low",
    "quality_score": 0-100,
    "key_findings": ["string"],
    "methods": ["string"],
    "limitations": ["string"]
  }],
  "synthesis": "string",
  "research_gaps": ["string"],
  "n_total": 0,
  "n_high": 0,
  "sources_used": ["string"]
}
```

## Keywords Mapping
```yaml
cetacean:
  zh: [江豚, 鼠海豚, 鲸, 豚, 白鱀豚, 中华白海豚]
  en: [finless porpoise, Neophocaena, Phocoenidae, cetacean, dolphin, whale]
acoustic:
  zh: [声学, 回声定位, 被动声学, 脉冲, click]
  en: [NBHF, narrow-band high-frequency, echolocation, PAM, passive acoustic]
ecology:
  zh: [丰度, 密度, 分布, 栖息地, 种群, 食性]
  en: [abundance, density, distribution, habitat, population, diet]
conservation:
  zh: [保护, 威胁, 评估, IUCN, 极危, 迁地保护]
  en: [conservation, threat, assessment, critically endangered, ex situ]
```

## References
- Akamatsu et al. (2005) JASA — NBHF click source level
- Kimura et al. (2010) JASA — A-tag density estimation
- Wang et al. (2015) Endang Species Res — Yangtze PAM monitoring
- Zhou et al. (2021) Front Mar Sci — SoundTrap click classification
- cognitive-search-engine v5.0 — Hub-and-Spoke search protocol
