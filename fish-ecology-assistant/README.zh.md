# Fish Ecology Assistant 🌊

> 🌊 万物皆变 · Panta Rhei
>
> 把你的编码智能体变成拥有动态世界观的博士级研究团队。
>
> 🛠️ **16 MCP 工具** · 🤖 **12 AI 子智能体** · 🔍 **5 引擎搜索** · 📚 **13 个知识库**

[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Reasonix](https://img.shields.io/badge/Reasonix-Code-brightgreen)](https://reasonix.ai)
[![species](https://img.shields.io/badge/species-30-green)]()

[English](README.md) · [中文](README.zh.md) · [更新日志](CHANGELOG.md) · [架构](docs/ARCHITECTURE.md)

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

## ⚡ 快速上手

```bash
git clone https://github.com/fangtaocai041/fish-ecology-assistant
cd fish-ecology-assistant
powershell -ExecutionPolicy Bypass -File setup.ps1
```

🔄 重启 Reasonix，全部就绪。你🎤说，它⚡做。

| 🎤 你说 | ⚡ 它做什么 |
|:--------|:-----------|
| "研究长江禁渔对鱼类群落的影响，跑流水线" | 5 阶段：📋规划 → 🔍搜索 → 🧠分析 → ✍️写作 → ✅审查（中英双语搜索，自动标记涌现信号）|
| "验证手册 2.2 章" | 自动查 CRAN 📦包版本，比对手册，计算📅复查日期 |
| "查一下鳤的文献" | 自动路由到正确知识库，多库并行搜索，合成结果 |
| "帮我做个同位素分析" | R 代码 + 方法选择 + 诊断，标记截至 YYYY-MM 的推荐做法 |

---

## 🤖 AI 子智能体

### 🔄 研究流水线（5 阶段自动编排 · 🌊 动态世界观贯穿）

| 🤖 智能体 | 🎯 角色 | ⚙️ 功能 | 🌊 哲学体现 |
|:----------|:--------|:---------|:-----------|
| **🎯 research-orchestrator** | 调度 | 调度全部 5 阶段 | — |
| **📋 research-planner** | 规划 | 中英双语关键词，覆盖国内外文献 | 🌐 全面覆盖 |
| **🔍 research-executor** | 搜索 | 5 引擎并行，标注文献发表年份 | ⏳ 时间轴感知 |
| **🧠 research-analyst** | 分析 | 共识演变时间轴 + 涌现信号检测 | 🔄 动态共识 · 🌟 涌现 |
| **✍️ research-writer** | 写作 | calibrated language，时间锚定，不确定性标记 | 📖 校准语言 · ⏰ 知识暂时性 |
| **✅ research-reviewer** | 审查 | 4 维评分，最多 3 轮修订 | 🔄 质量控制闭环 |

### 🧪 领域专家智能体

| 🤖 智能体 | ⚙️ 功能 | 🌊 哲学体现 |
|:----------|:---------|:-----------|
| **📄 paper-analyzer** | 深度分析单篇论文 | ⏳ 时间轴 · 🌟 涌现信号 |
| **📊 stats-assistant** | R 代码 + 方法选择 | 📦 版本标注 · ✅ 方法标注验证日期 |
| **🔎 stats-method-finder** | 搜索 CRAN/期刊标记方法 | ⏰ 方法的"最后验证时间" |
| **💡 ima-smart-search** | 跨知识库智能搜索 | 🔄 动态发现 KB，不过期不硬编码 |
| **✅ verify-stats-handbook** | 自动查 CRAN 包版本 | 📊 按活跃度算复查周期 |
| **🔭 frontier-tracker** | 跟踪前沿，时间排序 | 🧪 实验室最新发现 |
| **📝 phd-proposal-writer** | 博士论文计划书 | 📋 动态履历，标注时效性 |
| **📚 zotero-assistant** | 查 Zotero 文献库 | — |
| **📓 obsidian-assistant** | 导出到 Obsidian 笔记 | — |

---

## 🛠️ MCP 服务（16 个工具）

| 🛠️ 服务 | 🎯 用途 |
|:---------|:--------|
| **🤖 tavily** | AI 深度搜索 |
| **🔍 exa** | 语义搜索 |
| **🎓 google-scholar** | 学术论文 |
| **📰 article** | 文献元数据 |
| **🌐 scholarly** | 多源聚合 |
| **🧠 ima** | 13 个知识库 + IMA 笔记 + OpenAPI（14 个工具）|
| **📊 rplay** | R 4.6.0（形态测量、同位素、群落生态）|
| **💻 coderunner** | 多语言沙箱代码执行 |
| **📈 echarts** | ECharts 可视化 |
| **👁️ PaddleOCR** | 中英文 OCR |
| **🔤 Tesseract.js fallback** | 离线 OCR 备用 |
| **🎭 playwright** | Chromium 网页抓取 |
| **🔧 git** | Git CLI（版本控制）|
| **🐙 github** | GitHub API（仓库管理）|
| **📖 Zotero** | SQLite 文献库查询 |

---

## 📁 项目结构

```
fish-ecology-assistant/
├── 📄 README.md                       主文档（英文）
├── 📄 README.zh.md                    主文档（中文）
├── 📁 .reasonix/
│   ├── 📁 mcp-servers/               ← 16 个 MCP 服务
│   │   ├── 🧠 ima-server.mjs           IMA 知识库
│   │   └── ...                         其余 14 个
│   ├── 📁 skills/                    ← 12 个 AI 子智能体
│   │   ├── 💡 ima-smart-search.md
│   │   ├── ✅ verify-stats-handbook.md
│   │   ├── 📄 paper-analyzer.md
│   │   ├── 🧠 research-analyst.md
│   │   ├── ✍️ research-writer.md
│   │   └── ...                         其余 7 个技能
│   └── 📁 handbooks/
│       ├── 📊 stats-methods.md         统计方法全手册
│       └── 📖 learning-guide.md        学习指南
├── 📁 research_output/                 生成的分析报告
└── ⚡ setup.ps1                        一键安装脚本
```---


## 🔗 生态体系

> 🔥 和则无穷力量，分则顶尖专家引擎。

本项目是「三生万物」生态的 V0。

```
三角核心 (sealed 3):
  📦 fish-ecology-assistant    → 知识供给 (V0)
  🔍 cognitive-search-engine   → 搜索验证 (V1)
  ⚙️ eon-core                  → 协调内核 (Coord)

万物衍生 (open N):
  🐬 porpoise-agent    → 江豚专研 (P₁)
  🐟 coilia-agent      → 刀鲚专研 (P₂)
  🐟 culter-agent      → 鲌类专研 (P₃)
  🔥 conflict-arbiter  → 冲突仲裁 (C)
```

> 🌊 万物皆变 · Panta Rhei
>
> 🏛️ 赫拉克利特说：人不能两次踏进同一条河流。
>
> 💻 我们说：你也不能用上个月的代码分析今天的生态数据。
>
> 🔄 这个项目不是一套固定的工具集——它是一个活的系统。每个组件都内置了过期机制、版本追踪和涌现感知。随着你的研究深入、R 包更新、新方法涌现，它会和你一起进化。
>
> **📅 最后更新: 2026-06-17 · 🖥️ 适用环境: Reasonix Code · ⚡ DeepSeek 驱动**

[⬆ 回到顶部](#)
