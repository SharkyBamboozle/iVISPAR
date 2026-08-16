#!/usr/bin/env bash
# Regression cases for scripts/issue_close_decision.sh (the issue-close
# guard logic). Runs inside `make verify`, so it binds in CI (D-004).
# Hermetic: a mocked `gh` on PATH serves canned close-event lines and
# records revert calls to files — no network. Asserts BOTH sides (revert
# and close-stands) so a fix can't silently over/under-tighten, and asserts
# the SIDE EFFECTS (reopen PATCH + comment POST) — an exit code alone can't
# distinguish "stood" from "reverted".
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/issue_close_decision.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Mock gh, dispatching on the call shape:
#   api …/events…        -> $MOCK_EVENTS lines (oldest→newest), rc $MOCK_EVENTS_RC
#   api -X PATCH …       -> logged to $CALLS_DIR/patch, rc $MOCK_PATCH_RC
#   api …/comments…      -> logged to $CALLS_DIR/comment, rc $MOCK_COMMENT_RC
cat >"$TMP/gh" <<'MOCK'
#!/usr/bin/env bash
args="$*"
case "$args" in
  *events*)
    if [ "${MOCK_EVENTS_RC:-0}" -ne 0 ]; then
      printf '%s\n' "${MOCK_EVENTS_ERR:-gh: HTTP 500 backend error}" >&2
      exit "${MOCK_EVENTS_RC}"
    fi
    [ -n "${MOCK_EVENTS:-}" ] && printf '%s\n' "$MOCK_EVENTS"
    exit 0 ;;
  *"-X PATCH"*)
    printf '%s\n' "$args" >>"$CALLS_DIR/patch"
    exit "${MOCK_PATCH_RC:-0}" ;;
  *comments*)
    printf '%s\n' "$args" >>"$CALLS_DIR/comment"
    exit "${MOCK_COMMENT_RC:-0}" ;;
esac
exit 0
MOCK
chmod +x "$TMP/gh"

# check <want_rc> <want_reverted:yes|no> <must_match_ERE|-> <label>
check() {
  local calls="$TMP/calls.$RANDOM"
  mkdir -p "$calls"
  local out rc ok=1 why=""
  out=$(PATH="$TMP:$PATH" CALLS_DIR="$calls" REPO="org/repo" ISSUE_NUMBER=42 \
    bash "$SCRIPT" 2>&1)
  rc=$?
  [ "$rc" -eq "$1" ] || { ok=0; why="rc=$rc want $1"; }
  if [ "$2" = "yes" ] && [ ! -f "$calls/patch" ]; then
    ok=0; why="$why; expected a reopen PATCH, none made"
  fi
  if [ "$2" = "no" ] && [ -f "$calls/patch" ]; then
    ok=0; why="$why; unexpected reopen PATCH: $(cat "$calls/patch")"
  fi
  if [ "$2" = "yes" ] && [ "${MOCK_PATCH_RC:-0}" -eq 0 ] && \
     [ "${MOCK_COMMENT_RC:-0}" -eq 0 ] && [ ! -f "$calls/comment" ]; then
    ok=0; why="$why; revert posted no explanatory comment"
  fi
  if [ "$3" != "-" ] && ! printf '%s\n' "$out" | grep -qE "$3"; then
    ok=0; why="$why; missing /$3/ in output"
  fi
  if [ "$ok" -eq 1 ]; then echo "PASS (rc=$rc): $4"
  else echo "FAIL ($why): $4"; fails=$((fails + 1)); fi
  unset MOCK_EVENTS MOCK_EVENTS_RC MOCK_EVENTS_ERR MOCK_PATCH_RC MOCK_COMMENT_RC
  rm -rf "$calls"
}

# ---- close stands -----------------------------------------------------
export MOCK_EVENTS="operator|User|commit|-"
check 0 no "gated close path" \
  "close via merged PR / commit keyword -> stands"

export MOCK_EVENTS="operator|User|-|-"
check 0 no "operator's own action" \
  "plain human manual close (no app) -> stands (the operator)"

export MOCK_EVENTS="operator|User|commit|some-merge-bot"
check 0 no "gated close path" \
  "app-performed but commit-driven (merge queue / auto-merge) -> stands"

export MOCK_EVENTS="github-actions[bot]|Bot|-|github-actions"
check 0 no "ledgered app 'github-actions'" \
  "repo's own workflow automation -> stands (ALLOWED_APPS ledger)"

export MOCK_EVENTS="operator|User|-|github-mobile"
check 0 no "ledgered app 'github-mobile'" \
  "operator closing from the first-party mobile app -> stands (ledger)"

export MOCK_EVENTS=""
check 0 no "no closed event" \
  "no closed event served -> nothing to judge, stands"

export MOCK_EVENTS="agent-op|User|-|claude-for-github
operator|User|-|-"
check 0 no "plain human close" \
  "agent close later re-closed by the operator -> LAST event wins, stands"

# ---- revert side ------------------------------------------------------
export MOCK_EVENTS="operator|User|-|claude-for-github"
check 0 yes "Reverting" \
  "app-mediated manual close (user-to-server agent) -> reverted"

export MOCK_EVENTS="copilot-swe-agent[bot]|Bot|-|-"
check 0 yes "Reverting" \
  "bot-actor manual close (no app field) -> reverted"

export MOCK_EVENTS="operator|User|-|-
operator|User|-|claude-for-github"
check 0 yes "Reverting" \
  "operator close earlier, agent re-close last -> LAST event wins, reverted"

export MOCK_EVENTS="operator|User|-|unknown-new-agent"
check 0 yes "app 'unknown-new-agent'" \
  "unledgered app slug -> reverted (allowlist, not denylist)"

# ---- failure modes ----------------------------------------------------
export MOCK_EVENTS_RC=1
check 0 no "fail-open by design" \
  "events read fails -> guard SKIPPED loudly, close stands (fail-open)"

export MOCK_EVENTS="operator|User|-|claude-for-github"
export MOCK_PATCH_RC=1
check 1 yes "REVERT FAILED" \
  "revert PATCH fails -> loud red run (exit 1)"

export MOCK_EVENTS="operator|User|-|claude-for-github"
export MOCK_COMMENT_RC=1
check 1 yes "silent revert is half a gate" \
  "reopen ok but comment fails -> loud red run (exit 1)"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
