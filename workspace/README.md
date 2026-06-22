# 三生万物 · 五项目工作空间 (v8.0.0)

> **物种全栈分析管线 · Phase 0:画像 → 1:统计 → 2:趋势 → 3:空白 → 4:涌现 → 5:假设**

## 架构概览

| 项目 | 角色 | 五行 | gRPC 端口 |
|------|------|:----:|:---------:|
| **eon-core** | UNIFIED_KERNEL (全层协调) | 全部 | — |
| **fish-ecology-assistant** | S (State) → V0 SupplyVertex | 土 🟫 | 50051 |
| **cognitive-search-engine** | V (Validation) → V1 VerifyVertex | 金 ✨ | 50052 |
| **porpoise-agent** | P₁(衍生, DomainVertex) | 水 💧 | 50053 |
| **coilia-agent** | P₂(衍生, DomainVertex) | 木 🌳 | 50054 |
| **culter-agent** | P₃(衍生, DomainVertex) | 火 🔥 | 50055 |

## 搜索协议

`workspace/skills/` 与 `.reasonix/skills/` 内容一致，从两目录均可调用同一套搜索协议：

| Skill | 用途 | 模式 |
|-------|------|:----:|
| `graph-search-engine` | 图谱物种搜索 v4.1 | subagent |
| `cognitive-species-search` | 认知物种搜索 v3.2 | subagent |
| `chinese-academic-search` | 中文期刊搜索 | inline |
| `self-evolve` | 自进化反馈引擎 | subagent |
| `parallel-farm` | 并行子 agent 派发 | inline |
| `meso-orchestrator` | 跨项目协调 | subagent |
| `auto-skill` | 自动技能沉淀 | inline |
| `ocr-solution-audit` | OCR 方案审计 | subagent |

### 调用方式

```
# 从 workspace 目录调用
/run_skill name:graph-search-engine arguments:"搜索 Ochetobius elongatus 文献"

# 从 .reasonix 目录调用（等效）
/run_skill name:graph-search-engine arguments:"搜索 Ochetobius elongatus 文献"

# 物种全栈分析（推荐）
python scripts/run_full_analysis.py "珠星三块鱼" "Tribolodon brandti"

# 运行测试集
python scripts/test_pipeline.py

# 单模块
python scripts/trend_analyzer.py "珠星三块鱼"
python scripts/gap_analyzer.py "珠星三块鱼"
python scripts/cross_synthesis.py "珠星三块鱼" "Tribolodon brandti"
python scripts/reasoning_engine.py "珠星三块鱼" "Tribolodon brandti"

# CLI 交互入口
python scripts/search_species.py "珠星三块鱼"

# 旧搜索管线（兼容）
python scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"
python scripts/coordinator.py           # 自检
python scripts/credibility_scorer.py --example
python scripts/self_evolve.py --example
```

## 快速开始

```bash
# 1. 验证工作空间完整性
python workspace/launch_all.py

# 2. 物种文献搜索（全管线）
python workspace/scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"

# 3. 仅查知识库
python workspace/scripts/pipeline_search_species.py "珠星三块鱼" --phase lookup

# 4. 全栈健康检查
python -c "from workspace.scripts.coordinator import coordinator; print(coordinator.info('cognitive'))"
```

### 🧭 目的模糊？跟我聊聊

当你不知道想做什么的时候，试试这些斜杠命令：

| 命令 | 用途 |
|------|------|
| `/explore-workspace` | "不知道能做什么" — 聊聊兴趣，推荐路径 |
| `/focus-research` | "有个模糊的研究想法" — 逐步聚焦到可执行计划 |
| `/discover-species` | "不知道研究哪种鱼" — 随机发现/关联发现/主题发现 |
| `/capabilities` | "还有什么我能用的？" — 全景能力一览 + 场景推荐 |

**用法：** 直接敲 `/explore-workspace` 然后跟我聊天就行。不问"你想做什么"，问"你对什么感兴趣"。

## 统一入口 API

| 函数 | 路由 | 用途 |
|------|------|------|
| `search_species(name)` | → cognitive-search-engine | 物种文献搜索 |
| `lookup_species(name)` | → fish-ecology-assistant | 物种知识库查询 |
| `assess_conservation(name)` | → porpoise-agent | 保护评估 |
| `assess_species(name)` | → coilia-agent | 物种评估（洄游/资源） |
| `health_check()` | → 全部项目 | 全栈健康检查 |

## 目录结构

