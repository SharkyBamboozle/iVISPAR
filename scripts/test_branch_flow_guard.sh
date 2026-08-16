#!/usr/bin/env bash
# Regression cases for scripts/branch_flow_decision.sh (the branch-flow guard
# logic). Runs inside `make verify`, so it binds in CI (D-004). Hermetic:
# a mocked `gh` on PATH returns a chosen exit code + stderr — no network.
# Asserts BOTH sides (block and allow) so a fix can't silently over/under-tighten.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/branch_flow_decision.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Mock gh: echoes $MOCK_ERR to stderr and exits $MOCK_RC.
cat >"$TMP/gh" <<'MOCK'
#!/usr/bin/env bash
[ -n "${MOCK_ERR:-}" ] && printf '%s\n' "$MOCK_ERR" >&2
exit "${MOCK_RC:-0}"
MOCK
chmod +x "$TMP/gh"

expect() { # expect <rc> <HEAD> <HEAD_REPO> <BASE_REPO> <MOCK_RC> <MOCK_ERR> <label>
  HEAD="$2" HEAD_REPO="$3" BASE_REPO="$4" MOCK_RC="$5" MOCK_ERR="$6" \
    PATH="$TMP:$PATH" bash "$SCRIPT" >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$1" ]; then echo "PASS (rc=$rc): $7"
  else echo "FAIL (rc=$rc, want $1): $7"; fails=$((fails + 1)); fi
}

expect 0 development org/repo   org/repo 0 ""                          "same-repo development -> allow (promotion)"
expect 1 development fork/repo  org/repo 0 ""                          "fork branch named development -> blocked"
expect 1 feature     org/repo   org/repo 0 ""                          "feature, development exists (armed) -> blocked"
expect 0 feature     org/repo   org/repo 1 "gh: Not Found (HTTP 404)"  "feature, development absent (404) -> grace allow"
expect 1 feature     org/repo   org/repo 1 "gh: HTTP 403 rate limited" "feature, transient gh error -> blocked (fail closed)"
expect 1 feature     org/repo   org/repo 1 "could not resolve host"    "feature, network error -> blocked (fail closed)"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
