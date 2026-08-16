# Releases

You are promoting `development` into `main`. *Enforcement (D-004): the
`release-gate` required check — detailed below.*

Promoting `development` into `main` is a **release**, and it is a
standardized two-PR train run by the `/promote` ritual
(`.claude/commands/promote.md`); the step-by-step canonical path is the
[release checklist](release-checklist.md). The shape:

1. **Bump decision — the operator's call.** The agent derives the release
   contents from `main..development` (first-parent merges), proposes a bump
   class per change with reasoning, and **stops for the operator to pick
   patch / minor / major** — a hard STOP; an unanswered question blocks, it
   never defaults.
2. **Caboose PR** into `development`: the version file bumped and the
   release-log entry prepended (both named by the seam
   `.claude/release.txt`), the entry derived from the contents list —
   bundling every promoted change, never written from memory.
3. **Promotion PR** `development → main` from
   `.github/PULL_REQUEST_TEMPLATE/promotion.md`, **restating `Closes #N`
   for every issue the train completed**. This restatement is
   default-branch-agnostic by construction: closing keywords only fire on
   PRs into the repo's *default* branch, so on a main-default repo the
   restated lines are what actually closes the issues (integration merges
   never did), while on a dev-default repo they are a harmless no-op that
   doubles as the release's issue manifest. The `issue-link-guard` vets the
   restated set either way ([Opening a PR](opening-a-pr.md) has the
   closing-keyword grammar). If the guard passes on a **waiver**, the
   promotion PR body also names each waived finding with its true reason.
   *Advisory, stated as such (D-004):* nothing checks a promotion PR body,
   and the guard announces every `Skip-Issue-Link-Guard` trailer in range
   without matching any to a finding — a promotion range can hold stale
   trailers — so a human states the finding-to-reason match; review
   verifies it.
4. **Operator-only finish:** merge (never self-merge, never the agent) and
   the annotated tag on the `main` merge commit.

Enforcement (D-004): the `release-gate` job
(`.github/workflows/branch-flow-guard.yml`, required on `main`) fails a
promotion whose seam-named version file is not bumped by **exactly one
semver step**, or whose release log lacks an entry for the new version
(logic: `scripts/release_gate_decision.sh`; suite:
`scripts/test_release_gate.sh`). A project that does not version its
promotions declares `mode: off <reason>` in `.claude/release.txt` — the
bootstrap gate forces every seeded project to resolve that seam either
way. *Advisory, stated as such:* whether the operator was actually asked
(the ritual STOP + the promotion template's confirmation checkbox are the
enforcers) and whether the restated `Closes` set is complete (the ritual
generates it; review verifies it).
