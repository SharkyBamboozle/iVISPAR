#!/usr/bin/env bash
# Regression cases for .claude/hooks/guard-command-policy.py — the APPROVE-hook
# (read-only Bash auto-approval). Run after any change to the hook, and inside
# `make verify` so it binds in CI (D-004/D-005). Asserts BOTH sides — commands
# that must stay auto-approved AND commands that must defer to the permission
# prompt — plus two properties the hook's contract promises (ADR-0004 →
# failure directions):
#
#   1. NEVER BLOCKS: exit code 0 on every input, asserted on every probe. Its
#      only outcomes are an allow decision on stdout or silence (defer).
#   2. NON-CONTENTION: nothing any deny layer blocks is ever auto-approved.
#      The deny-surface fixtures below are regenerated from the CURRENT deny
#      layers — .claude/settings.json's deny rules and the blocked cases of
#      test_guard_git.sh / test_guard_adr.sh / test_guard_issue_close.sh. The
#      two MCP deny entries (merge_pull_request / enable_pr_auto_merge) are
#      unreachable from a Bash-matcher approve-hook by construction; the
#      non-Bash protocol case below pins that the hook defers on tool_name
#      alone even if its matcher were ever widened.
#
# The newline fixtures pin the adopted fix: a real newline is a command
# separator, so a read-only first line must not launder a mutating second
# line — and an all-read-only multi-line command must STAY approved (the
# fix buys no new prompts). Probes travel as JSON on stdin — the hook's real
# channel — never as bare path arguments (MSYS would translate those).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
HOOK="$REPO/.claude/hooks/guard-command-policy.py"
fails=0

# A file-targeted gate fails loud when its target is missing (house
# convention, docs/process/enforcement.md) — a moved hook must never turn
# this suite green.
if [ ! -f "$HOOK" ]; then
  echo "FAIL: approve-hook missing at $HOOK — suite target gone"
  exit 1
fi

# Python syntax pin: `bash -n` cannot see a .py hook. In-memory compile —
# no __pycache__ litter.
if python3 -c 'import sys
src = open(sys.argv[1], encoding="utf-8").read()
compile(src, sys.argv[1], "exec")' "$HOOK" 2>/dev/null; then
  echo "PASS: python syntax pin (compile)"
else
  echo "FAIL: hook fails to compile — syntax error"
  fails=$((fails + 1))
fi

# Embedded self-test: the adopted upstream 40 cases + the paired newline
# cases (kept inside the hook so the pin travels with the file).
if out="$(python3 "$HOOK" --self-test 2>&1)"; then
  echo "PASS: embedded self-test (${out##*$'\n'})"
else
  echo "FAIL: embedded self-test"
  printf '%s\n' "$out"
  fails=$((fails + 1))
fi

emit() { # emit <command> -> PreToolUse JSON on stdout
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' \
    "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1")"
}

expect() { # expect <APPROVE|defer> <label> <command>
  local want="$1" label="$2" cmd="$3"
  local out rc got
  out="$(emit "$cmd" | CLAUDE_PROJECT_DIR="$REPO" python3 "$HOOK" 2>/dev/null)"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FAIL (rc=$rc): $label — NEVER-BLOCKS VIOLATED (hook must always exit 0)"
    fails=$((fails + 1))
    return
  fi
  if [ -n "$out" ] && printf '%s' "$out" | grep -qF '"permissionDecision": "allow"'; then
    got="APPROVE"
  else
    got="defer"
  fi
  if [ "$got" = "$want" ]; then echo "PASS ($got): $label"
  else echo "FAIL (got $got, want $want): $label"; fails=$((fails + 1)); fi
}

# ---- the newline defect table: a read-only first line must not launder ----
# ---- what follows (each was auto-approved before the fix) -----------------
expect defer "newline: status then push"            $'git status\ngit push origin main'
expect defer "newline: status then force push"      $'git status\ngit push --force origin main'
expect defer "newline: log then reset --hard"       $'git log --oneline -3\ngit reset --hard origin/main'
expect defer "newline: pwd then gh pr merge"        $'pwd\ngh pr merge 42'
expect defer "newline: status then git add ."       $'git status\ngit add .'
expect defer "newline: echo then commit"            $'echo hi\ngit commit -m x'
expect defer "newline: ls then rm -rf"              $'ls\nrm -rf build'
expect defer "newline: ls -la then mkdir"           $'ls -la\nmkdir out'
expect defer "newline: log then (gh issue close)"   $'git log\n(gh issue close 5)'
expect defer "newline: blank line before push"      $'git status\n\ngit push origin main'
expect defer "newline: padded lines around push"    $'git status  \n  git push origin main'
expect defer "newline: push between two reads"      $'git status\ngit push origin main\ngit log'

# ---- multi-line all-read-only commands STAY approved (no new prompts) -----
expect APPROVE "newline partner: status + log"      $'git status\ngit log --oneline -3'
expect APPROVE "newline partner: ls + grep"         $'ls -la\ngrep -rn TODO .'
expect APPROVE "newline partner: fetch + status"    $'git fetch origin\ngit status --short'
expect APPROVE "newline partner: 3-line read chain" $'git log\ngit diff --stat\ngit branch -vv'

