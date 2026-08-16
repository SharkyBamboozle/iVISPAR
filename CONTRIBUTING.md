# Contributing to Project Blueprint

Thanks for looking at the blueprint itself. **This guide is for people improving
the template.** If you came here wanting to *use* it to start a project, you
don't contribute here — see the [README](README.md) and run `BOOTSTRAP.md` in
your new repo. Like the lifecycle rituals, this file is blueprint machinery: it
is deleted the moment a project is seeded, so nothing here ships downstream.

For the *process* itself — ADRs, stable IDs, notes vs sub-issues, epics, the
changelog, commit conventions — the blueprint follows its own manual,
[`docs/process/contributing.md`](docs/process/contributing.md). Read it; it
applies here too. This page only covers what's **different** about working on a
template.

## Two hats — the shipped records instructions are addressed to seeded projects

The blueprint wears two hats: it is a **template under development** and the
**worked example** of the process it ships. Nearly all of the
`docs/process/` pages hold under both hats. The per-session
**records** instructions do not — `CLAUDE.md` → *Repo workflow* ("every working
session ends with a `docs/records/changelog.md` entry"), the changelog and
lessons steps of `.claude/commands/session-close.md`, and the page headers under
`docs/records/` are **shipped furniture**: correct downstream, inapplicable
here, because in this repo those files are the *stub* of a downstream project's
diary, not a diary. Neither does one premise of the linking pages — that a
`Closes` fires when its PR merges into `development` — because here the
default branch must stay `main` (rule 4). Only the *premise* fails — the
procedure those pages prescribe runs here unchanged. Leave that text exactly
as it is — the exception is declared here, never by weakening the
instructions a seeded project needs.

Four rules follow. They reach every blueprint session through the
blueprint-state admonition at the top of `CLAUDE.md`, and die with it at
bootstrap.

**1 · No tracker IDs in seed-shipped content.** An issue or PR number from this
repo becomes a dangling pointer the moment a project is seeded: downstream it
reads as *that* project's tracker, pointing at work nobody there did. Cite them
freely in commits, PR bodies, and the machinery that never ships (this file, the
lifecycle rituals, `blueprint/` — which is why the examples further down this
page carry issue numbers); in `docs/`, `CLAUDE.md`, `.claude/`, `.github/`,
`scripts/`, and `modules/`, describe the change instead of citing its ticket.
*Overrides:* nothing — citing issues in a changelog or an epic page is correct
downstream and stays correct; the rule is about which *repo's* tracker the
number belongs to. *Enforcement:* advisory (D-004) — a checker needs a
keep/sweep classification as its exemption ledger, so it waits on the sweep that
produces one; review is the backstop until then.

**2 · No session records during regular work.** `docs/records/changelog.md` and
`docs/records/lessons.md` ship to seeded projects. Here they are the stubs a
seeded project fills in, so anything written into them arrives downstream as
false history — a diary of a project the reader never worked on, which
`scripts/check_bootstrap_complete.sh` cannot catch (no `{{TOKEN}}`, no
`BLUEPRINT:` marker). Leave both at their stub state. *Overrides:* `CLAUDE.md` →
*Repo workflow* (the session-changelog rule), steps 1 and 3 of
`.claude/commands/session-close.md`, and the records-commit half of its
step 5 — all correct downstream. *Where the
content goes instead:* whatever will still be true in a seeded project — a
regression case in the matching `scripts/test_*.sh` suite, a rule on a ritual
card under `.claude/commands/`, a page under `docs/process/` — plus the release
line of rule 3. *Enforcement:* the blueprint-records lane of
`scripts/check_docs_truth.py`, which runs in `make verify` and self-disarms when
`blueprint/` is deleted at bootstrap.

**3 · `blueprint/CHANGELOG.md` is written exactly once per release.** It is the
blueprint's only log, and it is written in the caboose commit of the promotion
PR that bumps `blueprint/VERSION` (`/promote`) — not incrementally as work
lands, where entries accumulate for a release that has not happened and drift
from what the tag actually shipped. *Enforcement:* the `release-gate` CI check
fails a promotion whose release log has no entry for the new version, so the
entry cannot be forgotten; "no mid-work edits" is advisory (D-004) — no check
can tell an early entry from a timely one.

**4 · Issues do not auto-close at integration here.** GitHub fires closing
keywords only on PRs merging into the repo's *default* branch. Seeded projects
make `development` the default (`scripts/github_setup.sh`), so the shipped
premise — "the integration branch is the repo default, so every integration PR
is a live close surface" (`docs/process/opening-a-pr.md`) — holds downstream.
It cannot hold here: a template is seeded from its default branch, so `main`,
the released line, must stay the default, and a PR merging into `development`
closes nothing in this repo, however correct its `Closes #NN` line. The issues
close at promotion instead — the promotion PR restates `Closes #N` for every
issue the train completed, and `docs/process/releases.md` step 3 exists
precisely for this main-default case. A merged PR whose target issue is still
open is therefore the *normal between-releases state*: not drift to flag in a
summary, and never cause for a manual close. The **procedure is unchanged —
only the firing moment moves**: tick, readout, and `Closes #NN` land exactly
as the manual says; the `issue-link-guard` vets the keyword at integration,
and the promotion restatement is what finally fires it. In particular, never
downgrade a completing PR to `Part of #NN` on the grounds that the close will
not fire at merge — that hides a completed issue from the guard's completion
check and from the promotion sweep that closes it. *Overrides:* nothing —
the linking pages stay as written (true downstream), and `/session-close`
step 4 already carries the branch this rule feeds: "state why it stays open" —
*awaiting promotion* is the standing answer. *Enforcement:* the manual-close
half is the hard rule's gate (`guard-issue-close.sh` hook +
`issue-close-guard.yml`); the no-false-alarm half is advisory (D-004) — no
check can read a session summary; review is the backstop.

