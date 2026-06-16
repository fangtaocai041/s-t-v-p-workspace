<p align="center">
  🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🔥 Conflict Arbiter — 冲突仲裁层 (C)</h1>
  <p><strong>三角闭环衍生项目 · 多源保护等级冲突检测 · 加权仲裁 · 熔断机制</strong></p>
  <p>Python 3.11+ · 3 级冲突分级 · 中国优先策略</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-1.0.0-ec4899?style=flat-square" alt="v1.0.0"></a>
  <a href="config/arbitration_rules.yaml"><img src="https://img.shields.io/badge/rules-8_sources-f59e0b?style=flat-square" alt="8 sources"></a>
</p>

---

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

**Conflict Arbiter** is the **C** derivative project of the Triangle Core ecosystem. It detects and resolves conflicts between species protection classifications from multiple sources (IUCN, Chinese Red List, CITES, provincial protections, etc.), using weighted arbitration with a circuit breaker for unresolvable cases.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| 🔄 **Multi-source normalization** | Map IUCN / Chinese Red List / CITES / provincial → unified [0-100] numeric scale |
| ⚡ **3-level conflict detection** | 0=Consensus / 1=Minor / 2=Significant / 3=**Circuit Breaker** |
| ⚖️ **Weighted arbitration** | China-priority strategy when `region="china"` |
| ⏱ **Spatiotemporal comparability** | Detects false conflicts (different time periods or regions) |
| 🛡️ **Circuit breaker** | Auto-escalate to manual review for severe conflicts |

---

## Quick Start

### Installation

```bash
git clone https://github.com/fangtaocai041/conflict-arbiter.git
cd conflict-arbiter
pip install -e .
```

### Basic Usage

```python
from conflict_arbiter.src.arbiter import ConflictArbiter

arbiter = ConflictArbiter()

# Detect conflicts between multiple protection sources
result = arbiter.detect_conflicts(
    species_name="Coilia nasus",
    sources=[
        {"source": "iucn", "protection_level": "EN"},
        {"source": "chinese_red_list", "protection_level": "国家二级"},
        {"source": "cites", "protection_level": "II"},
    ],
    region="china",
)

print(f"Conflict Level: {result['conflict_level']}")   # 0-3
print(f"Verdict: {result['verdict']}")                  # Arbitration conclusion
print(f"Consensus Score: {result['consensus']['score']:.1f}")
```

### Via Cross-Project Protocol

```python
from conflict_arbiter.src.adapter import get_adapter

adapter = get_adapter()
print(adapter.health())
# {'project': 'conflict-arbiter', 'status': 'HEALTHY', 'source_weights_loaded': True}
```

---

## Core Features

### 1. Multi-Source Protection Level Detection

```python
from conflict_arbiter.src.arbiter import ConflictArbiter

arbiter = ConflictArbiter()

result = arbiter.detect_conflicts(
    species_name="Neophocaena asiaeorientalis",
    sources=[
        {"source": "iucn", "protection_level": "CR"},
        {"source": "chinese_red_list", "protection_level": "极危"},
        {"source": "provincial_protection", "protection_level": "国家一级"},
    ],
    region="china",
)

print(result)
# {
#   'conflict_level': 0,        # Full consensus
#   'consensus': {'score': 95.0, 'mapped_level': 'CR/极危'},
#   'verdict': '完全一致: 所有来源均判定为最高保护等级',
#   'details': [...]
# }
```

### 2. General Claim Arbitration (with Spatiotemporal Check)

```python
# Arbitrate general claims with time/region awareness
result = arbiter.arbitrate(
    species_name="Culter alburnus",
    claims=[
        {"claim": "种群数量下降", "source": "Resource Survey 2020",
         "weight": 80, "value": 65,
         "time_period": {"start": 2018, "end": 2020},
         "region": "长江中游"},
        {"claim": "资源量稳定", "source": "Fishery Report 2015",
         "weight": 60, "value": 40,
         "time_period": {"start": 2010, "end": 2015},
         "region": "长江下游"},
    ],
    region="china",
)
# Spatiotemporal check: different time periods → no conflict
```

### 3. Conflict Levels

