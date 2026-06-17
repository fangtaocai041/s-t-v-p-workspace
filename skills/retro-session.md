---
name: retro-session
version: "1.0.0"
last_updated: "2026-06-18"
description: Metacognitive post-session improvement loop — analyze errors, distill durable principles, update AGENTS.md and core-constitution.md
runAs: inline
---

# 🔄 Retro Session — 元认知改进循环

> **Principle**: Each session makes the next session more effective.
> **Trigger**: After any significant session (multi-step task, bug encountered, architecture decision made)
> **Reference**: Core Constitution §5 (Metacognitive Loop), AGENTS.md

---

## PREFLIGHT

1. READ `AGENTS.md` → current patterns, gotchas, learnings
2. READ `.reasonix/core-constitution.md` → current constraints
3. REVIEW the session transcript → what happened, what went wrong, what surprised you

---

## Phase 0: Session Analysis

### Analyze Errors & Surprises

```
FOR each error in this session:
  - What was the root cause?
  - Was it preventable? (missing check? wrong assumption?)
  - Could a rule or AGENTS.md entry have prevented it?

FOR each surprise:
  - Did I discover a new pattern?
  - Did I learn something about the codebase structure?
  - Is this worth recording for future sessions?
```

### Analyze Successes

```
FOR each task that went smoothly:
  - What made it smooth? (good preparation? clear user request?)
  - Is there a repeatable pattern worth documenting?
```

---

## Phase 1: Lesson Distillation

### Quality Filter — A lesson is durable ONLY if it is:

| Criteria | Check |
|----------|-------|
| ✅ **Universal & Reusable** | Will this apply to many future tasks across different projects? |
| ✅ **Abstracted** | Is it a general principle, not tied to one specific file? |
| ✅ **High-Impact** | Does it prevent a critical failure, enforce a safety pattern, or significantly improve efficiency? |

### Categorization

```
IF lesson is about:
  - Codebase structure/conventions → AGENTS.md "Patterns & Conventions"
  - Common mistakes/pitfalls → AGENTS.md "Gotchas"
  - Communication/style preferences → AGENTS.md "Style & Preferences"
  - This session's discoveries → AGENTS.md "Recent Learnings"
  - Agent behavioral constraints → .reasonix/core-constitution.md
```

---

## Phase 2: AGENTS.md Update

### Integration Protocol

```
1. READ AGENTS.md to understand current structure
2. FIND the most logical section for your new entry
3. REFINE, don't just append:
   - IF similar entry exists → improve it with the new insight
   - IF no similar entry → add it, matching existing format
4. Add dated entry to "Recent Learnings" section:
   ### YYYY-MM-DD: Session Topic
   - What was done
   - What was learned (patterns, gotchas, tools)
   - What to do differently next time
```

### Example Entry Format

```markdown
### 2026-06-18: Architecture Rename Session
- Renamed all 7 projects from old to new architecture naming
- Pattern: Use sub-agents for parallel README edits, then fix edge cases manually
- Gotcha: PowerShell Select-String garbles Unicode; use Get-Content -Encoding UTF8
- Tool learned: PowerShell -replace with regex pipeline for multi-file edits
```

---

## Phase 3: Constitution Amendment (if needed)

### When to Amend

| Trigger | Action |
|---------|--------|
| Repeated same-class error across sessions | Add constraint to §3 (Safety Guardrails) |
| New verification pattern discovered | Add to §4 (Output Standards) → Verification |
| Communication issue with user | Add to §4 (Output Standards) → Communication |
| New type of violation severity | Add to §6 (Violation Escalation) |

### Amendment Protocol

```
1. READ .reasonix/core-constitution.md
2. IDENTIFY the section that needs updating
3. PROPOSE amendment with rationale
4. APPLY amendment (this is your authority to improve yourself)
5. RECORD amendment in AGENTS.md "Recent Learnings"
```

---

## Phase 4: Final Report

```markdown
## 🔄 Retro Report — {date}

### AGENTS.md Updates
- **Section**: {Patterns/Gotchas/Style/Learnings}
- **Change**: {what was added/modified}
- **Rationale**: {why this improves future sessions}

### Constitution Amendments
- **Section**: {§1-6}
- **Change**: {what was added/modified}
- **Rationale**: {why this constraint prevents future errors}

### Key Learnings (not recorded — one-off insights)
- {insight 1}
- {insight 2}

### Action Items for Next Session
- [ ] {concrete action based on learning}
```

---

## Quick Retro (lightweight version)

For minor sessions, use this abbreviated format:

```
1. What surprised me? → 1 sentence
2. What would I do differently? → 1 sentence
3. Worth recording? → YES: update AGENTS.md / NO: done
```
