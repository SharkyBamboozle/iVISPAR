---
description: Close out an epic — note triage, retrospective, pointer comment, verify
argument-hint: <epic issue #NN>
disable-model-invocation: true
---

Close out epic $ARGUMENTS. Steps, in order:

1. **Sub-issue check (mechanical)** — query the epic's sub-issues via the
   API (`gh sub-issue list` / this session's GitHub tools); never trust the
   body's checklist by eye. If any are still open, list them and **STOP for
   the user's decision** (close/move/keep the epic open) — do not proceed
   past this step on your own. Notes never count: they are not sub-issues
   and never block closeout.
2. **Note triage** — sweep the epic's `note` set (the epic body's Related
   notes section, cross-checked against `label:note`): for **accepted /
   applied / moot** notes, post a one-line resolution comment and request
   the operator close them (CLAUDE.md hard rule); **re-home** still-live
   ones to the successor epic (update both epics' Related-notes
   sections); leave truly standalone ones in the `label:note` index.
3. **Retrospective** — finalise the epic's page under `docs/records/epics/` into the
   story (goal → built → found → decided → carried forward), with the note
   list carrying inline resolutions (*resolved — how* / *moot — why* /
   *live — carried to #NN*). Update its row in `docs/records/epics/index.md`
   (status ✅, or 🧊 Superseded with a pointer admonition).
4. **Changelog** — add the session's entry to `docs/records/changelog.md` citing the
   epic, its outcome, and any `D-xxx` that moved to ✅.
5. **Pointer comment** — post the closeout comment from the skeleton in
   `docs/.templates/epic-closeout-comment.md` (retrospective link, outcome,
   sub-issues, note-triage verbs, next frontier) and request the operator
   close the epic (CLAUDE.md hard rule). The narrative lives on the page —
   never duplicate it into the comment. If closing via the closeout PR
   instead, `Closes #NN (epic)` is the one sanctioned closing keyword on
   an epic — the `issue-link-guard` gate allows it only once every
   sub-issue is closed (step 1).
6. Run `make verify` (strict docs build must pass).
7. Report: what was closed, what was re-homed where, and the next frontier.
