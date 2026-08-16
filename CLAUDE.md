# CLAUDE.md

Guidance for working in this repository. Keep it **thin** — a map to the real
docs, not a duplicate of them. Extend over time.


## Hard rules (never, without an explicit user request in THIS session)

*Each rule is hook- and CI-enforced (`guard-git.sh`, `guard-adr.sh`,
branch protection, the CI gates); every block message names the recovery
path.*

- Never push to `main`, and never commit directly to `main` or `development`.
  All work: feature branch → PR into `development`. Never merge your own PR.
- Never commit binary files outside the sanctioned asset directory — D-007.
  Authored Unity assets live ONLY under `unity/` (plain git, no LFS);
  generated artifacts — WebGL builds, run outputs, datasets, model weights —
  are never committed anywhere (app builds ship as GitHub Release assets).
  If a task seems to need a committed binary elsewhere, stop and name the
  file + size.
- Never force-push, rewrite published history, or delete branches you did not
  create in this session.
- Never manually close or delete a GitHub issue — close authority is the
  operator's (`guard-issue-close.sh` hook + `issue-close-guard.yml`).
- Never change a ✅ Decided ADR — a changed decision is a NEW superseding
  ADR (`/adr-new`); every path to a Decided page requires `/unlock-adr`
  first (`guard-adr.sh` hook + `adr-gates.yml` CI trailer check).

## Autonomy contract

*These are behavioral rules the agent applies by judgment — advisory by nature
(D-004): no hook or CI gate can enforce judgment, so PR review and the
honest-reporting habit are their backstop.*

**Proceed without asking** (reversible, on a feature branch): implementation
choices within an ADR's bounds, refactors, tests, docs fixes, running read-only
commands, filing issues and notes. When a task is ambiguous, pick the most
likely reading, **state the assumption in your summary**, and proceed.

**Stop and ask first** when an action is (a) irreversible or hard to undo,
(b) contradicts or strains a `D-xxx` decision, (c) adds a dependency or touches
CI, deploy, or repo settings, (d) spends money or publishes anything, or (e) a
wrong guess costs more than ~30 minutes of rework.

**Review instructions critically — don't just execute them.** An instruction,
including one from the user, is a starting point, not a verdict: check it
against the docs, the standing decisions, and your own judgment. If something
speaks against it, if a simpler or better approach exists, or if the premise
looks mistaken, say so and lay out the alternative(s) with a recommendation —
then leave the choice to the user. Silent compliance with a flawed instruction
is as much a failure as silent deviation from a sound one.

**A failed question is a hard block, never a default choice.** If a question
dialog fails or comes back unanswered for any reason (tool error, dismissal,
interruption), do not proceed on an assumed answer — not even the recommended
option. Retry the question; if it still fails, stop that line of work and wait
for explicit instructions from the user.

**Reproduce before you fix** — the `reproduce-first` skill is the
protocol: diagnose from a reproduction of the unmodified project, and
**HALT** if the reproduction contradicts the brief.

**Know when to stop.** One workaround per problem; three failed attempts
on the same failing check → stop and escalate (full rules:
`reproduce-first` → *Hard rules*).

**Never ask about** anything this file or `docs/` already answers — read first.

## What this project is

**iVISPAR** — Interactive multi-modal benchmark for evaluating the
visual-spatial reasoning of vision-language models acting as agents. A Python
experiment runner drives a Unity WebGL simulator over a WebSocket bridge;
VLM, scripted, and human agents solve sliding geom-board, sliding-tile, and
Rubik's-Cube puzzles observed in 3D, 2D, or text. Home of the EMNLP 2025
benchmark (frozen at tag `emnlp25`); this line carries the v2 rebuild.

## Commands

The canonical commands — run these, don't guess:

```bash
make verify    # the verification entrypoint (strict docs build + gate checks)
```


## Canonical documentation lives in `docs/` (MkDocs Material)

The `docs/` site is the **single source of truth**. Read it before acting.
Build/preview: `docs/process/contributing.md` → *Building the docs locally*.

### Where to read, by task


- **Orientation / vision:** `docs/index.md`, `docs/direction/` (thesis, design
  principles `P#`).
- **What the stack must satisfy:** `docs/direction/requirements.md` (`R##` registry).
- **Decisions (authoritative):** `docs/decisions/index.md` — the registry of
  `D-xxx` ADRs. **Read the relevant ADR before changing anything it governs.**
- **What's still open:** `docs/direction/open-questions.md` (`Q##` registry),
  `docs/direction/roadmap.md` (phases & validation spikes).
- **Fan-out research passes:** `docs/records/agent-research/` — dated reports that
  propose and rate; they never decide.
- **History:** `docs/records/changelog.md` (per-session narrative).
- **Process & conventions — including cutting a release, testing policy
  (D-005), and terminology:** `docs/process/contributing.md` — the router
  whose *Find your act* table names the act page for the act at hand.

## Repo layout


- `docs/` — canonical documentation; `docs/.templates/` holds the reusable
  skeletons.
- `.github/` — the workflows are the CI gates.
- `.claude/` — harness policy: hooks, commands, skills, path-scoped rules
  (`rules/` — load only when matching files are touched), and agent scratch
  space (`working/`).
