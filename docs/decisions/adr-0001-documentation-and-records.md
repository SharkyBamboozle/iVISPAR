# ADR-0001 — Documentation & decision records

- **Status:** ✅ Decided
- **Decision ID:** D-001
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** D-004 (enforcement doctrine — names the gates that
  keep these records true)

## Context

This project keeps humans and AI agents productive across many sessions, and
that only works if knowledge survives the session that produced it. Left
unmanaged, project knowledge scatters — decisions live in chat threads,
rationale in commit messages, current state in someone's memory — and every
copy drifts from the others. The failure mode is not missing documentation
but *contradictory* documentation: two pages answering the same question
differently, with no way to tell which one is load-bearing.

The countermeasure is structural: one canonical home per fact, stable
addresses for everything worth citing, and records that are appended and
superseded rather than silently rewritten.

## Decision

**The documentation site is the single source of truth, decisions are
recorded as addressable ADRs, and every record type has exactly one home.**

- **Docs are canonical.** The MkDocs site under `docs/` supersedes any
  working notes, issue threads, or playbooks (agent working notes live in
  `.claude/working/`, outside the canon, and never graduate uncurated). It
  builds with `--strict` as a merge gate — internal links must always
  resolve. Issues track *work*; docs hold *truth*.
- **Stable typed IDs, one status legend.** `D-###` decisions, `R##`
  requirements, `Q##` open questions, `P#` principles, and `Session N`
  changelog entries are never renumbered or reused; new items take the next
  free number. One status legend everywhere: ✅ Decided/Done · 🟡 Proposed/In
  progress · 🔴 Open · 🧊 Deferred/Superseded — a deferred 🧊 entry names its
  reactivation trigger; a superseded one points at its successor.
- **Decisions via ADRs + registry.** Each significant decision gets one ADR
  page (Context / Decision / Consequences / Alternatives where meaningful /
  Reversibility / References), a one-line registry row, and a nav entry —
  created and updated together. The registry
  holds the canonical statement + status; topic pages hold deep analysis;
  ADRs link rather than duplicate. A ✅ Decided ADR is never edited into a
  different decision — a changed decision is a **superseding ADR**, and the
  old page stays, marked 🧊 with a pointer.
- **Record lenses — one home per record type.** Epic pages tell the curated
  story; the changelog is the chronological diary (one entry per working
  session); lessons hold the distilled "never again" list; epic issues carry
  the live plan; the registry + topic docs hold canonical state;
  agent-research reports propose and rate but never decide. Details: [contributing → The record lenses](../process/contributing.md#the-record-lenses).

**Enforcement** (per [D-004](adr-0004-enforcement-doctrine.md)): the strict
docs build and the docs-truth checker's consistency lane bind in
`make verify` and CI — dead citations, duplicate IDs, registry ↔ page status
drift, and page/row/nav mismatches fail the gate. ADR immutability is
enforced by the ADR guard hook and the ADR gates workflow (unlock token +
trailer for maintenance edits — a typo fix, an annotation, a supersession
marker; never a change to what was decided). The remaining discipline — one home per
fact, cross-referencing, no hardcoded ID ranges — is advisory: upheld by
review, because prose meaning isn't mechanically checkable.

## Consequences

- A fresh human or agent can navigate the project from `CLAUDE.md` and the
  docs site alone; conventions are enforceable because they are written.
- Every decision, requirement, and question is citable by a stable ID, so
  discussions, commits, and configs can reference them without ambiguity.
- Small ceremony cost per decision (page + registry row + nav entry) and per
  session (changelog entry) — accepted as the price of drift-free records.

## Alternatives considered

- **Free-form wiki docs** — rejected: without one-home-per-fact and stable
  IDs, parallel pages drift apart and nothing is reliably citable.
- **Decisions recorded in issue threads** — rejected: threads are
  chronological, not canonical; outcomes get buried, and issue state is not
  part of the repository's reviewable history.
- **Rewriting decisions in place** — rejected: silently edited history makes
  it impossible to tell what was decided when, or what older artifacts were
  built against.

## Reversibility / notes

- Any individual convention here can be dropped or replaced by a superseding
  ADR that names what changes and why; this page then gains a pointer and 🧊
  status for the affected part.
- The conventions are a starting point, not a cage — the ceremony is
  deliberately the minimum that keeps records addressable and honest.

## References

- Related docs: [Contributing](../process/contributing.md),
  [Decisions registry](index.md),
  [Epics](../records/epics/index.md),
  [Agent-Research](../records/agent-research/index.md)
- Related decisions: [ADR-0004](adr-0004-enforcement-doctrine.md)
