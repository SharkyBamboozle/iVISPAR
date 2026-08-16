---
name: reproduce-first
description: >-
  Reproduce-before-you-fix protocol: capture the behaviour of the unmodified
  project before diagnosing or fixing anything. Use before diagnosing a
  reported failure, implementing from a brief or issue, or citing a prior
  PR's diagnosis as ground truth. Includes the HALT step for briefs the
  reproduction contradicts.
---

# Reproduce first

Task descriptions, issues, prior PRs, and memory entries are **hypotheses**.
What the unmodified project actually does is **ground truth**. Diagnosing
from the hypothesis instead of the reproduction is how hours of fix-authoring
get aimed at the wrong target.

**Invoke this protocol before:** diagnosing any reported failure,
implementing from any brief or issue, or re-using a prior PR's diagnosis.

## Protocol

### 1. Name the claim and its source

Write one line: "The brief claims X, sourced from <issue #N | prior PR #N |
user message | doc>." That source is now a hypothesis awaiting confirmation —
never load-bearing for the fix design.

### 2. Pin the environment

Record the commit you are on (and the toolchain version where relevant) so
the reproduction is repeatable.

### 3. Run the unmodified project

No fixes applied. Capture verbatim: the exact command(s), exit codes, and the
failing output itself (log excerpt, stack trace, wrong value) — not a
paraphrase.

### 4. Write the two-block working doc

In `.claude/working/<task>-reproduction.md`, two explicitly separated blocks:

```markdown
## Hypothesis (context only, NOT load-bearing)

<what the brief / issue / prior PR claimed>

## Reproduction (load-bearing)

- Commit: … · Toolchain: …
- Command: …
- Exit code: … · Key output: …

## Diagnosis (grounded ONLY in the reproduction block)

…
```

If a sentence in the diagnosis cites the hypothesis block, rewrite it or
measure it.

### 5. Compare — proceed or HALT

- **Reproduction confirms the brief** → proceed; it becomes the "before"
  evidence in the PR.
- **Reproduction contradicts the brief** → **HALT**: stop implementing, write
  the contradicting evidence into the working doc, and report to the user. An
  approved plan built on a premise the first measurement disproved is not
  approved.

### 6. Fix, then re-run the SAME command

The fix claim is "the same command's output changed from A to B", with both
outputs captured.

## Hard rules

- **One workaround per problem.** If the same failure returns after a
  workaround, the diagnosis is wrong — escalate; don't bump the workaround
  again.
- **Three strikes on the same check.** After three failed attempts on the
  same failing check, stop and report what was tried, with logs.
- **Identical symptom ≠ identical root cause.** Re-diagnose every recurrence
  from a fresh reproduction.

## Cheap mode

For trivially reproducible failures (a test failing on the current commit),
the "reproduction" is just: run the test, capture the failure verbatim, fix,
re-run. The protocol scales down — but the two-block separation and the
re-run-same-command fix evidence never drop.
