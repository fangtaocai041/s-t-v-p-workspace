# Conflict Arbiter 🔥

**冲突仲裁层 (C)** — IUCN 说濒危、国标说无危？它来裁决。

[English](README.md) · [更新日志](CHANGELOG.md)

---

## 快速开始

```bash
# 直接调用仲裁引擎
python -c "
from src.arbiter import ConflictArbiter
a = ConflictArbiter()
result = a.arbitrate('Ochetobius elongatus')
print(result)
"
```

```python
from src.arbiter import ConflictArbiter

arbiter = ConflictArbiter()
# 多源保护级别冲突检测
result = arbiter.arbitrate("Ochetobius elongatus")
print(result.final_status)     # 最终裁决
print(result.confidence)       # 可信度
```

## 项目结构

```
conflict-arbiter/
├── src/
│   ├── arbiter.py    ← 仲裁引擎核心
│   └── adapter.py    ← 跨项目接口
├── config/           # 仲裁规则
└── tests/
```

## 角色

三角核心的 **质量控制层**，保证输出结论可靠。

## 许可证

MIT © 2026 fangtaocai041
