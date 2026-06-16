<div align="center">
  <h1>🐬 Porpoise Agent</h1>
  <p><strong>Yangtze Finless Porpoise Research Agent Framework</strong> — Multi-Agent System · BDI Decision · 5 Cognitive Layers · External Integrations</p>
  <p>Python 3.11+ · 7 Agents · 5 Cognitive Layers · 4 Integrations</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-2.1.0-8b5cf6?style=flat-square" alt="v2.1.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/agents-7-f59e0b?style=flat-square" alt="7 Agents"></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-4_suites-22c55e?style=flat-square" alt="Tests"></a>
</p>

<p align="center">
  🇨🇳 <a href="README.md">中文</a>
</p>

---

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [CLI Commands](#cli-commands)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [External Integrations](#external-integrations)
- [Configuration](#configuration)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

**Porpoise Agent** is an AI Agent framework for Yangtze finless porpoise (*Neophocaena asiaeorientalis asiaeorientalis*) research, built on a **Multi-Agent System (MAS)** with a **BDI cognitive architecture**. It automates literature search, acoustic analysis, ecological modeling, and conservation assessment workflows.

### Capabilities

| Capability | Description |
|------------|-------------|
| 🧠 **Multi-Agent System** | 7 specialized agents collaborating: Literature, Acoustic, Ecology, Conservation, Critic, Orchestrator |
| 🔍 **BDI Decision Engine** | Belief-Desire-Intention state machine for reasoning and action planning |
| 📚 **Three-Tier Memory** | Short-term (context window) + Long-term (ChromaDB vector store / RAG) |
| 🔌 **Quadruple Integration** | cognitive-search-engine, Neo4j graph, Zotero library, Obsidian vault |
| 🛡️ **Sandbox Execution** | Isolated Python runtime for safe code execution |
| 🧪 **Test Coverage** | BDI state machine + Memory + Serializer + 7 workflow scenarios + Stress tests |

---

## Quick Start

### Installation

```bash
git clone https://github.com/FFRC-LiuKai-Lab/porpoise-agent.git
cd porpoise-agent
pip install -e .
```

### Verify Installation

```python
from porpoise_agent.src.agents import OrchestratorAgent

orch = OrchestratorAgent()
print(f"Agents registered: {len(orch.list_agents())}")
```

### CLI Usage

```bash
porpoise doctor         # Health check
porpoise topology       # Show MAS topology
porpoise chat           # Interactive chat mode
porpoise run TASK       # Run a single research task
```

---

## Core Features

### 1. Multi-Agent System

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

### 2. BDI Decision Making

```python
from porpoise_agent.src.cognitive import BDICoordinator, Belief, Desire

bdi = BDICoordinator()
bdi.add_belief(Belief("species", "Neophocaena asiaeorientalis"))
bdi.add_belief(Belief("population", 1200))
bdi.add_desire(Desire("assess_threat", priority=0.9,
                       condition=lambda b: b.get("population", 0) < 1500))
plan = bdi.deliberate()
```

### 3. Memory System

```python
from porpoise_agent.src.memory import MemoryManager

memory = MemoryManager()
memory.stm.store("last_query", "porpoise habitat")
memory.ltm.store_document("paper_001", "Acoustic analysis of finless porpoise")
results = memory.ltm.search("acoustic", top_k=5)
```

### 4. Sandbox Execution

```python
from porpoise_agent.src.execution import execute_safe

result = execute_safe("print(f'Mean: {sum([1,2,3,4,5])/5}')")
print(result.output)
```

---

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `porpoise chat` | Interactive chat (ReAct loop) | `porpoise chat --model deepseek-reasoner` |
| `porpoise run TASK` | Single research task | `porpoise run "Analyze acoustic data"` |
| `porpoise topology` | Show MAS topology | `porpoise topology` |
| `porpoise doctor` | Health check | `porpoise doctor` |

---

## API Reference

### `porpoise_agent.src.agents`

| Class | Description |
|-------|-------------|
| `OrchestratorAgent` | Central scheduler: NLU → route → multi-agent dispatch → aggregate |
| `LiteratureAgent` | Literature search via cognitive-search-engine |
| `AcousticAgent` | NBHF echolocation signal analysis |
| `EcologyAgent` | Habitat assessment and population dynamics |
| `ConservationAgent` | Threat level assessment and conservation recommendations |
| `CriticAgent` | Self-reflection and quality review |
| `BaseAgent` | Agent base class with BDI + ToolRegistry |

### `porpoise_agent.src.cognitive`

| Class | Description |
|-------|-------------|
| `BDICoordinator` | BDI state machine |
| `ReActLoop` | Reasoning-Acting cycle |
| `TaskDecomposer` | CoT / ToT / GoT decomposition strategies |
| `Critic` | Credit assignment + feedback loop |

### `porpoise_agent.src.execution`

| Class/Function | Description |
|----------------|-------------|
| `SandboxExecutor` | Isolated Python code execution |
| `ToolRegistry` | Tool registration and discovery |
| `APIClient` | PubMed / CrossRef / Semantic Scholar client |
| `execute_safe(code)` | Quick safe-execution function |

---

## Architecture

```
porpoise-agent/
├── README.md / README_en.md
├── pyproject.toml
│
├── src/
│   ├── __init__.py              ← Version + architecture declaration
│   ├── cli.py                   ← 4 CLI commands
│   ├── agents/                  ← Multi-Agent System (7 agents)
│   ├── cognitive/               ← BDI + ReAct + TaskDecomposer
│   ├── memory/                  ← STM + LTM (ChromaDB) + Manager
│   ├── mapping/                 ← Router + Serializer + Validator
│   ├── execution/               ← Sandbox + ToolRegistry + API clients
│   ├── interaction/             ← NLU + Response rendering
│   ├── integration/             ← External system bridges
│   ├── prompts/                 ← System prompts
│   └── utils/                   ← Config + logging + types
│
├── config/                      ← agent.yaml, models.yaml, mcp_servers.yaml
├── tests/                       ← 5 test suites (24+ test cases)
├── data/                        ← Knowledge base data
├── docs/                        ← Documentation
├── examples/                    ← Example scripts
└── scripts/                     ← Utility scripts
```

### Module Responsibilities

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `agents/` | Multi-Agent collaboration | `OrchestratorAgent`, `LiteratureAgent`, `AcousticAgent` |
| `cognitive/` | BDI reasoning + ReAct loop | `BDICoordinator`, `ReActLoop`, `TaskDecomposer` |
| `memory/` | Context + vector retrieval | `MemoryManager`, `ShortTermMemory`, `LongTermMemory` |
| `execution/` | Sandbox + API clients | `SandboxExecutor`, `ToolRegistry`, `APIClient` |
| `interaction/` | Intent recognition | `NLUProcessor`, `ResponseRenderer` |
| `mapping/` | Routing + serialization | `IntentRouter`, `EngineeringSerializer` |
| `integration/` | External bridges | `CognitiveSearchAdapter`, `KnowledgeGraph` |

---

## External Integrations

| System | Adapter | Purpose |
|--------|---------|---------|
| **cognitive-search-engine** | `CognitiveSearchAdapter` | Multi-engine literature search |
| **Neo4j Knowledge Graph** | `KnowledgeGraph` | Species relationship storage |
| **Zotero** | `ZoteroAdapter` | Research library access |
| **Obsidian** | `ObsidianAdapter` | Personal knowledge base |

---

## Configuration

### `config/agent.yaml`
Runtime configuration for all 5 layers (model selection, tool permissions, agent parameters).

### `config/models.yaml`
Model routing and pricing:
```yaml
models:
  - name: deepseek-chat
    context_window: 64000
    purpose: general_reasoning
  - name: deepseek-reasoner
    context_window: 64000
    purpose: complex_reasoning
```

### `config/mcp_servers.yaml`
MCP tool service registration (scholar search, article full-text, filesystem, etc.).

---

## Related Projects

| Project | Role | Relationship |
|---------|------|--------------|
| **eon-core** | Coordinator | Vertex V2 — porpoise domain agent |
| **fish-ecology-assistant** | Knowledge V0 | Species knowledge base |
| **cognitive-search-engine** | Search V1 | Literature search and scoring |
| **coilia-agent** | P₂ Coilia | Sister project (sister agent) |
| **culter-agent** | P₃ Culter | Sister project |

---

## Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/xxx`
3. Commit changes: `git commit -m "description"`
4. Push branch: `git push origin feature/xxx`
5. Create a Pull Request

### Running Tests

```bash
cd porpoise-agent
python -m pytest tests/ -v
```

---

## License

MIT License © 2026 Liu Kai Research Group, FFRC

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
