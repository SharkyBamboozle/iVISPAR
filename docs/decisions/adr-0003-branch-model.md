# ADR-0003 — Branch model & promotion

- **Status:** ✅ Decided
- **Decision ID:** D-003
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** D-004 (enforcement doctrine — every rule below
  names a mechanical enforcer: the flow and history rules bind at the
  server, the self-merge and branch-deletion rules are client-guarded)

## Context

Agents produce changes fast and in parallel, and a single bad merge to the
published branch is expensive to unwind — especially where history rewrites
are off the table. The repository needs one integration funnel where every
change meets the gates, and a published branch that is always in a
presentable, promotable state. That structure cannot rely on contributor
discipline alone: the flow rules must hold for every client, hooks
installed or not.

## Decision

**All work flows feature branch → PR into `development` → promotion PR into
`main`.**

- **`development` is the integration branch** and the repository default:
  every feature branch merges into it by pull request, where the CI gates
  bind.
- **`main` is the promoted branch.** It advances only by pull request from
  `development` — never by direct push. The single sanctioned exception is
  the repository's birth commit during bootstrap, before the branch
  structure exists.
- **Never merge your own PR.** Review is a second pair of eyes by
  construction, human or agent.
- **No force-pushes, no history rewrites, no deleting branches you did not
  create.** Published history is append-only; mistakes are fixed forward.

**Enforcement** (per [D-004](adr-0004-enforcement-doctrine.md)): the
branch-flow guard workflow rejects PRs into `main` from anything but
`development`; branch protection on both long-lived branches enforces
PR-only advancement and required checks server-side; the git guard hook
blocks direct pushes to `main`, force-pushes, and self-merges at the
client; and the permission deny-list removes the sharpest commands from
the agent's reach entirely. The flow and history rules therefore bind at
the server; the self-merge and branch-deletion rules are client-guarded —
review approvals are deliberately not server-required (solo-maintainer
calibration), so those two rules rest on the hook, the deny-list, and
review discipline.

## Consequences

- Every change meets the gates at the PR into `development` — no path to
  `main` skips the integration funnel.
- `main` is always demo-able and releasable; promotion is a deliberate,
  reviewable act rather than a side effect.
- Small integration latency (two PRs from feature to `main`) — accepted:
  promotion being explicit is the point.
- Append-only history means occasional ugly revert commits — accepted in
  exchange for never invalidating anyone's clone or provenance.

## Alternatives considered

- **Trunk-based development on `main`** — rejected: with agents committing
  at machine pace, there is no staging surface where gates and review can
  catch a bad change before it lands on the published branch.
- **Full GitFlow (release/hotfix/support branches)** — rejected: ceremony
  designed for parallel release maintenance this project doesn't have; two
  long-lived branches are the minimum that separates integration from
  publication.
- **Allowing self-merge for trivial changes** — rejected: "trivial" is
  self-assessed by the party with the least distance from the change; the
  exception would swallow the rule.

## Reversibility / notes

- Cheap to relax by superseding ADR (e.g. collapse to trunk-based if the
  project becomes single-maintainer and low-risk); the guards are
  configuration, not architecture.
- Expensive to tighten *after* a violation: a rewritten or polluted `main`
  history cannot be repaired without invalidating downstream clones — which
  is why every rule here names a mechanical guard, not advice.

## References

- Related docs: [Contributing → Branch model](../process/contributing.md#branch-model)
- Related decisions: [ADR-0004](adr-0004-enforcement-doctrine.md)
