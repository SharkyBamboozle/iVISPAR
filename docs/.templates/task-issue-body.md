<!-- Build-task body skeleton (epic sub-issue OR standalone task) — use with:
gh issue create --title "<Epic short-name> — <task>" --body-file <this file>
For epic work, attach it to the epic as a NATIVE sub-issue (standalone
tasks: drop the "Part of Epic" fragment below). Build tasks are concrete,
completable deliverables; sub-issues count toward epic completion. Title
convention for epic work: prefix with the epic short-name
("Env-gen — Phase 2B: ...").

Close at completion: the moment every box below is ticked, this issue
CLOSES — via the completing PR's `Closes #NN (epic: #MM)`, or, when no
single PR completes it, via a readout comment + operator close request
(the close click is operator-only — CLAUDE.md hard rule). Never batch
closes to session end or epic closeout. The issue-link guard blocks a
`Closes` aimed here while boxes are unchecked (declared exception:
`Skip-Issue-Link-Guard: <reason>` trailer). -->

**<Bold thesis: the payoff of this task.>**

🟡 Part of Epic #NN · depends on #MM · governed by D-0NN

## Scope

<What is in — the narrowest slice that delivers the payoff.>

## Deliverables

*Tick each box the moment its artifact lands — ticking is the completing
session's job (edit this body via `/tick`: attest with evidence first, then
the flip; sanctioned in `CLAUDE.md` → Repo workflow).
A box a PR delivers is ticked at PR-open; the readout box, right after the
readout posts. `issue-link-guard` blocks a `Closes` aimed here while boxes
are unchecked.*

<!-- The boxes are the machine-readable completion state: GitHub renders
the n/m progress and the gate counts unchecked boxes. Honest ticking
(D-006): boxes make state visible and gateable, not true. -->

- [ ] <Concrete artifact/change.>
- [ ] **Readout** posted on this issue, cross-linked to the epic — results
  live on the tracker; heavy artifacts live in the data repo.

## Acceptance criteria

<Testable conditions, including any gate ("X must pass before Y starts").>

- [ ] <Condition.>

## Non-scope (deferred)

<What this task deliberately does not do, and where each deferred item lives.>
