---
description: File a finding as a note issue — cross-linked to its epic, never a sub-issue
argument-hint: <the finding> (epic #NN)
disable-model-invocation: true
---

File a `note` issue for: $ARGUMENTS

A note is an observation/design consideration/run finding that is **not** a
build task. It is NEVER attached as a sub-issue (it would leave the epic
perpetually unfinished). Steps, in order:

1. Compose the body from `docs/.templates/note-issue-body.md`: provenance
   line ("A finding from <source> (Epic #NN). **Not a build task** — filing
   per the `note` convention."), **The finding** (evidence; add a caveat if a
   number shouldn't be over-read), **Why it matters later** (options, none
   decided), **Triage** trigger.
2. Create the issue titled `note: <finding>` with the `note` label (+ the
   relevant `area:*`). Use `gh issue create --label note --body-file ...` if
   gh is available, otherwise this session's GitHub tools.
3. Add a **one-line entry to the epic issue's "Related notes & findings"
   section** (fetch the current body, append the line, update the body). Do
   NOT add the note as a sub-issue.
4. Report: the note's number, its epic, and the one-line summary added.
