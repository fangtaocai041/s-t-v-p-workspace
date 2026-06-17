# Porpoise Agent 🐬

**P₁ 万物衍生** — Yangtze Finless Porpoise Research · Multi-Agent System · BDI Decision · 5 Cognitive Layers

> 🌊 Everything Flows · Panta Rhei
>
> The finless porpoise has swum the Yangtze for 25 million years.
> Our code is another language trying to understand them.

[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![version](https://img.shields.io/badge/version-0.1.0-8b5cf6)]()
[![agents](https://img.shields.io/badge/agents-7-f59e0b)]()

[English](README.md) · [中文](README_en.md) · [Changelog](CHANGELOG.md)

---

## 📋 Introduction

**Porpoise Agent** is an AI Agent framework for Yangtze finless porpoise (*Neophocaena asiaeorientalis asiaeorientalis*) research, built on a **Multi-Agent System (MAS)** with a **BDI cognitive architecture** and **5-layer dimensional evolution engine**. It automates literature search, NBHF acoustic analysis, ecological modeling, and conservation assessment.

### 🚀 Capabilities

| 🚀 Capability | 📝 Description |
|:--------------|:---------------|
| 🧠 **Multi-Agent System** | 7 specialized agents: Orchestrator, Literature, Acoustic, Ecology, Conservation, Critic + Topology |
| 🔍 **BDI Decision Engine** | Belief-Desire-Intention state machine — `BDICoordinator` |
| 📚 **Three-Tier Memory** | STM (context) + LTM (ChromaDB vector store) + Manager |
| 🔄 **Dimensional Evolution** | 5-layer cognitive architecture: Loop → MesoExperiment → ResilienceEngine → STVCore → DimensionalEvolution |
| 🔌 **Quadruple Integration** | cognitive-search-engine, Neo4j, Zotero, Obsidian |
| 🛡️ **Sandbox Execution** | Isolated Python runtime via `SandboxExecutor` |
| 🧪 **Test Coverage** | BDI state machine + Memory + Serializer + workflow scenarios |

---

## ⚡ Quick Start

### 📦 Installation

```bash
git clone https://github.com/FFRC-LiuKai-Lab/porpoise-agent.git
cd porpoise-agent
pip install -e .
```

### ✅ Verify Installation

```python
from porpoise_agent.src.agents import OrchestratorAgent

orch = OrchestratorAgent()
print(f"Agents registered: {len(orch.list_agents())}")
```

### 🎮 CLI Usage

```bash
porpoise doctor         # Health check
porpoise topology       # Show MAS topology
porpoise chat           # Interactive chat mode
porpoise run TASK       # Run a single research task
```

---

## 🚀 Core Features

### 1️⃣ Multi-Agent System

```python
from porpoise_agent.src.agents import (
    OrchestratorAgent, LiteratureAgent, AcousticAgent,
    EcologyAgent, ConservationAgent, CriticAgent,
)

orch = OrchestratorAgent()
orch.register_agent(LiteratureAgent())
orch.register_agent(AcousticAgent())
orch.register_agent(EcologyAgent())
orch.register_agent(ConservationAgent())
orch.register_agent(CriticAgent())

result = orch.run("Analyze porpoise population status")
```

### 2️⃣ BDI Decision Making

```python
from porpoise_agent.src.cognitive import BDICoordinator, Belief, Desire

bdi = BDICoordinator()
bdi.add_belief(Belief("species", "Neophocaena asiaeorientalis"))
bdi.add_belief(Belief("population", 1200))
bdi.add_desire(Desire("assess_threat", priority=0.9,
                       condition=lambda b: b.get("population", 0) < 1500))
plan = bdi.deliberate()
```

### 3️⃣ Memory System

```python
from porpoise_agent.src.memory import MemoryManager

memory = MemoryManager()
memory.stm.store("last_query", "porpoise habitat")
memory.ltm.store_document("paper_001", "Acoustic analysis of finless porpoise")
results = memory.ltm.search("acoustic", top_k=5)
```

### 4️⃣ Sandbox Execution

```python
from porpoise_agent.src.execution import execute_safe

result = execute_safe("print(f'Mean: {sum([1,2,3,4,5])/5}')")
print(result.output)
```

---

## 🎮 CLI Commands

| 🎮 Command | 📝 Description | 💡 Example |
|:-----------|:---------------|:-----------|
| `porpoise chat` | Interactive chat (ReAct loop) | `porpoise chat --model deepseek-reasoner` |
| `porpoise run TASK` | Single research task | `porpoise run "Analyze acoustic data"` |
| `porpoise topology` | Show MAS topology | `porpoise topology` |
| `porpoise doctor` | Health check | `porpoise doctor` |

---

## 📚 Project Structure

```
porpoise-agent/
├── src/
│   ├── cli.py                    ← CLI 入口 (porpoise doctor/chat/run/topology)
│   ├── agents/                   ← Multi-Agent System (7 agents)
│   │   ├── orchestrator.py       ← OrchestratorAgent 调度器
│   │   ├── literature.py         ← LiteratureAgent 文献搜索
│   │   ├── acoustic.py           ← AcousticAgent NBHF 声学分析
│   │   ├── ecology.py            ← EcologyAgent 栖息地评估
│   │   ├── conservation.py       ← ConservationAgent 保护建议
│   │   ├── critic.py             ← CriticAgent 自反思审查
│   │   ├── topology.py           ← MAS 拓扑管理
│   │   └── base.py               ← BaseAgent 基类
│   ├── agent/                    ← 5 层认知架构
│   │   ├── orchestrator.py       ← 领域编排器
│   │   ├── loop.py               ← ReAct 循环
│   │   ├── meso_experiment.py    ← 中层实验引擎
│   │   ├── resilience_engine.py  ← 韧性引擎
│   │   ├── stv_core.py           ← STV 核心
│   │   ├── dimensional_evolution.py ← 维度进化
│   │   ├── memory.py             ← 记忆管理
│   │   ├── tools.py              ← 工具注册
│   │   └── deepseek_optimizer.py ← DeepSeek 优化器
│   ├── cognitive/                ← BDI + ReAct + TaskDecomposer
│   ├── memory/                   ← STM + LTM (ChromaDB) + Manager
│   ├── execution/                ← Sandbox + ToolRegistry + APIClient
│   ├── interaction/              ← NLU 意图识别 + Response 渲染
│   ├── mapping/                  ← Router + Serializer + Validator
│   ├── integration/              ← 外部系统桥接
│   ├── knowledge/                ← 知识图谱
│   ├── prompts/                  ← 系统提示词
│   ├── skills/                   ← 技能模块
│   ├── tools/                    ← 工具集
│   └── utils/                    ← Config + logging + types
├── config/                       ← agent.yaml / models.yaml / mcp_servers.yaml
├── data/                         ← 知识库数据
├── docs/                         ← 文档
├── examples/                     ← 示例脚本
├── external/                     ← 外部依赖
├── scripts/                      ← 工具脚本
└── tests/                        ← 5 测试套件
```

---

## 🔌 External Integrations

| 🖥️ System | 🔗 Adapter | 🎯 Purpose |
|:----------|:-----------|:-----------|
| **cognitive-search-engine** | `CognitiveSearchAdapter` | Multi-engine literature search |
| **Neo4j Knowledge Graph** | `KnowledgeGraph` | Species relationship storage |
| **Zotero** | `ZoteroAdapter` | Research library access |
| **Obsidian** | `ObsidianAdapter` | Personal knowledge base |

---

## 🔗 Related Projects
```
| 🏗️ Project | 🎯 Role | 🔗 Relationship |
|:-----------|:--------|:----------------|
| **eon-core** | Coordinator | Vertex V2 — porpoise domain agent |
| **fish-ecology-assistant** | Knowledge V0 | Species knowledge base |
| **cognitive-search-engine** | Search V1 | Literature search and scoring |
| **coilia-agent** | P₂ Coilia | Sister project |
| **culter-agent** | P₃ Culter | Sister project |
```

---
```
## 📜 License
```
MIT License © 2026 Liu Kai Research Group, FFRC-----------|:--------:|:--------|
| [fish-ecology-assistant](../fish-ecology-assistant/) | V0 | 📦 Knowledge Supply |
| [cognitive-search-engine](../cognitive-search-engine/) | V1 | 🔍 Search Verification |
| [eon-core](../eon-core/) | Coord | ⚙️ Coordinator |
| [porpoise-agent](../porpoise-agent/) | P₁ | 🐬 Porpoise Research |
| [coilia-agent](../coilia-agent/) | P₂ | 🐟 Coilia Research |
| [culter-agent](../culter-agent/) | P₃ | 🐟 Culter Research |
| [conflict-arbiter](../conflict-arbiter/) | C | 🔥 Conflict Arbiter |
```

---
---

```
## 🔗 Ecosystem
```
> 🔥 Together infinite power, apart top expert engines.
```
This project is the Porpoise Domain Expert Engine (P1) in the SanShengWanWu ecosystem.
```
```
Triangle Core (sealed 3):
  📦 fish-ecology-assistant    → Knowledge Supply (V0)
  🔍 cognitive-search-engine   → Search Verification (V1)
  ⚙️ eon-core                  → Coordinator
```
Derived Projects (open N):
  🐬 porpoise-agent    → Porpoise Research (P₁)
  🐟 coilia-agent      → Coilia Research (P₂)
  🐟 culter-agent      → Culter Research (P₃)
  🔥 conflict-arbiter  → Conflict Arbitration (C)
```

> 🌊 Everything Flows · Panta Rhei
>
> 🏛️ Heraclitus said: No man ever steps in the same river twice.
>
> 💻 We say: You can't analyze today's porpoise data with last month's code.
>
> **📅 Last updated: 2026-06-17 · 🖥️ Reasonix Code · ⚡ Powered by DeepSeek**

[⬆ Back to top](#)
