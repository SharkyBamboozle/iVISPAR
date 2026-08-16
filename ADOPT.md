# ADOPT.md — retrofit the blueprint's process into an existing project

**Who runs this:** a Claude session **in the mature project**, with the
blueprint cloned alongside, invoked as *"Run <blueprint-clone>/ADOPT.md."*
There is no common ancestor, so nothing merges — this is judgment work,
staged in **owner-approved waves**, one PR per wave. Budget days, not
hours.

## Ground rules

- **Adopt invariants, not shape.** What transfers are the rules — every
  fact has one home; decisions are addressable and superseded, never
  rewritten; every rule names its enforcer or is explicitly advisory;
  exception lists are ledgers. The project's existing layout, branch
  names, and tooling stay; the rules are mapped onto them. Do not move
  their docs tree to match the blueprint's.
- **Graft, never replace.** Their existing agent-guidance file stays the
  base and keeps its voice; blueprint rules merge into it. Same for an
  existing docs site: registries and templates transplant into it. **Where a
  surface does not exist at all** — no agent-guidance file, no docs site —
  creating a minimal one in the project's own vocabulary *is* the graft
  base; that is additive (near-zero risk), not the replacement this rule
  forbids.
- **No-go zones:** never rewrite their history (binary hygiene applies
  from adoption forward, not retroactively); never renumber their existing
  IDs; no bulk reformatting; nothing lands without its wave's approval.
- **Reproduce before you fix:** when the inventory contradicts an
  assumption this file makes, stop and report — do not force the
  blueprint's shape onto evidence that resists it.

## 0 · Inventory — never assume

- Map what exists, with file evidence per claim: agent guidance and its
  rules; docs system and its build; decision records in any form; CI host
  and gates; branch model; the implicit conventions (read their
  contributing guide, README, and CI configs — not just the obvious
  files).
- Produce a **gap-and-conflict matrix**: for each blueprint invariant —
  *exists-equivalent* / *exists-but-conflicts* / *missing* — each row
  citing its evidence. A surface that is present but partial is
  *exists-equivalent-with-gap*, not *missing*: a docs system with pages but
  no strict build, a decisions folder with records but no registry. The gap
  to close is the missing piece, not the whole surface — grafting onto what
  exists beats replacing it.
- The matrix drives everything downstream, which makes it high-risk
  output: propose a **grade-2 adversarial verify** (an independent
  re-check of every matrix row; protocol:
  `.claude/skills/adversarial-verify/SKILL.md` in the blueprint clone).
  The owner scales up, down, or skips; a skip is recorded in the matrix.
- The owner reviews the matrix and picks the wave scope. **Nothing is
  edited in this step.**

## 1 · Wave 1 — prose rules (near-zero risk)

Graft the prose rules into their agent-guidance file (creating a minimal
one first, in their vocabulary, if they have none): honest
reporting (unmeasured values are "not measured"; numbers carry source and
sample size; capability claims carry exactly one maturity state);
reproduce-before-you-fix with the halt-on-contradicted-brief rule;
escalation caps (one workaround per problem; three attempts then report);
exceptions-as-commit-trailers; review-instructions-critically. A small
diff, reviewable in minutes.

## 2 · Wave 2 — additive files (collision-free by design)

A lessons ledger in their docs; the agent scratch space with the
archive-never-delete lifecycle; the skill cards (paths adapted); a
release-checklist skeleton if they cut releases. Nothing existing
changes.

## 3 · Wave 3 — guards, one at a time

Each guard ships with: a plain-language cover note (what it blocks and
why), a **both-ways demonstration** (proven to block the bad case AND
still allow the good case), a documented escape hatch, and its own
regression test. Adapt to their CI host — the blueprint's gates are
GitHub Actions; on another host, port the *check*, not the file.

Priority follows the project's existing surfaces, not a fixed sequence:
adopt first the guard whose surface the project already exposes and most
needs — a repo taking external PRs wants the branch-flow and binary-hygiene
guards early; a decisions-heavy repo wants the decided-records edit lock and
the paired-change gate (decision page ↔ registry row) first. The full set to
work through: decided-records edit lock, paired-change gates, branch-flow
guard, **binary-hygiene guard**, secret + dependency scanning, and the CI
meta-gate.

One tension to flag as you go: a guard adopted here may ship a **label-based
escape hatch** (the binary-hygiene guard's `allow-binaries` label is the
blueprint's own example), while wave 4 proposes the exception-ledger
doctrine that prefers commit **trailers** to labels. Adopt the guard with
its label hatch now — a working guard beats a blocked one — and let wave 4
revisit the hatch when it lands; record the deferral so it is not lost.

## 4 · Wave 4 — doctrine, as THEIR decisions

Enforcement layering and the exception-ledger rules are proposed as new
decision records **in the project's own registry** — creating a minimal
registry first is itself wave-4 work if none exists — under their next
free IDs, 🟡 Proposed until the owner flips them.

## Close-out

- Every adopted rule names its enforcer, or is labelled advisory with a
  reason.
- Run their verification entrypoint; every wave's PR body reports honestly
  what was run (unchecked plus a sentence beats an optimistic tick).
- File back anything learned that would improve the blueprint
  (`HARVEST.md`, run in the blueprint repo) — an adoption is the best
  harvest source there is.
