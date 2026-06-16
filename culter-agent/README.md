<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🐟 Culter Agent — 鲌类专研 (P₃)</h1>
  <p><strong>三角闭环衍生项目 · P₃ 鲌类专研 · 基因组与遗传·年龄生长·同位素·同域共存·资源评估</strong></p>
  <p>8 Skills · DirectLoader cognitive search · 9-phase pipeline · 6 target species</p>
  <p>🤝 Sister agents: <a href="https://github.com/fangtaocai041/porpoise-agent">porpoise-agent (P₁ 江豚)</a> · <a href="https://github.com/fangtaocai041/coilia-agent">coilia-agent (P₂ 刀鲚)</a></p>
  <p>🧠 Coordinator: <a href="https://github.com/fangtaocai041/eon-core">eon-core</a></p>
  <p>🌊 Panta Rhei · Everything Flows</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/DeepSeek-V3%2BR1-6366f1?style=flat-square" alt="DeepSeek"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-8-f59e0b?style=flat-square" alt="Skills:8"></a>
  <a href="#"><img src="https://img.shields.io/badge/pipeline-9_phase-22c55e?style=flat-square" alt="Pipeline:9"></a>
  <a href="#"><img src="https://img.shields.io/badge/rules-18-8b5cf6?style=flat-square" alt="Rules:18"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v2.0.0-ec4899?style=flat-square" alt="Agent:v2.0.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/dynamic_worldview-core-ec4899?style=flat-square" alt="Dynamic Worldview"></a>
</p>

---

## 🧠 Powered by eon-core Intelligent Coordination

