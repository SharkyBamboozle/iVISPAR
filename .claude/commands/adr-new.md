---
description: Scaffold a new ADR — page from template, registry row, nav entry, cross-links
argument-hint: <one-line statement of the decision>
disable-model-invocation: true
---

Create a new ADR for: $ARGUMENTS

Steps, in order — do not skip any (registry and ADR must never drift apart):

1. Find the **next free `D-0NN`** by scanning the table in
   `docs/decisions/index.md` (never reuse or renumber).
2. Create `docs/decisions/adr-00NN-<slug>.md` from
   `docs/.templates/adr-template.md`. Status: 🟡 Proposed unless the user
   explicitly said it is decided. Fill Context / Decision (bold one-sentence
   ruling first) / Consequences / **Reversibility** (mandatory) / References.
3. Add the registry row to `docs/decisions/index.md`: ID · one-line statement
   · status · ADR link.
4. Add the page to the `nav` in `mkdocs.yml` under Decisions
   (`"ADR-00NN — <short name>": decisions/adr-00NN-<slug>.md`).
5. Cross-link **both directions**: if this resolves a `Q##`, flip that row in
   `docs/direction/open-questions.md` to ✅ with `**Resolved (Session N):** <outcome>` +
   `Resolved by [ADR-00NN]`, and note "resolves Q##" in the ADR's Status line.
   Reference related `R##` requirements in the header.
6. Run `make verify` (the strict docs build catches broken links).
7. Report: the new ID, what it resolves, and the files touched.
