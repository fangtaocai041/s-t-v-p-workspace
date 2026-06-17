# fishkb

鱼类生态学知识库核心库 — 从 fish-ecology-assistant 提取的独立纯 Python 库。

## 功能

- **KnowledgeDB**: SQLite + FTS5 物种知识库，支持精确查询、全文搜索、文献写回
- **FishSpeciesMatcher**: KB-first 物种查找与模糊匹配
- **Credibility Scoring**: 三角验证文献可信度评分 (0–100)
- **SpeciesVariants**: 物种拼写变体注册表
- **Core Types**: ResearchContext, SourceEntry, AnalysisFinding 等研究流水线数据类型

## 安装

```bash
pip install fishkb
# 或开发模式
pip install -e .
```

## 快速开始

```python
from fishkb import KnowledgeDB, FishSpeciesMatcher

db = KnowledgeDB()
db.init_from_index("config/fish_species_index.yaml", "config/knowledge_base/species")

matcher = FishSpeciesMatcher(db)
result = matcher.kb_first_lookup(query="鳤")
print(result.summary_text)
```

## 依赖

- pyyaml >= 6.0
- 可选: fastapi, uvicorn (用于 server 模式)
