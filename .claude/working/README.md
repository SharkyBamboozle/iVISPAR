# Agent working directory

Sanctioned scratch space for agent working docs: task checklists, triage
notes, investigation logs, reproduction captures, session handoffs.

Rules:

- Working docs live **here, never under `docs/`** — `docs/` is human-curated
  and canonical. If a working doc earns reference status, the user decides
  its promotion and names the target path.
- This directory should be **near-empty between sessions**. At the end of a
  task or session, run `/handoff <task-slug>` to move its contents to
  `.claude/archive/YYYY-MM-DD/<task-slug>/`.
- **Archive, never delete.** Purging happens only on explicit user
  instruction.
- **No hook or nudge ever asks for a git action on working docs** — never
  commit, push, or delete anything here on account of an automated
  reminder. A hook cannot know whether a task is finished; whether a
  *finished* task's records get committed is the rituals' call
  (`/handoff`, `/session-close`).
- **Exception:** never archive the state files of a still-running task or
  loop — a cold restart depends on them.
- **Mid-task checkpoints** — `<task>-progress.md`, written via `/checkpoint`
  (schema: end goal / approach / steps done with evidence / current failure /
  next step). The PreCompact hook reminds when compaction is imminent; on
  resume, trust the checkpoint + `git log` over recollection. A running
  task's checkpoint is exactly the kind of state file `/handoff` leaves in
  place.

This README stays in place (`/handoff` leaves it here).
