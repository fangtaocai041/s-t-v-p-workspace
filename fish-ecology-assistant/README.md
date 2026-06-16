# Fish Ecology Assistant 🐟

**鱼类生态学知识供给引擎** — 26 个物种知识库 + 文献搜索 + 可信度评分。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# 安装
pip install -e .

# 查物种（先查知识库）
python -c "from src import get_orchestrator; o = get_orchestrator(); print(o.health())"

# 文献搜索
python scripts/run_lit_search.py "鳤"

# 可信度评分
python scripts/credibility_scorer.py
```

## 核心功能

### 知识库查询
```python
from src import get_orchestrator

orch = get_orchestrator()
# KB-First：先查知识库
result = orch.kb_first_lookup(query="鳤")
print(result.found)               # True/False
print(result.summary_text)        # 已有信息摘要
print(result.search_recommendation)  # stay_in_kb 或 continue_to_c
```

### 文献搜索
```bash
python scripts/run_lit_search.py "珠星三块鱼"
python scripts/run_lit_search.py "Ochetobius elongatus" --max 20
```

### 知识库 ↔ 图谱同步
```bash
python scripts/kb_to_graph_sync.py
```

### 分类学变更回写
```bash
python scripts/taxonomy_sync.py
```

### 📚 方陶文库 — 个人研究空间
- [研究札记](方陶文库/蔡方陶/01-研究札记.md) — 理论思考、假说、行动清单
- [百宝箱理论](方陶文库/蔡方陶/04-百宝箱理论.md) — 研究方法论工具箱
- [技术报告](方陶文库/分析报告/) — 珠星三块鱼、刀鲚等物种分析
- [理论笔记](方陶文库/theories/) — 10 个生态学理论

## 项目结构

```
fish-ecology-assistant/
├── src/
│   ├── orchestrator.py    ← KB-First 搜索入口
│   ├── project_hub.py     ← 跨项目协调
│   └── adapter.py         ← 跨项目接口
├── scripts/
│   ├── run_lit_search.py  ← 文献搜索
│   ├── kb_to_graph_sync.py← 图谱同步
│   └── taxonomy_sync.py   ← 分类学同步
├── config/                # 物种知识库 YAML
└── tests/
```

## 角色

三角核心的 **S (知识供给)** 层。

## 许可证

MIT © 2026 fangtaocai041
