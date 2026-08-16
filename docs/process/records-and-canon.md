# Records & canon

Where truth and history live: canonicality, registry doctrine, the record
lenses, agent-research reports, and artifact conventions. This is the
doctrine page — the act-shaped counterpart for page placement and IDs is
[Adding docs pages](adding-docs-pages.md).

## Canonicality convention

**The docs site is canonical** — it supersedes any working notes or playbooks.

- The [decisions registry](../decisions/index.md) is the **authoritative list** of
  every `D-xxx` decision with its one-line statement + status.
- **Topic pages** hold the **detailed analysis** behind each decision. Each
  fact has exactly one canonical home; ADRs link to the topic pages rather than
  duplicating them. *(Advisory — no gate detects duplicated analysis; the
  single-home discipline is upheld by review, per D-004.)*
- Decision IDs (`D-xxx`), requirement IDs (`R##`), question IDs (`Q##`), and
  principle IDs (`P#`) are **shared across all pages** — there is one `D-004`,
  referenced from wherever it is relevant.
- When a decision's status changes, update its registry row and its ADR
  together so they stay in sync (gated by `registry-sync` —
  [Writing ADRs](writing-adrs.md)).

## Registry doctrine

- **Resolved registry rows are never deleted** — they flip to ✅ with a
  one-line outcome and a link to the resolving ADR; the ADR reciprocally notes
  which question it resolves. *(The reciprocal ADR↔question citation is gated by
  the docs-truth consistency lane; "never delete a resolved row" itself is
  advisory review discipline — D-004.)*
- **Annotate, don't rewrite.** When a premise weakens, a standing entry gets an
  admonition naming the gating question and session; the entry stands as
  written. *(Advisory — annotation vs. rewrite is a judgment call upheld by
  review; D-004.)*

## The record lenses

Every unit of project history has exactly one home; the other surfaces link to
it (*advisory — no gate checks record placement; the one-home-per-record-type
discipline is upheld by review, per D-004*). Extend this table if a new record
type appears — one home per record type:

| Surface | Lens |
|---|---|
| [Epic page](../records/epics/index.md) | the epic's **curated story / retrospective** — the clean arc, dead-ends dropped |
| [Changelog](../records/changelog.md) | the **chronological diary** — every session (newest first), cross-epic, intermediate steps kept |
| [Lessons](../records/lessons.md) | the **distilled "never again" list** — load-bearing lessons only; append-only, superseded in place, real incidents only |
| The **GitHub epic issue** | the **live plan + tracker** — scope, sub-issue DAG, notes index |
| [Decisions](../decisions/index.md) + topic docs | the **canonical decisions & current system state** |
| [Agent-Research](../records/agent-research/index.md) | the curated output of a **fan-out research pass** — proposes and rates, never decides |
| `.claude/archive/` | the **raw record** of finished agent work — working docs moved by `/handoff`, unedited; append-only, never deleted; the layer under the changelog's narrative and lessons' distillate |

**Agent memory vs the canon.** A coding agent's private auto-memory
(machine-local, uncommitted) is its own scratch; the record lenses above are
the committed, **human-curated** canon. The only bridge is a proposal: the
`/session-close` reflection step proposes a [lessons](../records/lessons.md)
entry and writes it only on explicit approval — an agent never writes the
canon on its own initiative (advisory — the approval gate is the enforcer).

## Agent-research reports

Large fan-out research/analysis passes (many agents reading the codebase and
literature in parallel) get a dated report page under
[Agent-Research](../records/agent-research/index.md), from
`docs/.templates/agent-research-report.md`.

- A report is a **snapshot in time** — it reflects the codebase and literature
  as of its date.
- It **proposes and rates — it does not decide.** Anything load-bearing
  graduates into the appropriate canonical home (an ADR, an epic, a topic
  page, or a new open question); the report stays as the durable record of
  *how* the direction was found.
- Reports include a **"How this was produced"** methodology footer, including
  any adversarial-verification stage and what it downgraded.
- Code observations surfaced along the way are handed off to the `note` system.

## Standard artifact packs & figures

*Adopt this section when the project produces experiments, figures, or other
non-textual outputs; otherwise leave it as a pointer. Every rule here is
advisory — review-upheld conventions with no mechanical gate (D-004).*

- **Standard artifact pack per change-class.** A change that isn't *seen* can't
  really be reviewed. For each change-class that warrants it (environments, UI,
  performance), define a **fixed artifact set** produced by **one shared
  helper** (never re-invented per issue); the canonical list lives on exactly
  one docs page; issues reference the pack by name in acceptance criteria; and
  `CLAUDE.md` carries a one-line trigger pointing at it.
- **Figures read as one system.** One shared plotting helper applies the house
  style globally; any curve aggregating ≥2 seeds/runs is drawn as the **mean
  with a shaded variance band** (state which measure), never a bare line.
  Exclude padding/placeholder data from any reported distribution.
- **Run provenance.** One namespaced config file is a run's single source of
  truth; the **fully-resolved** config (overrides + seed applied) is
  snapshotted into the run's artifact folder; every parameter single-sourced;
  validate and fail fast before running. Durable artifacts go to the data repo
  (data-repo module), never into this repo's history.
