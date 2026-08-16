#!/usr/bin/env bash
# PreCompact hook (registered in .claude/settings.json) — fires just before
# Claude Code compacts the conversation, i.e. the one moment context loss is
# KNOWN to be imminent. Prints a checkpoint reminder unless a fresh one
# already exists (zero-noise, D-004: silence when there is nothing to say).
#
# Print-only by design: it never blocks and never fails — a broken reminder
# must not brick compaction. Whether PreCompact stdout reaches the agent's
# context is Claude-Code-version-dependent; the durable mechanism is the
# /checkpoint habit (context-engineering skill) — this hook is the nudge at
# the highest-value moment, not the guarantee.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-.}"
WORK="$ROOT/.claude/working"

# A checkpoint touched in the last 15 minutes counts as fresh — stay silent.
fresh=$(find "$WORK" -maxdepth 1 -name '*-progress.md' -mmin -15 2>/dev/null | head -1 || true)
[ -n "$fresh" ] && exit 0

cat <<'EOF'
== Pre-compaction checkpoint reminder ==
Context is about to be compacted. If a task is in flight, write or refresh
its checkpoint NOW (/checkpoint; schema in .claude/working/README.md):
  .claude/working/<task>-progress.md
  end goal / approach / steps done (with evidence) / current failure / next step
Files survive compaction; chat history may not. On resume, trust the
checkpoint + git log over recollection.
EOF
exit 0
