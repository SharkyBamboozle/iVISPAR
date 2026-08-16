# AGENTS.md

**The agent instructions for this repository live in [`CLAUDE.md`](CLAUDE.md).
Read it first and follow it — the contract there applies to *every* AI coding
agent working here, not just Claude Code.**

This file is a pointer, not a second copy. Tools that look for `AGENTS.md`
(Codex and others following the convention) are sent to the one maintained
home so the rules never drift between two files. When `CLAUDE.md` and this
file seem to disagree, `CLAUDE.md` wins.

## What applies to you, whatever agent you are

The *process and behavior* in `CLAUDE.md` is tool-neutral and binding:

- **Hard rules** — feature branch → PR into `development`; never push to or
  commit on `main`; no self-merges; no force-pushes or history rewrites; no
  committed binaries; never change a ✅ Decided ADR (supersede it instead).
- **Autonomy contract** — when to proceed vs. stop and ask; review
  instructions critically instead of executing them blindly; reproduce before
  you fix; honest reporting and adversarial verification of load-bearing claims.
- **`docs/` is the single source of truth** — read it before acting; the
  decisions registry (`docs/decisions/`) is authoritative for `D-xxx` ADRs.

These are enforced **server-side by CI** (`.github/workflows/`) for every
change, by any agent or human — so they bind you even though the Claude-only
tooling below never runs in your session.

## What is Claude Code-specific (other agents can ignore it)

The `CLAUDE.md` file and the entire `.claude/` directory are Claude Code
harness config; other tools simply skip them. You don't need them to comply —
CI is the backstop — but note these conveniences won't fire for you:

- `.claude/hooks/` — edit-time guard hooks that nudge or block bad commits;
- `.claude/commands/` — ritual slash commands (`/adr-new`, `/note`, …); do the
  steps by hand, following `docs/process/contributing.md`;
- `.claude/skills/` — on-demand protocol cards (still readable as plain
  Markdown if you want the detail);
- `.claude/rules/` and `.claude/settings.json` — path-scoped rules and
  permission wiring, specific to Claude Code (still readable as plain
  Markdown).

Everything else in the repo — `docs/`, `.github/`, `scripts/`, `Makefile` —
is tool-neutral. When in doubt, start at `docs/` and `CLAUDE.md`.
