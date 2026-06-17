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

<div align="center"><h3>🌊 Everything flows.</h3></div>

The world is dynamic, knowledge is temporary, emergence is the norm.

---
## 📖 Table of Contents

- [Philosophy](#-philosophy)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Ecosystem](#-ecosystem)

---

## 🎯 Core Philosophy

> 🌍 The world is dynamic. 📖 Knowledge is temporary. 🌟 Emergence is the norm.

This is not a slogan. It is the operating system running through every line of code, every search, and every analysis in this project.

### 📜 Three Tenets

**🌍 The world is dynamic** — R packages update, species distributions shift, scientific consensus evolves, climate change reshapes ecosystems. A correct conclusion today may be outdated in six months. We treat no knowledge as eternal truth, but place it on a timeline and view it dynamically.

**📖 Knowledge is temporary** — The foundation of science is falsification (Popper). No discovery is ultimate truth—only the "best current explanation." We use calibrated language: "evidence suggests" not "proves," "Smith (2022) found" not "studies show." Every output carries a temporal anchor.

**🌟 Emergence is the norm** — Life, consciousness, ecosystems, AI reasoning—all are emergent phenomena. You cannot assemble the whole by analyzing only the parts. When ≥3 independent sources point to the same unexpected pattern, the system flags it as an emergence signal—not dismisses it as noise.

### ⚖️ Why This Matters for Research

| 🎯 Scenario | ❌ Traditional | ✅ Dynamic Worldview |
|:------------|:--------------|:--------------------|
| 📦 Package versions | Run 2020 code, ignore version drift | Auto-check, tag "Last verified on glmmTMB v1.1.10" |
| 📝 Citations | "Studies prove it" | "Smith (2022) found X, but Jones (2024) added Y" |
| 📊 Outliers | Ignore as noise | ≥3 sources → emergence signal, actively track |
| ⏰ Knowledge decay | Handbook frozen, never updated | Review records include "Next review date," computed by package activity |
| 🔧 Method selection | Fixed pipeline forever | Dynamic method selection, dynamic confidence |

---

## 🧩 What This Is

**Fish Ecology Assistant** is a complete configuration package that transforms Reasonix Code from a general-purpose coding assistant into a professional fish ecology research team.

It integrates **16 MCP tools**, **12 domain-specific AI sub-agents**, **5-engine parallel search**, an automated **5-stage research pipeline**, and an **R statistical computing environment**—all outputs guided by the dynamic worldview above.

### 📊 Capability Matrix

| 🚀 Capability | ✨ With This Config | 💭 Vanilla Reasonix |
|:--------------|:-------------------|:-------------------|
| 🔍 Search | 5 (tavily, exa, google-scholar, article, scholarly) | 1 (web_search) |
| 🤖 AI Sub-agents | 12 (domain-specific, incl. emergence detection) | 4 (general) |
| 📊 R Statistics | R 4.6.0 + 20+ ecology packages | — |
| 👁️ OCR | PaddleOCR + Tesseract.js | — |
| 📚 References | Direct Zotero query | — |
| ✍️ Writing | 5-stage + auto-review + emergence detection | — |
| 🏛️ Knowledge Bases | 13 IMA knowledge bases | — |
| ⚡ Setup | One script, 5 minutes | — |

---


## 📜 Three Tenets

**🌍 The world is dynamic** — R packages update, species distributions shift, scientific consensus evolves, climate change reshapes ecosystems. A correct conclusion today may be outdated in six months.

**📖 Knowledge is temporary** — The foundation of science is falsification (Popper). No discovery is ultimate truth—only the best current explanation. We use calibrated language: evidence suggests not proves.

**🌟 Emergence is the norm** — Life, consciousness, ecosystems, AI reasoning—all are emergent phenomena. When >=3 independent sources point to the same unexpected pattern, the system flags it as an emergence signal.

## 🚀 Quick Start

```bash
# Clone
git clone git@github.com:fangtaocai041/fish-ecology-assistant.git
cd fish-ecology-assistant

# Install
pip install -e .

# Run
python src/main.py search --species "Coilia nasus"
```

---

## 🏗️ Architecture

```
fish-ecology-assistant/
  src/           Core Python engine
  ├── adapter.py     IProjectAdapter (V0 canonical)
  ├── orchestrator.py    KB-first species search
  ├── project_hub.py     Cross-project coordination
  ├── dao_engine.py      Philosophical chain executor
  ├── types.py           8 dataclasses + 4 enums
  └── kalman_emergence.py  Kalman Filter emergence detection
  config/
  ├── knowledge_base/   30 species .md profiles
  └── fish_species_kb.yaml  430 species index
  data/
  ├── species.db         SQLite (species + traits + literature)
  ├── FISHMORPH.csv      2.3MB global morphology database
  └── reports/           HTML/CSV exports
  scripts/
  ├── fishbase_pull.py   FishBase API auto-sync
  ├── trait_network.py   Network Science trait analysis
  └── gen_report.py      Bilingual HTML report generator
```

---

## ✨ Features

| Feature | Status | Description |
|---------|:------:|-------------|
| 🗃️ 430 Species DB | ✅ | Yangtze fish species with bilingual conservation |
| 📏 289 Morphology | ✅ | FISHMORPH (251) + FishBase + FAO + manual |
| 🌊 Population-level | ✅ | 26 records with water-body annotation |
| 🔬 Trait Catalog | ✅ | 61 traits in 7 categories |
| 🏛️ Conservation | ✅ | IUCN + China Red List + National + CITES |
| 📊 Excel/HTML | ✅ | Bilingual reports, 2-level headers |
| 🔗 KB-First | ✅ | SQLite FTS5, zero-network for 30 core spp |
| 🕸️ Trait Network | ✅ | Jaccard co-occurrence, keystone traits |
| 📡 Kalman Filter | ✅ | Emergence detection from noisy data |
| 🔄 FishBase Sync | 🟡 | Script ready, SSL blocked in env |

---

## 📁 Project Structure

```
fish-ecology-assistant/
  (see Architecture section above)
```

---

## 🔗 Ecosystem

This project is the Knowledge Supply Core (V0) in the SanShengWanWu ecosystem.

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

