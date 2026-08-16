# Writing ADRs

You are recording a significant decision — or touching a page that records
one. *Enforcement (D-004): the `guard-adr.sh` hook gates every path to a
✅ Decided page, `adr-gates.yml` checks the commit trailers, and the
docs-truth consistency lane catches drift — detailed at the end of this
page.*

Architecture Decision Records capture significant decisions.

1. A new significant decision gets the **next free `D-0NN` ID**.
2. Create an `adr-00NN-*.md` page under `docs/decisions/` from the template at
   `docs/.templates/adr-template.md` (Status, Decision ID, Related
   requirements/questions, then Context / Decision / Consequences /
   Reversibility / References).
3. Add a row to the [decisions registry](../decisions/index.md) — ID + one-line
   statement + status + link — and add the page to the `nav` in `mkdocs.yml`.
4. Use the status legend consistently. Where a decision resolves an open
   question, note it in both places and link the two.
5. Keep ADRs focused: the deep analysis lives on the topic pages — link to
   them. The **Reversibility** section is mandatory: record what makes the
   decision cheap or expensive to undo.
6. A ✅ decision is never edited into something else — a changed decision is a
   **new ADR that supersedes** the old one (the old page stays, marked 🧊 with
   a pointer). An ADR may declare itself a *refinement* of another ("D-015
   refines D-014, not a reversal").

Config files that enforce a decision (`.gitignore`, `.gitattributes`, CI
workflows) **cite the decision ID in a comment**, so the file explains itself.
*(Advisory — salience via `.claude/rules/config-cites-decision.md`; no gate
verifies the citation, per D-004.)*

**Any path to a ✅ Decided page is gated** — an in-place edit (typo fix,
annotation admonition, the 🧊 supersession marker), **creating** an ADR
already stamped ✅, **promoting** a 🟡 page to ✅, and **deleting or
renaming** a Decided page via `git rm`/`git mv` — each goes through
`/unlock-adr <id>` first. The `guard-adr.sh` hook (registered for
Edit/Write/MultiEdit **and** Bash) blocks all of these without a fresh
token; `adr-gates.yml` requires an `Unlock-ADR: <id> — <reason>` commit
trailer for any path that reaches or leaves a Decided page — created-as-Decided,
promoted, edited, deleted, or renamed.
The same workflow's `registry-sync` job enforces "update the ADR **and**
the registry row together" (typo-only override: `Skip-Registry-Sync:
<reason>` trailer). Independently, `make verify`'s docs-truth **consistency
lane** fails whenever a registry row and its ADR page disagree on status, a
page/row/nav entry is missing its partners, or an ADR header cites a
`D-###`/`R##`/`Q##` that no registry contains — so drift that slips past a
diff-time check is still caught on every later run.
