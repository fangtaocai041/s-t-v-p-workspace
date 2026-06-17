---
name: logic-engine
version: "1.0"
last_updated: "2025-07-15"
description: >
  Formal logic reasoning — syllogism, deduction, induction, abduction.
  Three laws of thought (identity, non-contradiction, excluded middle).
  Detect logical fallacies in claims and verify deductive chains.
runAs: inline
---

# ⚖️ Logic Engine — 逻辑推理引擎

> *Playbook for formal reasoning. Not a logic textbook — a diagnostic toolkit.*

---

## PREFLIGHT

Before engaging this skill, **read** the raw claim(s) under examination in full.
If a claim cites authority, **locate the primary source** — never reason from secondary paraphrase.
Flag any claim you cannot trace to a verifiable premise.

---

## THREE LAWS (the iron frame)

| Law | Rule | Violation signal |
|-----|------|-------------------|
| **Identity** | A = A; a thing is itself | Term shifts meaning mid-argument ("species" → "population" → "individual") |
| **Non-contradiction** | ¬(A ∧ ¬A); nothing is both true and false | Same source asserts P and ¬P within a single argument span |
| **Excluded middle** | A ∨ ¬A; a proposition is either true or false | "It's kind of both" without probabilistic framing — flag evasion |

---

## REASONING MODES

### 1. Syllogistic (major → minor → conclusion)

```
MAJOR: All X are Y
MINOR: Z is X
CONCLUSION: ∴ Z is Y
```

Check validity: if either premise is false, the conclusion is unsupported even if the form is valid.

### 2. Deductive chain verification

```
IF A → B  AND  B → C  THEN  A → C
```

Walk the chain link by link. Demand evidence for each →. A single broken link collapses the entire deductive structure.

### 3. Inductive strength

- Sample size adequate? (>30 for normal heuristics)
- Sampling bias? (publication bias, geographic bias, taxonomic bias)
- Counterexamples acknowledged? An induction that ignores disconfirming cases is propaganda, not inference.

### 4. Abductive inference (best explanation)

```
Observe B. IF A → B, THEN hypothesize A.
```

Competing hypotheses are ranked by: **plausibility × simplicity × explanatory scope**.
Always hold ≥2 abductive hypotheses — single-hypothesis abduction is confirmation bias.

---

## FALLACY DETECTION → quick-scan checklist

| Fallacy | Pattern | Counter |
|---------|---------|---------|
| **Circular reasoning** | Conclusion restates premise | Demand independent evidence for the premise |
| **False dichotomy** | "Either X or Y" when Z₁…Zₙ exist | Enumerate the excluded middle |
| **Straw man** | Opponent's position weakened before attack | Restore the strongest form of the opposing argument |
| **Appeal to authority** | "X said so" without evidence | Authority licenses attention, not belief — demand the data |
| **Post hoc** | A preceded B, therefore A caused B | Require mechanism + controls |
| **Cherry-picking** | Selective citation of supporting studies | Search for disconfirming studies explicitly |

---

## WHEN → THEN decision rules

```
WHEN claim contains "therefore" / "thus" / "hence" / "所以" / "因此"
  → extract premise set → verify logical chain integrity → flag gaps

WHEN ≥2 sources contradict AND both appear credible
  → flag contradiction under Non-contradiction law
  → do NOT resolve by averaging; surface the tension

WHEN argument invokes authority without data
  → reclassify as "testimony" not "evidence"
  → downgrade weight unless primary data is produced

WHEN abduction yields only 1 hypothesis
  → force generation of ≥1 competing hypothesis
  → rank by plausibility × simplicity × scope

WHEN deductive chain length > 4 links
  → raise scrutiny: probability of error compounds per link
  → request verification of the weakest link
```

---

## CAPABILITY REFERENCES

- **Source credibility weight**: see `fish-ecology-assistant/credibility.py` — the `CredibilityScorer` class weights sources by peer-review status, replication record, and conflicts of interest. Apply those weights before accepting premises.
- **Contradiction flagging**: pipe to graph-search-engine for cross-source consistency checks.
- **Probabilistic framing**: when excluded-middle binary fails, escalate to bayesian-reasoning skill (if available) or flag as "requires probabilistic treatment."

---

## CLOSING PRINCIPLE

> *"That which is asserted without evidence can be dismissed without evidence."* — Hitchens's razor. A skill is not a belief system. Drive every conclusion back to data or suspend judgment.
