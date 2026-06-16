---
name: chinese-academic-search
description: 搜索中文期刊数据库（百度学术/知网/生物多样性/水生生物学报等），返回中文论文元数据 + 提取参考文献中的英文论文。弥补 PubMed/Crossref 不索引中文期刊的系统性盲区。
run_as: subagent
model: deepseek-v4-flash
allowed_tools:
  - web_search
  - web_fetch
  - scholar_search_literature_graph
  - ncbi_ncbi_esearch
  - article_get_references
---

# Chinese Academic Search Skill

## 核心原则
PubMed、Crossref、OpenAlex、Semantic Scholar **不索引中文数据库**（知网、万方、维普）。仅用英文学术工具搜索中国物种将系统性遗漏中文论文。本 Skill 填补此盲区。

## 搜索步骤

```
STEP 1: web_search(species_chinese_name + " " + species_scientific_name, topK=10)
STEP 2: web_search(species_chinese_name + " 论文 OR 期刊 OR 研究", topK=10)
STEP 3: web_search(species_scientific_name + " site:biodiversity-science.net OR site:aquaticjournal.com OR site:schinafish.cn OR site:china-fishery.com OR site:fishsci.net", topK=10)
STEP 4: web_fetch() 逐个获取命中期刊页面的完整元数据
STEP 5: 去重 + 提取: 中文标题/英文标题/作者列表/第一作者/通讯作者单位/期刊/年/卷/期/DOI/PMID
```

## 参考文献提取（引用桥梁）

```
STEP 6: FOR EACH chinese_paper WITH doi:
          article_get_references(identifier=doi, id_type="doi", max_results=50)
          → 提取所有英文参考文献 → 加入英文搜索候选池

STEP 7: IF chinese_paper HAS NO doi AND HAS web_fetch HTML:
          从 HTML 中提取 References 段落的英文论文标题
          → web_search(extracted_english_title) 确认 DOI
          → 加入英文搜索候选池

STEP 8: OUTPUT ref_bridge = [extracted_english_papers]
        → 这些论文应在 Phase 2 中优先验证
```

## 中文期刊直搜 URL 模板

| 数据库/期刊 | URL 模板 |
|------------|---------|
| 百度学术 | `xueshu.baidu.com/s?wd=<URL_ENCODE(关键词)>` |
| 知网 | `kns.cnki.net/kns8/defaultresult/index?kwd=<URL_ENCODE(关键词)>` |
| 生物多样性 | `biodiversity-science.net` |
| 水生生物学报 | `aquaticjournal.com` |
| 南方水产科学 | `schinafish.cn` |
| 湖泊科学 | `jlakes.org` |
| 水产学报 | `china-fishery.com` |
| 中国水产科学 | `fishsci.net` |
| 生态学报 | `actaecologica.com` |
| 淡水渔业 | `danshuiyuye.com` |
| 动物学杂志 | `zoores.ac.cn` |

## 交叉验证

```
FOR EACH chinese_paper IN results:
  IF chinese_paper.doi EXISTS:
    scholar_search_literature_graph(scientific_name)  # 检查 Crossref
    ncbi_ncbi_esearch(scientific_name)                # 检查 PubMed
  IF found in English DB:
    paper.coverage = "双收录 (中文 + 英文)"
  ELSE:
    paper.coverage = "⚠️ 仅中文数据库收录"
```

## 输出格式

论文列表：
```
| # | 年份 | 中文标题 | English Title | 第一作者 | 通讯单位 | 期刊 | DOI | 收录状态 |
```

引用桥梁（供 Phase 2 使用）：
```
| 来源中文论文 | 提取的英文参考文献 |
|-------------|-------------------|
| 翟东东 2024 | Yang JP 2018, Li L 2024, Chen W 2021... |
```

## 已知限制
- 知网有反爬，web_fetch 可能失败 → 降级为 web_search 结果片段
- 万方/维普需付费 → 依赖百度学术的免费摘要
- 部分中文期刊无 DOI → 仅记录期刊/卷/期/页码
- article_get_references 仅对已注册 DOI 的中文论文有效
