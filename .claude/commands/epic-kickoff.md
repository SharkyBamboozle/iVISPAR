---
description: Start an epic — issue from template, docs story-page stub, index row
argument-hint: <epic name / thesis>
disable-model-invocation: true
---

Kick off a new epic: $ARGUMENTS

Steps, in order:

1. **Epic issue** — compose the body from
   `docs/.templates/epic-issue-body.md`: bold thesis + relation to existing
   epics (successor to / peer with an explicit boundary / supersedes), status
   line, the "Living scope" blockquote, Why this epic exists (cite triggering
   `note` issues), Strands, build-order DAG, empty Related notes section,
   **Explicit non-goals** (with where each deferred item lives), Home &
   relation. Create it with the `epic` label (+ relevant `area:*`), via
   `gh issue create --label epic --body-file ...` or this session's GitHub
   tools.
2. **Story-page stub** — create `docs/records/epics/<slug>.md` from
   `docs/.templates/epic-page-template.md`: status line linking the issue +
   the "Why this epic exists" section only (the rest fills in as work lands).
3. **Index row** — add the epic to the table in `docs/records/epics/index.md`
   (name · status 🟡 · page link · issue link).
4. Add the page to `mkdocs.yml` nav under Records → Epics.
5. Run `make verify`.
6. Report: issue number, page path, and what the first sub-issue should be.
   Sub-issues are added incrementally (build tasks only — findings become
   `note` issues, see /note).
7. Restate the PR linking convention for this epic in the report:
   `Closes #<sub-issue> (epic: #NN)` when a PR completes a sub-issue,
   `Closes — · Part of #NN (epic)` otherwise — never a closing keyword on
   the epic itself before its closeout PR (the `issue-link-guard` gate
   blocks it; `docs/process/opening-a-pr.md`).
   And the mirror rule: each sub-issue **closes at the moment its
   deliverable boxes are all ticked** — by its completing PR or a manual
   readout-close, never batched to closeout
   (`docs/process/closing-issues.md`).
