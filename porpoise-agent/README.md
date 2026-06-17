# 🐬 Porpoise Agent

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge) ![Version](https://img.shields.io/badge/Version-v0.2-blueviolet?style=for-the-badge) ![Agents](https://img.shields.io/badge/Agents-7-MAS-success?style=for-the-badge) ![Arch](https://img.shields.io/badge/Arch-5-Layer-important?style=for-the-badge) ![BDI](https://img.shields.io/badge/BDI-ReAct-critical?style=for-the-badge) ![GoT](https://img.shields.io/badge/GoT-MCTS-informational?style=for-the-badge) ![SSE](https://img.shields.io/badge/SSE-Streaming-ff69b4?style=for-the-badge) ![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-orange?style=for-the-badge) ![StateGraph](https://img.shields.io/badge/StateGraph-LangGraph-red?style=for-the-badge)

> 🎯 Porpoise Domain Expert Engine — 5-layer cognitive architecture with BDI+ReAct+Reflexion, 7-agent MAS, and frontier techniques.
> A porpoise knows the river — an agent knows the domain.

[English](README.md) · [中文](README.zh.md) · [CHANGELOG](CHANGELOG.md)

---

## 📖 Table of Contents

- [Philosophy](#-philosophy)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Ecosystem](#-ecosystem)

---

## 🏛️ Philosophy

> The river flows, knowledge drifts, emergence patterns.

This is not a slogan. It is the operating system running through every line of code, every search, every analysis.

### 📜 Three Tenets

**🌊 The River Flows** — Packages update, species migrate, consensus shifts, climate reshapes. Today's certainty is tomorrow's footnote. We place knowledge on a timeline and view it dynamically.

**🍂 Knowledge Drifts** — The foundation of science is falsifiability (Popper). No discovery is final — only the best current explanation. We speak in calibrated language: evidence suggests, not proves.

**🌟 Emergence Patterns** — Life, consciousness, ecosystems, AI reasoning — all emergent. When three or more independent sources converge on the same unexpected pattern, the system flags emergence — never dismisses it as noise.

### ⚖️ Why This Matters

| Scenario | Traditional | Dynamic Worldview |
|:---------|:-----------|:-------------------|
| Citations | Studies prove | Smith (2022) found X; Jones (2024) added Y |
| Outliers | Dismiss as noise | Three or more sources → emergence signal |
| Knowledge Decay | Handbook frozen | Review records include next review date |
| Method | Fixed pipeline | Dynamic selection, dynamic confidence |

> 道生一，一生二，二生三，三生万物。

From One comes Two, from Two comes Three, from Three come all things.


## 📜 Three Tenets

**🌍 The world is dynamic** — R packages update, species distributions shift, scientific consensus evolves, climate change reshapes ecosystems. A correct conclusion today may be outdated in six months.

**📖 Knowledge is temporary** — The foundation of science is falsification (Popper). No discovery is ultimate truth—only the best current explanation. We use calibrated language: evidence suggests not proves.

**🌟 Emergence is the norm** — Life, consciousness, ecosystems, AI reasoning—all are emergent phenomena. When >=3 independent sources point to the same unexpected pattern, the system flags it as an emergence signal.

### ⚖️ Why This Matters

| Scenario | Traditional | Dynamic Worldview |
|:---------|:-----------|:------------------|
| Citations | Studies prove it | Smith (2022) found X, Jones (2024) added Y |
| Outliers | Ignore as noise | >=3 sources → emergence signal |
| Knowledge decay | Handbook frozen | Review records include Next review date |

> 道生一，一生二，二生三，三生万物。

This is the **S-state (V0)** of the Triangle — Knowledge Supply, holding 430 Yangtze fish species.


## 🚀 Quick Start

```bash
# Clone
git clone git@github.com:fangtaocai041/porpoise-agent.git
cd porpoise-agent

# Install
pip install -e .

# Run
python src/cli.py chat "Analyze finless porpoise acoustic data"
```

---

## 🏗️ Architecture

```
porpoise-agent/
  src/
  ├── interaction/     L1 — NLU intent parser + Markdown renderer
  │   └── sse_emitter.py   SSE streaming output
  ├── cognitive/       L2 — BDI + ReAct + Reflexion + Decomposer (CoT/ToT/GoT)
  │   ├── bdi.py            Formal BDI with MDP correspondence
  │   ├── react_loop.py     Think→Act→Observe→Reflect engine
  │   ├── reflexion.py      Credit assignment + self-critique
  │   ├── decomposer.py     CoT/ToT/GoT task decomposition
  │   ├── search.py         BFS/DFS/Beam/MCTS thought-space search
  │   └── stategraph.py     LangGraph-inspired StateGraph topology
  ├── memory/          L3 — STM + LTM (ChromaDB RAG)
  ├── mapping/         L4 — IntentRouter + Serializer + Validator
  ├── execution/       L5 — Sandbox + ToolRegistry + APIClient
  ├── agents/          7 specialized agents with graph topology
  └── integration/     4 adapters (cognitive-search/Zotero/Obsidian/Neo4j)
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 BDI+ReAct+Reflexion | Formal cognitive loop with MDP correspondence |
| 🌳 CoT/ToT/GoT/MCTS | Multiple task decomposition and search strategies |
| 🕸️ StateGraph | LangGraph-inspired conditional edge routing |
| 🔴 SSE Streaming | Real-time agent output via Server-Sent Events |
| 🗄️ ChromaDB RAG | Vector-backed long-term memory with graceful degradation |
| 🔧 7-Agent MAS | Literature, Acoustic, Ecology, Conservation, Critic... |
| 🔀 6 Topology Types | Sequential, Hierarchical, Star, Debate, DAG, Dynamic |
| 🔒 Subprocess Sandbox | Safe code execution with import whitelist |
| 📚 4 Integrations | cognitive-search, Zotero, Obsidian, Neo4j/KnowledgeGraph |

---

## 📁 Project Structure

```
porpoise-agent/
  (see Architecture section above)
```

---

## 🔗 Ecosystem

This project is the Porpoise Domain Expert Engine (P₁) in the SanShengWanWu ecosystem.

```
Triangle Core (sealed 3):
  📦 fish-ecology-assistant    → Knowledge Supply (V0)
  🔍 cognitive-search-engine   → Search Verification (V1)
  ⚙️ eon-core                  → Coordination Hub (Coord)

Derived Projects (open N):
  🐬 porpoise-agent    → P₁ Porpoise Expert
  🐟 coilia-agent      → P₂ Coilia Expert
  🐟 culter-agent      → P₃ Culter Expert
  🔥 conflict-arbiter  → C  Conflict Arbitration
```

> 🔥 Together infinite power, apart top expert engines.

---

🌱 **Everything Flows · Panta Rhei**

> Heraclitus said: No man ever steps in the same river twice.
>
> We say: You cannot analyze today''s ecological data with last month''s code.

This project is not a fixed toolset — it is a **living system**. Every component has built-in expiration mechanisms, version tracking, and emergence awareness. As your research deepens, packages update, and new methods emerge, it evolves with you.

*Last updated: 2026-06-17　|　Environment: Reasonix Code · DeepSeek Powered*

