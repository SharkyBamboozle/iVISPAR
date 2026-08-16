<!-- Promotion PR — development → main. Opened by the /promote ritual
     (.claude/commands/promote.md); canonical path:
     docs/process/release-checklist.md. Not the default template — the
     ritual selects it (GitHub cannot auto-pick a template by base branch).

     Restate below one `Closes #N` per issue this train COMPLETED, collected
     from the merged PRs' bodies. On a main-default repo these lines are
     what actually closes the issues — integration merges never did; on a
     dev-default repo they are a harmless no-op that doubles as the
     release's issue manifest. Either way the issue-link-guard gate vets
     them (an unfinished epic in the list fails). -->

Closes #___ · Closes #___          <!-- one per completed issue; "Closes —" if none -->

## Promotion — v___ → v___ (**___ bump**, operator-approved)

<!-- 1–3 lines: what this release is, for whom. -->

### Contents (all already merged to `development`)

| Change | PR | Bump class |
|---|---|---|
| ___ | #___ | patch / minor / major |

### Release checklist

- [ ] Caboose merged to `development`: version bumped in the seam-named file
  (`.claude/release.txt`) + release-log entry bundling every change above
  *(N/A if the seam declares `mode: off`)*
- [ ] CI green on this PR (`flow-guard` · `release-gate` · `issue-link-guard` · `build`)
- [ ] Operator merges — never the agent, never self-merge
- [ ] Operator cuts the annotated tag on the **`main` merge commit**
  (commands: `.claude/commands/promote.md` step 5)

### Hard-rule confirmations

- [ ] Promotion is `development → main` (the one sanctioned path; `flow-guard` enforces)
- [ ] Bump class proposed with per-change reasoning and **approved by the
  operator** at the /promote STOP — never assumed *(advisory per D-004:
  `release-gate` checks the increment's arithmetic, not the approval)*
- [ ] No binaries added
- [ ] The `Closes` lines above restate only issues this train fully completed
