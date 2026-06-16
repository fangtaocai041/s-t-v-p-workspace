<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🔥 Conflict Arbiter — 冲突仲裁层 (C)</h1>
  <p><strong>三角闭环衍生项目 · C 冲突仲裁 · 火元素</strong></p>
  <p>Multi-source conflict detection · Weighted arbitration · Circuit breaker · China regional policy</p>
  <p>🧠 Coordinator: <a href="../eon-core/">eon-core</a></p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="../VERSION.yaml"><img src="https://img.shields.io/badge/workspace-v8.1.0-6366f1?style=flat-square" alt="Workspace:v8.1.0"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v1.0.0-ec4899?style=flat-square" alt="Agent:v1.0.0"></a>
</p>

## Architecture Role: **Derived Project C (Conflict Arbitration)**

> **Triangle Core**: fish(Knowledge V0) + cognitive(Validation V1) + eon-core(Coordinator T)
> **C** derived from Triangle Core. Receives outputs from any project and arbitrates conflicts.

## Core Function

```python
assess_conflict(species: str, sources: list[dict]) → ConflictReport
```

**Three-stage arbitration**:
1. **Normalize** — Map all source protection levels to unified [0-100] numeric axis
2. **Detect** — Compute conflict level [0-3] with spatiotemporal comparability check
3. **Arbitrate** — Weighted consensus with circuit breaker

## China Regional Policy

When `region="china"`, Chinese protection classifications take authority:
- `chinese_red_list` weight = 100 (primary)
- `provincial_protection` weight = 90 (secondary)
- `iucn` / `cites` weight = 40 (reference only)

## Conflict Levels

| Level | Name | Action |
|:-----:|------|--------|
| 0 | Full Consensus | Pass through |
| 1 | Minor Difference | Accept with note |
| 2 | Significant Difference | Weighted arbitration |
| 3 | Severe Opposition | **Circuit breaker** → manual review |

## Quick Start

```bash
# Via project_loader
python -c "from scripts.project_loader import get_conflict; a=get_conflict(); print(a.info())"

# Via coordinator
python -c "from scripts.coordinator import coordinator; print(coordinator.health('conflict'))"

# Direct arbitration test
python -c "
from conflict_arbiter.src.arbiter import ConflictArbiter
arbiter = ConflictArbiter()
result = arbiter.detect_conflicts('Coilia nasus', [
    {'source': 'iucn', 'protection_level': 'EN'},
    {'source': 'chinese_red_list', 'protection_level': '国家二级'},
], region='china')
print(result['verdict'])
"
```

## Directory Structure

```
conflict-arbiter/
├── config/agent.yaml              # Arbiter configuration (v1.0.0)
├── src/
│   ├── adapter.py                 # IProjectAdapter → ConflictArbiterAdapter
│   ├── arbiter.py                 # ConflictArbiter engine
│   └── __init__.py
└── README.md
```

## Linked Projects

| Project | Role | Relationship |
|---------|------|-------------|
| [eon-core](../eon-core/) | Coordinator (T) | Routes outputs to conflict detection |
| [fish-ecology-assistant](../fish-ecology-assistant/) | Knowledge V0 | Primary source of conservation data |
| [cognitive-search-engine](../cognitive-search-engine/) | Validation V1 | Provides literature-based protection evidence |
| [porpoise-agent](../porpoise-agent/) | P₁ Porpoise | Source of porpoise conservation recommendations |
| [coilia-agent](../coilia-agent/) | P₂ Coilia | Source of coilia conservation recommendations |
| [culter-agent](../culter-agent/) | P₃ Culter | Source of culter conservation recommendations |
