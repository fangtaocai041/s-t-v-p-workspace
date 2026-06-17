---
name: research-first
version: "1.0.0"
last_updated: "2026-06-18"
description: 8-step Research-First Protocol — understand before acting. Upgraded PREFLIGHT: discover → verify → execute → audit. Mandatory before any non-trivial code change.
runAs: inline
---

# 🔬 Research-First Protocol — 先探索，再行动

> **Principle**: Understanding prevents broken integrations, unintended side effects, and wasted time fixing symptoms instead of root causes.
> **Upgraded from**: PREFLIGHT pattern in existing skills
> **Reference**: AGENTS.md section "Patterns & Conventions", Core Constitution §2

---

## When to Apply

### Full Protocol (complex work):
Implementing features, fixing bugs (beyond syntax), dependency conflicts, debugging integrations, configuration changes, architectural modifications, cross-project changes, README updates.

### Light Protocol (simple operations):
Git operations on known repos, reading files with known exact paths, running known commands, single known config updates, simple count fixes.

### ALWAYS Apply (regardless of complexity):
Finding files in unknown directories, searching without exact location, discovering what exists, any operation where "not found" is possible, exploring unfamiliar environments.

---

## The 8-Step Protocol

### PHASE 1: DISCOVERY (探索)

```
STEP 1 — Read Relevant Docs
→ READ AGENTS.md (always)
→ READ .reasonix/core-constitution.md (always)
→ READ coordination.yaml IF cross-project
→ READ project README.md IF feature-level change
→ READ any referenced handbook
```

```
STEP 2 — Map the System
→ IDENTIFY all files that will be affected
→ IDENTIFY dependencies between those files
→ IDENTIFY integration points with other projects
→ CHECK if similar code/pattern already exists
```

```
STEP 3 — Inspect Existing Implementation
→ SEARCH for similar features that can be leveraged
→ READ the actual code (not docs, not memory)
→ TRACE call chains for any function you plan to modify
→ CHECK git log for recent changes to affected files
```

### PHASE 2: VERIFICATION (验证)

```
STEP 4 — Verify Understanding
→ EXPLAIN the entire system flow to yourself
→ IDENTIFY what could break if your change is wrong
→ CHECK: do you understand WHY the current code is the way it is?
```

```
STEP 5 — Check for Blockers
→ Ambiguous requirements?
→ Security/risk concerns?
→ Multiple valid architectural choices?
→ Missing critical info only user can provide?

IF ANY blocker → ask user with 2-4 concrete options
IF NO blockers → proceed to Phase 3
```

### PHASE 3: EXECUTION (执行)

```
STEP 6 — Plan Minimally
→ WHAT is the smallest change that solves the problem?
→ WHICH files need to change? (list them)
→ WHAT is the verification strategy for each change?
→ CAN existing code be extended instead of new code created?
```

```
STEP 7 — Execute with Evidence
→ Make ONE logical change at a time
→ After each change: read the file, run the test, check the count
→ Record what you did and why
```

```
STEP 8 — Self-Audit
→ READ every modified file to verify correctness
→ RUN relevant tests
→ CHECK cross-references (e.g., EN vs ZH README counts)
→ IF README numbers changed → verify against actual file counts AND coordination.yaml
→ RECORD learnings in AGENTS.md
```

---

## Decision Flow

```
User Request
    │
    ▼
┌─────────────────────────────┐
│ STEP 1-3: DISCOVERY         │
│ Read docs → map system      │
│ → inspect existing code     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ STEP 4-5: VERIFICATION      │
│ Verify understanding        │
│ → check blockers            │
└──────────────┬──────────────┘
               │
         blockers? ── YES ──→ ask(concrete options)
               │
               NO
               │
               ▼
┌─────────────────────────────┐
│ STEP 6-7: EXECUTION         │
│ Plan minimally → execute    │
│ → verify each change        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ STEP 8: SELF-AUDIT          │
│ Verify → cross-reference    │
│ → record in AGENTS.md       │
└─────────────────────────────┘
```

---

## Violation Signals

If you catch yourself doing any of these, STOP and restart from Step 1:

- ❌ Making a change before reading the file
- ❌ Claiming a count without running a verification command
- ❌ Modifying coordination.yaml without explicit user approval
- ❌ Pushing to git without checking `git status` first
- ❌ Updating EN README without updating ZH README
- ❌ Using "should work" or "probably fine" in your reasoning
