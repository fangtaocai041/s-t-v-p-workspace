---
name: academic-species-search
description: 学术物种文献深度检索：PubMed E-utilities API → NCBI → Crossref → 引用回溯，返回论文数/作者/单位/论文名/DOI
runAs: subagent
allowed-tools: web_fetch
---
# 学术物种文献深度检索协议 v2.0（快模式）

## 核心原则
用 **E-utilities JSON API** 替代 HTML 页面抓取——每次调用 2-5 秒，3 次调用即可拿到全部数据。

## 3 步快速协议（不是 7 步）

### Step 1: PubMed ESearch + ESummary（一步完成）
```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={学名}&retmax=50&retmode=json"
```
返回 JSON，提取 `idlist[]`（论文 PMID）。

然后一步拉所有论文元数据：
```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={逗号分隔的PMID列表}&retmode=json"
```
返回 JSON，提取每篇的：`title`、`authors[].name`、`source`（期刊）、`pubdate`、`epubdate`、`articleids[].value`（DOI）。

### Step 2: PubMed EFetch XML（拿单位——关键区别）
```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={PMID}&retmode=xml&rettype=abstract"
```
从 XML 中提取:
- `Author/AffiliationInfo/Affiliation` — **精确单位，实验室级别**
- `Abstract/AbstractText` — 摘要
- `ReferenceList/Reference` — 引用列表（用于 Step 3）

### Step 3: 引用回溯（发现遗漏的中文论文）
对 Step 2 获取的 References 逐一检查：
- 如果标题含 "Ochetobius" 或 "鳤"
- 提取：作者、期刊、年份、DOI

### 输出

#### 专项研究论文（鳤为核心研究对象）
| 序号 | 论文名 | 期刊 | 年份 | 作者 | 单位 | DOI |

#### 附带提及论文（鳤不是核心）
单独列出并标注。

#### 置信度声明
- [确认] = 从 PubMed API Affiliation 字段直接提取
- [需核实] = 标记
