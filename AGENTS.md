# AGENTS.md — SanShengWanWu Workspace Persistent Memory

> **Purpose**: Cross-session knowledge base. Every pattern, gotcha, and convention discovered is recorded here so future agent sessions automatically benefit from past learning.
> **Principle**: Each improvement makes future improvements easier.
> **Last updated**: 2026-06-18

---

## Patterns & Conventions

### Architecture
- **Triangle Core (sealed 3)**: fish(S/V0) + cognitive(V/V1) + eon-core(Coord) — must never be broken
- **Derived Projects (open N)**: P₁(porpoise) + P₂(coilia) + P₃(culter) + C(conflict-arbiter) — can add new ones without touching core
- **Single Source of Truth**: `D:/Reasonix/coordination.yaml` — all 7 projects load this
- **Never reference "T" or "meso-cosmos-agent"** — deleted in v7.1, replaced by eon-core
- **Never use "S-T-V" naming** — use "Triangle Core + Derived" or "S/V0, V/V1, Coord"

### README Synchronization
- **Every feature change → update BOTH README.md and README.zh.md in lockstep**
- Check: EN badge counts = ZH badge counts = coordination.yaml counts = actual file counts
- Always add an entry to `## 📋 README Changelog` section
- After any README edit, verify with: `Select-String -Path *.md -Pattern "最后更新|Last updated"` — dates must match

### Git Conventions
- Commit messages: `type: description` (e.g., `docs:`, `fix:`, `refactor:`, `feat:`)
- Push all repos after changes — check `git status` in each project directory
- All 7 repos have both `origin` (GitHub) and `gitee` remotes — push to `origin` for GitHub

### Code Style
- Python: 3.10+ for fish/cognitive/coilia/culter/conflict, 3.12+ for eon-core, 3.11+ for porpoise
- All projects use MIT License
- YAML config files use 2-space indent, no tabs
- SKILL.md files require `---` frontmatter with name/version/last_updated/description

---

## Gotchas (Common Pitfalls)

### Dates
- ⚠️ **Never use future dates.** coordination.yaml `last_sync` and all changelog entries must be ≤ today.
- ⚠️ Check actual date with `Get-Date -Format "yyyy-MM-dd"` before committing.
- ⚠️ ZH READMEs use `:` (ASCII colon) not `：` (full-width) in "最后更新: YYYY-MM-DD"

### Architecture References
- ⚠️ eon-core README claims 10-layer architecture but actual code only has `src/kernel/` (10 modules). proto/ files exist. README now has honest labeling (✅/🟡/🔮) — maintain this honesty.
- ⚠️ porpoise-agent submodule at `external/cognitive-search-engine/` — check if it's active before making breaking changes to cognitive.

### Encoding
- ⚠️ PowerShell `Select-String` on UTF-8 files may display garbled Unicode (emoji, subscript numbers). Use `Get-Content -Encoding UTF8` for accurate reading.
- ⚠️ `write_file` tool writes UTF-8. Files on disk are UTF-8. Don't re-encode.

### Multi-Repo Operations
- ⚠️ When updating all 7 repos, use separate `git -C D:\Reasonix\<project>` commands — don't chain with `;` in a single git command.
- ⚠️ eon-core branch is `main`, all others are `master`.

---

## Style & Preferences

### Communication
- **Language**: Match the user's language. Chinese user → Chinese response. Code/technical terms stay in English.
- **Tone**: Professional, direct, factual. No sycophantic language ("You're absolutely right!", "Great question!").
- **Structure**: Lead with conclusion. Use tables for comparisons. Use lists for steps.
- **Evidence**: Every claim backed by code reference (file:line), command output, or verified count.

### Tool Usage
- **Code exploration**: Prefer `codegraph` tools over `grep` for architecture questions.
- **Multi-step work**: Use `todo_write` to track progress. Keep exactly one `in_progress`.
- **File editing**: Use `multi_edit` for multiple changes to one file (atomic). Use `edit_file` for single changes.
- **Sub-agents**: Use `task`/`explore`/`research` for context-heavy work. Sub-agent results don't enter your context.

### Verification
- **Always verify before claiming completion**: Read the file, run the test, check the count.
- **Cross-reference**: When a number appears in README, verify against actual file count AND coordination.yaml.
- **No assumptions**: If you haven't run the command or read the file, don't claim it exists.

---

## Recent Learnings

### 2026-06-18: Architecture Rename Session
- Renamed all 7 projects from "S-T-V-P₁-P₂" → "Triangle Core(S/V0,V/V1,Coord)+Derived(P₁,P₂,P₃,C)"
- Fixed coordination.yaml dates from 2026-07-11 → 2026-06-18
- eon-core README: added honest 10-layer labeling with ✅/🟡/🔮 status
- Tool learned: PowerShell `-replace` regex in UTF-8 files works; `Select-String` displays garbled but actual content is fine
- Pattern: Use sub-agents for parallel README edits across multiple repos, then fix edge cases manually

### 2026-06-17: README Restoration Session
- Restored 14 README files (7 projects × 2 languages) from historical conversation records
- Created culter-agent and conflict-arbiter READMEs from stubs
- Pattern: Always add `## 📋 README Changelog` section for traceability
- Gotcha: ZH READMEs use `:` not `：` in footer dates
