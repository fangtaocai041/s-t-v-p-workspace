![Python 3.10+](https://img.shields.io/badge/Python%203.10%2B-3776AB?style=flat-square)
  ![MIT](https://img.shields.io/badge/MIT-34D058?style=flat-square)
  ![v8.1](https://img.shields.io/badge/v8.1-8A4FCE?style=flat-square)
  ![430 species](https://img.shields.io/badge/430%20species-007EC6?style=flat-square)
  ![289 traits](https://img.shields.io/badge/289%20traits-FE7D37?style=flat-square)
  ![FISHMORPH](https://img.shields.io/badge/FISHMORPH-0EA5E9?style=flat-square)
  ![population-level](https://img.shields.io/badge/population-level-D73A4A?style=flat-square)
  ![CN-EN](https://img.shields.io/badge/CN-EN-EC4899?style=flat-square)
  ![SQLite](https://img.shields.io/badge/SQLite-6B7280?style=flat-square)
</p>

[English](README.md) · [中文](README.zh.md)

<div align="center"><h3>🌊 万物皆流。</h3></div>

世界是动态的，知识是暂时的，涌现是常态。

---
## 📖 目录

- [哲学](#-哲学)
- [快速开始](#-快速开始)
- [架构](#-架构)
- [功能特性](#-功能特性)
- [项目结构](#-项目结构)
- [生态体系](#-生态体系)

---

## 🎯 核心哲学

> 🌍 世界是动态的，📖 知识是暂时的，🌟 涌现是常态。

这不是一句口号，而是贯穿整个项目每一行代码、每一次搜索、每一篇分析的操作系统。

### 📜 三大信条

**🌍 世界是动态的** — R 包在更新，物种分布在变化，科学共识在演变，气候变化在重塑生态系统。今天正确的结论半年后可能过时。我们不把任何知识当作永恒真理，而是放在时间轴上动态看待。

**📖 知识是暂时的** — 科学精神的基石是证伪主义（Popper）。没有发现是终极真理，只有"当前最佳解释"。我们使用 calibrated language（校准语言）——说"证据表明"而不说"证明了"，说"Smith(2022) 发现"而不说"研究表明"。每一个输出都标注时间锚点。

**🌟 涌现是常态** — 生命、意识、生态系统、AI 推理能力——都是涌现的结果。单独分析局部拼凑不出整体。当 ≥3 个独立来源指向同一个非预期模式时，系统自动标记为涌现信号，而不是当成异常值忽略。

### ⚖️ 为什么这对科研至关重要

| 🎯 场景 | ❌ 传统做法 | ✅ 动态世界观的做法 |
|:---------|:------------|:------------------|
| 📦 包版本 | 跑 2020 年的代码，不管版本差 | 包版本自动检查，标注"最后验证于 glmmTMB v1.1.10" |
| 📝 引用 | "研究表明确实如此" | "Smith(2022) 发现 X，但 Jones(2024) 补充了 Y" |
| 📊 异常值 | 忽略，当噪声 | ≥3 个独立来源 → 涌现信号，主动追踪 |
| ⏰ 知识过期 | 手册写死，不再更新 | 验证记录含"下次复查日期"，按包活跃度动态计算 |
| 🔧 方法选择 | 固定方法用到死 | 方法动态选择，置信度动态计算 |

---

## 🧩 这个项目是什么

**Fish Ecology Assistant** 是一个将 Reasonix Code 从通用编码助手转变为专业鱼类生态学研究团队的完整配置包。

它集成了 **16 个 MCP 工具**、**12 个领域 AI 子智能体**、**5 引擎并行搜索**、自动化的 **5 阶段研究流水线**，以及 **R 统计计算环境**——所有输出都遵循上述动态世界观。

### 📊 能力清单

| 🚀 能力 | ✨ 加上本配置 | 💭 原生 Reasonix |
|:---------|:-------------|:-----------------|
| 🔍 搜索 | 5 个 (tavily, exa, google-scholar, article, scholarly) | 1 个 (web_search) |
| 🤖 AI 子智能体 | 12 个（领域专用，含涌现检测）| 4 个（通用）|
| 📊 R 统计 | R 4.6.0 + 20+ 生态学包 | — |
| 👁️ OCR | PaddleOCR + Tesseract.js | — |
| 📚 文献 | Zotero 直接查询 | — |
| ✍️ 写作 | 5 阶段 + 自动审查 + 涌现检测 | — |
| 🏛️ 知识库 | 连接 13 个 IMA 知识库 | — |
| ⚡ 装机 | 手动？一个脚本，5 分钟 | — |

---

## 🧩 这个项目是什么

**Fish Ecology Assistant** 是一个将 Reasonix Code 从通用编码助手转变为专业鱼类生态学研究团队的完整配置包。

它集成了 **16 个 MCP 工具**、**12 个领域 AI 子智能体**、**5 引擎并行搜索**、自动化的 **5 阶段研究流水线**，以及 **R 统计计算环境**——所有输出都遵循上述动态世界观。

### 📊 能力清单

| 🚀 能力 | ✨ 加上本配置 | 💭 原生 Reasonix |
|:---------|:-------------|:-----------------|
| 🔍 搜索 | 5 个 (tavily, exa, google-scholar, article, scholarly) | 1 个 (web_search) |
| 🤖 AI 子智能体 | 12 个（领域专用，含涌现检测）| 4 个（通用）|
| 📊 R 统计 | R 4.6.0 + 20+ 生态学包 | — |
| 👁️ OCR | PaddleOCR + Tesseract.js | — |
| 📚 文献 | Zotero 直接查询 | — |
| ✍️ 写作 | 5 阶段 + 自动审查 + 涌现检测 | — |
| 🏛️ 知识库 | 连接 13 个 IMA 知识库 | — |
| ⚡ 装机 | 手动？一个脚本，5 分钟 | — |

---


## 📜 三大信条

**🌍 世界是动态的** — R包在更新，物种分布变化，科学共识在演进。今天正确的结论，六个月后可能过时。

**📖 知识是暂时的** — 科学的基石是可证伪（波普尔）。没有发现是终极真理——只有当前最佳解释。我们用校准语言：证据表明，而非证明。

**🌟 涌现是常态** — 生命、意识、生态系统、AI推理——都是涌现现象。当≥3个独立来源指向同一意外模式，系统标记为涌现信号。

### ⚖️ 为什么这对研究很重要

| 场景 | 传统做法 | 动态世界观 |
|:-----|:--------|:----------|
| 引用 | 研究证明 | Smith(2022)发现X，Jones(2024)补充Y |
| 异常值 | 当作噪声 | ≥3来源→涌现信号 |
| 知识衰减 | 手册冻结 | 含下次审查日期 |

> 道生一，一生二，二生三，三生万物。

这是三角之核心，承载 430 种长江鱼类。


## 🚀 快速开始

```bash
git clone git@github.com:fangtaocai041/fish-ecology-assistant.git
cd fish-ecology-assistant
pip install -e .
python src/main.py search --species "刀鲚"
```

---

## 🏗️ 架构

```
fish-ecology-assistant/
  src/           核心 Python 引擎
  ├── adapter.py     IProjectAdapter 标准接口
  ├── orchestrator.py    KB-First 物种搜索
  ├── project_hub.py     跨项目协调中枢
  ├── dao_engine.py      哲学链执行引擎
  ├── types.py           8 个 dataclass + 4 个枚举
  └── kalman_emergence.py 卡尔曼滤波涌现检测
  config/
  ├── knowledge_base/   30 种 .md 物种档案
  └── fish_species_kb.yaml  430 种索引
  data/
  ├── species.db         SQLite (物种+性状+文献)
  ├── FISHMORPH.csv      2.3MB 全球形态数据库
  └── reports/           HTML/CSV 导出
  scripts/
  ├── fishbase_pull.py   FishBase API 自动同步
  ├── trait_network.py   网络科学性状分析
  └── gen_report.py      双语 HTML 报告生成器
```

---

## ✨ 功能特性

| 功能 | 状态 | 说明 |
|------|:--:|------|
| 🗃️ 430 物种库 | ✅ | 长江鱼类 + 双语保护等级 |
| 📏 289 形态性状 | ✅ | FISHMORPH(251) + FishBase + FAO + 手动 |
| 🌊 种群级数据 | ✅ | 26条含水域标注 |
| 🔬 性状目录 | ✅ | 61项性状分7大类 |
| 🏛️ 保护等级 | ✅ | IUCN + 中国红皮书 + 国家重点 + CITES |
| 📊 Excel/HTML | ✅ | 双语报告，双层表头 |
| 🔗 KB-First | ✅ | SQLite FTS5，30种核心零网络 |
| 🕸️ 性状网络 | ✅ | Jaccard共现，关键性状识别 |
| 📡 卡尔曼滤波 | ✅ | 噪声数据涌现检测 |
| 🔄 FishBase同步 | 🟡 | 脚本就绪，SSL环境限制 |

---

## 📁 项目结构

```
fish-ecology-assistant/
  (见上方架构图)
```

---

## 🔗 生态体系

本项目是「三生万物」生态的 知识供给核心 (V0)。

```
三角核心 (sealed 3):
  📦 fish-ecology-assistant    → 知识供给 (V0)
  🔍 cognitive-search-engine   → 搜索验证 (V1)
  ⚙️ eon-core                  → 协调内核 (Coord)

万物衍生 (open N):
  🐬 porpoise-agent    → P₁ 江豚专研
  🐟 coilia-agent      → P₂ 刀鲚专研
  🐟 culter-agent      → P₃ 鲌类专研
  🔥 conflict-arbiter  → C  冲突仲裁
```

> 🔥 和则无穷力量，分则顶尖专家引擎。

---

🌱 **万物皆变 · Panta Rhei**

> 赫拉克利特说：人不能两次踏进同一条河流。
>
> 我们说：你也不能用上个月的代码分析今天的生态数据。

这个项目不是一套固定的工具集——它是一个**活的系统**。每个组件都内置了过期机制、版本追踪和涌现感知。随着你的研究深入、R包更新、新方法涌现，它会和你一起进化。

*最后更新：2026-06-17　|　适用环境：Reasonix Code · DeepSeek 驱动*

