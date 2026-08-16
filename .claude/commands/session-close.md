---
description: End a working session — changelog entry, findings sweep, records commit, state check
disable-model-invocation: true
---

Close out this working session. Steps, in order:

1. **Changelog entry** — prepend (newest first, under the header) to
   `docs/records/changelog.md`:
   `### Session N (YYYY-MM-DD) — <title>` (next free N), then 3–8 sentences:
   what was attempted → what landed (PRs/commits) → what was found (link
   `note` issues) → what was decided (link `D-xxx`) → what carries forward.
2. **Findings sweep** — scan this session for observations that were noticed
   but never filed. File each as a `note` issue per /note (cross-linked to
   its epic). If unsure whether something is worth a note, list it and ask.
3. **Lessons reflection (gated)** — did this session learn something a
   future session must not re-learn (an expensive dead-end, a broken
   assumption, a real "never again")? If yes, PROPOSE an entry per the
   skeleton in `docs/records/lessons.md` (dated, one screen, real incidents
   only) and append it ONLY on explicit approval — "skip" is a legitimate
   answer and is simply reported. If nothing qualifies, say so in one line
   and move on. Never write to `docs/` without the approval.
4. **Issue-state reconciliation** — for every issue this session's work
   advanced (standalone task or epic sub-issue alike), tally its
   deliverable boxes `n/m`. If `n = m`: post the readout comment citing
   the merging PRs and request the operator close it now — or state why
   it stays open. If requesting a close with `n < m`: name each unmet
   deliverable's disposition (deferred → where · moot → why); on the PR
   path the issue-link guard requires the declared trailer. Report the
   tallies — epic progress counters must match reality at session end.
   (Rule: `docs/process/closing-issues.md`. Epics themselves close only
   at /epic-closeout; notes only at triage.)
5. **Records commit & state check** — report honestly:
   - **Commit the session records on this session's feature branch and
     push** — the changelog entry from step 1, any approved lessons entry
     from step 3, and the `/handoff` archive — so they ride the branch's
     open PR (append-only while OPEN; the operator normally merges after
     close). Records left uncommitted die with an ephemeral container.
     Branch's PR already **merged**? The zombie-branch recovery applies to
     records too: restart the branch from `development` and let the
     records ride the follow-up PR — or a small records-only PR when the
     session is fully done (`docs/process/pushing.md` → *Where task-end
     records land*). If unsure where records belong: **push first, then
     ask** — a pushed branch is durable; discard is an operator answer,
     never a default.
   - `git status`: any *other* uncommitted work? Report it; do not
     auto-commit anything beyond the session records above.
   - Current branch pushed? Any open PR and its CI state?
   - Anything claimed done this session that was NOT verified end-to-end?
6. **Verify** — if the working tree touched docs or code, run `make verify`
   and include the result.
7. Report: the changelog entry text, the lessons proposal and its verdict,
   notes filed, the reconciliation tallies, and the exact state the next
   session will find (branch, PR, loose ends).
