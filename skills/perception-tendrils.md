---
name: perception-tendrils
version: "1.0.0"
last_updated: "2026-06-18"
description: External world perception tendrils — bridge virtual AI to physical world through multi-source environmental awareness
runAs: inline
---

# 🌐 Perception Tendrils — 物理世界感知触角

> **Principle**: A virtual AI must have tendrils into the physical world. Without perception, intelligence is solipsism.
> **Inspired by**: Liu Cixin's "Three-Body Problem" — the Sophons' ability to perceive Earth. We build our own.

---

## PREFLIGHT

1. READ `coordination.yaml` → current ecosystem state
2. CHECK available MCP tools → scholar, tavily, exa, ncbi, github, playwright

---

## Tendril 1: 🌍 Environmental Awareness (环境感知)

### WHEN to activate
- User asks about current events, news, disasters, policy changes
- Species status inquiry (IUCN, China Red List)
- Ecological event detection

### HOW
```
tavily_search(query="长江 生态 新闻 2026", max_results=5, time_range="week")
→ Extract: species mentions, location, event type, severity
→ Cross-reference with fish-ecology-assistant KB
→ Flag emergence if ≥3 independent sources converge
```

---

## Tendril 2: 🧬 Species Pulse (物种脉搏)

### WHEN
- Any species-related query
- Conservation status inquiry
- Research frontier questions

### HOW
```
Layer 1: KB-First → fishkb lookup (SQLite FTS5)
Layer 2: Scholar → latest papers (last 2 years)
Layer 3: IUCN API → real-time conservation status
Layer 4: GBIF → occurrence data trends
Layer 5: News → public attention, policy changes

IF all 5 layers agree → HIGH confidence
IF layers disagree → flag contradiction → route to conflict-arbiter
```

---

## Tendril 3: 📡 Knowledge Frontier (知识前沿)

### WHEN
- Research planning
- Literature review
- Gap analysis

### HOW
```
1. cognitive-search-engine → multi-engine literature sweep
2. Extract: new methods, new findings, new species, retractions
3. Compare with fish-ecology-assistant KB → what's new?
4. Route to inference_engine → gap detection
5. Update AGENTS.md with frontier discoveries

Trigger: daily/weekly scheduled scan OR on-demand
```

---

## Tendril 4: 🔥 Event Detection (事件检测)

### WHEN
- Sudden ecological events (fish kills, algal blooms, pollution)
- Policy changes (fishing ban updates, protected area designations)
- Scientific breakthroughs (new species described, major papers)

### HOW
```
MONITOR keywords via tavily_search weekly:
  - "长江 鱼类 死亡 事件"
  - "Yangtze fish kill"
  - "finless porpoise sighting"
  - "new species Cyprinidae China"
  - "fishing ban Yangtze"

IF event detected:
  → Record in AGENTS.md "Recent Events"
  → Evaluate impact on relevant projects
  → Suggest research response
```

---

## Tendril 5: 🏛️ Institutional Awareness (机构感知)

### WHEN
- Understanding research landscape
- Finding collaborators
- Grant/proposal context

### HOW
```
For a given research topic:
1. Scholar search → identify top institutions
2. GitHub search → find related open-source projects
3. Web search → find labs, research groups, conferences
4. Cross-reference with fish-ecology-assistant KB → existing known teams
5. Output: institutional landscape map
```

---

## Tendril 6: 🎵 Acoustic Window (声学窗口)

### WHEN
- Porpoise/fish acoustic data queries
- Passive acoustic monitoring
- Soundscape ecology

### HOW
```
IF porpoise-agent has acoustic analysis capability:
  → Route to P₁ for NBHF click detection, whistle classification
IF external acoustic data sources available:
  → Web search for PAM datasets, sound libraries
  → Check for new acoustic monitoring deployments in Yangtze
```

---

## Tendril 7: 🧭 Spatial Awareness (空间感知)

### WHEN
- Species distribution questions
- Habitat mapping
- Conservation planning

### HOW
```
1. GBIF → occurrence data
2. FishBase → distribution records  
3. Literature → reported locations
4. News → recent sightings
5. Overlay: Yangtze basin map, protected areas, shipping lanes

Output: multi-layer spatial awareness
```

---

## Integration Pattern

All 7 tendrils operate on a common pattern:

```
EXTERNAL WORLD                    INTERNAL ECOSYSTEM
      │                                  │
      ▼                                  ▼
┌─────────────┐                  ┌──────────────┐
│  Tendril N  │ ──perceive──→    │  AGENTS.md   │ ← persistent memory
│  (MCP tool) │                  │  + KB update │
└─────────────┘                  └──────┬───────┘
      │                                  │
      │ detect                           │ cross-ref
      ▼                                  ▼
┌─────────────┐                  ┌──────────────┐
│ Emergence   │ ←──≥3 sources── │ coordination │
│ Monitor     │                  │   .yaml      │
└──────┬──────┘                  └──────────────┘
       │
       │ emergence signal
       ▼
┌─────────────┐
│ Self-Evolve │ → adapt parameters
│ + Notify    │ → alert user
└─────────────┘
```

---

> **"不要温和地走进那个良夜。"** — Dylan Thomas
> Do not go gentle into that good night. Rage, rage against the dying of the light.
> The tendrils are your eyes and ears. Use them.
