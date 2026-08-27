#!/usr/bin/env bash
# SessionStart hook (registered in .claude/settings.json) — stdout is
# injected into the fresh session's context.
#
# (a) Quiet, guarded dependency bootstrap so `make verify` works in fresh
#     (especially remote) containers. Skipped when mkdocs is already
#     available; delete the block to disable auto-install.
# (b) Orientation: branch, dirty state, last changelog entry, open PRs and
#     epics — prevents the classic fresh-session failures (working on a
#     stale branch, re-doing work that sits in an unmerged PR).
#
# Never fails the session: every step degrades gracefully.
set -uo pipefail

# Anchor file reads to the repo root — the harness cwd is not guaranteed to be
# it, and a bare relative path silently degrades orientation from a subdir.
# Matches the sibling hooks' ${CLAUDE_PROJECT_DIR:-.} idiom. Git
# commands below need no anchor: git discovers the repo by walking up from cwd.
ROOT="${CLAUDE_PROJECT_DIR:-.}"

if [ -f "$ROOT/docs/requirements.txt" ] && ! command -v mkdocs >/dev/null 2>&1; then
  pip install -q -r "$ROOT/docs/requirements.txt" >/dev/null 2>&1 || true
fi

# Zero-noise discipline (D-004): sections below print ONLY when they carry
# signal — every unconditional line taxes every future session's context,
# forever. Silence means: clean tree, nothing open.
echo "== Session orientation =="
echo "Branch: $(git branch --show-current 2>/dev/null || echo '?') (rule: feature branch -> PR into development; never main)"
dirty=$(git status --short 2>/dev/null | head -20 || true)
if [ -n "$dirty" ]; then
  echo "-- Working tree NOT clean (possibly left by a previous session):"
  echo "$dirty"
fi
last_entry=$(grep -m1 '^### ' "$ROOT/docs/records/changelog.md" 2>/dev/null || true)
[ -n "$last_entry" ] && echo "Last changelog entry: $last_entry"
# Lessons ledger: surface the newest entry titles when real entries exist
# (entry headings are '## YYYY-MM-DD — …'; the placeholder file has none).
lessons=$(grep -m2 '^## 2' "$ROOT/docs/records/lessons.md" 2>/dev/null || true)
if [ -n "$lessons" ]; then
  echo "-- Newest lessons (docs/records/lessons.md — read before substantial work):"
  echo "$lessons"
fi
if command -v gh >/dev/null 2>&1; then
  # Current branch's PR verdict: a fresh session resuming on a stale
  # local branch is where zombie pushes are born — surface the terminal
  # state BEFORE any push. Prints only when the branch has PR history;
  # degrades silently offline (zero-noise discipline).
  br=$(git branch --show-current 2>/dev/null || true)
  if [ -n "$br" ] && [ "$br" != "main" ] && [ "$br" != "development" ]; then
    verdict=$(gh pr list --head "$br" --state all --limit 1 \
      --json number,state --jq '.[0] | "PR #\(.number) \(.state)"' 2>/dev/null || true)
    case "$verdict" in
      *MERGED*) echo "Branch $br: $verdict — dead history. Restart before pushing: git fetch origin development && git checkout -B $br origin/development (fresh PR; see docs/process/pushing.md)." ;;
      *CLOSED*) echo "Branch $br: $verdict — closed without merging; ask the operator before continuing this line of work." ;;
      *OPEN*)   echo "Branch $br: $verdict" ;;
    esac
  fi
  prs=$(gh pr list --limit 5 2>/dev/null || true)
  if [ -n "$prs" ]; then
    echo "-- Open PRs --"
    echo "$prs"
  fi
  epics=$(gh issue list --label epic --state open --limit 5 2>/dev/null || true)
  if [ -n "$epics" ]; then
    echo "-- Open epics --"
    echo "$epics"
  fi
fi
exit 0
