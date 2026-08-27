#!/usr/bin/env bash
# Regression cases for .claude/hooks/guard-issue-close.sh — run after any
# change to the hook (and inside `make verify`, so it binds in CI; D-004).
# Asserts BOTH sides (deny and still-allowed) so a fix can't silently
# over-tighten. Fully hermetic: the hook reads only its stdin — no repo
# state, no network, no fixtures.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../.claude/hooks/guard-issue-close.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# --input body fixtures: the hook inspects the FILE, never the flag alone.
printf '{"state":"closed","state_reason":"completed"}\n' >"$TMP/close.json"
printf '{"title":"renamed"}\n' >"$TMP/title.json"
printf '{"query":"mutation { closeIssue(input:{issueId:\\"I_x\\"}) { issue { number } } }"}\n' \
  >"$TMP/close-mutation.json"
printf 'closed\n' >"$TMP/statefile"                     # -F state=@file value
printf 'mutation { closeIssue(input:{issueId:"I_x"}) { clientMutationId } }\n' \
  >"$TMP/close-mutation-gql"                             # -F query=@file value
# The hook opens --input/@file bodies with ITS python; on Windows that is often
# a native python invoked from MSYS bash, which cannot open the MSYS `/tmp/...`
# path bash created here (it would fail closed and block a body meant to be
# readable). $D is the C:/-mixed form (cygpath -m) both resolve to the same
# file; a no-op off MSYS. Files are created at $TMP, but PASSED to the hook via
# $D so the guard's real read-and-decide logic is what gets exercised.
winpath(){ if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
D="$(winpath "$TMP")"

J() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

expect() { # expect <rc> <label> <tool_name> <tool_input_json>
  printf '{"tool_name":%s,"tool_input":%s}' "$(J "$3")" "$4" \
    | bash "$HOOK" >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$1" ]; then echo "PASS (rc=$rc): $2"
  else echo "FAIL (rc=$rc, want $1): $2"; fails=$((fails + 1)); fi
}

# The definite-close and inconclusive-body blocks carry DIFFERENT messages;
# assert which one fired so the two paths can't silently swap.
expect_msg() { # expect_msg <rc> <stderr-snippet> <label> <tool_name> <tool_input_json>
  local err rc
  err="$(printf '{"tool_name":%s,"tool_input":%s}' "$(J "$4")" "$5" \
    | bash "$HOOK" 2>&1 >/dev/null)"
  rc=$?
  if [ "$rc" -eq "$1" ] && printf '%s' "$err" | grep -qF "$2"; then
    echo "PASS (rc=$rc, msg ok): $3"
  else
    echo "FAIL (rc=$rc, want $1 + '$2'): $3"; fails=$((fails + 1))
  fi
}

# ---- deny side: MCP layer ---------------------------------------------
expect 2 "MCP issue_write update state=closed -> blocked" \
  mcp__github__issue_write '{"method":"update","owner":"o","repo":"r","issue_number":5,"state":"closed"}'
expect 2 "MCP issue_write close with state_reason -> blocked" \
  mcp__github__issue_write '{"method":"update","owner":"o","repo":"r","issue_number":5,"state":"closed","state_reason":"completed"}'
expect 2 "MCP issue_write create born-closed -> blocked" \
  mcp__github__issue_write '{"method":"create","owner":"o","repo":"r","title":"t","state":"closed"}'
expect 2 "issue_write on a differently-named MCP server -> blocked" \
  mcp__github-enterprise__issue_write '{"method":"update","issue_number":5,"state":"closed"}'

# ---- deny side: Bash layer --------------------------------------------
expect 2 "gh issue close -> blocked" \
  Bash "{\"command\":$(J 'gh issue close 12')}"
expect 2 "gh issue close with flags/comment -> blocked" \
  Bash "{\"command\":$(J 'gh issue close 12 --comment "readout done" -R o/r')}"
expect 2 "gh issue delete -> blocked" \
  Bash "{\"command\":$(J 'gh issue delete 12 --yes')}"
expect 2 "chained command hiding the close -> blocked" \
  Bash "{\"command\":$(J 'git status && gh issue close 5')}"
expect 2 "gh api PATCH state=closed on an issue -> blocked" \
  Bash "{\"command\":$(J 'gh api -X PATCH repos/o/r/issues/12 -f state=closed')}"
expect 2 "gh api graphql closeIssue mutation -> blocked" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation { closeIssue(input:{issueId:\"I_x\"}) { issue { number } } }"')}"
expect 2 "gh api graphql deleteIssue mutation -> blocked" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation { deleteIssue(input:{issueId:\"I_x\"}) { repository { name } } }"')}"

# ---- deny side: hardened parsing (global flags, subshells, newlines) ---
expect 2 "gh -R flag before issue close -> blocked" \
  Bash "{\"command\":$(J 'gh -R o/r issue close 5')}"
expect 2 "gh --repo flag before issue close -> blocked" \
  Bash "{\"command\":$(J 'gh --repo o/r issue close 5')}"
expect 2 "(gh issue close 5) subshell -> blocked" \
  Bash "{\"command\":$(J '(gh issue close 5)')}"
expect 2 "newline-joined issue close -> blocked" \
  Bash "{\"command\":$(J "$(printf 'gh issue list\ngh issue close 5')")}"
expect 2 "issue close with trailing comment -> blocked" \
  Bash "{\"command\":$(J 'gh issue close 5 # done')}"
expect 2 "absolute-path gh issue close -> blocked" \
  Bash "{\"command\":$(J '/usr/bin/gh issue close 5')}"
expect 2 "top-level backtick gh issue close -> blocked" \
  Bash "{\"command\":$(J '`gh issue close 5`')}"
expect 2 "attached -fstate=closed spelling -> blocked" \
  Bash "{\"command\":$(J 'gh api repos/o/r/issues/12 -fstate=closed')}"
expect 2 "--field=state=closed spelling -> blocked" \
  Bash "{\"command\":$(J 'gh api repos/o/r/issues/12 --field=state=closed')}"
expect_msg 2 "operator-only" "--input body that sets state=closed -> blocked" \
  Bash "{\"command\":$(J "gh api -X PATCH repos/o/r/issues/12 --input $D/close.json")}"
expect 2 "graphql closeIssue via --input body -> blocked" \
  Bash "{\"command\":$(J "gh api graphql --input $D/close-mutation.json")}"
expect_msg 2 "inconclusive body" "unreadable --input on closeable endpoint -> blocked (fail closed)" \
  Bash "{\"command\":$(J "gh api -X PATCH repos/o/r/issues/12 --input $D/no-such-file.json")}"
expect_msg 2 "inconclusive body" "--input - (stdin) on closeable endpoint -> blocked (fail closed)" \
  Bash "{\"command\":$(J 'gh api -X PATCH repos/o/r/issues/12 --input -')}"
expect 2 "full-URL issue endpoint + -f state=closed -> blocked (URL normalized)" \
  Bash "{\"command\":$(J 'gh api https://api.github.com/repos/o/r/issues/12 -X PATCH -f state=closed')}"
expect 2 "full-URL issue endpoint + --input close body -> blocked" \
  Bash "{\"command\":$(J "gh api https://api.github.com/repos/o/r/issues/12 -X PATCH --input $D/close.json")}"
expect 2 "GHES /api/v3 issue endpoint + state=closed -> blocked (prefix normalized)" \
  Bash "{\"command\":$(J 'gh api https://ghe.example.com/api/v3/repos/o/r/issues/12 -X PATCH -f state=closed')}"
expect 2 "-F state=@file (file contains 'closed') -> blocked" \
  Bash "{\"command\":$(J "gh api -X PATCH repos/o/r/issues/12 -F state=@$D/statefile")}"
expect 2 "full-URL graphql + inline closeIssue -> blocked (URL normalized)" \
  Bash "{\"command\":$(J 'gh api https://api.github.com/graphql -f query="mutation{closeIssue(input:{issueId:\"I_x\"}){clientMutationId}}"')}"
expect 2 "graphql -F query=@file (closeIssue in file) -> blocked" \
  Bash "{\"command\":$(J "gh api graphql -F query=@$D/close-mutation-gql")}"
expect 2 "graphql updateIssue(state:CLOSED) mutation -> blocked" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation { updateIssue(input:{id:\"I_x\", state:CLOSED}){issue{number}} }"')}"
expect 2 "graphql updateIssue with CLOSED bound to state via a variable -> blocked" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation($s:IssueState!){updateIssue(input:{id:\"I_x\",state:$s}){issue{id}}}" -f s=CLOSED')}"
expect 0 "graphql updateIssue with CLOSED bound to a NON-state field (title) -> allowed" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation($t:String){updateIssue(input:{id:\"I_x\",title:$t}){issue{number}}}" -f t=CLOSED')}"
expect 2 "gh api --cache <dur> then state=closed -> blocked (value flag consumed)" \
  Bash "{\"command\":$(J 'gh api --cache 5m repos/o/r/issues/12 -X PATCH -f state=closed')}"

# ---- allow side (anti-over-tighten) -----------------------------------
expect 0 "MCP issue_write create (no state) -> allowed" \
  mcp__github__issue_write '{"method":"create","owner":"o","repo":"r","title":"t","body":"b"}'
expect 0 "MCP issue_write reopen (state=open) -> allowed" \
  mcp__github__issue_write '{"method":"update","issue_number":5,"state":"open"}'
expect 0 "MCP issue_write body edit / box tick -> allowed" \
  mcp__github__issue_write '{"method":"update","issue_number":5,"body":"- [x] ticked"}'
expect 0 "MCP sub_issue_write (no state field) -> allowed" \
  mcp__github__sub_issue_write '{"method":"add","issue_number":5,"sub_issue_id":9}'
expect 0 "unrelated MCP tool -> allowed" \
  mcp__github__add_issue_comment '{"issue_number":5,"body":"readout"}'
expect 0 "gh issue view/list/comment -> allowed" \
  Bash "{\"command\":$(J 'gh issue view 12 && gh issue list && gh issue comment 12 --body readout')}"
expect 0 "gh issue edit (labels/body, no close) -> allowed" \
  Bash "{\"command\":$(J 'gh issue edit 12 --add-label note')}"
expect 0 "gh api comment POST (issues path, no state) -> allowed" \
  Bash "{\"command\":$(J 'gh api repos/o/r/issues/12/comments -f body="readout"')}"
expect 0 "gh api title-only PATCH -> allowed" \
  Bash "{\"command\":$(J 'gh api -X PATCH repos/o/r/issues/12 -f title="new"')}"
expect 0 "gh api reopen (state=open) -> allowed" \
  Bash "{\"command\":$(J 'gh api -X PATCH repos/o/r/issues/12 -f state=open')}"
expect 0 "graphql updateIssue(state:OPEN) reopen -> allowed" \
  Bash "{\"command\":$(J 'gh api graphql -f query="mutation { updateIssue(input:{id:\"I_x\", state:OPEN}){issue{number}} }"')}"
expect 0 "graphql READ query filtering states:CLOSED -> allowed (not a mutation)" \
  Bash "{\"command\":$(J 'gh api graphql -f query="query { repository(owner:\"o\",name:\"r\"){ issues(states:CLOSED){ nodes{ number } } } }"')}"
expect 0 "gh api --cache <dur> read (no state field) -> allowed (endpoint not shifted)" \
  Bash "{\"command\":$(J 'gh api --cache 5m repos/o/r/issues/12')}"
expect 0 "gh pr close (a PR, not an issue) -> allowed" \
  Bash "{\"command\":$(J 'gh pr close 7 --comment "superseded"')}"
expect 0 "gh -R flag before issue view -> allowed (partner)" \
  Bash "{\"command\":$(J 'gh -R o/r issue view 5')}"
expect 0 "(gh issue view 5) subshell -> allowed (partner)" \
  Bash "{\"command\":$(J '(gh issue view 5)')}"
expect 0 "commented-out issue close -> allowed (word-boundary comment)" \
  Bash "{\"command\":$(J 'echo hi # gh issue close 5')}"
expect 0 "body field merely CONTAINING state=closed text -> allowed" \
  Bash "{\"command\":$(J 'gh api -X PATCH repos/o/r/issues/12 -f body="reached state=closed today"')}"
expect 0 "--input body without close -> allowed (file inspected, flag not blocked)" \
  Bash "{\"command\":$(J "gh api -X PATCH repos/o/r/issues/12 --input $D/title.json")}"
expect 0 "-F body=@file (issue body edit, not a close) -> allowed" \
  Bash "{\"command\":$(J "gh api -X PATCH repos/o/r/issues/12 -F body=@$D/title.json")}"
expect 0 "/comments endpoint with close-shaped --input -> allowed (never close-capable)" \
  Bash "{\"command\":$(J "gh api repos/o/r/issues/12/comments --input $D/close.json")}"
expect 0 "plain git work -> allowed" \
  Bash "{\"command\":$(J 'git add -u && git commit -m x && git push -u origin b')}"
expect 0 "Edit tool (not this guard's concern) -> allowed" \
  Edit '{"file_path":"docs/x.md","new_string":"state=closed prose"}'

# ---- fail-open --------------------------------------------------------
printf 'not json at all' | bash "$HOOK" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then echo "PASS (rc=$rc): garbage stdin -> allowed (fail-open)"
else echo "FAIL (rc=$rc, want 0): garbage stdin -> allowed (fail-open)"; fails=$((fails + 1)); fi

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
