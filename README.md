<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

# eon-workspace

> **三生万物 v8.1 — 六项目统一工作空间**
> 道(eon-core) → S(fish知识) + T(cognitive验证) → 万物(P₁porpoise江豚 + P₂coilia刀鲚 + P₃culter鲌类)
> conflict-arbiter 已合并到 cognitive-search-engine T层

## 目录结构

```
根目录 (6项目 + workspace/)
├── eon-core/                    → 道: 协调内核 (OriginKernel + project_loader)
├── fish-ecology-assistant/      → S: 知识供给 (KB + lit-search v3.1)
├── cognitive-search-engine/     → T: 搜索验证 (credibility_scorer + species_graph + arbiter)
├── porpoise-agent/              → P₁: 江豚专研
├── coilia-agent/                → P₂: 刀鲚专研
├── culter-agent/                → P₃: 鲌类专研
├── workspace/                   → 统一入口 + 配置文件 + 数据 + 文档
│   ├── config/                  → coordination.yaml, VERSION.yaml
│   ├── data/                    → CSV, 下载数据
│   ├── scripts/                 → 工作空间级脚本
│   ├── logs/                    → 运行日志
│   └── docs/                    → 架构文档
└── .reasonix/                   → Reasonix 运行时配置
```

## 快速开始

```bash
# 加载全部适配器 (6/6)
python -c "from scripts.project_loader import load_all; print(load_all())"

# 物种搜索 (经由 eon-core → workspace)
python eon-core/src/main.py search "珠星三块鱼"

# 健康检查
python eon-core/src/main.py health

# 三角验证评分
python fish-ecology-assistant/scripts/run_lit_search.py "珠星三块鱼"

# 知识库→图谱同步
python fish-ecology-assistant/scripts/kb_to_graph_sync.py

# 分类学变更检查
python fish-ecology-assistant/scripts/kb_to_graph_sync.py --check
```

## 项目一览

| 项目 | 版本 | 角色 | 功能 |
|------|:----:|:----:|------|
| eon-core | v8.1.0 | 道(协调内核) | OriginKernel + project_loader → workspace 委托 |
| fish-ecology-assistant | v6.4.0 | S(三角·知识) | fish_species_kb + lit-search v3.1 + 6脚本 |
| cognitive-search-engine | v5.6.0 | T(三角·验证) | credibility_scorer + species_graph(48种176篇) + arbiter |
| porpoise-agent | v4.3.0 | P₁(江豚) | 声学+种群建模 |
| coilia-agent | v1.2.0 | P₂(刀鲚) | 耳石微化学+资源评估 |
| culter-agent | v2.0.0 | P₃(鲌类) | 生长+基因组+营养 |

## 架构

```
道 eon-core (协调内核)
├── S fish-ecology-assistant (知识供给)
│   ├── fish_species_kb.yaml (27条目)
│   └── lit-search v3.1 (12层管线 + 三角验证评分)
├── T cognitive-search-engine (搜索验证)
│   ├── species_graph.yaml (48物种, 176论文)
│   ├── credibility_scorer.py (0-100评分)
│   └── arbiter.py (冲突仲裁)
└── 万物衍生
    ├── P₁ porpoise-agent (江豚)
    ├── P₂ coilia-agent (刀鲚)
    └── P₃ culter-agent (鲌类)

精简: conflict-arbiter → cognitive 内嵌 (655行)
删除: 55个僵尸文件 (vertices/trigrams/samsara等)
```

## 数据结构

```
species_graph.yaml    48物种, 176论文, 12科
fish_species_kb.yaml  27条目 (species_graph_id已同步)
scripts/ (7个):
  credibility_scorer.py  🟢🟡🟠🔴 三角验证
  self_evolve.py         6维度自进化
  kb_to_graph_sync.py    KB↔图谱同步
  taxonomy_sync.py       分类学同步 (已合并入--check)
  run_lit_search.py      CLI搜索入口
  search_species.py      旧版 (deprecated)
  add_literature.py      DOI元数据采集
```

## Skills — 搜索协议

`.reasonix/skills/` 与 `workspace/skills/` 内容同步，两目录均可调用：

| Skill | 版本 | 用途 |
|-------|:----:|------|
| `graph-search-engine` | v4.1 | 图谱物种搜索 — 7引擎并行 + Pareto最优满意 + 自适应深度 |
| `cognitive-species-search` | v3.2 | 认知物种搜索 — 符号学+语言学+语音学+逻辑推理链 |
| `chinese-academic-search` | v1.0 | 中文期刊搜索 — 弥补 PubMed/Crossref 不索引中文期刊的盲区 |
| `self-evolve` | v1.0 | 自进化反馈 — 搜索后自动调参 + 指标驱动进化 |
| `parallel-farm` | — | 并行子 agent 派发 — 多角度独立调查汇总 |
| `meso-orchestrator` | v1.0 | 跨项目协调 — Macro(BDI)→Meso(Route)→Micro(Execute) |
| `auto-skill` | — | 自动技能沉淀 — 非平凡任务自动生成 SKILL.md |
| `ocr-solution-audit` | — | OCR 方案审计 — 五维对比推荐最优路径 |

调用方式：`/run_skill name:graph-search-engine arguments:"搜索 鳤 文献"`

Python 脚本入口：`python workspace/scripts/pipeline_search_species.py "检索珠星三块鱼"`

## 文档

| 文档 | 位置 |
|------|------|
| 架构规范 | `workspace/docs/root_docs/SANSHENG_WANWU.md` |
| 版本号 | `workspace/config/VERSION.yaml` |
| 协调配置 | `workspace/config/coordination.yaml` |
| 工程语法 (20条规则) | `fish-ecology-assistant/.reasonix/handbooks/engineering-grammar.md` |
