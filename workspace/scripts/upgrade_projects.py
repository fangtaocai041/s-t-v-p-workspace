"""Upgrade old projects: add RCCA integration section to README"""
import os

RCCA_SECTION = """

---

## 🧬 RCCA 集成 (v2.1.0 便携核心)

本项目已集成 [san-sheng-wanwu-core](https://github.com/fangtaocai041/san-sheng-wanwu-core) 的便携 RCCA 核心模块。

### 已部署的核心能力

| 模块 | 类名 | 用途 |
|:-----|:-----|:-----|
| 阻尼自我模型 | `SelfModelEngine` | 预测误差滑动窗口 → 稳定性检测 |
| 资源分配策略 | `EmotionEngine` | 事件驱动策略选择 → 行为倾向 |
| 概念转座层 | `TranspositionLayer` | 跳跃基因逻辑: 跨域推理模式迁移 |
| 反思循环 | `ReflectionLoop` | 递归思考→转座→自我适应闭环 |

### 快速开始

```python
from src.rcca_core import SelfModelEngine, EmotionEngine, TranspositionLayer, ReflectionLoop

# 初始化自我模型
sm = SelfModelEngine()
state = sm.reflect()  # 稳定性自检

# 情感驱动的转座
tl = TranspositionLayer()
e = EmotionEngine(transposition_layer=tl)
e.stimulate("discovery", 0.8)  # 发现新知识 → 自动推送到转座层

# 跨域转座：将搜索策略从 A 通道迁移到 B 通道
result = tl.transpose("search", "verify", {"concept": "cross_domain", "confidence": 0.9})

# 反思循环
loop = ReflectionLoop()
report = loop.run(["scholar", "cnki", "ncbi"], transposition=tl)
```

### 版本

核心版本: **RCCA v2.1.0** (2026-06-20) · 零外部依赖 · 即插即用
"""

projects = {
    "fish-ecology-assistant": "fish-ecology-assistant",
    "cognitive-search-engine": "cognitive-search-engine",
    "porpoise-agent": "porpoise-agent",
    "coilia-agent": "coilia-agent",
    "culter-agent": "culter-agent",
    "conflict-arbiter": "conflict-arbiter",
    "eon-core": "eon-core",
}

imported = 0
for p in projects:
    root = os.path.join("D:/Reasonix", p)
    readme = os.path.join(root, "README.md")
    if os.path.exists(readme):
        with open(readme, "r", encoding="utf-8") as f:
            content = f.read()
        if "RCCA" not in content and "rcca_core" not in content:
            with open(readme, "a", encoding="utf-8") as f:
                f.write(RCCA_SECTION)
            print(f"  Updated: {p}/README.md")
            imported += 1
        else:
            print(f"  Skipped (already has RCCA): {p}")
    else:
        print(f"  No README: {p}")

print(f"\nUpdated {imported}/{len(projects)} projects.")
