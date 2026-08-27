---
description: Run a release train — operator-decided bump, caboose PR, promotion PR
argument-hint: [optional context, e.g. "for the vX release"]
disable-model-invocation: true
---

Promote `development` into `main` as a release. Canonical path:
`docs/process/release-checklist.md`; conventions:
`docs/process/releases.md`. Steps, in order:

1. **Preflight** — fetch; confirm `development` is green and ahead of
   `main`. List the release contents:
   `git log --first-parent --oneline main..development`
   (the merged PRs since the last promotion — that list IS the release).
2. **Propose the bump** — a table: change · PR · proposed class, one line
   of reasoning each (breaking change to shipped machinery → major; new
   machinery, e.g. a gate or command → minor; fixes/docs → patch); overall
   proposal = the highest class present. Then **STOP for the operator's
   decision** (patch / minor / major) — do not open the caboose before the
   answer. A failed or unanswered question is a **hard block** (CLAUDE.md →
   Autonomy contract), never a default to patch.
3. **Caboose PR** into `development` — bump the version file and prepend
   the release-log entry (both named by `.claude/release.txt`; skip this
   step only if the seam declares `mode: off`), the entry **derived from
   the step-1 delta list** and bundling every promoted change — never
   written from memory. `make verify`; merge before step 4.
4. **Promotion PR** — head `development`, base `main`, body from
   `.github/PULL_REQUEST_TEMPLATE/promotion.md`. Restate `Closes #N` for
   **every issue the train completed** (collect them from the merged PRs'
   bodies): on a main-default repo these lines are what actually closes
   them; on a dev-default repo they are a harmless manifest. Confirm the
   required checks (`flow-guard`, `release-gate`, `issue-link-guard`,
   `build`) are green. If `issue-link-guard` passed on a **waiver** (a
   `::warning::` run, not a merits pass), the PR body must name each
   waived finding with its **true** reason: the guard announces every
   `Skip-Issue-Link-Guard` trailer in range but cannot match a trailer
   to a finding — a promotion range can hold stale trailers arguing
   findings that no longer exist — so the body states the match.
5. **Operator steps — never the agent's:** merge the promotion PR (never
   self-merge), then cut the annotated tag on the **`main` merge commit**
   (never a branch tip — see `docs/process/release-checklist.md` →
   *Merge, tag — operator-only* for why placement is load-bearing):

   ```
   git fetch origin main
   git tag -a v<VERSION> -m "<project name> v<VERSION>" origin/main
   git push origin v<VERSION>
   ```

6. **Post-check** — after the merge, confirm each restated issue is
   closed; for any issue the keyword path missed, post a one-line
   pointer comment and request the operator close it (CLAUDE.md hard
   rule). Report: version, contents, closed issues, tag status.
