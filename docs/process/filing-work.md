# Filing work

You have a task to track, a finding to record, or an epic to populate — and
must pick the right container. The contrast between the three containers is
the content of this page.

*Advisory (D-004): the issue-body templates (`docs/.templates/`) and the
`/note` and `/epic-*` ritual commands give these conventions their
structural scaffolding, but no gate rejects a mis-filed issue or a note
added as a sub-issue — the discipline is upheld by the templates, the
rituals, and epic-closeout review.*

Work and findings are tracked as GitHub issues, and the distinction between
them is deliberate:

- **Epics** (`epic` label) group a body of work; children are attached as
  **native sub-issues**. Kickoff, page, and closeout are their own act:
  [Running epics](running-epics.md).
- **Sub-issues are build tasks** — concrete deliverables that count toward an
  epic's completion. Add them incrementally and reconcile the epic body as they
  land ("Living scope").
- **Notes** (`note` label) are **observations, design considerations, or run
  findings that are *not* build tasks**. A note is filed as its own issue with
  `note` (+ the relevant `area:*`), cross-linked to its epic, and listed in
  that epic's **Related notes** section. It is **not** added as a sub-issue: a
  note-as-sub-issue never reaches "done," so it would leave the epic
  perpetually unfinished and quietly distort "progress."
- **The `note` label is the durable index.** `label:note` returns every finding
  regardless of which epic it came from or whether that epic is still open.
  Notes are triaged at [epic closeout](running-epics.md), never "done".

Issue-body skeletons live in `docs/.templates/` (`epic-issue-body.md`,
`task-issue-body.md`, `note-issue-body.md`) — usable directly with
`gh issue create --body-file`.

This keeps two questions cleanly separable: *what's left to build?*
(sub-issues) and *what did we learn / should we reconsider?* (notes).

Once filed work is delivered, [closing the issue](closing-issues.md) is its
own act — an issue closes the moment its deliverables are met.
