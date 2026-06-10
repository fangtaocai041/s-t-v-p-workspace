<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

<div align="center">
  <h1>🔥 Conflict Arbiter — 冲突仲裁层 (C)</h1>
  <p><strong>三角闭环衍生项目 · C 冲突仲裁 · 火 🟥</strong></p>
  <p>多源冲突检测 · 加权仲裁 · 熔断机制 · 中国物种区域策略</p>
  <p>🧠 协调器: <a href="../eon-core/">eon-core</a></p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="../VERSION.yaml"><img src="https://img.shields.io/badge/workspace-v8.1.0-6366f1?style=flat-square" alt="Workspace:v8.1.0"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v1.0.0-ec4899?style=flat-square" alt="Agent:v1.0.0"></a>
</p>

## 架构角色: **衍生项目 C (冲突仲裁)**

> **三角核心**: fish(知识 V0) + cognitive(验证 V1) + eon-core(协调 T)
> **C** 从三角核心衍生。接收任意项目输出，进行冲突仲裁。

## 核心函数

```python
assess_conflict(species: str, sources: list[dict]) → ConflictReport
```

**三阶段仲裁**:
1. **标准化** — 将所有来源的保护等级映射到统一数值轴 [0-100]
2. **检测** — 计算冲突等级 [0-3]，含时空可比性检查
3. **仲裁** — 加权共识 + 熔断判断

## 中国区域策略

当 `region="china"` 时，中国保护分类为权威：
- `chinese_red_list` 权重 = 100 (首要)
- `provincial_protection` 权重 = 90 (次要)
- `iucn` / `cites` 权重 = 40 (仅供参考)

## 冲突等级

| 等级 | 名称 | 动作 |
|:---:|------|------|
| 0 | 完全一致 | 直接通过 |
| 1 | 轻微差异 | 标记后通过 |
| 2 | 显著差异 | 加权仲裁 |
| 3 | 严重对立 | **触发熔断** → 人工复核 |

## 快速开始

```bash
# 通过 project_loader 加载
python -c "from scripts.project_loader import get_conflict; a=get_conflict(); print(a.info())"

# 通过 coordinator 健康检查
python -c "from scripts.coordinator import coordinator; print(coordinator.health('conflict'))"

# 直接仲裁测试
python -c "
from conflict_arbiter.src.arbiter import ConflictArbiter
arbiter = ConflictArbiter()
result = arbiter.detect_conflicts('刀鲚', [
    {'source': 'iucn', 'protection_level': 'EN'},
    {'source': 'chinese_red_list', 'protection_level': '国家二级'},
], region='china')
print(result['verdict'])
"
```

## 目录结构

```
conflict-arbiter/
├── config/agent.yaml              # 仲裁配置 (v1.0.0)
├── src/
│   ├── adapter.py                 # IProjectAdapter → ConflictArbiterAdapter
│   ├── arbiter.py                 # ConflictArbiter 引擎
│   └── __init__.py
└── README.md
```

## 关联项目

| 项目 | 角色 | 关系 |
|------|------|------|
| [eon-core](../eon-core/) | 协调内核 (T) | 路由输出到冲突检测 |
| [fish-ecology-assistant](../fish-ecology-assistant/) | 知识供给 V0 | 保护数据的主要来源 |
| [cognitive-search-engine](../cognitive-search-engine/) | 搜索验证 V1 | 提供文献保护证据 |
| [porpoise-agent](../porpoise-agent/) | P₁ 江豚 | 江豚保护建议来源 |
| [coilia-agent](../coilia-agent/) | P₂ 刀鲚 | 刀鲚保护建议来源 |
| [culter-agent](../culter-agent/) | P₃ 鲌类 | 鲌类保护建议来源 |