```
workspace/
├── __init__.py              — 包标记
├── launch_all.py            — 一键启动 + 健康检查
├── activate.ps1             — PowerShell 环境激活
├── README.md                — 本文档
├── skills/                  — 搜索协议 skill 定义（与 .reasonix/skills/ 同步）
│   ├── graph-search-engine.md
│   ├── cognitive-species-search.md
│   ├── chinese-academic-search.md
│   ├── self-evolve.md
│   ├── parallel-farm.md
│   ├── meso-orchestrator.md
│   ├── auto-skill.md
│   └── ocr-solution-audit.md
├── scripts/                 — Python 可执行实现
│   ├── run_full_analysis.py         — 一键全量分析 Phase 0-5 🪜
│   ├── kb_loader.py                 — 统一数据加载器       🪜
│   ├── trend_analyzer.py            — 研究趋势分析         🪜
│   ├── gap_analyzer.py              — 研究空白识别         🪜
│   ├── cross_synthesis.py           — 跨物种涌现(5检测器)  🪜
│   ├── reasoning_engine.py          — 生态假设推理(6假设)  🪜
│   ├── test_pipeline.py             — 管线测试集(38项)    🪜
│   ├── search_species.py            — CLI 交互入口
│   ├── pipeline_search_species.py   — 搜索管线(兼容)
│   ├── coordinator.py               — 五项目协调器
│   ├── credibility_scorer.py        — 三角验证评分
│   ├── self_evolve.py               — 自进化反馈
│   └── kb_to_graph_sync.py          — KB↔图谱同步
├── config/
│   └── root_config/
│       ├── species_graph.yaml       — 48物种 176论文
│       └── meso_agent.yaml          — Meso 协调配置
├── data/                  — 数据文件
├── docs/                  — 架构文档
├── ocr/                   — OCR 测试工具
├── logs/                  — 运行日志
├── search_records/        — 搜索记录
└── bin/                   — 可执行文件
```

## 五项目即五独立仓库

每个项目有独立的 `.git`，可单独开发、部署。`pipeline_search_species.py` 是它们的统一搜索入口。

---

## 🧬 RCCA 集成 (v2.1.0)

**RCCA** (Recursive Convergence Cognitive Architecture) 是本工作空间的递归收敛认知核心，已部署到**所有 7 个子项目**：

| 项目 | 部署状态 |
|:-----|:--------:|
| fish-ecology-assistant | ✅ |
| cognitive-search-engine | ✅ |
| porpoise-agent | ✅ |
| coilia-agent | ✅ |
| culter-agent | ✅ |
| conflict-arbiter | ✅ |
| eon-core | ✅ |

### 已部署的核心能力

| 模块 | 类名 | 用途 |
|:-----|:-----|:-----|
| 阻尼自我模型 | `SelfModelEngine` | 预测误差滑动窗口 → 稳定性检测 |
| 资源分配策略 | `EmotionEngine` | 事件驱动策略选择 → 行为倾向 |
| 概念转座层 | `TranspositionLayer` | 跳跃基因逻辑: 跨域推理模式迁移 |
| 反思循环 | `ReflectionLoop` | 递归思考→转座→自我适应闭环 |

### 从 workspace 使用

```python
from workspace import rcca_setup, rcca_health, rcca_health

# 一键初始化全部核心模块
core = rcca_setup()

# 阻尼自我模型：稳定性自检
state = core["self_model"].reflect()
print(f"Stability: {state.stability:.3f}")

# 情绪引擎：事件触发策略切换
core["emotion"].stimulate("contradiction", 0.9)
print(f"Tendency: {core['emotion'].behavioral_tendency}")

# 转座层：跨域推理模式迁移
tl = core["transposition"]
tl.transpose("search", "verify", {"concept": "cross_domain", "confidence": 0.9})

# 反思循环：多通道协作
loop = core["reflection"]
report = loop.run(["scholar", "cnki", "ncbi"], transposition=tl)

# 健康检查（含 RCCA 状态）
check = rcca_health()
print(f"RCCA: {check['status']}")
```

### 从子项目直接使用

```python
from src.rcca_core import SelfModelEngine, EmotionEngine, TranspositionLayer, ReflectionLoop
```

核心版本: **RCCA v2.1.0** (2026-06-20) · 零外部依赖 · 即插即用

---

## 相关文档

- `config/VERSION.yaml` — 版本单源真相
- `config/coordination.yaml` — 跨项目协调协议
- `docs/root_docs/ARCHITECTURE_OVERVIEW.md` — 整体架构说明
- `docs/root_docs/SANSHENG_WANWU.md` — 三生万物哲学
