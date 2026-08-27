# Opening a PR

You are opening (or editing) a pull request — the closing-keyword grammar
below decides what merging it will close. *Enforcement (D-004): the PR
template's forced-choice linking block + the `issue-link-guard` required
check — detailed below.*

A GitHub closing keyword (`close`/`closes`/`closed`, `fix`/`fixes`/`fixed`,
`resolve`/`resolves`/`resolved`) in a PR body, PR title, or commit message
**auto-closes its target** when the PR merges into `development` — the
integration branch is the repo default, so every integration PR is a live
close surface. GitHub ignores qualifiers: `Closes #7 (partial)` still closes
#7. Hence one rule:

**A closing keyword targets only an issue the PR fully completes.**

- **Completing a sub-issue:** `Closes #NN (epic: #MM)` — the keyword targets
  the sub-issue; its epic is referenced without a keyword.
- **Advancing an epic without completing any single issue:**
  `Closes — · Part of #MM (epic)` — closes nothing.
- **Closing an epic** is reserved for its own closeout PR (the
  `/epic-closeout` ritual, every sub-issue already closed): `Closes #MM
  (epic)` then closes it atomically when the retrospective lands.

**Tick *before* PR-open.** The gate counts boxes from PR-open, and an
issue-body edit fires **no PR event** — so a box ticked after the PR opens
leaves a red run that nothing re-triggers on its own. Order the work so
the first run is green:

1. Commit and push.
2. **Post the readout comment on the issue** — before opening the PR, so
   the readout box is tickable too. This is the step most often taken in
   the wrong order, and it is the usual cause of an avoidable red run.
3. `/tick` every box whose evidence now exists.
4. Open the PR, attestation lines in the body.

Only a box whose evidence *is* the open PR has to wait. Tick it after
opening, then **edit the PR body** to add its attestation line: the edit
fires `edited` and re-runs the gate, so the re-trigger is part of the
ritual rather than a manual re-run someone must remember. The ticking
discipline and its rationale live in [Closing issues](closing-issues.md).

Enforcement (D-004): the PR template's forced-choice linking block, and the
**issue-link guard** (`.github/workflows/issue-link-guard.yml`) — a required
check that fails any PR whose body, title, commit messages, or resolved link
set carry a closing reference to a target that is not completion-ready: an
`epic`-labeled issue with open sub-issues, or **any other issue whose body
still carries unchecked deliverable boxes — or none at all**
(`note`-labeled issues excepted: their completion semantics are the triage
verbs) — so closing with open or unstated deliverables requires the
argued, durable exception, never a silent close
(decision logic: `scripts/issue_link_decision.sh`; suite:
`scripts/test_issue_link_guard.sh`; deliberate exception:
`Skip-Issue-Link-Guard: <reason>` trailer — consulted only **after** the
merits check fails and announced as a workflow `::warning::` quoting the
reason, so a waiver-pass is never visually identical to a merits pass and
a re-run whose targets have become completion-ready passes on merits).
It runs on `edited` and
`synchronize` too, so a keyword added to the body or a commit after the
first CI run is re-checked; the meta-gate pins that event list. The
presence rule polices *form, not substance* — the same reasoning that
rejected coverage thresholds (D-005) applies: a ritual box can satisfy it,
and its guarantee is only that **no close is silently faith-based**;
checklist honesty stays with D-006 ticking discipline and review. The
forward direction — a PR that *should* have closed a now-complete issue
but didn't — is *advisory*: no gate can know which PRs complete what; the
`/session-close` reconciliation sweep, the template's two-sided checkbox,
and review carry it (D-004).

Two residual paths bypass the gate and are accepted, named (D-004): an
issue linked via the PR's *Development* sidebar **after** the gate's last
run (link edits emit no `pull_request` event), and a direct push to
`development` carrying a closing keyword in its commit message (no PR, no
gate). Both are caught after the fact by the docs-truth `epic-state` lane
(`scripts/check_docs_truth.py`): an epic page still marked 🟡 whose epic
issue is closed fails the next `make verify` / CI run.
