# ADR-0005 — Testing policy: self-testing scaffolding, event-driven test-writing

- **Status:** ✅ Decided
- **Decision ID:** D-005
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** applies D-004 (enforcement doctrine) to the tests
  themselves — the guards are code, so the guards get guarded

## Context

Two layers of the same question: *who tests the scaffolding, and what rules
test-writing?*

**Scaffolding that isn't self-tested is a silent liability.** The guard
hooks and checker scripts are the enforcement layer for every other rule —
a broken guard doesn't fail loudly, it simply stops guarding, and every
check stays green while the rule it enforced decays. The most leveraged
scripts in the repository are precisely the ones whose failure is least
visible.

**Unruled test-writing has known failure modes** — for agents especially:
writing no tests, writing bulk low-value tests to look diligent, and —
worst — weakening a failing assertion until CI goes green. A testing policy
must name these modes and take an explicit position, or volume gets
mistaken for protection.

## Decision

**Scaffolding is code with binding, hermetic self-tests — and test-writing
is event-driven, triggered by changes, never by schedule, quota, or
coverage target.**

- **Scaffolding self-tests are binding.** Every deny-hook ships a
  regression suite asserting both the deny side *and* the still-allowed
  side; every checker script ships a `--self-test` proving each check both
  fails on bad input and passes on good. All of them run inside
  `make verify`. *Enforcer:* CI runs `make verify` on every PR; its
  trigger wiring is itself pinned by the CI meta-gate (D-004).
- **Tests are hermetic.** No network, no dependence on mutable repo state —
  a state-dependent verdict is printed for human judgment, never asserted.
  *Advisory — upheld by review, and empirically by the suites having to
  pass in CI, where repo state differs from any dev machine.*
- **Test-writing is event-driven.** A test is added when a change creates
  the need: a behavior bugfix carries its regression test (the reproduction
  becomes the test, named on the commit's `Pin: <test path>` trailer line —
  see [contributing → Commit conventions](../process/contributing.md#commit-conventions)); new behavior at a
  seam lands with its test in the same PR; a hook or checker change extends
  its suite in the same diff. Batch "test-writing sessions" and frequency
  quotas are explicitly not a thing — they manufacture volume, not
  protection. *Advisory — upheld by the `Pin:` commit convention and PR
  review.*
- **Placement follows the project's layout.** Product code keeps tests
  where its stack expects them (a Python package: `python/tests/`
  mirroring the package); scaffolding tests live in `scripts/` as
  `test_<target>.sh` suites or as a checker's `--self-test` flag, wired
  into `make verify`.
- **Weakening or deleting a test is a declared exception, never silent** —
  a `Test-Adjusted: <one-line reason>` commit trailer (the D-004 trailer
  machinery). Making a red test green by loosening its assertion without
  declaring it is an honest-reporting violation (D-006), not a fix.
  *Advisory until a trailer-checking gate exists.*
- **No coverage thresholds.** A percentage target trains authors — human or
  agent — to write tests for the metric. Hard coverage gates of any kind
  are deliberately not adopted.

## Consequences

- `make verify` runs a few seconds longer; in exchange, a broken guard or
  checker fails the same gate CI runs, on every PR, with no human memory in
  the loop.
- Changing a hook or checker now *requires* touching its suite (the deny
  side breaks loudly); the still-allowed side keeps over-tightening honest.
- Agents get an explicit rule against assertion-weakening — naming the
  failure mode is the precondition for catching it in review.
- Several sub-rules stay advisory (event-driven writing, hermeticity, the
  `Test-Adjusted` trailer); per D-004 that label is honest visibility, not
  a defect.

## Alternatives considered

- **Hard coverage percentage** — rejected: metric-gaming; agents and humans
  alike hit numbers with junk tests, violating the honest-reporting norm.
- **Scheduled test-writing passes** — rejected: tests written without a
  triggering change protect nothing in particular and rot fastest.
- **Manual-run suites** — rejected: a rule with no enforcer, the exact
  drift mode D-004 exists to stop.

## Reversibility / notes

- Cheap to undo: remove the suite lines from `make verify`; every suite and
  self-test keeps working standalone. The policy prose unwinds by editing
  this page and the contributing section together.
- 🧊 **Deferred: opt-in coverage ratchet** ("coverage never decreases") as
  an opt-in lane for projects with product code — the defensible form of
  coverage enforcement if a project ever wants one. *Reactivation
  trigger:* the first time a coverage number is cited in a PR or requested
  by a project owner.

## References

- Related docs: [Contributing → Testing conventions](../process/contributing.md#testing-conventions-d-005),
  [Contributing → Enforcement layering](../process/contributing.md#enforcement-layering-d-004)
- Related decisions: [ADR-0004](adr-0004-enforcement-doctrine.md),
  [ADR-0006](adr-0006-verification-and-honesty.md)
