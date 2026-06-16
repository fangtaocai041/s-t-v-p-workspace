---
name: paywall-bypass
description: 绕过期刊付费墙获取论文全文：预印本→机构库→ResearchGate→数据附件→新闻稿，多路径并行尝试
---

# Paywall Bypass — 付费墙论文全文获取

## 触发条件
`web_fetch` 对目标期刊返回 403 / login-wall / paywall 时自动执行。

## 执行步骤（按成功率从高到低，并行搜索）

### Step 1 — 并行搜索预印本 + 作者上传 + 机构库
```
PARALLEL:
  web_search("{paper_title} preprint bioRxiv OR ResearchSquare OR arXiv", topK=5)
  web_search("{paper_title} ResearchGate OR Academia.edu", topK=5)
  web_search("{paper_title} PDF full text free", topK=5)
```

### Step 2 — Google Scholar 找 "All N versions"
```
web_search("site:scholar.google.com {paper_title}", topK=3)
→ web_fetch 第一条结果 → 点击 "All N versions" → 逐个尝试
```
如果 web_fetch Google Scholar 被屏蔽，改用：
```
scholar_search_literature_graph("{paper_title}", limit=5)
→ 从结果中提取 paperId / doi → 尝试 scholar 侧 PDF
```

### Step 3 — 数据附件 / 补充材料
```
IF DOI available:
  web_search("{doi} Dryad OR Figshare OR Zenodo OR supplementary", topK=5)
  web_fetch("https://datadryad.org/dataset/doi:{doi}")
```

### Step 4 — 中文单位新闻稿（中国作者论文特化）
```
web_search("{first_author_cn_name} {keyword_from_title} 新闻 OR 进展 OR 研究", topK=5)
→ 中文新闻稿通常保留更多细节，足以替代原文
```

### Step 5 — PubMed Central / Europe PMC 免费全文
```
ncbi_ncbi_esearch("{title}", maxResults=5)
→ ncbi_ncbi_efetch(pmid) → 提取 affiliations + abstract
article_get_article_details(pmcid) → 如果有 PMCID 直接拿全文
```

### Step 6 — 配套评论文章
```
web_search("{paper_title} commentary OR perspective OR editorial OR news views", topK=5)
→ 评论文章常总结原文核心发现，比原文更精炼
```

## 策略矩阵（参考）

| 路径 | 成功率 | 适用场景 |
|------|:------:|----------|
| PubMed Central | 高 | NIH 资助论文，6-12月后免费 |
| 预印本 (bioRxiv/ResearchSquare/arXiv) | 中高 | 近两年论文常有 |
| ResearchGate / Academia.edu | 中 | 作者主动上传 |
| 机构知识库 (CAS IR / 高校图书馆) | 中 | 中科院/高校论文 |
| Dryad / Figshare / Zenodo | 中 | 含补充材料，偶含全文 |
| 中文新闻稿 | 高 | 中国单位的论文比原文更详细 |
| Google Scholar "All N versions" | 低 | 偶尔有惊喜 |
| 配套评论 (News & Views / Perspective) | 中 | 比原文更精炼 |
| Unpaywall / Open Access Button | 中 | doi.org 后加 `?variant=oa` |
| 直接联系通讯作者 | 慢但可靠 | 最后的兜底 |

## 输出格式

每个尝试过的路径标注结果：
```
| 路径 | 状态 | 结果 |
|------|:----:|------|
| bioRxiv 预印本 | ❌ 未找到 | — |
| ResearchGate | ✅ 成功 | PDF 链接: https://... |
```

## 已知限制
- Science / Nature / Cell 系列付费墙最严，预印本是最优解
- Google Scholar 有反爬，可能返回空
- 部分中国作者论文无预印本习惯 → 中文新闻稿路径更有效
- 刚发表 (< 1 周) 的论文所有路径都低 → 等一周再试
