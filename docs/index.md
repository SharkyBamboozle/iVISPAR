# iVISPAR

iVISPAR is an interactive multi-modal benchmark that evaluates the
visual-spatial reasoning of vision-language models acting as agents: models
solve sliding geom-board, sliding-tile, and Rubik's-Cube puzzles in a closed
action–perception loop, observed as 3D renders, 2D schematics, or text. This
site is the project's single source of truth, written for the researchers
running, extending, and reviewing the benchmark.

!!! abstract "About this documentation"
    This site is the **single source of truth** for the project. It supersedes
    any pre-repo working notes. The [decisions registry](decisions/index.md) is
    the authoritative list of every `D-xxx` decision; topic pages hold the
    detailed reasoning; each fact has exactly one canonical home
    (see [contributing](process/contributing.md)).

## How the docs are organised

Everything project-meta lives in the **Project** tab, in four sections (the
directory layout under `docs/` mirrors the nav):

- **Direction** — why, and where this is going: [vision](direction/vision.md),
  [design principles](direction/design-principles.md),
  [requirements](direction/requirements.md),
  [open questions](direction/open-questions.md), and the
  [roadmap](direction/roadmap.md) — the traceability chain, in reading order.
- **Decisions** — the [decisions registry](decisions/index.md) and one ADR page
  per `D-xxx`.
- **Records** — the history lenses: [epic stories](records/epics/index.md),
  [agent-research reports](records/agent-research/index.md), and the
  [changelog](records/changelog.md).
- **Process** — the [contributing guide](process/contributing.md) (the process
  manual) and the [glossary](process/glossary.md) (track new terminology here).

## Status legend

One legend, used identically across registries, epic pages, issue bodies, and
ADRs:

| Symbol | Meaning |
|--------|---------|
| ✅ | Decided / Done |
| 🟡 | Proposed / In progress — *the default unless challenged* |
| 🔴 | Open |
| 🧊 | Deferred / Superseded — *always names its reactivation trigger* |
