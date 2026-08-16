# ADR-0002 — Work tracking: epics, sub-issues, and notes

- **Status:** ✅ Decided
- **Decision ID:** D-002
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** D-001 (documentation & records — issues track work,
  docs hold the truth those issues produce)

## Context

A project driven by agent sessions produces two very different kinds of
items, continuously: **work to do** and **things learned along the way**.
Mixed into one list, they corrupt each other. A finding filed as a task
never reaches "done" and leaves its parent perpetually unfinished; a task
buried among observations gets lost; and "how far along are we?" stops
having an answer. The tracking system must keep the two questions separable:
*what's left to build?* and *what did we learn / should we reconsider?*

## Decision

**GitHub issues track work; findings are first-class but never tasks.**

- **Epics** (`epic` label) group a body of work; children are attached as
  **native sub-issues**. Sub-issues are **build tasks** — concrete
  deliverables that count toward the epic's completion. Scope is living:
  sub-issues are added incrementally and the epic body is reconciled as they
  land.
- **Notes** (`note` label) are observations, design considerations, or run
  findings that are *not* build tasks. A note is its own issue, cross-linked
  to its epic and listed in the epic's **Related notes** section — never
  attached as a sub-issue. `label:note` is the durable, cross-epic index of
  everything learned.
- **Note triage at epic closeout:** before an epic closes, its note set is
  swept — accepted/moot notes closed, still-live ones re-homed under the
  successor epic. No finding goes stale by neglect.
- **Outcomes are written back.** Run/build results land as a readout comment
  on the issue that produced them; heavy artifacts live outside the source
  repo (D-007).
- **Epic pages** under the records section tell each epic's curated story
  (stub at kickoff, retrospective at closeout); the epic issue closes with a
  pointer comment, not the narrative.

**Enforcement** (per [D-004](adr-0004-enforcement-doctrine.md)): *mixed.*
Filing is advisory: the issue-body templates and the ritual commands give
the workflow its structural scaffolding, and epic-closeout review is the
backstop — no gate rejects a mis-filed issue, and none should: what counts
as a "finding" versus a "task" is judgment. Closing is guarded: when an
issue may close, and who may close it, are enforced mechanically, through
the layers described in [Enforcement](../process/enforcement.md).

## Consequences

- Epic progress is real: every child is completable, so "all sub-issues
  closed" actually means the work is done.
- Learning is never lost to a closed epic — the `note` index outlives the
  work that produced it, and triage forces an explicit keep/close decision.
- Slight filing overhead per finding (own issue + cross-link) — accepted;
  a finding worth recording is worth an address.

## Alternatives considered

- **Findings as sub-issues** — rejected: they never close, so epics stay
  perpetually "in progress" and completion percentages lie.
- **Project boards as the tracking surface** — rejected: board state lives
  outside the issue record, drifts from it, and is invisible to
  `label:`-based queries and agents working from the CLI.
- **Findings straight into docs, skipping issues** — rejected: docs are
  curated truth, not an inbox; unreviewed observations would erode the
  canonicality that D-001 establishes.

## Reversibility / notes

- Cheap to adjust: the label taxonomy and templates can be extended without
  migration; an unused label simply idles.
- If the note volume outgrows issue-based tracking, a superseding ADR can
  introduce a dedicated findings store — the `note` index migrates by query.

## References

- Related docs: [Contributing → Issues, sub-issues & notes](../process/contributing.md#issues-sub-issues-notes),
  [Contributing → Epic pages](../process/contributing.md#epic-pages)
- Related decisions: [ADR-0001](adr-0001-documentation-and-records.md),
  [ADR-0004](adr-0004-enforcement-doctrine.md)
