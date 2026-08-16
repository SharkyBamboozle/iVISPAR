# Adding docs pages

You are adding, renaming, or moving a page under `docs/`. *Enforcement
(D-004): the strict MkDocs build fails on broken internal links and nav
drift; the docs-truth consistency lane fails duplicate IDs; the placement
rules themselves are advisory, per the labels below.*

## How the docs are organised

The top level is deliberately small: **Home**, the **Project** tab, and one
top-level tab per **domain area**. Project holds four meta sections —
**Direction** (vision → principles → requirements →
open questions → roadmap, the traceability chain in reading order),
**Decisions** (the ADR registry + one page per ADR), **Records** (epic
stories, agent-research reports, the changelog), and **Process** (the process
pages + the glossary). The directory layout under `docs/` mirrors the nav — one
section, one directory.

**Where does a new page go?** Direction-setting pages → **Direction**; ADRs →
**Decisions**; history → **Records**; process manuals and lookups →
**Process**. Domain/system pages (architecture, design, …) get their own
**top-level tab** (`docs/<area>/`), a sibling of Home and Project — that is
where the topic pages ADRs link to live. Domain-area tabs are the one
sanctioned exception to a shallow top level: they are named up front (at
bootstrap, or when the project grows a new area) and need no ADR; otherwise
depth goes inside a tab. **Promoting any *other* section to a top-level tab
is a structural decision**: it gets an ADR and a registry row like any other
`D-xxx`. *(Advisory — no gate detects a new non-area nav tab that skipped its
ADR; caught at review, per D-004.)*

**Every page gets a `nav` entry.** A page no `nav` entry lists is unreachable
on the site, so the pairing is gated in both directions: the strict build
fails on a `nav` entry whose file is missing *and* on a page under `docs/`
that the `nav` omits. Reusable skeletons that are deliberately not pages live
under `docs/.templates/` — a dot-directory MkDocs skips, so it needs no
exemption. *(Gated — `mkdocs build --strict` via `make verify` and
`.github/workflows/docs.yml`, per D-004.)*

## Stable IDs & the status legend

- IDs are **never renumbered or reused**; new items take the next free number.
  This holds across every ID family — `D-###` decisions, `R##` requirements,
  `Q##` open questions, `P#` principles, `Session N` changelog entries —
  preserve and cross-reference them wherever relevant *(advisory —
  review-upheld, D-004)*. A duplicate `D-###` registry ID or ADR file
  number (e.g. two branches both claiming "the next free number") fails
  `make verify` — the docs-truth checker's consistency lane
  (`scripts/check_docs_truth.py`).
- One status legend everywhere — docs pages, registries, issue bodies, and
  epic pages alike: ✅ Decided/Done · 🟡 Proposed/In progress · 🔴 Open ·
  🧊 Deferred/Superseded. 🟡 means *default unless challenged* — it
  lets the project move fast without pretending things are final. Every 🧊
  entry states its **reactivation trigger**. *(Advisory — no gate checks legend
  consistency or that a 🧊 entry names its trigger; upheld by review, D-004.)*
- **Never hardcode ID ranges or counts in prose** ("Q1–Q21") — they go stale as
  registries grow. Link to the registry instead. *(Advisory — no gate greps for
  hardcoded ranges; D-004.)*

The doctrine behind these rules — canonicality, one home per fact, registry
discipline, the record lenses: [Records & canon](records-and-canon.md).
