<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🐟 Coilia Agent — 刀鲚专研 (P₂)</h1>
  <p><strong>三角闭环衍生项目 · P₂ 刀鲚专研 · 淡水渔业研究中心 刘凯研究员课题组</strong></p>
  <p>3 Skills · DirectLoader cognitive search · knowledge base · Panta Rhei philosophy</p>
  <p>🤝 Sister agent: <a href="https://github.com/fangtaocai041/porpoise-agent">porpoise-agent (P₁ 江豚)</a> · 🧠 Coordinator: <a href="https://github.com/fangtaocai041/eon-core">eon-core</a></p>
  <p>🌊 Panta Rhei · Everything Flows</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/DeepSeek-V3%2BR1-6366f1?style=flat-square" alt="DeepSeek"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-3-f59e0b?style=flat-square" alt="Skills:3"></a>
  <a href="#"><img src="https://img.shields.io/badge/knowledge_base-Coilia_nasus-8b5cf6?style=flat-square" alt="Knowledge"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v1.3.0-ec4899?style=flat-square" alt="Agent:v1.3.0"></a>
</p>

## 🧠 Coordinated by eon-core

> P₂ (derived from Triangle Core) coordinated by [eon-core](https://github.com/fangtaocai041/eon-core) (Triangle Core coordinator): **Chaos-enhanced routing** · **Samsara karma engine** · **DAG topology routing**.

## 🔺 Architecture Role: **Derived Project P₂ (Coilia Specialist)**

> Triangle Core: fish(Knowledge) + cognitive(Validation) + eon-core(Coordinator)
> P₂ derived from Triangle Core, depends on triangle for species knowledge and literature search.
> Coilia-specific: otolith microchemistry, migration ecology, resource assessment.
> **Sister agent**: [porpoise-agent (P₁)](https://github.com/fangtaocai041/porpoise-agent) — 江豚专研, same Derived level.

## 研究背景

刀鲚（长江刀鱼）是长江流域最重要的经济鱼类之一，也是"长江三鲜"之首。
由于过度捕捞、水利工程阻断洄游通道、栖息地退化，刀鲚资源量急剧下降。
2019年起农业农村部停止发放刀鲚专项捕捞许可证，2021年长江十年禁捕全面实施。

## 🔗 Linked Projects (Triangle Core + Derived)

| Project | Layer | Role | Description |
|---------|:-----:|------|-------------|
| **eon-core** | **Triangle** | Coordinator | EventBus · Samsara karma · DAG routing · self-healing |
| **fish-ecology-assistant** | **Triangle V0** | Knowledge | Multi-basin fish DB (Yangtze 443 + Tumen + Suifen) |
| **cognitive-search-engine** | **Triangle V1** | Validation | BDI+ReAct · literature search · authority scoring |
| **porpoise-agent** | **Derived P₁** | Porpoise domain | NBHF acoustics · habitat modeling (sister project) |
| **culter-agent** | **Derived P₃** | Culter specialist | Genomics · age-growth · isotopes · coexistence |
| **conflict-arbiter** | **Derived C** | Conflict arbitration | Multi-source protection-level arbitration |

> **DirectLoader Protocol**: cognitive-search-engine loaded via `importlib` from `D:\Reasonix\cognitive-search-engine\src\` — engine updates auto-propagate, zero MCP overhead.
> Full spec: workspace root `coordination.yaml`.

## 核心研究方向

| 方向 | 说明 |
|------|------|
| 🧬 群体遗传学 | 刀鲚洄游群体遗传结构、地理种群分化 |
| 🏷️ 耳石微化学 | Sr/Ca比分析洄游履历、生境履历重建 |
| 📐 形态学 | 刀鲚与近缘种(短颌鲚、凤鲚)的形态鉴别 |
| 🌊 洄游生态 | 溯河洄游路线、时间节律、环境驱动因子 |
| 📊 资源评估 | 禁捕后资源恢复监测、种群动态模型 |
| 🍽️ 食性分析 | 刀鲚摄食生态、营养级位置 |

## 📊 自我评价

| 维度 | 评分 | 说明 |
|------|:--:|------|
| 🐟 领域深度 | ⭐⭐⭐⭐⭐ | 刀鲚完整知识库：生物学、洄游特性、耳石微化学、资源评估 |
| 🔬 研究方法 | ⭐⭐⭐⭐☆ | 3 个核心 Skill 定义完整 (文献检索/洄游分析/资源评估) |
| 🔗 生态位整合 | ⭐⭐⭐⭐⭐ | 衍生项目 P₂，与 P₁(江豚) 同级衍生，统一由 eon-core 调度 |
| 📡 可执行性 | ⭐⭐⭐☆☆ | 当前为 delegation stub 架构，实际搜索通过 DirectLoader 调用 cognitive-search-engine |
| 🚀 可扩展性 | ⭐⭐⭐⭐⭐ | 与 porpoise-agent 共享 P 层模板，3 步复制出新物种 Agent |

> **核心优势**: 长江刀鲚（三鲜之首）专属研究 Agent。与 P₁ 江豚 Agent 共享刘凯研究员课题组方向，形成长江水生生物"豚-鱼"双专研体系。
> **待改进**: Skills 从 delegation stub 升级为可执行搜索逻辑。

---

## 🧠 Skills

| Skill | Role | Description |
|:------|:-----|:------------|
| 🔍 `search-literature` | 📚 Literature Review | Bilingual EN/CN search via cognitive-search-engine DirectLoader |
| 🏷️ `analyze-migration` | 🌊 Migration Analysis | Otolith Sr/Ca profiling + migration route reconstruction |
| 📊 `assess-stock` | 📊 Stock Assessment | CPUE analysis + population dynamics modeling |

---

## 📡 Search Infrastructure

**DirectLoader Protocol** — searches routed to cognitive-search-engine via `importlib`:

```
CoiliaAgent.search(query, genus="Coilia", species="nasus")
  └─ CognitiveSearchAdapter.search("Coilia", "nasus", full_pipeline=False)
       ├─ variant_generator.generate()    → OCR variants (Coilia→Coilia, etc.)
       ├─ build_search_queries()          → exact + variants + Chinese names
       └─ ParallelSearch.search_all()     → PubMed × Crossref × OpenAlex
```

> Engine path: `D:\Reasonix\cognitive-search-engine\src\` · Adapter: `src/adapter.py`

---

## 📁 Project Structure

```
coilia-agent/
├── README.md                 ← English
├── README.zh.md              ← 中文
├── coilia.bat                ← CLI launcher
│
├── config/
│   ├── agent.yaml            ← Agent behavior config
│   ├── component_registry.yaml
│   └── component_registry.yaml
│
├── src/
│   ├── main.py               ← CLI entry point
│   ├── adapter.py             ← CognitiveSearchAdapter (DirectLoader)
│   ├── agent/
│   │   └── orchestrator.py   ← Query routing + pipeline
│   ├── prompts/
│   │   └── system_prompts.py ← Panta Rhei philosophy prompts
│   └── skills/
│       ├── search-literature/    ← Bilingual literature search
│       ├── analyze-migration/    ← Otolith microchemistry analysis
│       └── assess-stock/         ← Stock assessment modeling
│
└── data/
    └── knowledge_base/
        └── species/           ← Coilia nasus knowledge entries
```

---

## 📋 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v1.2.0** | 2026-06-08 | ☯️ TAO (水·润下) + Monitoring + standalone DirectLoader search |
| **v1.1.0** | 2026-06-08 | Standalone/integrated dual mode |
| **v1.0.0** | 2026-06-08 | Initial release — P₂ 刀鲚专研 · 3 Skills · knowledge base |

> **Latest**: v1.3.0 · 2026-06-09

## 🗺️ 演进方向 (Personalized Roadmap)

| # | 方向 | 痛点 | 优先级 |
|:--:|------|------|:----:|
| 1 | **Coilia 文献双语搜索** | 刀鲚/凤鲚文献分散中英文 | `Coilia nasus` 自动中英双语检索 | 🔴 P0 |
| 2 | **耳石微化学自动分析** | LA-ICP-MS 数据手工处理 | 自动读取 csv → Sr/Ca 剖面图 → 生境履历重建 | 🔴 P0 |
| 3 | **洄游路线推断** | 耳石 Sr/Ca + 捕获位置 → 手工推断 | 贝叶斯状态空间模型 → 概率洄游路线 | 🟡 P1 |
| 4 | **种群连通性分析** | 不同水域 Coilia 是否同一群体 | 耳石元素指纹 + 遗传数据 → 聚类判别 | 🟡 P1 |
| 5 | **捕捞压力评估** | 产量数据分散 | CPUE 时间序列 → 资源状况评估 | 🟢 P2 |

---

## 📋 README Changelog

| Version | Date | Theme | What Changed |
|:--------|:-----|:------|:-------------|
| **v1.4.0** | 2026-06-20 | 🔗 KB-First 搜索集成 + 🧹 prompts/__init__.py 补全 |
| **v1.3.0** | 2026-06-09 | Cross-Project Sync | + Badge row, + S-T-V role (P₂/V3), + eon-core coordination, + Skills table, + Search Infrastructure, + Project Structure, + README Changelog |
| **v1.2.0** | 2026-06-08 | ☯️ TAO + Monitoring | + TAO (水·润下) + Monitoring + standalone DirectLoader search |
| **v1.1.0** | 2026-06-08 | Dual Mode | Standalone/integrated dual mode |
| **v1.0.0** | 2026-06-08 | Initial | P₂ 刀鲚专研 · 3 Skills · knowledge base |

---

## 📜 License

MIT License © 2026 fangtaocai041

---

## ⚡ Quick Start

```bash
cd coilia-agent
pip install -e .
coilia run --query "刀鲚洄游路线 长江"
```
