#!/usr/bin/env bash
# Regression cases for .claude/hooks/stale-working-docs.sh — run after any
# change to the hook, and inside `make verify`. Wired into verify BY HAND:
# the CI meta-gate (check_ci_gates.py) binds suites only for PreToolUse
# hooks read from .claude/settings.json, so for this Stop hook the
# Makefile line is the only wiring pin.
#
# Fully hermetic per docs/process/testing-changes.md: throwaway temp dirs
# + touch -d, no network, no dependence on this repo's live
# .claude/working/ state.
#
# What is pinned, and why:
#   - The nudge fires on a QUIESCENT stale dir, and the fired message
#     carries the closed action set — above all the load-bearing sentence
#     that this nudge never asks for a git action. The defect class this
#     guards: an unbounded "clean this up" naming untracked files gets
#     resolved by sessions (under dirty-tree + ephemeral-container
#     pressure) as "commit and push", publishing mid-task scratch onto the
#     feature branch. Reverting the message rewrite alone must go red here.
#   - LIVE-TASK silence: a flagged-age file with a recent sibling write is
#     a task in flight (e.g. one spanning midnight), not staleness.
#   - Silence on README-only and on a missing working dir.
#   - Print-only contract: exit 0 on EVERY path, message or none — a Stop
#     hook that starts blocking would brick every turn.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../.claude/hooks/stale-working-docs.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

out=""
rc=0
run() { # run <project-root>: hook output (stdout+stderr) -> $out, exit -> $rc
  out="$(CLAUDE_PROJECT_DIR="$1" bash "$HOOK" 2>&1)"
  rc=$?
}

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; fails=$((fails + 1)); }

expect_rc0() { # every path is print-only
  if [ "$rc" -eq 0 ]; then pass "$1 -> exit 0 (print-only)"
  else fail "$1 -> exit 0 (print-only; got rc=$rc)"; fi
}
expect_silent() {
  if [ -z "$out" ]; then pass "$1 -> silent"
  else fail "$1 -> silent (got output: $out)"; fi
}
expect_in_out() { # expect_in_out <fixed-string> <label>
  if printf '%s' "$out" | grep -qF "$1"; then pass "$2"
  else fail "$2 (missing: $1)"; fi
}

# ---- fires: quiescent stale dir -----------------------------------------
# README is written NOW, which doubles as a case: a fresh README must not
# suppress the nudge (README is excluded from both find(1) calls — its
# mtime carries no task-activity signal).
R="$TMP/stale-quiescent"; mkdir -p "$R/.claude/working"
printf 'contract\n' >"$R/.claude/working/README.md"
printf 'notes\n' >"$R/.claude/working/old-task-notes.md"
touch -d '2 days ago' "$R/.claude/working/old-task-notes.md"
run "$R"
expect_rc0 "quiescent stale dir (message fired)"
expect_in_out "[stale-working-docs]" "quiescent stale dir -> nudge fires (recent README does not suppress)"
expect_in_out "old-task-notes.md" "fired message names the stale file"
# The closed action set — the correctness layer. The git-action bound is
# the load-bearing sentence: reverting the message rewrite goes red HERE.
expect_in_out "never asks for a git action" "fired message carries the never-a-git-action sentence"
expect_in_out "do nothing" "fired message carries the first-class do-nothing branch"
expect_in_out "/handoff" "fired message names /handoff as the only action"

# ---- silent: live task (flagged-age file, recent sibling write) ---------
R="$TMP/live-task"; mkdir -p "$R/.claude/working"
printf 'contract\n' >"$R/.claude/working/README.md"
printf 'repro\n' >"$R/.claude/working/task-reproduction.md"
touch -d '2 days ago' "$R/.claude/working/task-reproduction.md"
printf 'progress\n' >"$R/.claude/working/task-progress.md"   # mtime: now
run "$R"
expect_rc0 "live task (recent sibling write)"
expect_silent "live task: flagged-age file + recent sibling write"

# ---- silent: README-only, even an old one -------------------------------
R="$TMP/readme-only"; mkdir -p "$R/.claude/working"
printf 'contract\n' >"$R/.claude/working/README.md"
touch -d '2 days ago' "$R/.claude/working/README.md"
run "$R"
expect_rc0 "README-only dir"
expect_silent "README-only dir (README excluded from the stale check)"

# ---- silent: no working dir at all --------------------------------------
R="$TMP/no-working-dir"; mkdir -p "$R"
run "$R"
expect_rc0 "missing .claude/working/"
expect_silent "missing .claude/working/"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
