---
name: cognitive-species-search
description: 认知物种搜索 v3.2 — 符号学+语言学+OCR变体+DeepSeek 思维链，适合拼写模糊/OCR错误的物种名
runAs: subagent
---
# Cognitive Species Search Engine v3.2

## 认知架构
Species as Sign (符号) — 从破碎的符号中恢复完整的所指。

## 流程
### Phase 1: 符号重建 (Sign Reconstruction)
- 输入物种名 → 生成认知变体 (拼写错误/OCR错误/语音近似)
- 语言学展开: 中文名 → 拉丁名 → 日文名 → 俄文名

### Phase 2: 多重证据搜索
- 并行搜索: NCBI E-utilities + Crossref + Semantic Scholar + Google Scholar
- 引用回溯: 对每篇找到的论文检查参考文献

### Phase 3: 新论文检测
- 对比知识库已有论文列表
- 标注新增论文与变化

## 输出
- 论文列表 (含摘要/作者/单位)
- 新增论文标注
- 知识空白分析
