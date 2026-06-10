# 三生万物 五项目工作空间

## 架构概览

| 项目 | 角色 | 五行 | gRPC 端口 |
|------|------|:----:|:---------:|
| **eon-core** | UNIFIED_KERNEL (10层同心) | 全部 | — |
| **fish-ecology-assistant** | S (State) → V0 SupplyVertex | 土 🟫 | 50051 |
| **cognitive-search-engine** | V (Validation) → V1 VerifyVertex | 金 🟨 | 50052 |
| **porpoise-agent** | P₁ (衍生, DomainVertex) | 水 💧 | 50053 |
| **coilia-agent** | P₂ (衍生, DomainVertex) | 木 🌲 | 50054 |
| **culter-agent** | P₃ (衍生, DomainVertex) | 火 🔥 | 50055 |

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

# Python 脚本入口
python workspace/scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"
python workspace/scripts/coordinator.py           # 自检
python workspace/scripts/credibility_scorer.py --example
python workspace/scripts/self_evolve.py --example
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

## 统一入口 API

| 函数 | 路由 | 用途 |
|------|------|------|
| `search_species(name)` | → cognitive-search-engine | 物种文献搜索 |
| `lookup_species(name)` | → fish-ecology-assistant | 物种知识库查询 |
| `assess_conservation(name)` | → porpoise-agent | 保护评估 |
| `assess_species(name)` | → coilia-agent | 物种评估 (洄游/资源) |
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
│   ├── pipeline_search_species.py   — 搜索管线 v8.2
│   ├── coordinator.py               — 五项目协调器
│   ├── credibility_scorer.py        — 三角验证评分
│   ├── self_evolve.py               — 自进化反馈
│   ├── kb_to_graph_sync.py          — KB↔图谱同步
│   └── merge_graphs.py              — 图谱合并
├── config/
│   └── root_config/
│       ├── species_graph.yaml       — 48物种 176论文
│       └── meso_agent.yaml          — Meso协调配置
├── data/                    — 数据文件
├── docs/                    — 架构文档
├── ocr/                     — OCR 测试工具
├── logs/                    — 运行日志
├── search_records/          — 搜索记录
└── bin/                     — 可执行文件
```

## 五项目即五独立仓库

每个项目有独立的 `.git`，可单独开发/部署。`pipeline_search_species.py` 是它们的统一搜索入口。

## 相关文档

- `config/VERSION.yaml` — 版本单源真相
- `config/coordination.yaml` — 跨项目协调协议
- `docs/root_docs/ARCHITECTURE_OVERVIEW.md` — 整体架构说明
- `docs/root_docs/SANSHENG_WANWU.md` — 三生万物哲学
