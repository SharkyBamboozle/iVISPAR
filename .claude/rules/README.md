---
paths:
  - ".claude/rules/**"
---

# `.claude/rules/` — path-scoped rules

Claude Code loads every `*.md` file in this directory as standing
instructions. A file **without** `paths:` frontmatter loads at launch (same
tier as `CLAUDE.md`); a file **with** `paths:` (glob patterns) loads only
when Claude works with matching files — guidance that stays out of context
until it is relevant.

Use a rule when guidance is genuinely **path-local** (an area's conventions,
a config directory's discipline) and would otherwise bloat the always-loaded
`CLAUDE.md`. Keep each rule a **thin pointer** into its canonical home in
`CLAUDE.md`/`docs/` — or be itself the canonical home of a purely path-local
convention (one home per fact either way) — one concern per file, ≤ ~30
lines. `config-cites-decision.md` is the worked example.

Hard limits, per D-004 (enforcement doctrine):

- **Rules are context, not enforcement.** A hard "never" rule stays in
  `CLAUDE.md` *and* keeps its hook/CI enforcer; a rule file may remind,
  never guard.
- **Known gap** (measured, Claude Code v2.1.224, headless probes): a
  path-scoped rule does **not** fire when Claude creates a new matching
  file — it fires when an existing match is read or edited — and a rule
  file created mid-session does not fire in the session that created it.
  One SDK-driven remote worker session type injected nothing on touch —
  re-verify on your Claude Code version and session type before relying
  on the trigger.

To check whether a rule fired, inspect your own context: an unscoped rule's
text is present from session start; a `paths:`-scoped rule's text appears
only after touching a matching file. No hook or log reports this.