## The repo is its own working skeleton

Core files live at their real destinations, so the blueprint self-tests. Three
consequences:

- **`make verify` is the gate for this repo, not just seeded ones.** Keep it
  green — the strict docs build, the CI meta-gate, and the docs truth-checker
  all run here.
- **The guards guard the blueprint.** Push-to-main, self-merge, and the ADR edit
  lock all apply here. Work on a feature branch → PR into `development`; never
  merge your own PR. Changing a ✅ Decided ADR means a *superseding* ADR (or
  `/unlock-adr` for a maintenance edit).
- **Your scratch stays out of the tree — the rule flips at the seed
  boundary.** `.claude/archive/` is gitignored in *this* repo only — seeded
  projects track theirs, so the `BLUEPRINT:` marker in `.gitignore` removes
  the block at bootstrap. Committing session notes here ships
  blueprint-internal history into every seed (#70). One visible consequence:
  a `/handoff` that follows an already-committed working doc lands as a
  **deletion**, not a rename. That is the intended shape. In the blueprint,
  sessions never commit working files or archives — the risk is
  **contamination**: one session's scratch ships into every seed. In a seeded
  project, the archive is a record of the agent's work, and the risk is
  **loss** — task-end records (the changelog entry, the `/handoff` archive)
  must land on a live branch and ride a PR before the branch or container is
  gone (`docs/process/pushing.md` → *PR lifecycle*). Under both hats, a
  still-running task's files stay uncommitted; only the fate of a *finished*
  task's records differs.
- **Never run `scripts/github_setup.sh` against this repo.** Its first act on
  the code profile is making `development` the default branch — right for
  every seed, wrong here, where `main` must stay the default (the CLAUDE.md
  admonition, rule 4). Blueprint-repo settings changes are made by hand in
  the GitHub UI; the script's payloads are the template that seeds inherit.

Durable findings therefore need a permanent home other than an archive file. A
reproduced bug in the machinery becomes a case in the matching
`scripts/test_*.sh` suite, where `make verify` keeps it honest. The #21
reproduction is the cautionary example: the 🟡→✅ block it demonstrated was
already asserted by `scripts/test_guard_adr.sh`, which shipped in v1.0.0 — the
archive file was redundant the day it was written, and still reached every seed.
A module's instructions are proved the same way, by executing them verbatim in a
throwaway `git init` repo and asserting the result (`git check-attr filter --
<path>` for lfs-assets, per #22), with the assertion folded back into the
module's own steps.

## Know which tier a file is before you touch it

Every file is one of three tiers (`blueprint/TOKENS.md`), and the tier sets the
blast radius of your change:

- **Literal** — byte-identical in every seeded project (hooks, workflows,
  commands, skills, doc templates, the `docs/process/` pages). A change here
  reaches every downstream project through `HARVEST` / `UPDATE`. Highest
  scrutiny; keep it project-agnostic.
- **Tokenized** — carries `{{TOKEN}}` placeholders filled at bootstrap. Never
  hardcode a value a project must choose for itself.
- **Generated / identity** — written fresh per project (README body, filled
  registries, changelog). A blueprint change must not presume its contents.

## Add invariants, not shape

The blueprint stays minimal on purpose. Before adding anything, ask the `HARVEST`
question: is this a **process invariant** (every project wants it → it belongs
here) or **project shape** (a language, a layout, a tool → a `modules/` payload,
or it stays downstream)? **When unsure, leave it out** — it can always be
harvested in a later round.

## Every rule names its enforcer (D-004)

A rule that names no enforcer is just a wish. If you add a convention to
`CLAUDE.md`, the process manual, or a template, wire the thing that catches
violations — a hook, a CI gate, a test, or a template section — and have that
artifact cite the rule back. If it genuinely can't be enforced, label it
*advisory — ⟨reason⟩*. Exception lists you grow are ledgers (D-004): a reason per
entry, a size ceiling, stale entries fail loud, itemized matching only.

## Changes are versioned and tagged

- `blueprint/VERSION` and `blueprint/CHANGELOG.md` record what each release
  changed. Both are written **once per release**, in the promotion caboose
  (`/promote`, rule 3 above) — not on your feature branch as the work lands.
- Releases are **tagged** `v<VERSION>` on `main`; `UPDATE.md` reads those tags to
  find a seeded project's merge base, so downstream sync depends on them. The tag
  is cut when the change lands on `main` (the `HARVEST` / release step) — not on
  your feature branch.

## Test the machinery you touched

- `make verify` green.
- `bash -n` any script you edited; run the guard suites when a hook changes
  (`scripts/test_guard_git.sh`, `scripts/test_guard_adr.sh`).
- A **new** guard ships with a both-ways demonstration — proof it blocks the bad
  case *and* still allows the good one — in the PR body.
- Touched a bootstrap-path file? A clean run must leave no orphaned `{{TOKEN}}`
  or `BLUEPRINT:` marker, and a new top-level machinery file must be added to
  `BOOTSTRAP.md`'s delete list **and** the bootstrap gate's exclude set (this
  file is the reference example — see `scripts/check_bootstrap_complete.sh`).

## Most improvements arrive through HARVEST

The best ideas are found in real projects, not invented here. Hit a rough edge in
a seeded project? That's a **harvest candidate** — file it as a `note` issue
mentioning the blueprint, and it gets judged and batched in via `HARVEST.md`.
Direct PRs are welcome too, especially for bugs, docs, and self-evident wins; for
anything larger, open an issue first so we can weigh it against "keep the
blueprint minimal."

The blueprint is MIT-licensed (see `LICENSE`); contributions are accepted under
the same license.
