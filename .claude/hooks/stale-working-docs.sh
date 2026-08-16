#!/usr/bin/env bash
# Stop hook: a short stderr nudge when .claude/working/ looks abandoned —
# files from before today and no recent write activity. Purely
# informational: always exits 0, never blocks. Convention: working docs
# are archived via /handoff at task end (.claude/working/README.md).
#
# Stop fires when Claude finishes responding — once per TURN, not once per
# session — so a multi-day task hears this nudge mid-flight, about its own
# live state files. Two consequences shape the design:
#   - The MESSAGE carries the correctness. It bounds the action set
#     (finished task -> /handoff; running task -> do nothing) and states
#     that no git action is ever requested: an unbounded "clean this up"
#     next to untracked paths, under dirty-tree and ephemeral-container
#     pressure, gets resolved as "commit and push" — which publishes
#     mid-task scratch onto the feature branch, the exact opposite of what
#     this nudge is for.
#   - The freshness check below is a NOISE DIAL, not a correctness claim:
#     "task still running" is not decidable from mtimes, so the predicate
#     only trims the obvious false-positive class and the message must
#     stay safe whenever it misfires.
#
# No -e, like the sibling print-only hook (pre-compact.sh): a freak
# failure mid-script must degrade to silence, never to a non-zero exit.
set -uo pipefail

dir="${CLAUDE_PROJECT_DIR:-.}/.claude/working"
[[ -d "$dir" ]] || exit 0

# Live-task suppression: any non-README write in the last 6 hours means a
# task is actively using the scratch space — a task that merely spans
# midnight must not have its own reproduction doc or checkpoint flagged
# the next morning. Known blind spot, accepted: a fresh clone stamps
# clone-time mtimes, hiding tracked leftovers from both find(1) calls —
# this heuristic aims at persistent checkouts and resumed containers.
recent=$(find "$dir" -mindepth 1 -not -name 'README*' \
  -mmin -360 2>/dev/null | head -1 || true)
if [[ -n "$recent" ]]; then
  exit 0
fi

stale=$(find "$dir" -mindepth 1 -not -name 'README*' \
  -not -newermt 'today 00:00' 2>/dev/null | head -5 || true)

if [[ -n "$stale" ]]; then
  {
    echo "[stale-working-docs] .claude/working/ holds files from before today:"
    echo "$stale"
    echo "Finished task -> run /handoff <task-slug> to archive them."
    echo "Task still running -> do nothing; mid-task state belongs in .claude/working/."
    echo "This nudge never asks for a git action: do not commit, push, or delete" \
      "working docs on account of this message."
  } >&2
fi
exit 0
