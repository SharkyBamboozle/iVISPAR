#!/usr/bin/env bash
# Regression cases for .claude/hooks/guard-git.sh — run after any change to
# the hook (and inside `make verify`, so it binds in CI; D-004). Asserts BOTH
# sides (forbidden blocks, allowed still succeeds) so a fix can't silently
# over-tighten. State-dependent verdicts (push-to-main birth-vs-armed, bulk-add
# worktree scan) are made HERMETIC by exercising the hook inside throwaway git
# repos built here, with gh mocked through the hook's GUARD_GH_BIN seam — no
# network, no dependence on this repo's mutable state.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../.claude/hooks/guard-git.sh"
fails=0

emit() { # emit <command> -> PreToolUse JSON on stdout
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' \
    "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1")"
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# The hook opens `@file`/`--input` bodies with ITS python, which on Windows is
# often a native python invoked from MSYS bash — it cannot open the MSYS
# `/tmp/...` path this suite creates, and would fail closed (block) on a body
# the test means to be readable. cygpath -m renders the C:/-mixed form both
# MSYS bash and a Windows python resolve to the same file; a no-op off MSYS.
winpath(){ if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }

# GraphQL body fixtures for the `-F query=@file` self-merge cases: gh reads
# a field value of the form '@file' from disk, so a merge mutation can hide
# in a file the raw tokens never contain.
MERGE_GQL="$TMP/merge.graphql"; PLAIN_GQL="$TMP/plain.graphql"
printf 'mutation { mergePullRequest(input:{pullRequestId:"PR_x"}) { pullRequest { number } } }\n' >"$MERGE_GQL"
printf 'query { viewer { login } }\n' >"$PLAIN_GQL"
# Pass the hook a path its interpreter can open (see winpath); the files stay
# where bash created them.
MERGE_GQL="$(winpath "$MERGE_GQL")"; PLAIN_GQL="$(winpath "$PLAIN_GQL")"

# Hermetic gh for the zombie-push check: the hook's `gh pr list` gets
# $MOCK_PRS (JSON array; default: no PR history) at rc $MOCK_GH_RC — so the
# suite never touches the network even on machines with a real gh. The mock
# is delivered through the hook's explicit GUARD_GH_BIN seam (exported in
# expect below as an "<absolute bash> <script>" argv), NOT via PATH: a
# Windows-native Python resolves the hook's spawn through CreateProcess,
# which cannot execute an extensionless shebang script and silently falls
# through to the real gh — PATH-only delivery would test the live API there
# while staying green on Linux. The bash in that argv must itself be an
# ABSOLUTE path: for bare program names CreateProcess searches System32
# BEFORE PATH, and System32 ships a bash.exe (the WSL launcher) that either
# errors with no distro installed or runs the script inside WSL, where this
# suite's MSYS temp paths do not exist — fail-open either way, red suite.
mkdir -p "$TMP/mock"
cat >"$TMP/mock/gh" <<'MOCK'
#!/usr/bin/env bash
[ "${MOCK_GH_RC:-0}" -ne 0 ] && exit "${MOCK_GH_RC}"
printf '%s\n' "${MOCK_PRS:-[]}"
MOCK
chmod +x "$TMP/mock/gh"

# PATH still gets a gh, but it is a static DECOY that always answers "no
# PRs" — never the mock above. The decoy keeps the seam revert-sensitive
# where CI runs: if the hook's spawn ever regresses to bare ["gh", ...],
# PATH resolution finds the decoy on Linux too, the terminal-PR zombie
# cases see [] instead of their fixtures, fail open to "allowed", and go
# red. (A marker-file canary could not pin this — with the seam reverted, a
# PATH-delivered mock still answers on Linux; only divergent answers make
# the regression visible where CI runs.)
mkdir -p "$TMP/bin"
cat >"$TMP/bin/gh" <<'DECOY'
#!/usr/bin/env bash
printf '[]\n'
DECOY
chmod +x "$TMP/bin/gh"

# Resolve the RUNNING bash to an absolute path for the seam argv (see the
# System32 note above). On MSYS the physical file is bash.exe and cygpath -m
# renders the Windows-mixed C:/ form CreateProcess accepts; on POSIX $BASH
# is already absolute and both probes are no-ops. Both seam tokens are
# shlex-quoted — the MSYS bash lives under "C:/Program Files/...".
SEAM_BASH="${BASH:-$(command -v bash)}"
[ -f "${SEAM_BASH}.exe" ] && SEAM_BASH="${SEAM_BASH}.exe"
command -v cygpath >/dev/null 2>&1 && SEAM_BASH="$(cygpath -m "$SEAM_BASH")"
SEAM_GH="\"$SEAM_BASH\" \"$TMP/mock/gh\""

# Form pin, asserted where CI runs: a bare-name regression here cannot
# diverge behaviorally on POSIX (any PATH bash works), so pin the FORM the
# Windows spawn depends on — the seam's program token must be absolute.
case "$SEAM_BASH" in
  /*|[A-Za-z]:/*) echo "PASS (form): seam bash path is absolute -> pin holds" ;;
  *) echo "FAIL (form): seam bash '$SEAM_BASH' not absolute -> CreateProcess would search System32 (WSL launcher) first"
     fails=$((fails + 1)) ;;
esac

expect() { # expect <rc> <label> <command> [cwd]
  local want="$1" label="$2" cmd="$3" dir="${4:-$HERE/..}"
  ( cd "$dir" && emit "$cmd" | env -u CLAUDE_PROJECT_DIR \
      PATH="$TMP/bin:$PATH" GUARD_GH_BIN="$SEAM_GH" \
      MOCK_PRS="${MOCK_PRS:-[]}" MOCK_GH_RC="${MOCK_GH_RC:-0}" \
      bash "$HOOK" >/dev/null 2>&1 )
  local rc=$?
  if [ "$rc" -eq "$want" ]; then echo "PASS (rc=$rc): $label"
  else echo "FAIL (rc=$rc, want $want): $label"; fails=$((fails + 1)); fi
}

# Force/broad-push fixtures must assert the MESSAGE, not just rc=2: on a
# repo state where two rules overlap, the wrong rule's block would make a
# regressed matcher look green (e.g. a push-to-main block masking a dead
# force detector). expect_msg pins which rule fired.
expect_msg() { # expect_msg <rc> <stderr-snippet> <label> <command> [cwd]
  local want="$1" snippet="$2" label="$3" cmd="$4" dir="${5:-$HERE/..}"
  local err rc
  err="$( ( cd "$dir" && emit "$cmd" | env -u CLAUDE_PROJECT_DIR \
      PATH="$TMP/bin:$PATH" GUARD_GH_BIN="$SEAM_GH" \
      MOCK_PRS="${MOCK_PRS:-[]}" MOCK_GH_RC="${MOCK_GH_RC:-0}" \
      bash "$HOOK" 2>&1 >/dev/null ) )"
  rc=$?
  if [ "$rc" -eq "$want" ] && printf '%s' "$err" | grep -qF "$snippet"; then
    echo "PASS (rc=$rc, msg ok): $label"
  else
    echo "FAIL (rc=$rc, want $want + '$snippet'): $label"
    fails=$((fails + 1))
  fi
}

# ---- state-independent cases (run against this repo) --------------------
expect 2 "force push -> blocked"                 "git push --force origin feature-x"
expect 2 "force-with-lease -> blocked"           "git push --force-with-lease origin feature-x"
expect 2 "gh pr merge -> blocked"                "gh pr merge 7 --squash"
expect 2 "gh api pulls/N/merge -> blocked"       "gh api repos/o/r/pulls/7/merge --method PUT"
expect 0 "gh api pulls/N (not merge) -> allowed" "gh api repos/o/r/pulls/7"
expect 2 "remote branch delete (--delete) -> blocked" "git push --delete origin somebranch"
expect 2 "remote branch delete (:dst) -> blocked"     "git push origin :somebranch"
expect 0 "feature push -> allowed"               "git push -u origin feature/x"
expect 0 "'main' inside a branch name -> allowed" "git push -u origin claude/fix-main-page"
expect 2 "binary add -> blocked"                 "git add plot.png"
expect 2 "quoted binary add -> blocked"          'git add "plot.png"'
expect 0 "quoted text add -> allowed"            'git add "docs/index.md"'
expect 0 "text add -> allowed"                   "git add docs/index.md"
expect 0 "read-only chain -> allowed"            "git status && git diff"
expect 0 "garbage input -> allowed (fail-open)"  "echo not even json"

# ---- hardened parsing: gh global flags, subshells, GraphQL merge --------
expect 2 "gh -R flag before pr merge -> blocked"      "gh -R o/r pr merge 7"
expect 2 "(gh pr merge 7) subshell -> blocked"        "(gh pr merge 7)"
expect 0 "(gh pr view 7) subshell -> allowed (partner)" "(gh pr view 7)"
expect 2 "gh api graphql mergePullRequest -> blocked" \
  'gh api graphql -f query="mutation { mergePullRequest(input:{pullRequestId:\"PR_x\"}) { pullRequest { number } } }"'
expect 0 "gh api graphql plain query -> allowed (partner)" \
  'gh api graphql -f query="query { viewer { login } }"'
expect 2 "gh api full-URL pulls/N/merge -> blocked (URL normalized)" \
  "gh api https://api.github.com/repos/o/r/pulls/7/merge --method PUT"
expect 2 "gh api graphql -F query=@file (merge mutation in file) -> blocked" \
  "gh api graphql -F query=@$MERGE_GQL"
expect 0 "gh api graphql -F query=@file (plain query in file) -> allowed" \
  "gh api graphql -F query=@$PLAIN_GQL"
expect 2 "gh api graphql --input - (stdin, unreadable) -> blocked (fail closed)" \
  "gh api graphql --input -"
expect 2 "gh api graphql enablePullRequestAutoMerge -> blocked" \
  'gh api graphql -f query="mutation { enablePullRequestAutoMerge(input:{pullRequestId:\"PR_x\"}) { pullRequest { number } } }"'

# ---- hermetic push-to-main + bulk-add cases (throwaway repos) -----------
mk() { git init -q "$1"; git -C "$1" config user.email t@t.t; git -C "$1" config user.name t; }

# armed: origin/main exists with >1 commit (not the template birth state)
git init -q --bare "$TMP/origin-armed.git"
mk "$TMP/armed"; git -C "$TMP/armed" checkout -q -b main
echo 1 >"$TMP/armed/f"; git -C "$TMP/armed" add f; git -C "$TMP/armed" commit -qm 1
echo 2 >"$TMP/armed/f"; git -C "$TMP/armed" commit -qam 2
git -C "$TMP/armed" remote add origin "$TMP/origin-armed.git"
git -C "$TMP/armed" push -q origin main; git -C "$TMP/armed" fetch -q origin
expect 2 "armed: bare push on main -> blocked"        "git push"                       "$TMP/armed"
expect 2 "armed: push origin (implicit) on main -> blocked" "git push origin"          "$TMP/armed"
expect 2 "armed: push origin HEAD on main -> blocked" "git push origin HEAD"           "$TMP/armed"
expect 2 "armed: HEAD:main -> blocked"                "git push origin HEAD:main"      "$TMP/armed"
expect 2 "armed: refs/heads/main full-ref -> blocked" "git push origin refs/heads/main" "$TMP/armed"
expect 2 "armed: feature:main -> blocked"             "git push origin feature:main"   "$TMP/armed"
expect 0 "armed: explicit non-main from main -> allowed" "git push origin featbranch"  "$TMP/armed"
# a --dry-run / -n push transmits nothing — never a hard-rule violation
expect 0 "armed: dry-run push on main -> allowed (transmits nothing)"      "git push --dry-run"      "$TMP/armed"
expect 0 "armed: -n dry-run push on main -> allowed"                       "git push -n"             "$TMP/armed"
# --tags on main pushes tags, not the main branch -> not an implicit main push
expect 0 "armed: push origin --tags on main -> allowed (tags only)"        "git push origin --tags"  "$TMP/armed"
expect 2 "armed: push origin main --tags -> still blocked (explicit main)" "git push origin main --tags" "$TMP/armed"

# ---- hardened parsing: global options, newlines, subshells, comments ----
expect 2 "armed: git -C . push origin main -> blocked"       "git -C . push origin main"       "$TMP/armed"
expect 2 "armed: --no-pager push origin main -> blocked"     "git --no-pager push origin main" "$TMP/armed"
expect 2 "armed: --git-dir=.git push origin main -> blocked" "git --git-dir=.git push origin main" "$TMP/armed"
expect 2 "armed: -c k=v push origin main -> blocked"         "git -c k=v push origin main"     "$TMP/armed"
expect 0 "armed: git -C . push origin featbranch -> allowed (partner)" "git -C . push origin featbranch" "$TMP/armed"
expect 2 "armed: newline-joined bare push on main -> blocked" $'git push\necho x'               "$TMP/armed"
expect 0 "armed: newline-joined non-main push -> allowed (partner)" $'echo x\ngit push origin featbranch' "$TMP/armed"
expect 2 "armed: (git push origin main) subshell -> blocked" "(git push origin main)"          "$TMP/armed"
expect 0 "armed: (git status) subshell -> allowed (partner)" "(git status)"                    "$TMP/armed"
expect 2 "armed: \$(git push origin main) -> blocked"        '$(git push origin main)'         "$TMP/armed"
expect 0 "armed: commented-out push -> allowed (word-boundary comment)" "echo hi # git push origin main" "$TMP/armed"
expect 2 'armed: double-quoted backtick push-to-main -> blocked' 'echo "`git push origin main`"' "$TMP/armed"
expect 0 'armed: benign double-quoted backtick (git status) -> allowed' 'echo "state `git status`"' "$TMP/armed"
expect 2 'armed: double-quoted $(...) push-to-main -> blocked' 'echo "$(git push origin main)"' "$TMP/armed"
expect 2 'armed: assignment $(...) push-to-main -> blocked' 'out=$(git push origin main)' "$TMP/armed"
expect 0 'armed: benign double-quoted $(...) (git status) -> allowed' 'echo "s $(git status) e"' "$TMP/armed"
expect 0 "armed: --dry-run push on main -> allowed (transmits nothing)" "git push --dry-run origin main" "$TMP/armed"
expect 0 "armed: --dry (abbrev) push on main -> allowed (no allow/block abbrev skew)" "git push --dry origin main" "$TMP/armed"
expect 0 "armed: --tags push -> allowed (branch not pushed)"        "git push --tags origin" "$TMP/armed"
expect 0 "armed: --tag (abbrev) push -> allowed"                    "git push --tag origin"  "$TMP/armed"
expect 2 "armed: push with trailing comment -> blocked (partner)" "git push origin main # sync" "$TMP/armed"
expect 0 "armed: quoted multi-line commit message -> allowed" $'git commit -m "subject\n\nbody mentions push origin main"' "$TMP/armed"
expect 0 "armed: quoted semicolon + push text in message -> allowed" 'git commit -m "x; git push origin main"' "$TMP/armed"

git -C "$TMP/armed" checkout -q -b feat
expect 0 "armed: bare push on feature -> allowed"     "git push"                       "$TMP/armed"

# ---- force / broad forms, hermetic on a FEATURE branch so only the rule
# ---- under test can fire, asserting the MESSAGE (not just rc) ----------
expect_msg 2 "no force-pushes" "armed/feat: --force-with-lea (abbrev) -> force-blocked" \
  "git push --force-with-lea origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: --force-w (short abbrev) -> force-blocked" \
  "git push --force-w origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: --force-with-lea=<ref> -> force-blocked" \
  "git push --force-with-lea=feat:deadbeef origin feat" "$TMP/armed"
expect 0 "armed/feat: --force-if-includes alone -> allowed (lease modifier, not force)" \
  "git push --force-if-includes origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: -fu bundled cluster -> force-blocked" \
  "git push -fu origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: -fo <val> (force + push-option) -> force-blocked" \
  "git push -fo opt=1 origin feat" "$TMP/armed"
expect 0 "armed/feat: -of (push-option value 'f', NOT force) -> allowed" \
  "git push -of origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: --force-with-lease=<v> -> force-blocked" \
  "git push --force-with-lease=feat origin feat" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: +feat:other refspec -> force-blocked" \
  "git push origin +feat:other" "$TMP/armed"
expect_msg 2 "no force-pushes" "armed/feat: +HEAD refspec -> force-blocked" \
  "git push origin +HEAD" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: +main -> blocked as push-to-main" \
  "git push origin +main" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --all carries main -> blocked" \
  "git push --all origin" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --al (abbrev of --all) -> blocked" \
  "git push --al origin" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --mir (abbrev of --mirror) -> blocked" \
  "git push --mir origin" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --branc (abbrev of --branches) -> blocked" \
  "git push --branc origin" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --branches carries main -> blocked" \
  "git push --branches origin" "$TMP/armed"
expect_msg 2 "never push to main" "armed/feat: --mirror carries main -> blocked" \
  "git push --mirror origin" "$TMP/armed"
expect_msg 2 "remote branch deletion" "armed/feat: -qd bundled cluster -> delete-blocked" \
  "git push -qd origin somebranch" "$TMP/armed"
expect_msg 2 "remote branch deletion" "armed/feat: --del (abbrev of --delete) -> delete-blocked" \
  "git push --del origin somebranch" "$TMP/armed"
expect 0 "armed/feat: branch literally named foo/main -> allowed (no false-block)" \
  "git push origin foo/main" "$TMP/armed"
expect 0 "armed/feat: --follow-tags non-main -> allowed" \
  "git push --follow-tags origin feature-x" "$TMP/armed"
expect 0 "armed/feat: HEAD:feature -> allowed" "git push origin HEAD:feature" "$TMP/armed"
expect 0 "armed/feat: push featX && echo main -> allowed" \
  "git push origin featX && echo main" "$TMP/armed"

# birth: remote genuinely has no main (ls-remote --exit-code returns 2)
git init -q --bare "$TMP/origin-empty.git"
mk "$TMP/birth"; git -C "$TMP/birth" checkout -q -b main
echo x >"$TMP/birth/BOOTSTRAP.md"; git -C "$TMP/birth" add -A; git -C "$TMP/birth" commit -qm birth
git -C "$TMP/birth" remote add origin "$TMP/origin-empty.git"
expect 0 "birth: push to main allowed (un-bootstrapped)" "git push origin main"        "$TMP/birth"

# inconclusive origin: remote URL does not exist -> must FAIL CLOSED (armed)
mk "$TMP/broken"; git -C "$TMP/broken" checkout -q -b main
echo x >"$TMP/broken/f"; git -C "$TMP/broken" add -A; git -C "$TMP/broken" commit -qm c
git -C "$TMP/broken" remote add origin "$TMP/nope.git"
expect 2 "inconclusive origin: push to main -> blocked (fail closed)" "git push origin main" "$TMP/broken"

# bulk add scans the worktree for un-LFS'd binaries
printf '\x89PNG' >"$TMP/armed/pic.png"
expect 2 "bulk add -A with untracked binary -> blocked" "git add -A" "$TMP/armed"
expect 2 "bulk add . with untracked binary -> blocked"  "git add ."  "$TMP/armed"
rm -f "$TMP/armed/pic.png"
expect 0 "bulk add -A, no binaries -> allowed"          "git add -A" "$TMP/armed"

# directory adds stage everything beneath, so they get the same scan —
# scoped to the added directory, so a binary ELSEWHERE never false-blocks
mkdir -p "$TMP/armed/sub" "$TMP/armed/docs"
printf '\x89PNG' >"$TMP/armed/sub/pic.png"
echo d >"$TMP/armed/docs/note.md"
expect_msg 2 "binary-type file" "dir add sub/ with binary inside -> blocked" \
  "git add sub/" "$TMP/armed"
expect 2 "dir add sub (no slash) with binary inside -> blocked" "git add sub" "$TMP/armed"
expect 2 "tree-wide add :/ with binary anywhere -> blocked"     "git add :/"  "$TMP/armed"
expect 0 "dir add docs/ scoped away from the binary -> allowed" "git add docs/" "$TMP/armed"
expect_msg 2 "binary-type file" "wildcard add '*' (whole tree) with binary -> blocked" \
  "git add '*'" "$TMP/armed"
expect 2 "wildcard add 'sub/*' with binary inside -> blocked"    "git add 'sub/*'" "$TMP/armed"
echo txt >"$TMP/armed/sub/note.txt"
expect 0 "wildcard add 'sub/*.txt' (text only) -> allowed"       "git add 'sub/*.txt'" "$TMP/armed"
rm -rf "$TMP/armed/sub"
expect 0 "dir add sub/ gone, docs/ still clean -> allowed"      "git add docs/" "$TMP/armed"
printf '\x89PNG' >"$TMP/armed/top.png"
expect 2 "filename-glob add 'top.*' matches a binary -> blocked" "git add 'top.*'" "$TMP/armed"
rm -f "$TMP/armed/top.png"

# a `-C sub` (or session cwd inside a subdir) must NOT shrink the scan below
# what git actually stages: -A/:/../ from a subdir still reach the repo root
mkdir -p "$TMP/armed/sub"
printf '\x89PNG' >"$TMP/armed/root.png"      # binary at repo ROOT
echo ok >"$TMP/armed/sub/note.txt"
expect_msg 2 "binary-type file" "-C sub add -A reaches repo-root binary -> blocked" \
  "git -C sub add -A" "$TMP/armed"
expect 2 "-C sub add :/ (root-anchored) reaches repo-root binary -> blocked" \
  "git -C sub add :/" "$TMP/armed"
expect 2 "-C sub add ../root.png (climbs out) -> blocked" \
  "git -C sub add ../root.png" "$TMP/armed"
expect 2 "session cwd in subdir: add -A reaches repo-root binary -> blocked" \
  "git add -A" "$TMP/armed/sub"
expect 0 "-C sub add . (cwd subtree only, no binary there) -> allowed" \
  "git -C sub add ." "$TMP/armed"
rm -f "$TMP/armed/root.png"; rm -rf "$TMP/armed/sub"

# absolute-/relative-path and .exe invocations are recognized (finding: a
# leading token that is not the bare name 'git' must still be caught)
git -C "$TMP/armed" checkout -q main
GITBIN="$(command -v git)"
expect 2 "absolute-path git push origin main -> blocked" "$GITBIN push origin main" "$TMP/armed"
git -C "$TMP/armed" checkout -q feat
expect 0 "absolute-path git push non-main -> allowed (partner)" "$GITBIN push origin featZ" "$TMP/armed"

# top-level backtick command substitution is split out and inspected
git -C "$TMP/armed" checkout -q main
expect 2 'top-level `git push origin main` backtick -> blocked' '`git push origin main`' "$TMP/armed"
git -C "$TMP/armed" checkout -q feat
expect 0 "single-quoted backtick text -> allowed (literal, not a command)" \
  "echo 'result: \`git push origin main\`'" "$TMP/armed"

# ---- zombie-push cases: terminal-PR branches, mocked gh -----------------
# Fixture: feat branched from development@c1; development then moved to c3
# (the "merge landed"), so feat's line no longer contains the integration
# tip — the zombie shape. Restarting feat onto origin/development is the
# sanctioned recovery and must stay allowed.
git init -q --bare "$TMP/origin-z.git"
mk "$TMP/z"; git -C "$TMP/z" checkout -q -b development
echo 1 >"$TMP/z/f"; git -C "$TMP/z" add f; git -C "$TMP/z" commit -qm c1
git -C "$TMP/z" remote add origin "$TMP/origin-z.git"
git -C "$TMP/z" push -q origin development
git -C "$TMP/z" checkout -q -b feat
echo 2 >"$TMP/z/f"; git -C "$TMP/z" commit -qam c2
git -C "$TMP/z" checkout -q development
echo 3 >"$TMP/z/f"; git -C "$TMP/z" commit -qam c3
git -C "$TMP/z" push -q origin development
git -C "$TMP/z" checkout -q feat

MOCK_PRS='[{"number":9,"state":"MERGED"}]'
expect 2 "zombie: latest PR merged, branch on pre-merge line -> blocked" "git push -u origin feat" "$TMP/z"
MOCK_PRS='[{"number":9,"state":"CLOSED"}]'
expect 2 "zombie: latest PR closed-unmerged -> blocked (operator decision)" "git push" "$TMP/z"
MOCK_PRS='[{"number":9,"state":"MERGED"},{"number":12,"state":"OPEN"}]'
expect 0 "open PR alongside an older merged one -> allowed (normal appending)" "git push" "$TMP/z"
MOCK_PRS='[]'
expect 0 "no PR history -> allowed (first push)" "git push -u origin feat" "$TMP/z"
MOCK_PRS='[{"number":9,"state":"MERGED"}]' MOCK_GH_RC=1
expect 0 "gh unavailable/errors -> allowed (fail OPEN by design)" "git push" "$TMP/z"
MOCK_GH_RC=0
git -C "$TMP/z" checkout -q -B feat origin/development
MOCK_PRS='[{"number":9,"state":"MERGED"}]'
expect 0 "restarted branch on current integration line -> allowed (fresh PR next)" "git push -u origin feat" "$TMP/z"
MOCK_PRS='[]'

# ---- MCP layer: the no-self-merge rule, parser-independent ------------
# The hook's matcher in .claude/settings.json routes the MCP merge tools
# here; the block must fire on tool NAME alone (there is no command to
# parse), and must not over-tighten onto unrelated PR tools.
expect_tool() { # expect_tool <rc> <label> <tool_name> <tool_input_json>
  local want="$1" label="$2" tool="$3" input="$4"
  printf '{"tool_name":"%s","tool_input":%s}' "$tool" "$input" \
    | env -u CLAUDE_PROJECT_DIR bash "$HOOK" >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$want" ]; then echo "PASS (rc=$rc): $label"
  else echo "FAIL (rc=$rc, want $want): $label"; fails=$((fails + 1)); fi
}
expect_tool_msg() { # expect_tool_msg <rc> <snippet> <label> <tool_name> <tool_input_json>
  local want="$1" snippet="$2" label="$3" tool="$4" input="$5"
  local err rc
  err="$(printf '{"tool_name":"%s","tool_input":%s}' "$tool" "$input" \
    | env -u CLAUDE_PROJECT_DIR bash "$HOOK" 2>&1 >/dev/null)"
  rc=$?
  if [ "$rc" -eq "$want" ] && printf '%s' "$err" | grep -qF "$snippet"; then
    echo "PASS (rc=$rc, msg ok): $label"
  else
    echo "FAIL (rc=$rc, want $want + '$snippet'): $label"; fails=$((fails + 1))
  fi
}

expect_tool_msg 2 "never the agent" "MCP merge_pull_request -> blocked (self-merge)" \
  mcp__github__merge_pull_request '{"owner":"o","repo":"r","pullNumber":5}'
expect_tool_msg 2 "Auto-merge counts" "MCP enable_pr_auto_merge -> blocked" \
  mcp__github__enable_pr_auto_merge '{"owner":"o","repo":"r","pullNumber":5}'
expect_tool 2 "merge tool on a differently-named MCP server -> blocked" \
  mcp__github-enterprise__merge_pull_request '{"pullNumber":5}'
expect_tool 0 "MCP disable_pr_auto_merge -> allowed (disabling merges nothing)" \
  mcp__github__disable_pr_auto_merge '{"owner":"o","repo":"r","pullNumber":5}'
expect_tool 0 "MCP update_pull_request -> allowed (no merge)" \
  mcp__github__update_pull_request '{"pullNumber":5,"body":"b"}'

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
