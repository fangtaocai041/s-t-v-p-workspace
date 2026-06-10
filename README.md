<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

# eon-workspace

> **三生万物 v8.1 — Seven Projects Unified**
> Triangle Core: fish + cognitive + eon-core (sealed, arity=3)
> Derived: P₁(porpoise) · P₂(coilia) · P₃(culter) · C(conflict) (open, arity≥0)

```
eon-core/                   → ☯️ Coordination kernel [Triangle Core]
fish-ecology-assistant/     → Triangle V0: Knowledge supply
cognitive-search-engine/    → Triangle V1: Validation engine
porpoise-agent/             → Derived P₁: Porpoise domain
coilia-agent/               → Derived P₂: Coilia domain
culter-agent/               → Derived P₃: Culter domain
conflict-arbiter/           → Derived C:  Conflict arbitration
scripts/project_loader.py   → Unified DirectLoader (7 adapters)
scripts/coordinator.py      → Unified coordinator (6 pathways)
scripts/quality_gate.py     → Quality gate (5 checks)
```

## Quick Start

```bash
# Quality gate — validate all 7 projects (5/5 gates)
python scripts/quality_gate.py

# Load all adapters (7/7)
python -c "from scripts.project_loader import get_all_adapters; print({k:type(v).__name__ for k,v in get_all_adapters().items()})"

# Full health check (7/7)
python -c "from scripts.coordinator import coordinator; [print(f'{p}: {coordinator.health(p)[\"status\"]}') for p in ['eon','fish','cognitive','porpoise','coilia','culter','conflict']]"
```

## Projects

| Project | Version | Layer | Role | Adapter |
|---------|:------:|:-----:|------|---------|
| [eon-core](eon-core/) | v8.0.0 | TriangleCore | Coordinator (T) | `EonCoreAdapter` |
| [cognitive-search-engine](cognitive-search-engine/) | v5.5.0 | TriangleCore | Validation V1 | `CognitiveSearchAdapter` |
| [fish-ecology-assistant](fish-ecology-assistant/) | v6.3.0 | TriangleCore | Knowledge V0 | `FishEcologyAdapter` |
| [porpoise-agent](porpoise-agent/) | v4.3.0 | Derived P₁ | Porpoise specialist | `PorpoiseAdapter` |
| [coilia-agent](coilia-agent/) | v1.2.0 | Derived P₂ | Coilia specialist | `CoiliaAdapter` |
| [culter-agent](culter-agent/) | v2.0.0 | Derived P₃ | Culter specialist | `CulterAdapter` |
| [conflict-arbiter](conflict-arbiter/) | v1.0.0 | Derived C | Conflict arbitration | `ConflictArbiterAdapter` |

## Architecture

```
道 (User) → 一 (IProjectAdapter) → 二 (YinYang Poles)
→ 三角 (fish + cognitive + eon-core) → 万物 (P₁ P₂ P₃ ... C)
```

**6 Data Pathways**: P1(fish→cognitive) · P2(cognitive→fish) · P3(cognitive→domain) · P4(health→karma) · P5(all→conflict) · P6(conflict→user)

## Documentation

| Document | Description |
|----------|-------------|
| [SANSHENG_WANWU.md](docs/SANSHENG_WANWU.md) | Architecture specification (canonical) |
| [ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md) | Module responsibilities |
| [PROJECT_RELATIONSHIPS.md](docs/PROJECT_RELATIONSHIPS.md) | Cross-project pathways |
| [EXECUTION_FLOW.md](docs/EXECUTION_FLOW.md) | Runtime execution flow |
| [VERSION.yaml](VERSION.yaml) | Single source of truth for versions |
| [coordination.yaml](coordination.yaml) | Unified coordination config |
