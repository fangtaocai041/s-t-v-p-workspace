# 🐬 江豚智能体

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge) ![协议](https://img.shields.io/badge/%E5%8D%8F%E8%AE%AE-MIT-brightgreen?style=for-the-badge) ![版本](https://img.shields.io/badge/%E7%89%88%E6%9C%AC-v0.2-blueviolet?style=for-the-badge) ![智能体](https://img.shields.io/badge/%E6%99%BA%E8%83%BD%E4%BD%93-7%E4%BD%93-success?style=for-the-badge) ![架构](https://img.shields.io/badge/%E6%9E%B6%E6%9E%84-%E4%BA%94%E5%B1%82-important?style=for-the-badge) ![BDI](https://img.shields.io/badge/BDI-ReAct-critical?style=for-the-badge) ![GoT](https://img.shields.io/badge/GoT-MCTS-informational?style=for-the-badge) ![SSE](https://img.shields.io/badge/SSE-%E6%B5%81%E5%BC%8F-ff69b4?style=for-the-badge) ![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-orange?style=for-the-badge) ![StateGraph](https://img.shields.io/badge/StateGraph-LangGraph-red?style=for-the-badge)

> 🎯 江豚领域专家引擎 — 5层认知架构，BDI+ReAct+Reflexion，7智能体MAS，前沿技术。
🎯 江豚领域专家引擎 — 五层认知架构，BDI+ReAct+Reflexion，七智能体。
> 江豚知江河，智能体知领域。

[English](README.md) · [中文](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 📖 目录

- [哲学](#-哲学)
- [快速开始](#-快速开始)
- [架构](#-架构)
- [功能特性](#-功能特性)
- [项目结构](#-项目结构)
- [生态体系](#-生态体系)

---

## 🏛️ 哲学

> 万象流转，真知若寄，涌现成章。

此非口号。乃贯穿每一行代码、每一次检索、每一份分析之操作系统。

### 📜 三谛

**🌊 万象流转** — R包迭代，物种迁徙，共识更迭，气候重塑生态。今日之确论，半载后或为陈迹。吾辈不视任何知识为永恒真理，而将其置于时间轴上，以动态眼光审之。

**🍂 真知若寄** — 科学之基石，在于可证伪（波普尔）。无发现乃终极真理——唯有「当下最佳解释」。吾辈用校准之语：「证据提示」而非「证明」，「Smith (2022) 发现」而非「研究表明」。每一条输出，皆镌刻时间之锚。

**🌟 涌现成章** — 生命、意识、生态、AI推理——莫非涌现。不可执一隅以窥全豹。当≥3个独立来源指向同一意外模式，系统不以其为噪声而弃之，乃标记为涌现信号而追踪之。

### ⚖️ 何以重要

| 事境 | 旧习 | 新观 |
|:-----|:----|:----|
| 引用 | 「研究证明」 | 「Smith(2022) 发现 X，Jones(2024) 补 Y」 |
| 异常 | 视为噪声弃之 | ≥3 来源 → 涌现信号，持续追踪 |
| 知识衰减 | 手册尘封不更 | 审查记录含「下次审查日期」 |
| 方法选择 | 流水线一成不变 | 择法动态，信心动态 |

> 道生一，一生二，二生三，三生万物。

此为三角之根，载 430 种长江鱼类。


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
git clone git@github.com:fangtaocai041/porpoise-agent.git
cd porpoise-agent
pip install -e .
python src/cli.py chat "分析长江江豚声学数据"
```

---

## 🏗️ 架构

```
porpoise-agent/
  src/
  ├── interaction/     L1 — NLU意图解析 + Markdown渲染
  │   └── sse_emitter.py   SSE 流式输出
  ├── cognitive/       L2 — BDI + ReAct + Reflexion + 任务分解
  │   ├── bdi.py            形式化BDI (MDP对应)
  │   ├── react_loop.py     Think→Act→Observe→Reflect 引擎
  │   ├── reflexion.py      信用分配 + 自我批判
  │   ├── decomposer.py     CoT/ToT/GoT 任务分解
  │   ├── search.py         BFS/DFS/Beam/MCTS 思维空间搜索
  │   └── stategraph.py     LangGraph 风格 StateGraph 拓扑
  ├── memory/          L3 — 短期记忆 + 长期记忆 (ChromaDB RAG)
  ├── mapping/         L4 — 意图路由 + 序列化 + 验证
  ├── execution/       L5 — 沙盒 + 工具注册 + API客户端
  ├── agents/          7 个专业智能体 + 图拓扑
  └── integration/     4 个适配器
```

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🧠 BDI+ReAct+Reflexion | 形式化认知循环 (MDP对应) |
| 🌳 CoT/ToT/GoT/MCTS | 多种任务分解和搜索策略 |
| 🕸️ StateGraph | LangGraph风格条件边路由 |
| 🔴 SSE 流式 | 实时智能体输出 |
| 🗄️ ChromaDB RAG | 向量长期记忆+优雅降级 |
| 🔧 7-Agent MAS | 文献/声学/生态/保护/批判... |
| 🔀 6种拓扑类型 | 顺序/层级/星形/辩论/DAG/动态 |
| 🔒 子进程沙盒 | 安全代码执行 |
| 📚 4项集成 | cognitive-search, Zotero, Obsidian, Neo4j |

---

## 📁 项目结构

```
porpoise-agent/
  (见上方架构图)
```

---

## 🔗 生态体系

本项目是「三生万物」生态的 江豚领域专家引擎 (P₁)。

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

