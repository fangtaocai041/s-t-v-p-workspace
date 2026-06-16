<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🐟 Culter Agent — 鲌类专研 (P₃)</h1>
  <p><strong>三角闭环衍生项目 · 鲌类 (Culter) 专研</strong></p>
  <p>8 Skills · 9-Phase Pipeline · 6 Target Species · Knowledge Base</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-2.0.0-ec4899?style=flat-square" alt="v2.0.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-8-f59e0b?style=flat-square" alt="Skills:8"></a>
  <a href="#"><img src="https://img.shields.io/badge/pipeline-9_phase-22c55e?style=flat-square" alt="Pipeline:9"></a>
  <a href="#"><img src="https://img.shields.io/badge/species-6-8b5cf6?style=flat-square" alt="Species:6"></a>
</p>

---

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Pipeline](#pipeline)
- [Skills](#skills)
- [CLI](#cli)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Knowledge Base](#knowledge-base)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

**Culter Agent** is the **P₃** derivative project of the Triangle Core, specializing in *Culter* genus fishes (鲌属), particularly **Culter alburnus** (翘嘴鲌). It provides an 9-phase analysis pipeline with 8 domain skills covering genomics, genetics, age-growth, trophic ecology, coexistence modeling, habitat assessment, and resource evaluation.

### Target Species

| Species | Chinese Name | Status |
|---------|-------------|--------|
| *Culter alburnus* | 翘嘴鲌 (大白鱼) | Primary — full knowledge base |
| *Culter mongolicus* | 蒙古鲌 | Related |
| *Culter oxycephalus* | 尖头鲌 | Related |
| *Chanodichthys erythropterus* | 红鳍原鲌 | Related |
| *Culter dabryi* | 达氏鲌 | Related |
| *Culter oxycephaloides* | 拟尖头鲌 | Related |

### Capabilities

| Capability | Description |
|------------|-------------|
| 🧬 **Genomics** | Genome assembly, RAD-seq/GBS, transcriptome, mitogenome analysis |
| 🧬 **Genetics** | SSR/mtDNA/SNP, population structure, phylogeography |
| 📐 **Age-Growth** | VBGF fitting, scale/otolith annuli, growth parameters |
| 🍽️ **Trophic Ecology** | Stable isotopes (δ¹³C/δ¹⁵N), MixSIAR, SIBER, gut content |
| 🌿 **Coexistence** | Niche partitioning, Pianka overlap, null models |
| 🏠 **Habitat Modeling** | HSI (3 methods), spawning ground assessment |
| 📊 **Resource Assessment** | CPUE standardization, surplus production, MSY |
| 🔍 **Literature Search** | Multi-engine parallel species literature search |

---

## Quick Start

### Installation

```bash
git clone https://github.com/fangtaocai041/culter-agent.git
cd culter-agent
pip install -e .
```

### CLI Usage

```bash
# Run a query through the 9-phase pipeline
culter run --query "翘嘴鲌 年龄 生长参数"

# Or in English
culter run --query "Culter alburnus growth parameters"
```

### Verify Installation

```python
from culter_agent.src.adapter import CulterAdapter, get_adapter

adapter = get_adapter()
print(adapter.health())
# {'status': 'HEALTHY', 'species': 'Culter alburnus', ...}

info = adapter.info()
print(f"Capabilities: {info['capabilities']}")
```

---

## Pipeline

The 9-phase analysis pipeline operates in two modes:

| Phase | Name | Focus |
|:-----:|------|-------|
| 1 | 🎯 **Species Detection** | Identify target species from query text |
| 2 | 🔍 **Literature Search** | Multi-engine parallel literature search |
| 3 | 🧬 **Genomics Analysis** | Genome assembly, sequencing strategies |
| 4 | 🧬 **Genetics Analysis** | Population genetics, SSR/mtDNA/SNP |
| 5 | 📐 **Age-Growth** | VBGF parameters, annuli interpretation |
| 6 | 🍽️ **Trophic Ecology** | Stable isotopes, MixSIAR, niche metrics |
| 7 | 🌿 **Coexistence** | Niche partitioning, overlap, null models |
| 8 | 🏠 **Habitat** | HSI modeling, environmental factors |
| 9 | 📊 **Resource Assessment** | CPUE, YPR, MSY models |

```python
from culter_agent.src.agent.orchestrator import CulterOrchestrator

orch = CulterOrchestrator()

# Auto-detect mode: standalone or integrated (via eon-core)
result = orch.run("翘嘴鲌 稳定同位素 营养生态位")

print(result["mode"])           # "standalone" or "integrated"
print(result["species"])        # "Culter alburnus"
print(result["phases"])         # ["trophic_ecology", "coexistence"]
print(result["synthesis"])      # Analysis summary text
```

---

## Skills

Each skill is defined as a `SKILL.md` playbook in `src/skills/<name>/`:

| Skill | Description |
|-------|-------------|
| `search-literature` | Multi-engine parallel search for culter species |
| `analyze-genomics` | Genome assembly, RAD-seq/GBS, transcriptome analysis |
| `analyze-genetics` | SSR/mtDNA/SNP population genetics |
| `analyze-growth` | Age determination, VBGF, von Bertalanffy parameters |
| `analyze-trophic` | Stable isotopes (δ¹³C/δ¹⁵N), MixSIAR, SIBER |
| `model-coexistence` | Niche partitioning, Pianka overlap, null models |
| `model-habitat` | HSI (3 methods), habitat suitability modeling |
| `assess-resource` | CPUE standardization, surplus production, MSY |

---

## CLI

```bash
culter run --query "研究问题"   # or -q "研究问题"
culter --help                   # Auto-generated argparse help
```

**Output (standalone mode)**:
```json
{
  "agent": "CulterAgent",
  "species": "Culter alburnus",
  "phases_executed": ["trophic_ecology"],
  "total_papers": 18,
  "synthesis": "..."
}
```

**Output (integrated mode via eon-core)**:
```json
{
  "agent": "CulterAgent",
  "phase": "trophic_ecology",
  "skill": "analyze-trophic",
  "delegate": "..."
}
```

---

## API Reference

### `src/adapter.py`

| Method | Description |
|--------|-------------|
| `search(query, **kwargs)` | Map query to pipeline execution |
| `health()` | Health status check |
| `info()` | Capability listing |

### `src/agent/orchestrator.py`

| Method | Description |
|--------|-------------|
| `run(question)` | 9-phase pipeline entry — auto-detect mode, route by keyword |
| `run_phase(phase, query)` | Execute single phase |

### `src/knowledge_base.py`

| Method | Description |
|--------|-------------|
| `get_species(name)` | Look up species by Chinese/common name |
| `find_by_scientific(name)` | Look up by scientific name |
| `find_by_chinese(name)` | Look up by Chinese name |

---

## Architecture

```
culter-agent/
├── README.md / README.zh.md     ← Documentation
├── pyproject.toml                ← Project metadata + CLI entry
│
├── src/
│   ├── __init__.py               ← Package marker
│   ├── main.py                   ← CLI entry (culter run)
│   ├── adapter.py                ← CulterAdapter (IProjectAdapter)
│   ├── knowledge_base.py         ← Species knowledge base loader
│   │
│   ├── agent/
│   │   └── orchestrator.py       ← CulterOrchestrator — 9-phase pipeline
│   │
│   ├── prompts/
│   │   └── system_prompts.py     ← Per-phase pipeline prompts
│   │
│   └── skills/                   ← 8 x SKILL.md playbooks
│       ├── analyze-genetics/
│       ├── analyze-genomics/
│       ├── analyze-growth/
│       ├── analyze-trophic/
│       ├── assess-resource/
│       ├── model-coexistence/
│       ├── model-habitat/
│       └── search-literature/
│
├── config/
│   ├── agent.yaml                ← 18 rules, 8 skills, 9-phase pipeline
│   └── component_registry.yaml   ← 11 components with expiry tracking
│
├── data/
│   └── knowledge_base/species/
│       └── culter-alburnus.md    ← Full species profile (400+ lines)
│
├── scripts/
│   └── shared_types.py           ← Shared type definitions
│
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
└── LICENSE
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `src/adapter.py` | Cross-project protocol — implements `IProjectAdapter` |
| `src/agent/orchestrator.py` | Pipeline orchestrator — 9-phase execution, mode detection |
| `src/knowledge_base.py` | Species knowledge base — zero-dependency parser |
| `src/skills/` | 8 domain-specific playbooks for agent execution |
| `config/agent.yaml` | Agent configuration — rules, skills, pipeline, species mapping |

---

## Knowledge Base

### `data/knowledge_base/species/culter-alburnus.md`

Full species profile with 12 sections:

| Section | Content |
|---------|---------|
| Conservation | IUCN NE, China status, Yangtze fishing ban |
| Biology | Max 105cm/15kg, lifespan 15-20yr, feeding ecology |
| Reproduction | Maturity at age 2-3, spawning May-Jul, fecundity 5-60万 |
| Habitat | Lakes/reservoirs/rivers, 0-30m depth, 15-30°C |
| Fishery | Historical importance, aquaculture, catch trends |
| Genomics | ~1.0-1.2Gb, 2n=48, sequencing status, key questions |
| Stable Isotopes | δ¹³C/δ¹⁵N/δ³⁴S, tissues, EA-IRMS, MixSIAR |
| Trophic Niche | 4-stage dietary shift, Levin 0.3-0.6, Pianka 0.5-0.7 |
| Coexistence | 3 co-occurring pairs, spatial/dietary/temporal partitioning |
| Related Species | 5 related species with comparison data |

---

## Related Projects

| Project | Role | Relationship |
|---------|------|--------------|
| **fish-ecology-assistant** | Knowledge V0 | Species knowledge base provider |
| **cognitive-search-engine** | Search V1 | Literature search engine |
| **eon-core** | Coordinator | Pipeline routing and coordination |
| **porpoise-agent** | P₁ Porpoise | Sister project |
| **coilia-agent** | P₂ Coilia | Sister project |

---

## Contributing

```bash
# Install dev dependencies
pip install -e .

# Run tests (when available)
python -m pytest tests/ -v

# Code style
pip install ruff
ruff check src/
```

---

## License

MIT License © 2026

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
