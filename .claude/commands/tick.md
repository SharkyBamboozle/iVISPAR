---
description: Tick delivered deliverable box(es) on an issue — attest each with evidence, then the anchored body edit
argument-hint: <issue #NN> [box-text fragment]
---

Tick deliverable box(es) on: $ARGUMENTS — an issue number, optionally followed
by a box-text fragment naming which box(es). With no fragment, attest every box
this session delivered; with no issue named, the one this session is completing.

A tick is an **attestation, never a routine step.** The boxes exist so no close
is faith-based; a tick is the session's on-record claim that a deliverable is
DONE (D-006). Running `/tick` over every box as PR boilerplate defeats the boxes
exactly as much as a routine `Skip-Issue-Link-Guard` trailer would — so the
per-box question below is mandatory, and *no attestable box* is a valid answer
(step 6).

**A tick is a full-body rewrite.** GitHub has no per-checkbox write: the only
primitive on every path is replacing the whole body. So the write is only ever
as good as the read it was composed from — which is why step 1 is a channel
choice, not a fetch.

Steps, in order:

1. **Read the body through a faithful channel.** Issue-body reads are *not*
   equally faithful, and the lossy ones destroy content silently:

   | Channel | Verdict |
   |---|---|
   | `gh api` (local shells, CI runners) | faithful |
   | GitHub MCP `search_issues` | faithful |
   | GitHub MCP `issue_read` / `list_issues` | **LOSSY — never compose a write from these** |

   The lossy tools strip HTML comments and `<angle-tokens>` — including inside
   inline code and fenced blocks — and escape `'` `"` `&` into `&#39;` `&#34;`
   `&amp;`. Stripping leaves no trace, so a body composed from one of them
   **permanently deletes** the stripped fragments, invisibly.

   With `gh api`, fetch the body directly. Without it, use `search_issues`
   (query `repo:OWNER/NAME is:issue in:title "<distinctive title words>"`, then
   **assert the returned issue number is the one you meant** — search has no
   number qualifier, so a wrong or multiple match means STOP, not guess).

   List every task-list line with its current state (`[x]` / `[ ]`).

2. **Prove the read is current.** The search index is asynchronous: a body
   edited moments ago can come back stale, and writing that back silently
   reverts the newer edit. Fetch `updated_at` from the real-time metadata read
   (`issue_read` is fine here — the transform touches body text, not
   timestamps) and require it to **match** the `updated_at` of the body you are
   about to edit. Mismatch → re-query, or stop. Never write across a mismatch.
   *(With `gh api` this is moot: one read is both current and faithful.)*

3. **Attest, box by box.** For each box you claim, write one line: the box text,
   then `evidence:` naming the PR / commit / file / posted readout **this
   session produced**. The rules are hard:
   - Concrete, checkable evidence or **no tick** — an unchecked box plus an
     honest sentence beats an optimistic tick (D-006).
   - Partially delivered stays unticked — state on the issue what remains, or
     re-home it and say where.
   - A box this session did not work stays untouched, **always**.
   - Box text no longer matching what was actually built → do NOT
     reword-and-tick; **STOP** and surface it (scope moved — the owner decides).

4. **Anchored edit.** Flip ONLY the attested lines from `- [ ]` to `- [x]`,
   byte-identical otherwise, composed from the step-1 body — never retyped from
   memory. Prefer a scripted flip (stage the body to a file, edit it
   programmatically) over retyping: it makes "nothing else changed" provable
   rather than asserted. An attested line matching more than one body line →
   **STOP** and disambiguate first.

5. **Write, then verify through the faithful channel.** Update the body, then
   re-read it **through the same faithful channel as step 1** and confirm: each
   attested line ticked, the unchecked count dropped by **exactly** the attested
   number, nothing else changed. Verifying through a lossy channel is worthless
   — it cannot see the damage it is meant to catch. Any other difference is a
   concurrent edit — redo from step 1; never overwrite it.

6. **Record.** Carry the attestation lines into the PR body (or session summary)
   next to the `n/m` tally. The gate polices *form* (boxes ticked); the
   attestation is the *substance* review checks the ticks against.

**No faithful channel available?** Then do not write the body at all: post the
attestations as a comment, request an operator tick, and declare the gate
exception with a `Skip-Issue-Link-Guard: <reason>` trailer. Honest unticked
boxes are a valid outcome of this ritual — a corrupted issue body is not.

## Timing — so the guard is green on its first run

The `issue-link-guard` counts boxes **at PR-open**, and an issue-body edit
fires no PR event, so ticking after the PR opens leaves a red run that nothing
re-triggers automatically. Order the work so that never happens:

1. Commit and push the work.
2. **Post the readout comment on the issue** — before opening the PR, so the
   readout box is already tickable.
3. `/tick` every box whose evidence now exists.
4. Open the PR, with the attestation lines in its body.

For the residual case — a box whose only evidence *is* the open PR — tick it
after opening, then **edit the PR body** to add its attestation line. That edit
fires `edited`, which re-runs the guard: the re-trigger is a step of the ritual,
never a manual re-run someone has to remember.
