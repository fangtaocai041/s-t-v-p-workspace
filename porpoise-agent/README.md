# Porpoise Agent 🐬

**江豚研究智能体 (P₁)** — 声学分析 + 种群建模 + 威胁评估。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# CLI 入口
python src/cli.py --help

# 分析物种
python src/cli.py analyze --species "Neophocaena asiaeorientalis"
```

```python
from src.cli import main
# 或直接调用核心模块
```

## 项目结构

```
porpoise-agent/
├── src/
│   ├── cli.py           ← 命令行入口
│   ├── agent/           ← 智能体核心
│   ├── cognitive/       ← 认知模块
│   ├── mapping/         ← 分布制图
│   └── execution/       ← 流水线执行
├── data/                # 知识库
├── scripts/             # 工具脚本
└── tests/
```

## 角色

三角核心的 **T (Transition)** 层，P₁ 江豚专研。

## 许可证

MIT © 2026 fangtaocai041
