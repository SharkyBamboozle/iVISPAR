# Contributing

The process manual, dispatched by **act**: each contribution act has its own
short page — find your situation in the table below and read that page, not
this hub. These conventions are what make the project navigable for humans
and AI agents alike; they are the project's founding decisions, recorded in
the [decisions registry](../decisions/index.md); the topic-shaped doctrine
behind them lives in [Enforcement](enforcement.md) and
[Records & canon](records-and-canon.md).

## Find your act

| About to… | Read |
|---|---|
| File a task, a finding, or an epic child | [Filing work](filing-work.md) |
| Write a commit message | [Committing](committing.md) |
| Push — especially to a branch that had a PR | [Pushing](pushing.md) |
| Open a PR, choose closing keywords | [Opening a PR](opening-a-pr.md) |
| Finish an issue: tick boxes, post the readout | [Closing issues](closing-issues.md) |
| Start, advance, or close out an epic | [Running epics](running-epics.md) |
| Record a significant decision | [Writing ADRs](writing-adrs.md) |
| Add or move a docs page | [Adding docs pages](adding-docs-pages.md) |
| Coin or look up a project term | [Glossary](glossary.md) |
| Decide whether/where a test is needed | [Testing changes](testing-changes.md) |
| End the working session | [Ending a session](ending-a-session.md) |
| Cut a release | [Release checklist](release-checklist.md) · doctrine: [Releases](releases.md) |

The stubs below preserve this page's long-standing section anchors — ✅
Decided ADRs and standing pointers cite them; each names its content's new
home.

## The ADR process

Moved: [Writing ADRs](writing-adrs.md) — the steps, the Decided-page gates,
and the registry-sync rules.

## The record lenses

Moved: [Records & canon → The record lenses](records-and-canon.md#the-record-lenses)
— one home per record type; agent memory vs the canon.

## Issues, sub-issues & notes

Moved: [Filing work](filing-work.md) (task vs note vs epic sub-issue) and
[Closing issues](closing-issues.md) (close-at-completion, ticking, readouts,
operator-only closes).

## Epic pages

Moved: [Running epics](running-epics.md) — stub at kickoff, retrospective at
closeout, note triage.

## Branch model

Moved: [Pushing → Branch model](pushing.md#branch-model) — feature branch →
PR into `development`; `main` is the promoted branch.

## PR lifecycle

Moved: [Pushing](pushing.md) — append-only while OPEN, the PR-state read,
zombie-branch recovery.

## PR ↔ issue linking

Moved: [Opening a PR](opening-a-pr.md) — the closing-keyword grammar and the
issue-link guard.

## Promotion & releases

Moved: [Releases](releases.md) — the two-PR train; step-by-step path:
[Release checklist](release-checklist.md).

## Commit conventions

Moved: [Committing](committing.md) — the story-shaped body and the trailer
machinery.

## Testing conventions (D-005)

Moved: [Testing changes](testing-changes.md) — scaffolding is code;
event-driven test-writing; no coverage thresholds.

## Enforcement layering (D-004)

Moved: [Enforcement](enforcement.md#enforcement-layering-d-004) — every rule
names its enforcer or is explicitly advisory; the four layers.

## Exception lists are ledgers (D-004)

Moved: [Enforcement](enforcement.md#exception-lists-are-ledgers-d-004) — a
reason per entry, a ceiling, staleness fails loud, itemized never blanket.

## Adversarial verification (advisory)

Load-bearing claims (research findings, audit results, a diagnosis about to
drive work, release readiness) get a check whose explicit job is to
**refute** them before they ship — three grades (self-adversarial /
independent verify / adversarial sweep), proposed by the agent with a rough
cost, scaled up, down, or skipped by the owner; a skip is recorded in the
deliverable, never silent. Decision home:
[D-006](../decisions/adr-0006-verification-and-honesty.md); full protocol:
`.claude/skills/adversarial-verify/SKILL.md`.

## Building the docs locally

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

The site builds with `mkdocs build --strict` (also via `make verify`), so
**all internal links must resolve** — check links when you add or move pages.

**Publishing is opt-in and off by default.** The strict build is a *merge
gate* — it runs on every push and PR (`docs.yml`'s `build` job) and publishes
nothing. Deploying the built site to GitHub Pages on merges to
`development`/`main` happens only when the `DEPLOY_DOCS` repository variable is
`true`, which `scripts/github_setup.sh` sets solely under its `--deploy-docs`
opt-in. Keep publishing off for private projects — a Pages site can be publicly
reachable and would expose the docs.

## Growth areas

Sections likely to be added as the project expands — extend the act pages
(and `CLAUDE.md`'s map) as they land, keeping each fact in one canonical home.

<!-- BLUEPRINT: list the areas this project will likely grow into. -->
