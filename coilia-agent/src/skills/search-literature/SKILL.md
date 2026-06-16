# Search Literature — 刀鲚文献检索 (P₂)

> **参考脚本**: `scripts/literature_search.py`
> **角色**: P₂ 刀鲚专研
> **搜索协议**: [Unified Search Protocol v1.0](../../cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md)
> **搜索执行**: cognitive-search-engine (Multi-engine: PubMed/Google Scholar/CNKI/万方/百度学术)
> **本文件定义**: 物种约束 + 输出格式

## 一、搜索流程

P₂ 的搜索流程与 D:\Reasonix 层 **Unified Search Protocol** 完全一致，
唯一的区别是物种约束为 **Coilia nasus (刀鲚/长颌鲚/长江刀鱼)**。

### Step 1: 精确名搜索 (Primary)

```
PARALLEL:
  scholar_search("Coilia nasus", limit=15)
  ncbi_esearch("Coilia nasus", maxResults=20)
  web_search("刀鲚 论文 site:cnki.net OR site:waterbiol.com")
```

### Step 2: 宽网搜索 (Secondary — 补漏)

```
PARALLEL:
  web_search("Coilia nasus Yangtze migration otolith 2024 2025 2026")
  scholar_search("Yangtze fishing ban Coilia nasus", limit=5)
```

### Step 3: OCR 变体搜索 (Safety net)

```
FOR EACH variant IN ["Coilia nasis", "Coilia nasua", "Coilia nasas",
                     "Coilia ectenes", "Coilia brachygnathus"]:
  scholar_search(variant, limit=3)
```

### Step 4-6: 合并去重 → 分类 → 输出

同 Unified Search Protocol。

## 二、P₂ 物种约束参数

```
agent_id:             "P₂"
species_scientific:   "Coilia nasus"
species_chinese:      ["刀鲚", "长颌鲚", "长江刀鱼", "刀鱼"]
species_variants:     ["Coilia nasis", "Coilia nasua", "Coilia nasas",
                       "Coilia ectenes", "Coilia brachygnathus"]
research_themes:
  - 洄游生态与耳石微化学     (theme: migration)
  - 群体遗传与种群结构       (theme: genetics)
  - 资源评估与管理           (theme: stock)
  - 食性与营养生态           (theme: feeding)
  - 早期资源与繁殖           (theme: early_life)
```

## 三、输出格式

搜索结果由 P₂ 做领域专研分析后，按主题分类输出:

| 主题 | 内容 |
|------|------|
| 🐟 洄游生态与耳石微化学 | 耳石 Sr/Ca 比值, 洄游路线, 关键栖息地 |
| 🧬 群体遗传与种群结构 | 微卫星, 线粒体, SNP, 群体分化 |
| 📊 资源评估与管理 | CPUE, MSY, 禁渔效果 |
| 🍽️ 食性与营养生态 | 稳定同位素, 食性转变 |
| 🥚 早期资源与繁殖 | 产卵场, 仔鱼资源, 繁殖生物学 |
