# 🐬 Porpoise Agent v2.1 — Yangtze Finless Porpoise Research Agent

[![test](https://github.com/FFRC-LiuKai-Lab/porpoise-agent/actions/workflows/test.yml/badge.svg)](https://github.com/FFRC-LiuKai-Lab/porpoise-agent/actions/workflows/test.yml)

> **Five-Layer Standard Agent Architecture + Triple External Integration**
>
> AI Agent framework for porpoise (especially *Neophocaena*) research
> Powered by DeepSeek + cognitive-search-engine (v5.0 Hub-and-Spoke)
> Serving: Liu Kai Research Group, FFRC / Wuxi Fisheries College, CAFS

---

## Vision

The Yangtze finless porpoise (*Neophocaena asiaeorientalis asiaeorientalis*) is critically endangered
with only ~1,000–1,200 individuals remaining. Conservation demands efficient data analysis,
literature review, and decision support.

**Porpoise Agent v2.1** bridges formal Agent theory with real-world research toolchains.

---

## Architecture

```
User Input
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  L1  Interaction & Perception  │  NLU + Multi-format    │
├─────────────────────────────────────────────────────────┤
│  L2  Cognitive & Decision      │  BDI + ReAct + Reflexion│
│                                 │  + ToT/GoT + Tree Search│
├─────────────────────────────────────────────────────────┤
│  L3  Memory System             │  STM (context window)  │
│                                 │  + LTM (ChromaDB RAG)  │
├─────────────────────────────────────────────────────────┤
│  L4  Mapping & Translation     │  Router + Serializer   │
│                                 │  + Validator           │
├─────────────────────────────────────────────────────────┤
│  L5  Tool & Execution          │  Sandbox + ToolRegistry│
│                                 │  + API Client          │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  External Integration Layer                             │
│  ├─ cognitive-search-engine (v5.0 Hub-and-Spoke)        │
│  ├─ Zotero Local DB (SQLite, 406 items)                 │
│  └─ Obsidian Vault (domain docs + literature notes)     │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- DeepSeek API Key ([get one](https://platform.deepseek.com))
- Zotero 7 (optional, for local library)
- Obsidian (optional, for knowledge management)

### Install

```bash
git clone https://github.com/FFRC-LiuKai-Lab/porpoise-agent.git
cd porpoise-agent
pip install -e .
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

### Usage

```bash
porpoise chat                          # Interactive (ReAct loop)
porpoise run "search porpoise papers"  # Single task (Orchestrator + MAS)
porpoise topology                       # View MAS topology
porpoise doctor                         # Health check (all 5 layers)
```

---

## Key Features

### 🧠 Theory-Driven

| Theory | Implementation | Description |
|--------|---------------|-------------|
| **BDI Model** | `src/cognitive/bdi.py` | Belief-Desire-Intention agent model |
| **MDP / POMDP** | `src/cognitive/react_loop.py` | S_t→A_t→O_{t+1}→S_{t+1} formalization |
| **ReAct** | `src/cognitive/react_loop.py` | Think→Act→Observe→Reflect cybernetic loop |
| **Tree / Graph of Thoughts** | `src/cognitive/decomposer.py`, `search.py` | BFS/Beam/MCTS + DAG merge |
| **Reflexion** | `src/cognitive/reflexion.py` | Critic + credit assignment + feedback loop |
| **Multi-Agent Topology** | `src/agents/topology.py` | Graph-based MAS (Sequential/Hierarchical/Debate/DAG) |
| **RAG** | `src/memory/long_term.py` | ChromaDB vector retrieval |

### 🔬 Porpoise-Specific

- **NBHF Click Detection**: 110–150 kHz narrow-band high-frequency pulses (SPL threshold + ICI matching)
- **PAM Pipeline**: SoundTrap, A-tag, C-POD, F-POD, RPCD-II support
- **Behavior Inference**: Buzz detection → foraging activity index → diel rhythm analysis
- **Abundance Estimation**: Cue Counting / Distance Sampling / SECR
- **18+ Acoustic Features**: Temporal, spectral, and energy-domain feature extraction

### 🔗 Triple External Integration

| Integration | Path | Capability |
|-------------|------|------------|
| **cognitive-search-engine** | `D:/Reasonix/cognitive-search-engine/` | v5.0 Hub-and-Spoke: OCR variants + 7-engine parallel + citation traversal + review mining + adaptive stop |
| **Zotero** | `D:/ZoteroData/zotero.sqlite` | SQLite direct read, 406 papers, zero-API local search |
| **Obsidian** | `D:/Obsidian Vault/` | Domain docs injected into BDI context, new papers auto-saved as literature notes |

### 🛡️ Safety & Auditability

- **Sandbox Execution**: Subprocess isolation + timeout + AST safety checks
- **Human Approval Gates**: Field surveys / conservation recommendations / data deletion
- **Audit Trail**: JSONL full decision logging
- **Citation Verification**: Critic Agent validates paper existence

---

## Literature Search Strategy (3-Layer)

```
User query "Neophocaena asiaeorientalis acoustic"
  │
  ├─ L0: Zotero Local DB (SQLite, 406 items, zero API)
  │     └─ Hit → instant return, no network
  │
  ├─ L1: cognitive-search-engine (search_rules.yaml full pipeline)
  │     ├─ generate_variants("Neophocaena", "asiaeorientalis") → 20 OCR variants
  │     ├─ build_search_queries() → exact + variants + Chinese + ecology keywords
  │     ├─ ParallelSearch.search_all() → PubMed × Crossref × OpenAlex
  │     └─ CognitiveAgent.search() → citation traversal + review mining
  │     └─ New papers → auto-saved to Obsidian literature notes/
  │
  └─ L2: Semantic Scholar + PubMed (fallback, when nothing else available)
```

---

## Advantages

### ✅ Theoretical Completeness
- Five-layer architecture maps directly to the Standard Agent Architectural Model
- Each layer has clear MDP-formalized semantics
- BDI + ReAct + Reflexion form a complete cybernetic feedback system
- ToT/GoT provides structured exploration of reasoning space (vs. linear generation)

### ✅ Engineering Practicality
- **Zero-API Search**: Zotero local library first — existing papers returned instantly
- **Auto Knowledge Crystallization**: New papers auto-saved to Obsidian, matching academic workflows
- **Hot Module Reload**: cognitive-search-engine loaded via importlib — updates take effect immediately
- **Three-Tier Degradation**: Zotero → cognitive-search-engine → builtin, each tier independently viable

### ✅ Porpoise Domain Depth
- Built-in 8 research direction classifications, 25+ institutions, 12+ related species
- Obsidian group analysis documents (87K+ characters) auto-injected into every BDI context
- Critic Agent reviews conservation recommendations, triggers human approval gates

### ✅ Performance & Security
- NLU: ~29K qps | BDI: ~630K cycles/s | Sandbox: 1,000 lines < 30ms
- AST safety checks + SQL injection prevention + subprocess isolation + timeout control
- All data stays local (Zotero/Obsidian are local files)

---

## Limitations & Future Work

### ❌ High LLM Dependency
- BDI policy function π(Belief, Desire) and Reflexion Critic require LLM for deep reasoning
- Falls back to keyword matching without LLM, with significant loss of semantic understanding
- **Future**: Explore small specialized models (fine-tuned classifiers) for partial LLM replacement

### ❌ CNKI / Wanfang / CQVIP Blind Spot
- cognitive-search-engine's PubMed/Crossref/OpenAlex do not index Chinese databases
- Many Chinese porpoise studies appear in Chinese core journals (Acta Hydrobiologica Sinica, J. Lake Sciences, etc.)
- Currently no auto-retrieval from these sources
- **Future**: Supplement via CNKI E-Study export or Zotero Chinese plugin

### ❌ Acoustic Analysis Not Fully Validated
- NBHF Click detection code is in `AcousticAgent` but needs real audio files for verification
- PAM device format parsing (SoundTrap .wav, A-tag, C-POD) needs per-device adaptation
- **Future**: End-to-end testing with the group's existing PAM data

### ❌ Multi-Agent Topology Simplified
- Current SOP workflow is sequential (literature→acoustic→ecology→conservation)
- Dynamic conditional routing ("if result.confidence > 0.7 then...") is defined but untested in production
- Debate mode (Generator ↔ Critic) only tested in isolation
- **Future**: Validate and tune topology routing in real multi-step research tasks

### ❌ Vector Retrieval Optional
- Falls back to in-memory keyword matching when ChromaDB is not installed
- Semantic recall quality of long-term memory depends on ChromaDB availability
- **Future**: Make ChromaDB auto-install as optional dependency

### ❌ Single-User, Single-Session
- BDI Belief and STM cleared after session end (unless manually persisted)
- No cross-session research context recovery
- **Future**: Persist session state via SQLite/JSON for auto-restore on next launch

---

## Theoretical Foundations

| Theory | Source | Implementation |
|--------|--------|---------------|
| BDI Model | Bratman 1987; Rao & Georgeff 1995 | `src/cognitive/bdi.py` |
| MDP / POMDP | Bellman 1957; Kaelbling et al. 1998 | `src/cognitive/react_loop.py` |
| ReAct | Yao et al. 2022 | `src/cognitive/react_loop.py` |
| Tree of Thoughts | Yao et al. 2023 | `src/cognitive/decomposer.py` |
| Graph of Thoughts | Besta et al. 2024 | `src/cognitive/decomposer.py` |
| Reflexion | Shinn et al. 2023 | `src/cognitive/reflexion.py` |
| RAG | Lewis et al. 2020 | `src/memory/long_term.py` |
| Multi-Agent Debate | Du et al. 2023; Liang et al. 2023 | `src/agents/topology.py` |
| Hub-and-Spoke Search | cognitive-search-engine v5.0 | `src/integration/cognitive_search_adapter.py` |

---

## Verification

| Dimension | Count | Result |
|-----------|:--:|:--:|
| Module imports | 24 | ✅ All pass |
| Functional + robustness | 61 | ✅ All pass |
| End-to-end workflows | 79 (7 scenarios) | ✅ All pass |
| Performance boundaries | 10 | ✅ All within thresholds |
| NLU throughput | — | ~29,000 qps |
| BDI cycles | — | ~630,000 cycles/s |
| Sandbox execution | — | 1,000 lines < 30ms |

---

## Related Projects

| Project | Inspiration |
|---------|-------------|
| [Reasonix](https://github.com/esengine/reasonix) | DeepSeek-native Agent Loop, prefix-cache |
| [cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) | v5.0 Hub-and-Spoke graph search (core dependency) |
| [Ecology-Harness](https://github.com/ECNU-ICALK/Ecology-Harness) | Ecology Agent orchestration |
| [AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | Research pipeline design |
| [SciToolAgent](https://github.com/hicai-zju/scitoolagent) | Scientific tool knowledge graph |
| [CetusID](https://github.com/Gui-Frainer/CetusID) | Cetacean acoustic classification |

---

## Research Group

- **Institution**: Wuxi Fisheries College, Nanjing Agricultural University / Freshwater Fisheries Research Center (FFRC), Chinese Academy of Fishery Sciences
- **Group**: Prof. Liu Kai Research Group
- **Research Areas**: Yangtze finless porpoise conservation biology, passive acoustic monitoring, habitat assessment, fisheries resource management
- **Contact**: liukai@ffrc.cn

---

## License

MIT License © 2025 FFRC / Liu Kai Research Group
