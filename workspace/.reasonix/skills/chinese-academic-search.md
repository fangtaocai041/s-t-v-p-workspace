---
name: chinese-academic-search
description: 中文期刊数据库搜索 — 百度学术/知网/万方/水生生物学报，弥补 PubMed/Crossref 不索引中文期刊的盲区
---
# Chinese Academic Search v1.0

## 用途
搜索中文期刊数据库，弥补英文搜索引擎不索引中文期刊的系统性盲区。

## 搜索源
1. 百度学术 (Baidu Scholar)
2. 知网 (CNKI)
3. 万方 (Wanfang)
4. 生物多样性 (Biodiversity Science)
5. 水生生物学报

## 流程
1. 构建中文学名搜索词 (中文名 + 学名)
2. 依次搜索各中文源
3. 去重合并结果
4. 提取参考文献中的英文论文

## 输出
- 中文论文元数据 (标题/作者/期刊/年份/摘要)
- 引用的英文论文列表
