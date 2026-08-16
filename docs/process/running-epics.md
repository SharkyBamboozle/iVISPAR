# Running epics

You are starting, advancing, or closing out an epic. *Advisory (D-004): the
`/epic-kickoff` and `/epic-closeout` rituals and the epic issue form are
the scaffolding; the docs-truth `epic-state` lane catches an in-progress
epic page whose issue is closed, and the `issue-link-guard` holds the
epic close-keyword rule — the rest is upheld at closeout review.*

Every epic gets a **page under [Epics](../records/epics/index.md)** that tells its story —
what it set out to do, what was built, what was found, what was decided, what
it carried forward — curated to *skip* the intermediate steps that don't matter
to the story.

- **Create** the page as a short stub with a status when the epic starts, from
  `docs/.templates/epic-page-template.md`; add its row to the epics index.
- **Fill it in** as work lands.
- **Finalise** it at **closeout** into the retrospective, and close the epic
  issue with a short pointer comment (skeleton:
  `docs/.templates/epic-closeout-comment.md`) plus the note triage below. The
  full narrative lives on the page — the closing comment is a pointer.
- Every epic body declares its **relation** to other epics (successor to /
  peer with an explicit boundary / supersedes / bridge before) and its
  **explicit non-goals**, naming where each deferred item lives.
- Superseded pages stay, marked 🧊 with a pointer admonition — nothing is
  deleted.

**Epic closeout triage.** Before closing an epic, sweep its `note` set:
request closure of the accepted or moot ones (resolution comment +
operator close), and re-home the still-live ones under the successor
epic, so no finding goes stale. ([Filing work](filing-work.md) defines the
note system.)

**Closing the epic issue:** an epic is keyword-closed only by its own
closeout PR — `Closes #MM (epic)`, every sub-issue already closed; the
grammar and its gate live in [Opening a PR](opening-a-pr.md).
