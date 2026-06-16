<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

# eon-workspace

**鱼类生态学多项目研究平台** — 7 个协同项目 + 知识库 + 搜索引擎 + 文献分析管线。

---

## 项目结构

```
eon-workspace/
├── eon-core/                    # 协调内核 — EventBus · DAG路由 · 健康监控
├── fish-ecology-assistant/      # 鱼类知识供给 — 26物种知识库 + KB-First搜索 + 可信度评分
├── cognitive-search-engine/     # 认知搜索引擎 — 20引擎并行 + 图谱遍历 + 冲突仲裁
├── porpoise-agent/              # P₁ 江豚专研 — NBHF声学 · 种群建模 · 威胁评估
├── coilia-agent/                # P₂ 刀鲚专研 — 耳石微化学 · 洄游生态 · 资源评估
├── culter-agent/                # P₃ 鲌类专研 — 基因组 · 年龄生长 · 同位素 · 同域共存
├── conflict-arbiter/            # 冲突仲裁 — 多源保护级别冲突检测与加权裁决
├── infrastructure/              # 涌现检测引擎 — 跨物种模式发现
├── scripts/                     # 工作空间级脚本（31个）
├── config/                      # 全局配置
├── docs/                        # 架构文档
└── skills/                      # Reasonix 技能定义
```

---

## 快速开始

```bash
# 加载全部项目适配器
python -c "from scripts.project_loader import load_all; print(load_all())"

# KB-First 物种查询（零网络开销）
python -c "from fish_ecology_assistant.src import get_orchestrator; \
  o = get_orchestrator(); print(o.kb_first_lookup(query='鳤').summary_text)"

# 文献搜索 + 三角验证评分
python fish-ecology-assistant/scripts/run_lit_search.py "珠星三块鱼"

# 跨项目健康检查
python -c "from scripts.coordinator import coordinator; print(coordinator.health())"

# 全量测试
python scripts/run_all_tests.py
```

---

## 项目一览

| 项目 | 语言 | 描述 |
|------|:--:|------|
| **eon-core** | 12 py | 协调内核：OriginKernel · EventBus · DAG路由 · 健康监控 · 10层同心架构 |
| **fish-ecology-assistant** | 12 py | 知识供给：26物种知识库 · KB-First两阶段搜索 · 期刊白名单可信度评分 · 分类变更回写 |
| **cognitive-search-engine** | 3 py | 搜索验证：20引擎并行搜索 · 物种图谱(48种/176篇) · 三角验证 · BDI+ReAct |
| **porpoise-agent** | 54 py | 江豚专研(P₁)：NBHF声学分析 · 栖息地建模 · 种群评估 · 威胁分析 |
| **coilia-agent** | 22 py | 刀鲚专研(P₂)：耳石Sr同位素 · 洄游推断 · 资源评估 · 9-phase管线 |
| **culter-agent** | 10 py | 鲌类专研(P₃)：6种鲌类 · 基因组分析 · von Bertalanffy生长 · δ¹³C/δ¹⁵N同位素 |
| **conflict-arbiter** | 3 py | 冲突仲裁：IUCN/红色名录/省级保护多源冲突检测 · 加权裁决 · 熔断 |
| **infrastructure** | 3 py | 涌现检测：跨物种模式发现 · 5检测器 · 34/34测试通过 |

---

## 数据资产

| 数据 | 位置 | 规模 |
|------|------|------|
| 鱼类物种知识库 | `fish-ecology-assistant/config/fish_species_kb.yaml` | 26 物种（长江 15 优势种 + 7 保护种 + 三块鱼跨国分布） |
| 物种文献图谱 | `cognitive-search-engine/config/species_graph.yaml` | 48 物种 / 176 篇论文 |
| 长江调查数据 | `fish_species_kb.yaml` metadata | 443 历史种 / 323 采集种 (2017-2021) |
| 物种拼写变体 | `C:\Users\小陶\.reasonix\config\species_variants.yaml` | 鳤/鯮/鱤 OCR 变体 + 同义名 |

---

## 搜索引擎

cognitive-search-engine 提供以下搜索能力：

| 引擎 | 覆盖 |
|------|------|
| PubMed E-utilities | 生物医学文献 |
| Crossref | 学术元数据 |
| OpenAlex | 开放学术图谱 |
| Semantic Scholar | AI增强文献 |
| Google Scholar | 综合学术搜索 |
| CNKI / 万方 / 百度学术 | 中文期刊（弥补 PubMed 盲区） |
| Europe PMC | 全文 + 引用 |
| arXiv | 预印本 |

---

## GitHub 仓库

全部 7 个项目均为公开仓库：

| 仓库 | URL |
|------|-----|
| eon-workspace | https://github.com/fangtaocai041/s-t-v-p-workspace |
| eon-core | https://github.com/fangtaocai041/eon-core |
| cognitive-search-engine | https://github.com/fangtaocai041/cognitive-search-engine |
| fish-ecology-assistant | https://github.com/fangtaocai041/fish-ecology-assistant |
| porpoise-agent | https://github.com/fangtaocai041/porpoise-agent |
| coilia-agent | https://github.com/fangtaocai041/coilia-agent |
| culter-agent | https://github.com/fangtaocai041/culter-agent |

---

## 架构

```
eon-core (协调内核 · 路由+调度)
    ├── fish-ecology-assistant (S: 知识供给 · 静态)
    │       ↕ 两阶段搜索 + 可信度评分反馈
    ├── cognitive-search-engine (V: 搜索验证 · 动态)
    │       ↕ 冲突检测 + 分类变更回写
    ├── porpoise-agent (P₁: 江豚 · 声学+种群)
    ├── coilia-agent   (P₂: 刀鲚 · 耳石+洄游)
    ├── culter-agent    (P₃: 鲌类 · 基因组+营养)
    └── conflict-arbiter (C: 仲裁 · 熔断)
```

---

## 核心脚本

| 脚本 | 用途 |
|------|------|
| `scripts/coordinator.py` | 跨项目协调器 — 路由 + 健康监控 |
| `scripts/project_loader.py` | 统一项目加载器 — importlib 零进程加载 |
| `scripts/pathway_contracts.py` | 通路合约 — P0-P7 跨项目通路定义 |
| `scripts/quality_gate.py` | 质量门控 — 5项检查 |
| `scripts/run_all_tests.py` | 全量测试运行器 |
| `scripts/verify_pathways.py` | 通路验证 — 25/25 |
| `fish-ecology-assistant/scripts/run_lit_search.py` | 文献搜索 CLI — 图谱→评分→交互展开 |
| `fish-ecology-assistant/src/dao_engine.py` | Dao 引擎 CLI — 道→一→二→三→万物 |

---

## 文档

| 文档 | 位置 |
|------|------|
| 架构总览 | `ARCHITECTURE.md` |
| 速查表 | `CHEATSHEET.md` |
| 迁移指南 | `MIGRATION.md` |
| 路线图 | `ROADMAP.md` |
| 安全策略 | `SECURITY.md` |
| 全局配置 | `VERSION.yaml` / `coordination.yaml` |
