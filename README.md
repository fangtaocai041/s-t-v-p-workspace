# SanSheng WanWu · 三生万物


> **Eon-Taiji v8.2 — 并行搜索重构 + DeepSeek优化 + 全周期审计**
>
 道生一 · 一生二 · 二生三 · 三生万物

```
eon-core/                   → Unified Kernel (Ten Layers)
fish-ecology-assistant/     → V0 SupplyVertex (S)
cognitive-search-engine/    → V1 VerifyVertex (V)
porpoise-agent/             → P1 Porpoise Specialist
coilia-agent/               → P2 Coilia Specialist
culter-agent/               → P3 Culter Specialist
conflict-arbiter/           → C  Conflict Arbitration
infrastructure/             → Infrastructure (Emergence/NLP/Image)
fishkb/                     → Fish Knowledge Base
workspace/                  → Unified Workspace (Config/Data/Scripts)
san-sheng-wanwu-core/       → Silicon Life Architecture (RCCA v2.1)
```

## Quick Start

See [workspace/README.md](workspace/README.md).

## Projects

| Project | Version | Vertex | GitHub |
|---------|:-------:|:------:|--------|
| eon-core | v8.1.1 | Kernel | [fangtaocai041/eon-core](https://github.com/fangtaocai041/eon-core) |
| fish-ecology-assistant | v6.5.0 | S/V0 | [fangtaocai041/fish-ecology-assistant](https://github.com/fangtaocai041/fish-ecology-assistant) |
| cognitive-search-engine | v5.7.0 | V/V1 | [fangtaocai041/cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) |
| porpoise-agent | v4.4.0 | P1 | [fangtaocai041/porpoise-agent](https://github.com/fangtaocai041/porpoise-agent) |
| coilia-agent | v1.3.0 | P2 | [fangtaocai041/coilia-agent](https://github.com/fangtaocai041/coilia-agent) |
| culter-agent | v2.1.0 | P3 | [fangtaocai041/culter-agent](https://github.com/fangtaocai041/culter-agent) |
| conflict-arbiter | v1.1.0 | C | [fangtaocai041/conflict-arbiter](https://github.com/fangtaocai041/conflict-arbiter) |
| san-sheng-wanwu-core | v1.1.0 | RCCA | [fangtaocai041/san-sheng-wanwu-core](https://github.com/fangtaocai041/san-sheng-wanwu-core) |
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

## v8.2 Highlights (2026-06-25)

### 并行搜索架构升级
- **retry + 指数退避 + 随机抖动**: 每个引擎失败后自动重试 2 次
- **4 层错误分类**: RETRY(timeout) / RATE_LIMIT(429) / SUSPEND(连续失败) / FATAL(403)
- **RRF + CombMNZ 双融合**: 论文跨引擎排位+共识度双重加权
- **熔断器**: 5 次连续失败 → 挂起 60s → 探测恢复
- **缓存混合**: species_graph 作为内置引擎 (0 token, <1ms)

### DeepSeek 优化
- 触发阈值放宽 3-5× (T5: 2500→10000, T3: 20%→35%)
- 满足阈值 8→15 篇, 总预算 50000→150000 (动态可调)
- 引擎超时 15s→45s, MCP 超时 20s→90s

### Token 动态预算
- `set_token_budget(300000)` 持久化 + `$env:REASONIX_TOKEN_BUDGET` 环境变量覆盖
- 每次搜索实时读取, 进组后可一键提高

### 全周期审计
- 37 文件 95 处修复: 裸 except 全项目清零, Token 迁移, eval 加固, 随机种子, 线程锁, 除零守卫
- 自动化扫描器 `scripts/auto_audit.py` (508 文件, <1 秒)
- 15 维专属审计模板 `docs/AUDIT_TEMPLATE.md`
- 完整调用框架 `docs/CALLING_FRAMEWORK.md`

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
