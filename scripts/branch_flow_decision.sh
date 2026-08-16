#!/usr/bin/env bash
# Decision logic for the branch-flow guard (.github/workflows/branch-flow-guard.yml).
# Extracted into a script so the subtle parts — fail-closed on an inconclusive
# existence check, and the head-repo == base-repo fork check — are
# unit-testable with a mocked `gh` (scripts/test_branch_flow_guard.sh).
#
# Exit 0 = allow this PR into `main` · exit 1 = block.
# Env: HEAD (PR head branch), HEAD_REPO (head repo full_name),
#      BASE_REPO (this repo full_name), GH_TOKEN (for `gh api`).
#
# Only `development` from THIS repo may promote into `main`. Pre-bootstrap
# grace (any head allowed once) applies ONLY when `development` genuinely does
# not exist yet — a 404. Any other `gh api` outcome is inconclusive and fails
# CLOSED, so a transient/auth/network error can't silently drop the guard.
set -uo pipefail

HEAD="${HEAD:-}"
HEAD_REPO="${HEAD_REPO:-}"
BASE_REPO="${BASE_REPO:-}"

# Legitimate promotion: development, from the same repo (not a fork branch
# that merely happens to be named `development`).
if [ "$HEAD" = "development" ] && [ "$HEAD_REPO" = "$BASE_REPO" ]; then
  echo "OK: development -> main (promotion)."
  exit 0
fi
if [ "$HEAD" = "development" ] && [ "$HEAD_REPO" != "$BASE_REPO" ]; then
  echo "::error::Head branch is 'development' but from a different repo ('$HEAD_REPO' != base '$BASE_REPO') — a fork branch named 'development' is not a promotion. Blocked."
  exit 1
fi

# Any other head is allowed only under pre-bootstrap grace, and only if the
# existence check DEFINITIVELY reports development absent (404).
err="$(gh api "repos/$BASE_REPO/git/ref/heads/development" 2>&1 >/dev/null)"
rc=$?
if [ "$rc" -eq 0 ]; then
  echo "::error::Only 'development' may PR into 'main' (got '$HEAD'). Flow: feature branch -> development -> main. Re-target this PR to 'development'."
  exit 1
fi
if printf '%s' "$err" | grep -qiE 'HTTP 404|not found'; then
  echo "::warning::Pre-bootstrap grace: 'development' does not exist on the remote yet, allowing '$HEAD' -> main this once. Run scripts/github_setup.sh to create and protect 'development'; this guard then arms."
  exit 0
fi
echo "::error::branch-flow-guard could not confirm 'development' exists — 'gh api' failed with a non-404 error (transient / auth / network). Failing CLOSED to avoid a silent policy bypass. Details: $err"
exit 1