> P₃ (derived from Triangle Core) coordinated by [eon-core](https://github.com/fangtaocai041/eon-core) (Triangle Core coordinator): **Chaos-enhanced routing** (Rössler + wildcard) · **Scholarly stopping** (Rule of Three) · **DeepSeek MoE gating** · **Samsara karma engine**.

## 🔺 Architecture Role: **Derived Project P₃ (Culter Specialist)**

> **Triangle Core**: fish(Knowledge V0) + cognitive(Validation V1) + eon-core(Coordinator T) — sealed_set(3)
> **P₃** derived from Triangle Core, depends on triangle for species knowledge and literature search.
> **P₁(porpoise) / P₂(coilia) / P₃(culter)** 为同级平行衍生项目，均由三角核心派生。
> **Sister agent**: [porpoise-agent (P₁)](https://github.com/fangtaocai041/porpoise-agent) · [coilia-agent (P₂)](https://github.com/fangtaocai041/coilia-agent)

---

## 📊 Self-Assessment

| Dimension | Rating | Notes |
|-----------|:-----:|-------|
| 🧬 Genomics Depth | ⭐⭐⭐⭐⭐ | 全基因组/简化基因组/比较基因组/系统发育基因组分析管线 |
| 📐 Age & Growth | ⭐⭐⭐⭐☆ | 鳞片/耳石轮纹鉴定 + von Bertalanffy 生长模型 |
| 🌿 Trophic Ecology | ⭐⭐⭐⭐⭐ | δ¹³C/δ¹⁵N 稳定同位素 + MixSIAR 混合模型 + 营养级 |
| 🔗 Coexistence Analysis | ⭐⭐⭐⭐☆ | 生态位重叠量化 + 同域共存机制建模 |
| 📊 Resource Assessment | ⭐⭐⭐⭐☆ | CPUE 标准化 + MSY 估算 + YPR 分析 |
| 🔬 Species Coverage | ⭐⭐⭐⭐⭐ | 6 种鲌亚科鱼类（翘嘴鲌/蒙古鲌/尖头鲌/红鳍原鲌/达氏鲌/拟尖头鲌） |
| 🔗 Ecosystem Integration | ⭐⭐⭐⭐⭐ | Derived P₃, coordinated by eon-core Triangle Core |

---

## 🎯 Target Species

| Species | Chinese | Family | Status |
|---------|---------|--------|:------:|
| *Culter alburnus* | 翘嘴鲌 (白鱼/翘壳) | Cyprinidae > Cultrinae | ⭐ Primary |
| *Culter mongolicus* | 蒙古鲌 (蒙古红鲌) | Cyprinidae > Cultrinae | ⭐ Primary |
| *Culter oxycephalus* | 尖头鲌 | Cyprinidae > Cultrinae | ⭐ Primary |
| *Chanodichthys erythropterus* | 红鳍原鲌 | Cyprinidae > Cultrinae | 🔵 Related |
| ***Chanodichthys dabryi*** | **达氏鲌 (青梢红鲌)** | **Cyprinidae > Cultrinae** | **🆕 Added** |
| *Culter oxycephaloides* | 拟尖头鲌 | Cyprinidae > Cultrinae | 🔵 Related |

> **达氏鲌** (*Chanodichthys dabryi*, syn. *Culter dabryi* / *Erythroculter dabryi*) — 别名大眼红鲌、青梢红鲌。分布于黑龙江、辽河、黄河、长江、珠江水系。体长可达 53.1 cm，多栖居于静水湖泊。

---

## 🧬 9-Phase Pipeline

```
Phase 1: 文献调研 (Literature Review)
    └─ 中英双语 → cognitive-search-engine DirectLoader
Phase 2: 年龄与生长 (Age & Growth)
    └─ 鳞片/耳石轮纹 → VBGF 拟合 → 生长参数比较
Phase 3: 基因组学 (Genomics)
    └─ 全基因组/简化基因组 → 组装注释 → 比较基因组
Phase 4: 群体遗传与谱系地理 (Population Genetics)
    └─ 遗传多样性 → 种群结构 → 基因流 → 谱系地理
Phase 5: 同位素与营养生态位 (Trophic Ecology)
    └─ δ¹³C/δ¹⁵N → MixSIAR → 营养级 → 摄食生态
Phase 6: 同域共存 (Sympatric Coexistence)
    └─ 生态位分化 → 资源分割 → 种间竞争
Phase 7: 资源评估 (Stock Assessment)
    └─ CPUE → MSY → YPR → 种群动态
Phase 8: 栖息地模型 (Habitat Modeling)
    └─ HSI → 环境因子 → 产卵场评估
Phase 9: 报告生成 (Report Generation)
    └─ 综合 → 出版级图表
```

---

## 🧠 Skills (8)

| Skill | Description |
|:------|:------------|
| 🔍 `search-literature` | 鲌类中英双语文献检索 — 通过 cognitive-search-engine DirectLoader |
| 📏 `analyze-growth` | 年龄鉴定与生长建模 — 鳞片/耳石轮纹、VBGF 拟合、生长参数比较 |
| 🧬 `analyze-genomics` | 基因组学分析 — 全基因组/简化基因组、组装注释、比较基因组、系统发育基因组 |
| 🧬 `analyze-genetics` | 群体遗传与谱系地理 — 遗传多样性、种群结构、基因流、谱系地理、种群历史 |
| 🌿 `analyze-trophic` | 同位素与营养生态位 — δ¹³C/δ¹⁵N 稳定同位素、MixSIAR 混合模型、营养级 |
| 🔗 `model-coexistence` | 同域共存建模 — 生态位分化量化、资源分割、种间竞争评估 |
| 📊 `assess-resource` | 资源评估 — CPUE 标准化、剩余产量模型、YPR 分析、MSY 估算 |
| 🏞️ `model-habitat` | 栖息地适宜性建模 — HSI 模型、环境因子关联分析、产卵场评估 |

---

## 📡 Search Infrastructure

**DirectLoader Protocol** — searches routed to cognitive-search-engine via `importlib`:

```
CulterAgent.search(query, genus="Culter", species="alburnus")
  └─ CognitiveSearchAdapter.search("Culter", "alburnus", full_pipeline=False)
       ├─ variant_generator.generate()    → OCR variants
       ├─ build_search_queries()          → exact + variants + Chinese names
       └─ ParallelSearch.search_all()     → PubMed × Crossref × OpenAlex
```

> Engine path: `../cognitive-search-engine/src/` · Adapter: `src/adapter.py`

---

## 🧠 Dual-Core Philosophy

> 🧠 **Panta Rhei** (worldview) — knowledge is dynamic, provisional, emergent.
> 🧠 **Systems Thinking** (methodology) — analyze contradictions, concentrate force, advance in phases.

All philosophy mapped to executable code via [Engineering Grammar](docs/ENGINEERING_GRAMMAR.md).

### DeepSeek Efficiency Principles

| ID | Principle | Code Mapping |
|:---|-----------|-------------|
| **DS-1** | **Entropy Budget** — compute proportional to question importance | `pipeline.phases[].activation` |
| **DS-2** | **Sparse Activation** — MoE routing, ~2-4/8 skills active per request | `pipeline.phases[].activation` |
| **DS-3** | **Differential Verification** — P(stale) scoring only changed methods | `verify-stats-handbook` |
| **DS-4** | **Information-Gain Routing** — exact match first → stop on hit | `ima-smart-search` |

---

## 🔗 Linked Projects (Triangle Core + Derived)

| Project | Layer | Role | Description |
|---------|:-----:|------|-------------|
| **eon-core** | **Triangle (T)** | Coordinator | EventBus · Samsara karma · DAG routing · 10-layer kernel |
| **fish-ecology-assistant** | **Triangle V0** | Knowledge | Multi-basin fish DB (Yangtze 443 + Tumen + Suifen) |
| **cognitive-search-engine** | **Triangle V1** | Validation | BDI+ReAct · literature search · authority scoring |
| **porpoise-agent** | **Derived P₁** | Porpoise domain | NBHF acoustics · habitat modeling (sister) |
| **coilia-agent** | **Derived P₂** | Coilia domain | Otolith microchemistry · migration ecology (sister) |
| **conflict-arbiter** | **Derived C** | Conflict arbitration | Multi-source protection-level arbitration |

> **DirectLoader Protocol**: cognitive-search-engine loaded via `importlib` — engine updates auto-propagate, zero MCP overhead.
> Full spec: workspace root `coordination.yaml`.

### 🧠 eon-core Unified Kernel (Workspace Level)

> **10-layer concentric architecture** — OriginKernel → YinYang → 6 Vertices → 8 Trigrams → Tetrahedron → Monitoring → Samsara → Sphere → Tendrils → Evolution.
> Unified coordination by [eon-core](https://github.com/fangtaocai041/eon-core).

```
UNDERSTAND → ROUTE → EXECUTE → VALIDATE → SYNTHESIZE → EVOLVE
 (Macro)     (Meso)   (Micro)   (Cross)     (Merge)     (Feedback)
```

---

## ⚡ Quick Start

```bash
# Standalone
python culter-agent/src/main.py --query "翘嘴鲌 年龄与生长"

# Via workspace project_loader
python -c "from scripts.project_loader import get_culter; a=get_culter(); print(a.info())"

# Via coordinator
python -c "from scripts.coordinator import coordinator; print(coordinator.health('culter'))"
```

---

## 📁 Project Structure

```
culter-agent/
├── README.md                 ← English
├── README.zh.md              ← 中文
│
├── config/
│   ├── agent.yaml            ← Agent behavior (v2.0.0)
│   └── component_registry.yaml
│
├── src/
│   ├── main.py               ← CLI entry point
│   ├── adapter.py             ← IProjectAdapter → CulterAdapter
│   ├── knowledge_base.py     ← Species knowledge retrieval
│   ├── agent/
│   │   └── orchestrator.py   ← 9-phase pipeline orchestrator
│   ├── prompts/
│   │   └── system_prompts.py ← Panta Rhei philosophy prompts
│   └── skills/               ← 8 skill modules (SKILL.md each)
│       ├── search-literature/
│       ├── analyze-growth/
│       ├── analyze-genomics/
│       ├── analyze-genetics/
│       ├── analyze-trophic/
│       ├── model-coexistence/
│       ├── assess-resource/
│       └── model-habitat/
│
├── data/
│   └── knowledge_base/
│       └── species/          ← Species knowledge entries
│
└── scripts/
    └── shared_types.py       ← Shared type definitions
```

---

## 🤝 Human-AI Responsibility Boundary

> Execution is mine. Final judgment is yours.

AI does: search · analyze · generate · flag emergence · suggest revisions
Human does: judge truth · choose methods · set direction · own published results

## 🌱 Panta Rhei · Everything Flows

> Heraclitus: No man ever steps in the same river twice.
>
> We say:
> Lakes change. Fish populations shift. Methods evolve.
> Yesterday's growth parameter is today's baseline. Today's unknown is tomorrow's discovery.
> Our eyes never rest on what is already known.
> Our steps will reach the vast expanse where the stars gather.

## 🗺️ 演进方向 (Personalized Roadmap)

| # | 方向 | 痛点 | 优先级 |
|:--:|------|------|:----:|
| 1 | **鲌类文献双语搜索增强** | 翘嘴鲌/达氏鲌文献分散中英文 | 自动中英双语检索 + 分类学同义名展开 | 🔴 P0 |
| 2 | **基因组分析自动化** | 全基因组/简化基因组数据处理手工 | 自动流水线：质控→组装→注释→比较基因组 | 🔴 P0 |
| 3 | **稳定同位素生态位建模** | δ¹³C/δ¹⁵N 数据手工处理 | 自动 MixSIAR → 营养级 → 生态位重叠量化 | 🟡 P1 |
| 4 | **达氏鲌专题知识库** | 达氏鲌文献分散 | 专门知识库 + 文献集（同义名展开确保全覆盖） | 🟡 P1 |
| 5 | **同域共存量化** | 多种鲌类共存机制不明确 | 生态位分化 + 资源分割 + 时间/空间维度 | 🟢 P2 |

---

## 📋 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v2.1.0** | 2026-06-10 | 🐟 新增达氏鲌 (*Chanodichthys dabryi*), README 全面升级 — 补齐所有标准区块 |
| **v2.0.0** | 2026-06-09 | Initial release — 8 skills · 9-phase pipeline · 5 target species |

> **Latest**: v2.1.0 · 2026-06-10
> **Running on Reasonix Code · Powered by DeepSeek**

---

## 📋 README Changelog

| Version | Date | Theme | What Changed |
|:--------|:-----|:------|:-------------|
| **v2.1** | 2026-06-10 | 全面升级 | + 达氏鲌物种表, + Panta Rhei哲学, + Self-Assessment, + Linked Projects, + Version History, + README Changelog, + Roadmap, + DeepSeek效率原则, + 全部 badge |
| **v2.0** | 2026-06-09 | Initial | 初始版本 · 8 skills · 9-phase pipeline · 5 species |

---

## 📜 License

MIT License © 2026 fangtaocai041