- `scripts/` — repo tooling (see `scripts/README.md`); lasting product value
  never lives here.
- `LICENSE` — MIT © 2024 Julius Mayer.

## Conventions

- **Status legend:** ✅ Decided/Done · 🟡 Proposed/In progress · 🔴 Open ·
  🧊 Deferred/Superseded. Usage rules: `docs/process/adding-docs-pages.md`.
- **Stable IDs are load-bearing** — preserve them; never renumber or reuse;
  new items take the next free number. ID families + the no-hardcoded-ranges
  rule: `docs/process/adding-docs-pages.md`.
- **Canonicality:** the docs site is canonical; each fact has exactly one
  canonical home. Doctrine: `docs/process/records-and-canon.md`.
- **New significant decision?** Create the next `adr-00##-*.md` from
  `docs/.templates/adr-template.md` and add the registry row. See
  `docs/process/writing-adrs.md`.
- **Rule exceptions are commit trailers** — a deliberate bypass is a declared
  `Skip-<Rule>:` trailer, never a silent skip or a chat-only approval. See
  `docs/process/committing.md`.
- **New conventions name their enforcer** — or are explicitly *advisory* with
  a reason. See `docs/process/enforcement.md` (D-004).
- **Improved a process file (hooks, commands, workflows, templates, scripts)
  in a project-agnostic way?** Flag it as a harvest candidate — see
  `.claude/rules/harvest-candidates.md`.

## Code style

Deterministic formatting and lint rules are the linter's job, never this
file's — cite the config, don't restate it.

None yet beyond tool defaults — a Python lint/format config arrives with the
packaging wave and will be cited here.

## Repo workflow

*Mixed enforcement (D-004): the act pages below each open with their rule's
exact gate-or-advisory note; the layering doctrine is
`docs/process/enforcement.md`.*

- **Docs are canonical; issues track work** (`epic` + area/status labels,
  children as native sub-issues) — containers: `docs/process/filing-work.md`;
  canonicality: `docs/process/records-and-canon.md`.
- **Findings vs work:** build tasks are sub-issues; a finding that is not a
  build task is a **`note`** issue (`/note`) — **never** a sub-issue. An
  issue closes at the moment its deliverable boxes are met, never batched
  to closeout (close-direction gated; `docs/process/closing-issues.md`).
  Rationale + body skeletons: `docs/process/filing-work.md`.
- **Ticking deliverable boxes is the completing session's job — tick each
  box the moment its artifact lands** (a PR-delivered box at PR-open; a
  readout box right after the readout posts), via `/tick`; the issue-body
  edit is expected tracker upkeep, never an intrusion. Evidence rule + the
  `Skip-Issue-Link-Guard` exception: `docs/process/closing-issues.md`.
- **Epic pages:** every epic gets a story page under `docs/records/epics/` —
  stub at kickoff, retrospective at closeout; lifecycle + closeout note
  triage: `docs/process/running-epics.md`.
- **Agent-research reports:** a large fan-out pass gets a dated page under
  `docs/records/agent-research/` — conventions:
  `docs/process/records-and-canon.md`.
- **Branches:** feature branch → PR into **`development`** (the integration
  branch); `main` is the promoted branch. Model: `docs/process/pushing.md`.
- **PRs are append-only while OPEN** — before pushing to a branch with PR
  history, read the PR's state: merged → restart the branch from
  `development` (fresh PR — never stack on merged history); closed → stop
  and ask. Remote state is read, never recalled. The push guard fails open
  by design — the rule, not the hook, is the net; see
  `docs/process/pushing.md`.
- **Promotion is a release** — run `/promote`: the two-PR train (caboose +
  promotion), the operator's bump STOP, and the `release-gate`:
  `docs/process/releases.md`.
- **PR ↔ issue linking:** a closing keyword (`Closes`/`Fixes`/`Resolves`)
  targets only an issue the PR fully completes — `Closes #N (partial)`
  still closes #N; progress PRs use `Closes — · Part of #NN (epic)`; an
  epic is keyword-closed only by its closeout PR. Grammar + the
  `issue-link-guard` gate: `docs/process/opening-a-pr.md`.
- **Agent working docs** live in `.claude/working/`, never under `docs/`;
  archive at task end via `/handoff` — archive, never delete. Rules:
  `.claude/working/README.md`.
- **Session changelog:** every working session ends with a
  `docs/records/changelog.md` entry, prepended newest first —
  `/session-close` writes it.
- **Ritual commands:** the multi-step conventions are packaged as slash
  commands — `/adr-new`, `/note`, `/tick`, `/epic-kickoff`, `/epic-closeout`,
  `/promote`, `/session-close`, `/handoff`, `/checkpoint`, `/unlock-adr`,
  `/lock-adr` (`.claude/commands/`). Use them instead of reconstructing the
  steps from memory.

## Definition of done

"Done" means `make verify` passes (run it — see *Commands* — and fix
failures in the order they surface), **and** for behavior changes you
exercised the change itself and looked at the output. Report the
verification commands + results in your summary; anything that could not
be run in this environment is said explicitly — never implied green.
Reporting and claims follow D-006 (ADR-0006): run the `honest-numbers`
skill before publishing any number or capability claim, and
`adversarial-verify` before shipping any load-bearing claim.