| Level | Name | Action |
|:-----:|------|--------|
| 0 | **Full Consensus** | Pass through |
| 1 | **Minor Difference** | Accept with annotation |
| 2 | **Significant Difference** | Weighted arbitration with CI |
| 3 | **Severe Opposition** | 🛡️ **Circuit Breaker** → manual review |

### 4. China Regional Policy

When `region="china"`:

| Source | Weight | Role |
|--------|:------:|------|
| `chinese_red_list` | 100 | Primary authority |
| `provincial_protection` | 90 | Secondary |
| `iucn` | 40 | Reference only |
| `cites` | 40 | Reference only |

---

## API Reference

### `ConflictArbiter`

| Method | Description |
|--------|-------------|
| `detect_conflicts(species, sources, region)` | Multi-source protection conflict detection |
| `arbitrate(species, claims)` | General claim arbitration with spatiotemporal check |
| `health()` | Engine health status |
| `info()` | Metadata and capabilities |

### `ConflictArbiterAdapter`

| Method | Description |
|--------|-------------|
| `search(query, **kwargs)` | Route to `detect_conflicts` or `arbitrate` based on input |
| `health()` | Proxy to `ConflictArbiter.health()` |
| `info()` | Proxy to `ConflictArbiter.info()` |

---

## Architecture

```
conflict-arbiter/
├── README.md / README.zh.md     ← Documentation
├── pyproject.toml                ← Project metadata (dep: pyyaml)
│
├── src/
│   ├── __init__.py               ← Version v1.0.0
│   ├── arbiter.py                ← ConflictArbiter — core engine
│   │                               • detect_conflicts()
│   │                               • arbitrate()
│   │                               • _normalize_source()
│   │                               • _compute_conflict_level()
│   │                               • _weighted_arbitration()
│   │                               • _circuit_judgment()
│   │                               • _check_spatiotemporal_comparability()
│   └── adapter.py                ← ConflictArbiterAdapter (IProjectAdapter)
│
├── config/
│   ├── agent.yaml                ← Trust thresholds, source weights, circuit breaker
│   └── arbitration_rules.yaml    ← Arbitration rules (custom format)
│
├── tests/                        ← (empty — test infrastructure needed)
├── Dockerfile
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

### Arbitration Flow

```
Sources (IUCN / Chinese Red List / CITES / Provincial)
    │
    ▼
1. Normalize — Map to unified [0-100] numeric axis
    │
    ▼
2. Detect — Compute conflict level [0-3] with spatiotemporal check
    │
    ▼
3. Arbitrate — Weighted consensus with China-first strategy
    │
    ▼
4. Judge — Circuit breaker for level ≥ 3 or insufficient sources
    │
    ▼
Verdict
```

---

## Configuration

### `config/agent.yaml`

```yaml
trust_thresholds:
  high: 75
  medium: 45
  low: 20

source_weights:
  iucn: 80
  chinese_red_list: 100
  cites: 70
  provincial_protection: 90

circuit_breaker:
  max_conflict_level: 3
  min_sources: 3
```

### Normalization (IUCN → Score)

| IUCN | Chinese Red List | Score |
|------|------------------|:-----:|
| EX | 灭绝 | 100 |
| CR | 极危 | 95 |
| EN | 濒危 | 85 |
| VU | 易危 | 70 |
| NT | 近危 | 55 |
| LC | 无危 | 0 |

---

## Related Projects

| Project | Role | Relationship |
|---------|------|--------------|
| **fish-ecology-assistant** | Knowledge V0 | Primary source of conservation data |
| **cognitive-search-engine** | Search V1 | Literature-based protection evidence |
| **eon-core** | Coordinator | Routes outputs to conflict detection |
| **porpoise-agent** | P₁ Porpoise | Source of porpoise conservation data |
| **coilia-agent** | P₂ Coilia | Source of coilia conservation data |
| **culter-agent** | P₃ Culter | Source of culter conservation data |

---

## Contributing

```bash
# Install
pip install -e .

# Test basic functionality
python -c "from conflict_arbiter.src.arbiter import ConflictArbiter; a=ConflictArbiter(); print(a.health())"
```

---

## License

MIT License © 2026

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
