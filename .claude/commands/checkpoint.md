---
description: Write/refresh a mid-task progress checkpoint that survives context loss
argument-hint: <task-slug> (optional)
---

Write a compaction-proof checkpoint for the task in flight. The slug is:
$ARGUMENTS (if empty, derive a short kebab-case slug from the current task
and say which you chose).

Steps, in order:

1. Write — or overwrite; one live checkpoint per task — the file
   `.claude/working/<slug>-progress.md` with exactly this skeleton, filled
   from the CURRENT state of the work (from files and `git log`, never from
   recollection):

   # <task> — progress checkpoint
   - Updated: <YYYY-MM-DD HH:MM>
   ## End goal
   ## Approach
   ## Steps done (with evidence — commits, files, verify runs)
   ## Current failure / blocker (verbatim, if any)
   ## Next step

2. Keep it honest and ≤1 screen: a checkpoint that misstates state is worse
   than none (incorrect > missing > noise — the `context-engineering`
   skill's failure ordering).
3. Report the path written. On resume after compaction or context loss,
   read the checkpoint + `git log` FIRST and trust them over recollection.

Notes: `/handoff` archives working docs at task END; this checkpoint is
mid-task survival — never archive a still-running task's checkpoint. This
command is deliberately model-invocable (no side effects beyond the
sanctioned scratch space): checkpointing is something the agent should do
on its own initiative when the window fills.
