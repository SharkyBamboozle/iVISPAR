# Testing changes

You changed behavior, fixed a bug, or touched a hook or checker — does a
test land with it, and where? *Enforcement (D-005/D-004): the hook suites
and checker `--self-test`s run inside `make verify` and CI, and the
meta-gate binds the next hook's suite; the judgment-call rules below are
labelled advisory.*

**Scaffolding is code.** Every deny-hook ships a regression suite that
asserts both the deny side *and* the still-allowed side
(`scripts/test_guard_git.sh`, `scripts/test_guard_adr.sh`) — a fix must
not over-tighten; an approve-hook's suite asserts the approve and the
defer side the same way (`scripts/test_guard_command_policy.sh`); every
checker
script ships a `--self-test` proving each check both fails on bad input and
passes on good. All of them run inside `make verify` — and therefore in CI
on every PR (`docs.yml`) — so a broken guard fails the gate instead of
waiting for someone to remember a manual run. *This coverage binds the
**next** hook too:* the CI meta-gate (`scripts/check_ci_gates.py`) reads
the PreToolUse registrations in `.claude/settings.json` and fails
`make verify` if any hook there — deny or approve, `.sh` or `.py` — lacks
a wired `scripts/test_*.sh`, or any
`check_*` checker lacks a wired `--self-test` — so "add a guard, skip its
suite" can't pass unnoticed. Tests are **hermetic**: no
network, no dependence on mutable repo state — a state-dependent verdict is
printed for human judgment, never asserted (`scripts/test_guard_git.sh`'s
push-to-main case is the reference implementation).

**Test-writing is event-driven, never scheduled.** A test is added when a
change creates the need — not on a cadence, and never to meet a number:

- **A behavior bugfix carries its regression test** — the reproduction
  becomes the test, and the commit body names it on its `Pin:` line (see
  [Committing](committing.md)). *Advisory — enforced by the commit
  convention and PR review.*
- **New behavior at a seam lands with its test in the same PR.** What makes
  a test worth writing is that it exercises observable behavior at a seam —
  not restating the implementation, testing mocks, or bulk snapshots.
  *Advisory — deliberately unenforced: "same PR" and "worth writing" are
  judgment calls no gate can make; upheld by review (D-004).*
- **A hook or checker change extends its suite in the same diff** —
  enforced on the deny side by the suites running in `make verify`; the
  still-allowed side relies on review.
- **Placement is module-defined:** product code follows its module's layout
  (python-package: `python/tests/` mirroring the package); scaffolding
  tests live in `scripts/` as `test_<target>.sh` suites or as a checker's
  `--self-test`. *(Advisory — placement is a convention upheld by review;
  D-004.)*
- **Weakening or deleting a test is a declared exception, never silent** —
  a `Test-Adjusted: <one-line reason>` commit trailer (the D-004 trailer
  machinery — [Committing](committing.md)). Making a red test green by
  loosening its assertion without declaring it is an honest-reporting
  violation, not a fix. *Advisory until a trailer-checking gate exists.*
- **No coverage thresholds.** A percentage target trains authors — human or
  agent — to write tests for the metric. The defensible form, if a project
  ever wants coverage enforcement, is a ratchet (coverage never decreases),
  🧊 deferred as an opt-in python-module lane — reactivation trigger: the
  first time a coverage number is cited in a PR or requested by an owner
  (see [ADR-0005](../decisions/adr-0005-testing-policy.md)).
