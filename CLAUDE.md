# CLAUDE.md

Guidance for working in this repository. Keep it **thin** — a map to the real
docs, not a duplicate of them. Extend over time.

> **Blueprint state.** This repository was seeded from **Project Blueprint**.
> Until `BOOTSTRAP.md` has been run (interview → fill placeholders → delete the
> blueprint machinery), `{{TOKEN}}` placeholders and `<!-- BLUEPRINT: ... -->`
> comments mark unfinished sections — see `blueprint/TOKENS.md`. In the
> blueprint repo itself, this file doubles as the template every new project
> starts from.
>
> **While this admonition is here, you are authoring the template, not working
> in a seeded project.** The per-session *records* instructions below (*Repo
> workflow* → session changelog; `.claude/commands/session-close.md`) — and
> the expectation that merging an integration PR closes its issues — are
> shipped furniture addressed to seeded projects. Four rules override them
> here; reasoning and scope: `CONTRIBUTING.md` → *Two hats*.
>
> 1. **No tracker IDs in seed-shipped content** — an issue or PR number from
>    this repo points at nothing downstream. Cite them in commits, PR bodies,
>    and the machinery deleted at bootstrap; in `docs/`, `.claude/`, and this
>    file, describe the change instead.
> 2. **No session records during regular work** — `docs/records/changelog.md`
>    and `docs/records/lessons.md` ship to seeded projects and stay at their
>    stub state here; an entry written here reaches every seed as false
>    history. Durable findings go where they stay true downstream (a
>    regression case, a ritual card, a `docs/process/` page).
> 3. **`blueprint/CHANGELOG.md` is written exactly once per release**, in the
>    caboose of the promotion PR that bumps `blueprint/VERSION`. It is the
>    blueprint's only log.
> 4. **Issues do not auto-close at integration here — run the PR ritual
>    unchanged anyway.** Closing keywords fire only on PRs into the *default*
>    branch, which stays `main` in this repo (projects seed from it; seeded
>    repos flip theirs to `development`). Tick delivered boxes, post the
>    readout, and write `Closes #NN` on the completing PR exactly as
>    `docs/process/opening-a-pr.md` prescribes — never downgrade to
>    `Part of #NN` because the close "won't fire here". The `issue-link-guard`
>    vets the keyword at integration; the promotion PR restates it, and that
>    restatement is what closes the issue. A merged PR whose issue is still
>    open is expected state — no anomaly to report, never a manual close.
>
> <!-- BLUEPRINT: delete this whole admonition, rules included, at bootstrap. -->

## Hard rules (never, without an explicit user request in THIS session)

*Each rule is hook- and CI-enforced (`guard-git.sh`, `guard-adr.sh`,
branch protection, the CI gates); every block message names the recovery
path.*

- Never push to `main`, and never commit directly to `main` or `development`.
  All work: feature branch → PR into `development`. Never merge your own PR.
- Never commit binary files — D-007. Durable run artifacts go to the data
  repo ({{DATA_REPO}}, if this project has one); if a task seems to need a
  committed binary, stop and name the file + size.
  <!-- BLUEPRINT: binary policy is a per-project decision — this bullet states
  the default (strict/split) posture. At bootstrap, pick a posture per
  modules/README.md → "Binary policy", finalize ADR-0007 (rewrite its Decision
  to the chosen posture, flip it to ✅ Decided, update its registry row), and
  rewrite this bullet to match; wire the same choice in .claude/asset-dirs.txt
  — the single data file read by both the guard-git hook and the repo-hygiene
  CI. For an in-repo-assets project (e.g. a static website) the bullet becomes:
  "Binaries live ONLY under <assets dirs> (LFS for large types); generated
  artifacts are never committed anywhere." -->
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

<!-- BLUEPRINT: Replace with 2–4 dense sentences of project identity: what it
is, what it is for, and the one thing that makes it distinctive. -->

**{{PROJECT_NAME}}** — {{ONE_LINER}}

## Commands

The canonical commands — run these, don't guess:

```bash
make verify    # the verification entrypoint (strict docs build + gate checks)
```

<!-- BLUEPRINT: extend with the project's real build / test / run / lint
commands as they land — one line each, a comment naming what it does. Every
command an agent cannot guess belongs here; deeper how-tos stay in docs/. -->

## Canonical documentation lives in `docs/` (MkDocs Material)

The `docs/` site is the **single source of truth**. Read it before acting.
Build/preview: `docs/process/contributing.md` → *Building the docs locally*.

### Where to read, by task

<!-- BLUEPRINT: Add one row per domain area of this project. Embed any per-task
obligation inline in its row (e.g. "Changing X? Ship the standard artifact
pack — see <page>"). Never hardcode ID ranges or counts (e.g. "Q1–Q21") — they
go stale; link to the registry instead. -->

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

<!-- BLUEPRINT: One bullet per top-level directory, each ≤2 lines, pointing at
the ADR that governs it. Record the layout decision itself as an ADR (Context /
Decision / Consequences / Reversibility) before code lands. -->

- `docs/` — canonical documentation; `docs/.templates/` holds the reusable
  skeletons.
- `.github/` — the workflows are the CI gates.
- `.claude/` — harness policy: hooks, commands, skills, path-scoped rules
  (`rules/` — load only when matching files are touched), and agent scratch
  space (`working/`).
- `scripts/` — repo tooling (see `scripts/README.md`); lasting product value
  never lives here.
<!-- BLUEPRINT: delete the three bullets below at bootstrap — they describe
machinery BOOTSTRAP.md → "Delete the machinery" removes (modules/, blueprint/,
LICENSE). -->
- `modules/` — optional payloads applied via `MODULE.md`; deleted at
  instantiation.
- `blueprint/` — blueprint machinery; deleted by `BOOTSTRAP.md`.
- **LICENSE** — MIT with a template-use waiver; seeded projects choose their
  own.

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

<!-- BLUEPRINT: record only the conventions that DIFFER from tool defaults
(naming, imports, idioms), each ≤1 line, pointing at the linter/formatter
config — or state "none yet — linter defaults apply." -->

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
