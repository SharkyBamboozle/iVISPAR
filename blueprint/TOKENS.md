# Placeholder conventions (normative)

The blueprint uses **two tiers of placeholders**, both machine-checkable.
Instantiation is complete only when **both greps below return empty**.

## Tier 1 — mechanical tokens

Substituted verbatim during bootstrap. The full vocabulary (keep it ≤ 8):

| Token | Meaning |
|---|---|
| `{{PROJECT_NAME}}` | Human-readable project name ("Tidepool") |
| `{{PROJECT_SLUG}}` | Repo-name slug ("tidepool") |
| `{{GITHUB_OWNER}}` | GitHub user/org |
| `{{PACKAGE_NAME}}` | Installable package name (python-package module) |
| `{{ONE_LINER}}` | One-sentence project description |
| `{{DATA_REPO}}` | Paired data repo name (data-repo module; else remove) |

Check: run `scripts/check_bootstrap_complete.sh` — its Tier-1 grep is
`git grep -nE '\{\{[A-Z_]+\}\}'` with the machinery excluded
(`blueprint/`, `modules/`, `BOOTSTRAP.md`, `HARVEST.md`, the script itself),
plus the same pattern over file/directory NAMES. The `[A-Z_]+`-immediately-
after-braces regex is what keeps GitHub Actions' `${{ ... }}` (brace, then
space or lowercase) from false-matching — workflow files must never use
bare `{{UPPERCASE}}` forms of their own.

## Tier 2 — judgment blocks

`<!-- BLUEPRINT: ... -->` comments mark **decisions, not substitutions**:
sections a bootstrap session must *write* (project identity, routing-table
rows, which doc areas exist) or *decide* (prune vs keep, adapt patterns).
Unprocessed files still render sanely because the blocks are HTML comments.

In `CLAUDE.md` specifically, Claude Code **strips block-level HTML comments
before injecting the file** into the agent's context (confirmed against the
official memory docs, 2026-07): the markers are invisible to the runtime
agent yet visible to bootstrap/`Read`. This is by design — do not "clean
them up"; they resolve and die at bootstrap.

Check: the same script's Tier-2 grep — `git grep -n 'BLUEPRINT:'` with
the machinery exclusions above — must be empty.

## File-treatment rule of thumb

**Process files are literal** (byte-identical across projects except
explicitly marked judgment spots — e.g. `docs/process/contributing.md`'s
growth-areas block; the `docs/.templates/` skeletons are fully literal);
**identity files are generated** (Tier 2 — `CLAUDE.md` identity sections,
`docs/index.md`, vision seeds); **config files are tokenized** (Tier 1 —
`mkdocs.yml`, `pyproject.toml`). Keeping the literal set byte-identical is
what makes cross-project harvest diffs work.
