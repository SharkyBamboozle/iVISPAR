# ADR-0006 — Verification & honesty

- **Status:** ✅ Decided
- **Decision ID:** D-006
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** applies D-004 (enforcement doctrine) to reporting —
  the forced-choice PR blocks are its mechanical backstop; D-005 (testing
  policy) supplies the checks that `make verify` runs

## Context

In an AI-assisted project, the agent's report *is* the interface to
reality: the owner acts on what the session says happened, not on what
happened. That interface has systematic failure modes — claiming a check
passed that never ran, reporting a plausible number instead of a measured
one, calling a capability "done" when it exists only behind a flag — and
each one compounds, because later work builds on the misreport. Gates catch
what they were built to catch; nothing mechanical can catch a confident,
wrong sentence. Verification and honest reporting are therefore one
decision, not two: verifying without reporting honestly is theatre, and
honest reporting without verification is guessing.

## Decision

**One verification entrypoint, an evidence-based definition of done, honest
reporting rules, and risk-proportional adversarial verification.**

- **`make verify` is the single verification entrypoint.** Every layer that
  can run locally runs there, and CI runs the same target — one command,
  same verdict everywhere.
- **Definition of done:** `make verify` passes, **and** for behavior
  changes the change itself was exercised (run the script, hit the
  endpoint, open the page) and its output looked at. The verification
  commands and results appear in the session summary. Anything that could
  not be run in the environment is said explicitly — never implied to have
  passed.
- **Honest reporting.** A checked box is something actually run in the
  session — unchecked plus an honest sentence beats an optimistic tick. A
  number not measured is reported as "not measured", never as a plausible
  value; every reported number names its source and sample size (`n=`), and
  two numbers are compared only over the same base. A capability claim
  states exactly one of: on the promoted branch / on the integration branch
  only (the D-003 branch roles) / behind a flag (named, with its default) /
  built but not wired in — backed by a file reference.
- **Adversarial verification.** A load-bearing claim — a research finding,
  an audit result, a diagnosis about to drive work, any "safe / done /
  faster" — gets a check that tries to *refute* it before it ships. Three
  grades, scaled to what a wrong claim would cost: self-adversarial
  (re-open everything cited; near-free, always on) → independent verify
  (one fresh checker, no shared context, forced
  confirmed/corrected/refuted verdict) → adversarial sweep (several
  independent checkers). The agent proposes the grade with a rough cost;
  the owner scales it up, down, or skips — and a skipped pass is stated in
  the deliverable, never silent.

**Enforcement** (per [D-004](adr-0004-enforcement-doctrine.md)): the
forced-choice verification blocks in the PR template are the mechanical
backstop — "didn't check" cannot hide inside "didn't tick". Everything else
here is *advisory by nature*: no gate can catch a dishonest or unmeasured
number, so PR review and the habits this page names are the enforcers.

## Consequences

- Reports become actionable: a green summary means commands were run and
  outputs were seen, so the owner can build on it without re-checking.
- "Not measured", "not run here", and "skipped the verify pass" become
  normal, cheap sentences — removing the incentive to bluff.
- Verification effort scales with risk instead of being flat: trivial
  claims cost a self-check, load-bearing ones cost an independent refuter.
- The rules bind the agent's *words*, not just its code — which is exactly
  the layer mechanical gates cannot reach.

## Alternatives considered

- **Trust-by-default reporting** — rejected: reporting failures are
  systematic, not occasional, and each one poisons the work built on it.
- **Mechanical gates only** — rejected: gates verify artifacts, not
  claims; the confident wrong sentence sails through every CI check.
- **Mandatory adversarial sweeps for everything** — rejected: flat-rate
  paranoia is unaffordable and trains everyone to route around the
  process; proportionality keeps the expensive grades credible.

## Reversibility / notes

- Cheap to relax by superseding ADR — the habits degrade gracefully into
  ordinary diligence, and `make verify` keeps working as a plain command.
- The forced-choice PR blocks stay useful even if the reporting rules were
  dropped; they are wired per D-004 and versioned with the PR template.

## References

- Related docs: `CLAUDE.md` → *Definition of done*,
  [Contributing → Adversarial verification](../process/contributing.md#adversarial-verification-advisory)
- Related decisions: [ADR-0004](adr-0004-enforcement-doctrine.md),
  [ADR-0005](adr-0005-testing-policy.md)
