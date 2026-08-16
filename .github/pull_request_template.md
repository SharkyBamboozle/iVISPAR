<!-- Linked issues — keep exactly ONE of the two lines below, filled in.
     A closing keyword (Closes/Fixes/Resolves) AUTO-CLOSES its target when
     this PR merges into development (the repo default branch), and GitHub
     ignores qualifiers — "Closes #7 (partial)" still closes #7. So a
     closing keyword targets ONLY an issue this PR fully completes —
     normally a sub-issue; an epic ONLY in its own closeout PR, when every
     sub-issue is already closed. Enforcement (D-004): the issue-link-guard
     CI gate blocks closing references to an epic with open sub-issues and
     to any other issue with unchecked (or no) deliverable boxes.
     See docs/process/opening-a-pr.md. -->

**Tick before opening:** on every issue this PR `Closes`, tick each
deliverable box this PR completes — via `/tick`: per box, *did I deliver
this?* with named evidence, then the body edit; that is the completing
session's job (`CLAUDE.md` → Repo workflow). `issue-link-guard` counts the
boxes from PR-open and an issue-body edit fires no PR event, so post the
**readout comment before opening this PR** — then every box, readout
included, is tickable while the count still matters. A box whose evidence
is this PR itself: tick it after opening, then edit this body to add its
attestation line — that edit re-runs the gate.

Closes #___ (epic: #___)          <!-- fully completes that issue — its deliverable boxes all ticked
                                       (state the tally in What/why: "deliverables n/n"); drop
                                       "(epic: #___)" if it has no epic -->

Closes — · Part of #___ (epic)    <!-- advances work, completes no issue: closes nothing.
                                       Before picking this line, check the target's deliverable
                                       boxes — a finished issue left open goes invisible (the
                                       inverse failure). If it stays open, state its tally
                                       in What/why: "advances #NN — deliverables 3/5". -->

## What / why

<!-- 2–4 lines. Deep reasoning belongs in docs/ (ADR or topic page), not here. -->

## Verification — tick exactly one per block (D-004)

<!-- A checked box is something you actually ran in this session. "Deferred"
     needs a reason AND a follow-up issue — never a silent skip.
     Enforcement of this block is advisory: the forced-choice layout + PR
     review are the enforcers, not a CI parser. A tick's *truth* (did you
     actually run verify?) is un-mechanizable — see D-006 honest reporting;
     a checkbox count would police form, not substance. -->

**`make verify`:**

- [ ] Green — result reported in the session summary
- [ ] Not run — reason: ___

**Behavior exercised end-to-end** (ran the script / hit the endpoint / opened the page):

- [ ] Done — evidence in the session summary
- [ ] N/A — no runtime behavior changed
- [ ] Deferred — reason + follow-up issue: ___

**Docs & records currency** (decision/convention changes: ADR **and** registry row together; changelog entry):

- [ ] Updated — listed in the session summary
- [ ] N/A — nothing decision- or convention-bearing changed
- [ ] Deferred — reason + follow-up issue: ___

## Hard-rule confirmations

- [ ] Target branch is `development` (never `main`)
- [ ] No binaries added (LFS-covered assets excepted; artifacts go to the data repo)
- [ ] Closing keywords, both ways: every issue this PR fully completes has
  one, and nothing this PR does not complete has one — an epic mid-flight
  never (closeout PR excepted; `issue-link-guard` gates epics by sub-issue
  count, other issues by unchecked deliverable boxes)
- [ ] Findings surfaced along the way filed as `note` issues, linked to their epic (or none surfaced — say so)
