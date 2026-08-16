---
name: adversarial-verify
description: >-
  Risk-proportional adversarial verification: an independent check that
  tries to REFUTE a claim before it ships. Use before presenting any
  load-bearing claim — research findings, audit results, a diagnosis about
  to drive work, "safe / done / faster" statements, release readiness.
  Includes the grade-proposal protocol (self-check / independent verify /
  sweep, with cost framing) so the owner can scale up, down, or skip.
---

# Adversarial verification

The author of a piece of work is the worst-placed checker of that work —
the assumptions that produced an error will also approve it, and whatever
fooled the author once fools them twice. An adversarial check is a second
look whose explicit job is to **break the claim, not confirm it**: the
stance flips from "does this look right?" to "prove this wrong."

## The three grades

| Grade | What happens | Cost |
| ----- | ------------ | ---- |
| **1 — Self-adversarial** | Before publishing, re-open every cited file, re-check every quote and number, and actively try to break your own claim. | Minutes. **Always on — never skipped, never needs approval.** |
| **2 — Independent verify** | One fresh agent (no shared context with the author) is handed the claim + pointers and instructed to refute it; forced verdict per claim. | Roughly **doubles** the checked work. |
| **3 — Adversarial sweep** | Several independent checkers per finding or dimension (majority or unanimity rule), optionally with distinct lenses (correctness, security, does-it-reproduce). | **Many ×** the checked work. |

## Risk → recommended grade

Judge by **what it costs if the claim is wrong**, then propose accordingly:

| If wrong… | Tier | Default proposal |
| --------- | ---- | ---------------- |
| Minutes of rework; would be caught naturally soon anyway | low | Grade 1 only — no proposal needed |
| Hours of misdirected work; a doc, note, or diagnosis others will build on | medium | Grade 1, **plus propose Grade 2** when the claim will drive further work |
| Days of waste, external visibility, or a hard-to-reverse action (audit reports, release readiness, "safe to delete/migrate", decision-driving research) | high | **Propose Grade 2 as the default; Grade 3** for the claims everything downstream depends on |

## The proposal protocol — the owner decides the scale

Grades 2–3 cost real tokens: **never launch them unasked** (the autonomy
contract's spend rule applies). Propose in one line, with the pieces the
owner needs to decide:

> "⟨claim⟩ is ⟨tier⟩-risk (⟨why⟩). I recommend Grade ⟨n⟩ (⟨rough cost:
> "~doubles this task" / "N extra agents"⟩). Scale up, down, or skip?"

The owner may scale up, scale down, or skip. **A skip is legitimate — and
recorded:** the deliverable states "no adversarial pass ran (owner's
call)". Visible, never silent (D-006).

## What makes a check genuinely adversarial (not review theater)

1. **Fresh eyes, empty pockets.** The verifier gets the claim and its
   pointers — never the author's reasoning, working notes, or chat.
2. **Refute framing.** The instruction is "hunt for reasons this is
   wrong": open every cited file, re-run every command, check quotes
   verbatim. Evidence that can't be confirmed defaults toward *refuted*,
   never toward *confirmed*.
3. **Forced verdict.** Every claim returns exactly one of: **confirmed** /
   **corrected** (with the fix) / **refuted** (with the evidence).
4. **Disclosure.** Downgrades are folded into the deliverable AND
   reported. Agent-research reports name the verification stage and what
   it downgraded in their "How this was produced" footer — and "none ran"
   is itself a required disclosure, so absence is a visible fact.

## Enforcement status

Advisory (D-006) — nothing can mechanically prove a check was genuinely
adversarial. Its edges are enforced where they can be: the report footer
(disclosure surface) and review habit. The cheap grade is behavioral and
always on.
