---
name: unified-species-search
version: "3.0.0"
last_updated: "2026-06-06"
description: 统一物种文献搜索——NCBI E-utilities API 直搜 + 引用回溯 + 拼写变体 + 中文回溯。3 步出结果，快速精确。
runAs: subagent
allowed-tools: web_fetch, web_search, read_file
---
# Unified Species Search v3.0

> **核心理念**：用 API 直调替代网页抓取，用引用回溯弥补中文文献盲区，用预计算变体覆盖拼写错误。

## 0. 前处理（读配置 + 解析参数）

### 0.1 读取物种变体配置
```
read_file "config/species_variants.yaml"
```
提取该物种的：`known_misspellings[]`, `taxonomic_synonyms[]`, `chinese_aliases[]`, `target_journals[]`。

### 0.2 解析 arguments
收到格式如 `"中文名：鳤，学名：Ochetobius elongatus"`，解析出 `chinese_name` 和 `scientific_name`。

### 0.3 构建搜索词列表
```
search_queries = [scientific_name] + known_misspellings + taxonomic_synonyms + chinese_aliases
# 例：Ochetobius elongatus, Ochetobibus elongatus, Ochetobius elongates,
#      Luciobrama macrocephalus, 鳤, 鳤鱼, 金刀鱼
```

### 0.4 预估文献量 + 自适应策略
```
# 先用精确学名搜一次，获取 count
count = ncbi_esearch(scientific_name).total_count
IF count < 20: mode = "exhaustive"     # 穷举，100% recall
ELSE IF count 20-200: mode = "classified"  # 先分类
ELSE: mode = "satisficing"             # 满意即止
```

## 1. PubMed ESearch（搜到什么）

```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={scientific_name}&retmax=50&retmode=json"
```

提取：`total_count`（总论文数）、`idlist[]`（PMID 列表）。

同时搜变体：
```
FOR EACH variant != scientific_name:
  web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={variant}&retmax=20&retmode=json"
  MERGE idlist (去重)
```

## 2. ESummary（拉元数据——标题/作者/期刊/DOI）

```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={逗号分隔PMID}&retmode=json"
```

对每篇论文提取：
- `title` — 论文标题（判断是否鳤核心对象）
- `authors[].name` — 作者
- `source` — 期刊名
- `pubdate` / `epubdate` — 年份
- `doi` — DOI（从 articleids 中找 idtype="doi"）

## 3. EFetch（拿单位——这是关键区别）

对每篇明显与鳤相关的论文：
```
web_fetch "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={PMID}&retmode=xml&rettype=abstract"
```

从 XML 提取：
- `Author/AffiliationInfo/Affiliation` — **精确单位，实验室级别**
- `Abstract/AbstractText` — 摘要前 300 字
- `ReferenceList/Reference[ArticleTitle 含 Ochetob/鳤]` — 引用回溯

## 4. 引用回溯（发现中文论文的关键）

对已找到论文的 `ReferenceList`，逐一检查：
```
IF ref.title 含 "Ochetob" OR ref.title 含 "鳤":
  提取: ref.title, ref.journal, ref.year, ref.doi
  标记来源: [从{PMID}引用回溯发现]
```

## 5. 分类输出

### 专项研究论文（鳤为第一/正标题核心对象）
| 序号 | 论文名 | 期刊 | 年份 | 作者 | 单位 | DOI |

### 附带提及论文（鳤在大型调查中顺带记录）
单独列出。

### 置信度标注
- ✅ = 从 PubMed Affiliation 直接提取
- 📎 = 从引用回溯发现
- ❓ = 需人工核实

## 关键提示
- **单位不要猜** — 只从 EFetch XML 的 Affiliation 字段提取
- **拼写变体** — Ochetobius ≠ Ochetobibus，必须同时搜两者（从 `config/species_variants.yaml` 加载）
- **分类学异名** — Luciobrama macrocephalus 曾为鳤的同义名，必须同步搜索
- **引用回溯** — 中文论文不在 PubMed 中，但会被英文论文引用，从 References 抓
- **分类标准** — 正标题含 Ochetobius/鳤/Luciobrama = 专项；仅材料中出现 = 附带提及
- **置信度标注** — 每条记录标注来源：✅ PubMed Affiliation / ⚠️ 引用回溯 / ❓ 需核实
