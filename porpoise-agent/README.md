# 🐬 Porpoise Agent

<p align="center">
  ![Python 3.11+](https://img.shields.io/badge/Python%203.11%2B-3776AB?style=flat-square)
  ![MIT](https://img.shields.io/badge/MIT-34D058?style=flat-square)
  ![v0.2](https://img.shields.io/badge/v0.2-8A4FCE?style=flat-square)
  ![7-agent MAS](https://img.shields.io/badge/7-agent%20MAS-007EC6?style=flat-square)
  ![5-layer](https://img.shields.io/badge/5-layer-FE7D37?style=flat-square)
  ![BDI+ReAct](https://img.shields.io/badge/BDI%2BReAct-D73A4A?style=flat-square)
  ![SSE stream](https://img.shields.io/badge/SSE%20stream-0EA5E9?style=flat-square)
  ![ChromaDB](https://img.shields.io/badge/ChromaDB-EC4899?style=flat-square)
  ![MCTS](https://img.shields.io/badge/MCTS-F59E0B?style=flat-square)
</p>


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

| Feature | Status | Description |
|---------|:------:|-------------|
| 🧠 BDI+ReAct+Reflexion | ✅ | Full cognitive loop with MDP |
| 🌳 CoT/ToT/GoT/MCTS | ✅ | 4 decomposition + 5 search strategies |
| 🕸️ StateGraph | ✅ | LangGraph-style conditional routing |
| 🔴 SSE Streaming | ✅ | Real-time agent output |
| 🗄️ ChromaDB RAG | ✅ | Vector LTM with graceful degradation |
| 🔧 7-Agent MAS | ✅ | 6 topology types + condition edges |
| 🔒 Subprocess Sandbox | ✅ | Import whitelist + resource limits |
| 📚 4 Integrations | ✅ | cognitive-search, Zotero, Obsidian, KG |
| ⚠️ Acoustic/Ecology | 🟡 | Framework ready, core methods stub |
| 🐬 Domain Focus | ✅ | Yangtze finless porpoise research |

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

