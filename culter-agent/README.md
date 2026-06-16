<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🐟 Culter Agent — 鲌类专研 (P₃)</h1>
  <p><strong>三角闭环衍生项目 · P₃ 鲌类专研</strong></p>
  <p>8 Skills · DirectLoader cognitive search · knowledge base · 9-phase pipeline</p>
  <p>🤝 Sister agents: <a href="../porpoise-agent/">porpoise-agent (P₁)</a> · <a href="../coilia-agent/">coilia-agent (P₂)</a></p>
  <p>🧠 Coordinator: <a href="../eon-core/">eon-core</a></p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-8-f59e0b?style=flat-square" alt="Skills:8"></a>
  <a href="../VERSION.yaml"><img src="https://img.shields.io/badge/workspace-v8.1.0-6366f1?style=flat-square" alt="Workspace:v8.1.0"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v2.0.0-ec4899?style=flat-square" alt="Agent:v2.0.0"></a>
</p>

## Architecture Role: **Derived Project P₃ (Culter Specialist)**

> **Triangle Core**: fish(Knowledge V0) + cognitive(Validation V1) + eon-core(Coordinator T)
> **P₃** derived from Triangle Core, depends on triangle for species knowledge and literature search.
> Culter-specific: genomics, age & growth, stable isotope ecology, sympatric coexistence, resource assessment.

## Target Species

| Species | Chinese | Family |
|---------|---------|--------|
| *Culter alburnus* | 翘嘴鲌 (白鱼/翘壳) | Cyprinidae > Cultrinae |
| *Culter mongolicus* | 蒙古鲌 (蒙古红鲌) | Cyprinidae > Cultrinae |
| *Culter oxycephalus* | 尖头鲌 | Cyprinidae > Cultrinae |
| *Chanodichthys erythropterus* | 红鳍原鲌 | Cyprinidae > Cultrinae |

## 9-Phase Pipeline

```
Literature → Growth → Genomics → Genetics → Trophic → Coexistence → Resource → Habitat → Report
```

## Skills (8)

| Skill | Description |
|-------|-------------|
| `search-literature` | Bilingual literature search via cognitive DirectLoader |
| `analyze-growth` | Age determination & von Bertalanffy growth modeling |
| `analyze-genomics` | Whole genome/RAD-seq assembly, comparative genomics |
| `analyze-genetics` | Population genetics, phylogeography, gene flow |
| `analyze-trophic` | δ¹³C/δ¹⁵N stable isotopes, MixSIAR mixing models |
| `model-coexistence` | Niche partitioning quantification, coexistence mechanisms |
| `assess-resource` | CPUE standardization, MSY estimation, YPR analysis |
| `model-habitat` | HSI modeling, spawning ground assessment |

## Quick Start

```bash
# Via project_loader
python -c "from scripts.project_loader import get_culter; a=get_culter(); print(a.info())"

# Via coordinator
python -c "from scripts.coordinator import coordinator; print(coordinator.health('culter'))"

# Standalone
python culter-agent/src/main.py --query "翘嘴鲌 年龄与生长"
```

## Directory Structure

```
culter-agent/
├── config/agent.yaml              # Agent configuration (v2.0.0)
├── data/knowledge_base/           # Species knowledge base
├── src/
│   ├── adapter.py                 # IProjectAdapter → CulterAdapter
│   ├── agent/orchestrator.py      # 9-phase pipeline orchestrator
│   ├── skills/                    # 8 skill modules
│   ├── prompts/                   # System prompts
│   └── main.py                    # CLI entry point
└── README.md
```

## Linked Projects

| Project | Role | Relationship |
|---------|------|-------------|
| [eon-core](../eon-core/) | Coordinator (T) | Coordinates P₃ via DAG topology |
| [fish-ecology-assistant](../fish-ecology-assistant/) | Knowledge V0 | Provides species profiles & credibility scoring |
| [cognitive-search-engine](../cognitive-search-engine/) | Validation V1 | Literature search & graph traversal |
| [porpoise-agent](../porpoise-agent/) | P₁ Porpoise | Sister derived project |
| [coilia-agent](../coilia-agent/) | P₂ Coilia | Sister derived project (template origin) |
| [conflict-arbiter](../conflict-arbiter/) | C Conflict | Multi-source conservation arbitration |
