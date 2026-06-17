# 🐟 Fish Ecology Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge) ![Version](https://img.shields.io/badge/Version-v8.1-blueviolet?style=for-the-badge) ![Species](https://img.shields.io/badge/Species-430-success?style=for-the-badge) ![Traits](https://img.shields.io/badge/Traits-289-important?style=for-the-badge) ![FISHMORPH](https://img.shields.io/badge/FISHMORPH-251%20spp-informational?style=for-the-badge) ![Population](https://img.shields.io/badge/Population-26%20records-critical?style=for-the-badge) ![Bilingual](https://img.shields.io/badge/Bilingual-CN%C2%B7EN-ff69b4?style=for-the-badge) ![DB](https://img.shields.io/badge/DB-SQLite-lightgrey?style=for-the-badge) ![Frontier](https://img.shields.io/badge/Frontier-Kalman-red?style=for-the-badge)

> 🌊 Knowledge Supply Core — 430 Yangtze fish species, 289 morphological traits, population-level variation.
> Panta Rhei — Everything flows.

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

| Feature | Description |
|---------|-------------|
| 🗃️ 430 Species | Complete Yangtze River fish species database |
| 📏 289 Morphology Traits | Sourced from FISHMORPH (251), FishBase, FAO, literature |
| 🌊 Population-level Data | 26 records with water-body-specific trait variation |
| 🔬 Trait Catalog | 61 traits in 7 categories (morphology→life history→feeding→...) |
| 🏛️ Bilingual Conservation | IUCN + China Red List + National Protection + CITES |
| 📊 Excel/HTML Reports | Double-click reports with 2-level hierarchical headers |
| 🔄 FishBase Auto-sync | Automated trait pulling with source traceability |
| 🕸️ Network Science | Trait co-occurrence networks, keystone trait identification |
| 📡 Kalman Filter | Emergence signal detection from noisy population data |
| 🔗 KB-First Architecture | Zero-network lookup for 30 core species |

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

