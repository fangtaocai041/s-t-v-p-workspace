# SanSheng WanWu · 三生万物


> **Eon-Taiji v8.2 \u2014 Seven-Project Dynamic Living System**
>
 道生一 \u00b7 一生二 \u00b7 二生三 \u00b7 三生万物

```
eon-core/                   \u2192 Unified Kernel (Ten Layers)
fish-ecology-assistant/     \u2192 V0 SupplyVertex (S)
cognitive-search-engine/    \u2192 V1 VerifyVertex (V)
porpoise-agent/             \u2192 P1 Porpoise Specialist
coilia-agent/               \u2192 P2 Coilia Specialist
culter-agent/               \u2192 P3 Culter Specialist
conflict-arbiter/           \u2192 C  Conflict Arbitration
infrastructure/             \u2192 Infrastructure (Emergence/NLP/Image)
fishkb/                     \u2192 Fish Knowledge Base
workspace/                  \u2192 Unified Workspace (Config/Data/Scripts)
san-sheng-wanwu-core/       \u2192 Silicon Life Architecture (RCCA v2.1)
```

## Quick Start

See [workspace/README.md](workspace/README.md).

## Projects

| Project | Version | Vertex | GitHub |
|---------|:-------:|:------:|--------|
| eon-core | v8.2.0 | Kernel | [fangtaocai041/eon-core](https://github.com/fangtaocai041/eon-core) |
| fish-ecology-assistant | v6.6.0 | S/V0 | [fangtaocai041/fish-ecology-assistant](https://github.com/fangtaocai041/fish-ecology-assistant) |
| cognitive-search-engine | v5.10.0 | V/V1 | [fangtaocai041/cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) |
| porpoise-agent | v2.2.0 | P1 | [fangtaocai041/porpoise-agent](https://github.com/fangtaocai041/porpoise-agent) |
| coilia-agent | v1.4.0 | P2 | [fangtaocai041/coilia-agent](https://github.com/fangtaocai041/coilia-agent) |
| culter-agent | v2.1.0 | P3 | [fangtaocai041/culter-agent](https://github.com/fangtaocai041/culter-agent) |
| conflict-arbiter | v1.1.0 | C | [fangtaocai041/conflict-arbiter](https://github.com/fangtaocai041/conflict-arbiter) |
| san-sheng-wanwu-core | v2.1.0 | RCCA | [fangtaocai041/san-sheng-wanwu-core](https://github.com/fangtaocai041/san-sheng-wanwu-core) |
| infrastructure | v0.8.0 | Shared | Internal |

## RCCA Integration (v2.1.0)

RCCA (Recursive Convergence Cognitive Architecture) is deployed across all 7 sub-projects.

See [workspace/README.md](workspace/README.md) for usage.

## Senses Layer (workspace/senses/)

Portable sensing protocol + domain knowledge (12 disciplines), zero external dependencies.

See [workspace/README.md](workspace/README.md) for usage.


## Interactive Guidance (fuzzy goals?)

When you don't know what to do, use these slash commands to find your way:

| Command | Purpose |
|---------|---------|
| `/explore-workspace` | "Not sure what I can do" - chat about interests, get recommendations |
| `/focus-research` | "I have a vague research idea" - progressively focus to an actionable plan |
| `/discover-species` | "I don't know which species to study" - random/related/topic discovery |
| `/capabilities` | "What else can I do here?" - full capability overview + scenario matching |

**Tip:** Start with `/explore-workspace` whenever you feel unsure. No need for a clear goal - we'll find one together.


## Pipelines

```
STANDARD:  fish.search -> cognitive.verify -> conflict.arbitrate -> fish.score
FAST:      fish.search -> fish.score
FULL:      fish.search -> cognitive.verify -> conflict.arbitrate -> eon.analyze -> fish.score
PHASE_0-5: portrait -> stats -> trend -> gaps -> synthesis -> reasoning
```

## Tests (910 total)

| Project | Tests |
|---------|:-----:|
| san-sheng-wanwu-core | 181 |
| porpoise-agent | 185 |
| coilia-agent | 144 |
| cognitive-search-engine | 97 |
| eon-core | 65 |
| fish-ecology-assistant | 59 |
| infrastructure | 57 |
| conflict-arbiter | 48 |
| culter-agent | 36 |
| workspace pipeline | 38 |

## Docs

- VERSION.yaml - Single-source version truth
- coordination.yaml - Cross-project coordination config
- [workspace/README.md](workspace/README.md) - Workspace-level guide

## License
MIT (c) 2026 fangtaocai041