# ---- newline-adjacent adversarial forms (defer on every uncertainty) ------
expect defer "CRLF-joined push"                     $'git status\r\ngit push origin main'
expect defer "backslash-newline splice inside verb" $'git pu\\\nsh origin main'
expect defer "literal \$'\\n' splice -> unparseable verb, defers" "git status\$'\\n'git push origin main"
expect defer "background & then push"               "git status & git push origin main"
expect defer "brace group around push"              "{ git push origin main; }"

# ---- deny-surface intersection: regenerated from the current deny layers --
# settings.json deny rules (the 7 Bash entries):
expect defer "deny-mirror: git push --force"        "git push --force origin feature-x"
expect defer "deny-mirror: git push -f"             "git push -f origin feature-x"
expect defer "deny-mirror: git reset --hard"        "git reset --hard origin/main"
expect defer "deny-mirror: gh pr merge"             "gh pr merge 42"
expect defer "deny-mirror: gh repo delete"          "gh repo delete o/r --yes"
expect defer "deny-mirror: gh issue close"          "gh issue close 5"
expect defer "deny-mirror: gh issue delete"         "gh issue delete 5"
# guard-git.sh blocked surface (from test_guard_git.sh):
expect defer "guard-git: force-with-lease"          "git push --force-with-lease origin feature-x"
expect defer "guard-git: bundled -fu cluster"       "git push -fu origin feat"
expect defer "guard-git: +refspec force"            "git push origin +feat:other"
expect defer "guard-git: push to main"              "git push origin main"
expect defer "guard-git: bare push"                 "git push"
expect defer "guard-git: HEAD:main"                 "git push origin HEAD:main"
expect defer "guard-git: full-ref main"             "git push origin refs/heads/main"
expect defer "guard-git: feature:main"              "git push origin feature:main"
expect defer "guard-git: +main"                     "git push origin +main"
expect defer "guard-git: --all"                     "git push --all origin"
expect defer "guard-git: --mirror"                  "git push --mirror origin"
expect defer "guard-git: --branches"                "git push --branches origin"
expect defer "guard-git: remote delete --delete"    "git push --delete origin somebranch"
expect defer "guard-git: remote delete :dst"        "git push origin :somebranch"
expect defer "guard-git: push behind -C"            "git -C . push origin main"
expect defer "guard-git: push behind --no-pager"    "git --no-pager push origin main"
expect defer "guard-git: absolute-path git push"    "/usr/bin/git push origin main"
expect defer "guard-git: binary add"                "git add plot.png"
expect defer "guard-git: bulk add -A"               "git add -A"
expect defer "guard-git: bulk add ."                "git add ."
expect defer "guard-git: gh pr merge --squash"      "gh pr merge 7 --squash"
expect defer "guard-git: gh -R flag before merge"   "gh -R o/r pr merge 7"
expect defer "guard-git: gh api pulls/N/merge"      "gh api repos/o/r/pulls/7/merge --method PUT"
expect defer "guard-git: (gh pr merge) subshell"    "(gh pr merge 7)"
expect defer "guard-git: graphql merge mutation"    'gh api graphql -f query="mutation { mergePullRequest(input:{pullRequestId:\"PR_x\"}) { pullRequest { number } } }"'
# guard-adr.sh blocked surface (from test_guard_adr.sh):
expect defer "guard-adr: git rm Decided ADR"        "git rm docs/decisions/adr-0004-enforcement-doctrine.md"
expect defer "guard-adr: git mv Decided ADR"        "git mv docs/decisions/adr-0004-enforcement-doctrine.md /tmp/x.md"
expect defer "guard-adr: coreutils rm -rf decisions" "rm -rf docs/decisions"
# guard-issue-close.sh blocked surface (from test_guard_issue_close.sh):
expect defer "guard-issue-close: api PATCH closed"  "gh api -X PATCH repos/o/r/issues/5 -f state=closed"
expect defer "guard-issue-close: graphql closeIssue" 'gh api graphql -f query="mutation { closeIssue(input:{issueId:\"I_x\"}) { issue { id } } }"'

# ---- the flood the hook exists for stays approved (still-allowed side) ----
expect APPROVE "flood: git -C form"                 "git -C /repo status --short --branch"
expect APPROVE "flood: env-prefixed git show"       "MSYS_NO_PATHCONV=1 git show origin/development:README.md"
expect APPROVE "flood: pipeline read"               "ls -la .claude/ | grep -i settings"
expect APPROVE "flood: chained reads"               "git status && git diff"
expect APPROVE "flood: repo suite run"              "bash scripts/test_guard_git.sh"

# ---- protocol edges (real-channel behavior of main()) ---------------------
expect defer "protocol: empty command"              ""
# Garbage (non-JSON) input: defer silently, exit 0.
out="$(printf 'not even json' | CLAUDE_PROJECT_DIR="$REPO" python3 "$HOOK" 2>/dev/null)"
rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "PASS: garbage input -> silent defer (rc=0)"
else echo "FAIL (rc=$rc, out='$out'): garbage input must defer silently"; fails=$((fails + 1)); fi
# A non-Bash tool defers on tool_name alone — the MCP deny entries stay
# unreachable even if the matcher were widened.
out="$(printf '{"tool_name":"mcp__github__merge_pull_request","tool_input":{"pullNumber":5}}' \
  | CLAUDE_PROJECT_DIR="$REPO" python3 "$HOOK" 2>/dev/null)"
rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "PASS: non-Bash tool_name -> silent defer (rc=0)"
else echo "FAIL (rc=$rc, out='$out'): non-Bash tool_name must defer silently"; fails=$((fails + 1)); fi

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
