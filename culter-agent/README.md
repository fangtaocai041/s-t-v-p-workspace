# Culter Agent 🐟

**鲌类专研 (P₃)** — 基因组 + 年龄生长 + 同位素 + 同域共存。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# CLI 入口
python src/main.py --help

# 鲌类物种评估
python -c "from src.adapter import CulterAdapter; a = CulterAdapter(); print(a.health())"
```

```python
from src.adapter import CulterAdapter

adapter = CulterAdapter()
info = adapter.info()
print(info["capabilities"])
```

## 项目结构

```
culter-agent/
├── src/
│   ├── main.py          ← CLI 入口
│   ├── adapter.py       ← 跨项目接口
│   └── knowledge_base.py← 知识库加载
├── data/                # 知识库
├── scripts/             # 共享类型
└── tests/
```

## 角色

三角核心的 **T (Transition)** 层，P₃ 鲌类专研。

## 许可证

MIT © 2026 fangtaocai041
