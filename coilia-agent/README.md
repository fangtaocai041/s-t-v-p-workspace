# Coilia Agent 🐟

**刀鲚专研 (P₂)** — 耳石微化学 + 洄游生态 + 资源评估。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# 文献搜索
python scripts/literature_search.py "Coilia nasus"

# 洄游分析（耳石微化学）
python scripts/migration_analysis.py --species "Coilia nasus"

# 食性分析
python scripts/feeding_analysis.py --species "Coilia brachygnathus"

# 资源评估
python scripts/stock_assessment.py --species "Coilia nasus"
```

## 项目结构

```
coilia-agent/
├── src/
│   ├── main.py          ← CLI 入口
│   └── adapter.py       ← 跨项目接口
├── scripts/
│   ├── literature_search.py  ← 文献搜索
│   ├── migration_analysis.py ← 洄游分析
│   ├── feeding_analysis.py   ← 食性分析
│   ├── genetics_analysis.py  ← 遗传分析
│   └── stock_assessment.py   ← 资源评估
├── data/                # 知识库
└── tests/
```

## 角色

三角核心的 **T (Transition)** 层，P₂ 刀鲚专研。

## 许可证

MIT © 2026 fangtaocai041
