---
name: context-engineering
description: >-
  Discipline for managing the agent's own context window. Use when a task
  will run long, before delegating search/read-heavy work to subagents,
  when the window approaches ~half full, or when resuming after a
  compaction or context loss.
---

# Context engineering

A turn is a stateless function call: context window in, next action out.
The window's contents are the main lever on output quality — manage them
deliberately, like a budget.

## The failure ordering

What can be wrong with a context window, worst first:

1. **Incorrect information** — actively poisons downstream work (the
   `reproduce-first` instinct: unverified claims are hypotheses, not facts).
2. **Missing information** — causes guessing.
3. **Too much noise** — dilutes attention; the least-bad failure.

Optimize in that order: verify what enters context first, fill gaps second,
prune noise last.

## Budget

Heuristic: on complex work, keep utilization roughly in the **40–60%** band
(source: HumanLayer's ACE field report — one team's practice; a starting
point, never a gate). Symptoms of an over-full window: re-asking answered
questions, drifting from the goal, confident errors about files already
read. When you see them, compact.

## Intentional compaction (mid-task)

When the window fills mid-task, do not push on degraded — distill and
restart (packaged as `/checkpoint`; the PreCompact hook reminds you when
compaction is imminent):

1. Write the state to `.claude/working/<task>-progress.md`:
   **end goal · approach · steps done (with evidence) · current failure ·
   next step**.
2. Re-verify the two or three load-bearing facts from files, not from
   memory.
3. Continue from the artifact; chat history is disposable.

Files are the checkpoint. This is distinct from `/handoff` (end-of-task
archival) — compaction is *mid-task survival*. A ledger of completed steps
plus `git log` outranks recollection after any context loss.

## Subagents are for context isolation

Delegate search-heavy discovery (Glob/Grep/Read sweeps, log digging, web
research) to a subagent so the noise lands in *its* window, not yours — and
require a compaction-shaped summary back (goal-relevant facts + file paths,
never raw dumps). Hand subagents **files, not pasted history**. Subagents
are not personas; the value is the fresh window.

## Enforcement status

Advisory (D-004) — behavioral discipline. The working-doc artifacts it
produces (`.claude/working/*-progress.md`) are the visible evidence a
session followed it.
