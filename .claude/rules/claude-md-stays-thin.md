---
paths:
  - "CLAUDE.md"
---

# CLAUDE.md stays thin

You are editing `CLAUDE.md` — the always-loaded map. Add sections as the
project grows (code layout, how to run the stack, test/lint commands,
service-specific notes), but keep each entry a **pointer** into `docs/` or a
short convention, never a second copy of the docs.

Two maintenance aids: Claude Code's `/doctor` can propose trims when the
file grows — it cuts content derivable from the codebase; keep pitfalls,
rationale, and conventions that differ from defaults. Prefer pointers over
`@path` imports — imports load eagerly into every session; reserve them for
rare, stable, always-needed blocks.
