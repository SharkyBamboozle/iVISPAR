---
name: honest-numbers
description: >-
  Pre-publication integrity checklist for any measured number or capability
  claim — benchmark results, coverage, success rates, "the project now does
  X" statements. Use before writing numbers or capability claims into a PR
  body, README, docs page, or report.
---

# Honest numbers

A fabricated or inflated number costs more than no number: readers build on
it. Run this checklist before any number or capability claim leaves the
working tree.

## Rule 1 — Null over guess

A value you did not measure is reported as "not measured" — never a plausible
number, never 0%, never 100%. Never render a success summary for a run that
errored or was skipped; report the degraded state instead.

## Rule 2 — The denominator is part of the number

Every published metric names its **source** (which run / artifact produced
it) and its **sample size** (`n=`). Deltas and comparisons only between
numbers counted over the same base — subtracting numbers with different
denominators produces claims that are actively wrong. At close-out, report
against the full denominator, never a silently narrowed subset.

## Rule 3 — Four maturity states, one per claim

Every capability claim carries exactly one label, with a file reference:

| Label              | Meaning                                                    |
| ------------------ | ---------------------------------------------------------- |
| on `main`          | merged and active by default                               |
| on `development`   | merged to the integration branch only                      |
| behind a flag      | shipped but opt-in — NAME the flag and its default         |
| built, not wired   | code (and maybe tests) exist; nothing calls it in production |

Describing anything below "on `main`" as shipped/live/working is the classic
failure. Check for the real call site before writing "live" — a test
importing the module is not a call path.

## Rule 4 — Use the code's own vocabulary

If the code labels something a heuristic, an estimate, or unverified, the
docs say that — not "proven", "guaranteed", or "certified".

## Pre-publication checklist

- [ ] Measured on a stated commit, with the command captured (see
      `reproduce-first`).
- [ ] Nothing converts absence-of-measurement into a value.
- [ ] Source + `n=` disclosed; comparisons same-base; close-out full-base.
- [ ] Every capability claim carries one maturity label + file reference.
- [ ] No proof-language beyond what the code itself claims.

If a box cannot be ticked, publish the honest degraded form ("not measured",
"deferred") or don't publish. A weaker-looking true number always beats a
stronger-looking fabricated one.
