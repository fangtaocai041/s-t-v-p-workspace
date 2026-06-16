# eon-workspace 🐟

**鱼类生态学多项目研究平台** — 7 个项目各司其职。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# 加载所有项目
python -c "from scripts.project_loader import load_all; print(load_all())"

# 查物种（f 项目知识库优先）
python fish-ecology-assistant/scripts/run_lit_search.py "鳤"

# 全项目健康检查
python -c "from scripts.coordinator import coordinator; print(coordinator.health())"

# 跑全部测试
python scripts/run_all_tests.py
```

## 项目一览

| 项目 | 怎么用 |
|------|--------|
| fish-ecology-assistant | `python scripts/run_lit_search.py "物种名"` |
| cognitive-search-engine | `python scripts/search_api.py --species "物种名"` |
| porpoise-agent | `python src/cli.py analyze --species "Neophocaena"` |
| coilia-agent | `python scripts/migration_analysis.py --species "Coilia nasus"` |
| culter-agent | `python src/main.py` |
| conflict-arbiter | `python -c "from src.arbiter import ConflictArbiter;..."` |

## 协作流程

```
S  fish-ecology-assistant   → 知识库查询
    ↓ 不够用？
V  cognitive-search-engine  → 多引擎搜索验证
    ↓ 结果写回
S  fish-ecology-assistant   → 知识库更新
```

## 许可证

MIT © 2026 fangtaocai041
