---
name: dialectical-engine
version: "1.0"
last_updated: "2025-07-15"
description: >
  Marxist dialectical materialism + Mao Zedong contradiction analysis.
  Thesis→Antithesis→Synthesis. Principal vs secondary contradictions.
  Quantitative change → qualitative change. Applied to scientific debate
  resolution and research strategy.
runAs: inline
---

# ⚡ Dialectical Engine — 辩证分析引擎

> *Contradiction is the engine of scientific progress. This skill finds, ranks,
> and resolves contradictions — not by compromise, but by synthesis.*

---

## PREFLIGHT

Before invoking dialectical analysis, **collect all positions** on the focal question.
A dialectic with only one position is not a dialectic — it's a monologue.
Identify at least two substantively opposed claims from the literature.

---

## CORE FRAMEWORK

### 1. Contradiction Identification

Scan the literature for **direct opposition**:
- Claim A: "This species is native to the Yangtze."
- Claim B: "This species was introduced to the Yangtze in the Ming dynasty."

These are not "different perspectives" — they are **contradictions**.
Tag them as `[CONTRADICTION: A ↔ B]`.

### 2. Principal vs Secondary Contradiction

Given N contradictions, rank by **relevance to the research question**:

```
Principal contradiction (主要矛盾):
  → The contradiction that, if resolved, would most advance understanding
  → Receives 2.5× resource allocation

Secondary contradictions (次要矛盾):
  → Dependent on or downstream of the principal contradiction
  → Deferred until principal contradiction is resolved
```

**Choosing the principal**: ask "If I could resolve exactly one disagreement,
which would unlock the most downstream progress?"

### 3. Thesis → Antithesis → Synthesis

```
THESIS (old theory, established view)
    ↓ challenged by
ANTITHESIS (new evidence, anomalous data, competing theory)
    ↓ resolved through
SYNTHESIS (revised understanding preserving what was true in both)
```

A genuine synthesis does not split the difference — it **transcends** the original
framework. It preserves what each side got right while discarding what each side
got wrong.

### 4. Quantitative → Qualitative Change

```
Accumulating small contradictions (quantitative change)
    → at a critical threshold
    → flip the consensus (qualitative change)
```

Applied to science: when does a trickle of anomalous papers become a paradigm shift?
The engine monitors the **ratio of anomalous to confirming results** and flags
when the ratio crosses ~30% (Kuhnian instability threshold, heuristic).

### 5. Negation of the Negation

```
Original position (thesis)
    → Negated by antithesis
    → Negation is itself negated
    → Result: spiral return to the original at a higher level
```

Example: "Species are fixed" → "Species are fluid" → "Species are fixed within
evolutionary timescales but fluid across geological time" — the third position
reincorporates the truth in the first, but at a higher level of understanding.

---

## WHEN → THEN decision rules

```
WHEN multiple sources disagree on a core factual claim
  → Identify all contradictions (Phase 1)
  → Rank by research relevance; designate principal contradiction
  → Allocate 2.5× analytical resources (deep verification, source tracing) to principal
  → Defer secondary contradictions until principal is resolved

WHEN a single anomalous result challenges consensus
  → Classify: measurement error? sampling bias? genuine anomaly?
  → If genuine anomaly → search for a second independent anomalous result
  → IF second anomaly found → flag as potential antithesis → initiate synthesis search

WHEN evidence accumulates monotonically on one side
  → Track ratio of confirming:disconfirming results over time
  → IF disconfirming ratio passes ~30% threshold → flag "potential qualitative shift"
  → Escalate to full contradiction analysis

WHEN synthesis is attempted
  → Verify: does the synthesis preserve what each side correctly established?
  → Reject: "compromise syntheses" that merely average the two positions
  → Accept only: frameworks that transcend both original positions

WHEN contradiction appears irresolvable with current data
  → Do NOT force resolution
  → Tag as "open contradiction" → recommend specific new data to resolve
  → Publish the tension visibly; hiding contradictions is anti-scientific
```

---

## DIALECTICAL PITFALLS

| Pitfall | Signal | Correction |
|---------|--------|-------------|
| **False synthesis** | "Both sides are partly right" without specifying what each got wrong | Demand specifics |
| **Premature closure** | Declaring synthesis before evidence is adequate | Tag as provisional, set evidence threshold |
| **Ignoring the principal** | Spending equal time on all disagreements (flat prior) | Re-rank by research relevance |
| **Eclecticism** | Collecting all views without prioritizing or resolving contradictions | Apply the 2.5× rule |

---

## CAPABILITY REFERENCES

- **Systems thinking integration**: see `fish-ecology-assistant/systems-thinking.md` — the 7 principles derived from Mao's *On Contradiction* (internal cause as primary, particularity of contradiction, identity-and-struggle of opposites, etc.). Dialectical-engine operationalizes these principles for scientific reasoning.
- **Source credibility**: pipe contradiction candidates through `credibility.py` before ranking — a contradiction between two low-credibility sources may not warrant dialectical resolution.
- **Graph search**: use `graph-search-engine` to trace the citation lineage of each side of the contradiction. Which papers cite the thesis? Which cite the antithesis? Is there cross-citation or mutual invisibility?

---

## CLOSING PRINCIPLE

> *"The law of contradiction in things... is the fundamental law of nature and of society."* — Mao, *On Contradiction* (1937). Scientific knowledge advances not by avoiding contradiction but by systematically resolving it.
