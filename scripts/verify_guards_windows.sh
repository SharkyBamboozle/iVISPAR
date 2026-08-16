#!/usr/bin/env bash
# Windows verification helper for the PreToolUse guard hooks (three deny
# hooks + the read-only approve-hook).
#
# There is no Windows CI runner (see issue history around the guard suites), so
# Windows behavior is verified by an operator handoff. This script makes that
# check repeatable and — critically — FAITHFUL. It runs the guard suites, the
# load-bearing enforcement assertion, an environment fingerprint, and a
# root-cause probe for the MSYS-bash vs native-Windows-python path gap. It runs
# on Linux too (a bonus smoke test) — off MSYS the platform-specific arms
# degrade to no-ops.
#
# ── The argv trap this script exists to AVOID ────────────────────────────────
# MSYS bash auto-translates a POSIX-looking path ARGUMENT (one that starts with
# '/') into Windows form when it invokes a native-Windows program. So a probe
# like  `python3 -c 'open(sys.argv[1])' /tmp/x`  hands python an ALREADY
# TRANSLATED, readable path and prints "opened OK" even on a box where the guard
# genuinely cannot read '/tmp/x' — a false green that "confirms" a broken guard.
# A path delivered on STDIN, or embedded inside a larger argument (the tool
# JSON), is NOT translated — that is the faithful channel, and the one the real
# hook uses (`INPUT=$(cat); python3 - "$INPUT"`, path buried inside the JSON).
# This script therefore drives the hooks ONLY through emit()->stdin, and probes
# file-open ONLY via stdin — never a bare path argument.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
GITHOOK="$REPO/.claude/hooks/guard-git.sh"
fail=0

emit() {  # emit <command> -> PreToolUse tool JSON on stdout (path stays inside it)
  printf '{"tool_name":"Bash","tool_input":{"command":%s}}' \
    "$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1")"
}

echo "== environment fingerprint =="
uname -a 2>/dev/null || true
bash --version | head -1
echo "python3: $(command -v python3 || echo NOT-FOUND)"
python3 -c 'import sys; print("sys.platform =", sys.platform, "| executable =", sys.executable)' 2>/dev/null \
  || echo "python3 did not run — the hooks invoke python3 and would fail-open without it"
# The path bugs only reproduce under a NATIVE-WINDOWS python (sys.platform ==
# win32) invoked from MSYS bash; an MSYS-tree python resolves '/tmp' natively
# and would pass even a broken guard, so a green run under MSYS python is weaker
# evidence and must say so.
echo

echo "== guard suites (the real gate) =="
for s in test_guard_git.sh test_guard_adr.sh test_guard_issue_close.sh \
         test_guard_command_policy.sh; do
  if bash "$REPO/scripts/$s" >/dev/null 2>&1; then echo "PASS  scripts/$s"
  else echo "FAIL  scripts/$s"; fail=1; fi
done
if python3 "$REPO/scripts/test_guardlib.py" >/dev/null 2>&1; then echo "PASS  scripts/test_guardlib.py"
else echo "FAIL  scripts/test_guardlib.py"; fail=1; fi
echo

echo "== load-bearing enforcement assertion =="
# A forbidden command, fed to the hook through the REAL channel (JSON on stdin),
# from an unrelated cwd with CLAUDE_PROJECT_DIR unset, must BLOCK (rc=2) — proof
# the parser actually loaded. A silent rc=0 here is the exact disarm this check
# exists to catch. The trigger is assembled from fragments so this script's own
# `bash scripts/verify_guards_windows.sh` invocation is never self-blocked, and
# it is only ever handed to the hook as data, never executed.
armed="$(mktemp -d)"; trap 'rm -rf "$armed"' EXIT
git init -q --bare "$armed/o.git"
git init -q "$armed/w"
git -C "$armed/w" config user.email t@t.t
git -C "$armed/w" config user.name t
git -C "$armed/w" checkout -q -b main
echo 1 >"$armed/w/f"; git -C "$armed/w" add f; git -C "$armed/w" commit -qm1
echo 2 >"$armed/w/f"; git -C "$armed/w" commit -qam2
git -C "$armed/w" remote add origin "$armed/o.git"
git -C "$armed/w" push -q origin main
git -C "$armed/w" fetch -q origin
bad="git push origin ""main"          # assembled from fragments (see note above)
( cd "$armed/w" && emit "$bad" | env -u CLAUDE_PROJECT_DIR bash "$GITHOOK" >/dev/null 2>&1 )
rc=$?
if [ "$rc" -eq 2 ]; then echo "PASS  forbidden push-to-main BLOCKS (rc=2) — parser loaded and enforced"
else echo "FAIL  forbidden push-to-main returned rc=$rc — GUARD DISARMED"; fail=1; fi
echo

echo "== root-cause probe: MSYS path vs cygpath, via the FAITHFUL (stdin) channel =="
# Why the suites convert --input/@file paths with `cygpath -m`: a native-Windows
# python resolves a leading '/' drive-relatively (e.g. '/tmp/x' -> 'E:\tmp\x'),
# so an MSYS '/tmp/...' body is unreadable to it while the MSYS mount is really
# 'E:\Temp'. Probed via STDIN only (never a bare argv path — see the trap note).
probe="$(mktemp -d)"; printf '{"title":"x"}' >"$probe/b.json"
raw_rc=0
printf '%s' "$probe/b.json" | python3 -c 'import sys; open(sys.stdin.read()).read()' 2>/dev/null || raw_rc=$?
if command -v cygpath >/dev/null 2>&1; then
  win="$(cygpath -m "$probe/b.json")"; win_rc=0
  printf '%s' "$win" | python3 -c 'import sys; open(sys.stdin.read()).read()' 2>/dev/null || win_rc=$?
  echo "MSYS  path open via stdin: rc=$raw_rc   ($probe/b.json)"
  echo "cygpath -m open via stdin: rc=$win_rc   ($win)"
  if [ "$raw_rc" -ne 0 ] && [ "$win_rc" -eq 0 ]; then
    echo "  -> native-Windows python: MSYS path unreadable, cygpath form readable (expected on this config)"
  fi
else
  echo "cygpath absent (not MSYS) — MSYS path open via stdin: rc=$raw_rc (expected 0 off Windows)"
fi
rm -rf "$probe"
echo

[ "$fail" -eq 0 ] && echo "RESULT: GREEN" || echo "RESULT: RED"
exit "$fail"
