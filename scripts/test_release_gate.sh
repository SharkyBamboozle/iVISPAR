#!/usr/bin/env bash
# Regression cases for scripts/release_gate_decision.sh (the release-gate
# logic). Runs inside `make verify`, so it binds in CI (D-004).
# Hermetic: drives throwaway fixture git repos (the check_bootstrap pattern)
# — no network. Asserts BOTH sides (block and allow) so a fix can't
# silently over/under-tighten.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/release_gate_decision.sh"
fails=0

GIT() { git -c user.email=t@test -c user.name=t "$@"; }

# fixture <base_version|-> <head_version|-> <head_changelog> [seam_body]
# Builds a two-commit repo: base commit (v1.0.2 changelog + optional version
# file), head commit (mutated version file + given changelog). Sets BASE/HEAD.
fixture() {
  DIR="$(mktemp -d)"
  mkdir -p "$DIR/.claude" "$DIR/blueprint"
  printf '%s\n' "${4:-mode: configured
version-file: blueprint/VERSION
changelog: blueprint/CHANGELOG.md}" >"$DIR/.claude/release.txt"
  [ "$1" != "-" ] && printf '%s\n' "$1" >"$DIR/blueprint/VERSION"
  printf '## v1.0.2 — base entry\n' >"$DIR/blueprint/CHANGELOG.md"
  GIT -C "$DIR" init -q
  GIT -C "$DIR" add -A && GIT -C "$DIR" commit -qm base
  BASE="$(GIT -C "$DIR" rev-parse HEAD)"
  if [ "$2" != "-" ]; then printf '%s\n' "$2" >"$DIR/blueprint/VERSION"
  else rm -f "$DIR/blueprint/VERSION"; fi
  printf '%s\n' "$3" >"$DIR/blueprint/CHANGELOG.md"
  GIT -C "$DIR" add -A && GIT -C "$DIR" commit -q --allow-empty -m head
  HEAD="$(GIT -C "$DIR" rev-parse HEAD)"
}

check() { # check <want_rc> <label> — runs the decision script in $DIR
  (cd "$DIR" && BASE="$BASE" HEAD="$HEAD" bash "$SCRIPT") >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$1" ]; then echo "PASS (rc=$rc): $2"
  else echo "FAIL (rc=$rc, want $1): $2"; fails=$((fails + 1)); fi
  rm -rf "$DIR"
}

fixture 1.0.2 1.0.3 "## v1.0.3 — patch entry"
check 0 "patch bump + log entry -> allow"

fixture 1.0.2 1.1.0 "## v1.1.0 — minor entry"
check 0 "minor bump (patch resets) -> allow"

fixture 1.0.2 2.0.0 "## v2.0.0 — major entry"
check 0 "major bump (minor+patch reset) -> allow"

fixture 1.0.2 1.0.2 "## v1.0.2 — base entry"
check 1 "version not bumped -> block (forgotten caboose)"

fixture 1.0.2 1.0.4 "## v1.0.4 — entry"
check 1 "skipped patch (1.0.2 -> 1.0.4) -> block (not a single step)"

fixture 1.0.2 1.2.1 "## v1.2.1 — entry"
check 1 "compound jump (1.0.2 -> 1.2.1) -> block (not a single step)"

fixture 1.0.2 v1.0.3-rc1 "## entry"
check 1 "head version not MAJOR.MINOR.PATCH -> block"

fixture 1.0.2 1.0.3 "## older entries only, no new version mentioned"
check 1 "bumped but no changelog entry for the new version -> block"

fixture 1.0.2 - "## v1.0.3 — entry"
check 1 "version file deleted at head while configured -> block (fail loud)"

fixture - 1.0.3 "## v1.0.3 — first release entry"
check 0 "no version file at base (first versioned release) -> allow with note"

fixture garbage 1.0.3 "## v1.0.3 — entry"
check 0 "unparsable base version (state the PR cannot repair) -> head-only checks, allow"

fixture 1.0.2 1.0.3 "## v1.0.3 — entry" "mode: off promotions are continuous deploys, unversioned"
check 0 "mode off with reason -> allow (declared dormant)"

fixture 1.0.2 1.0.2 "## v1.0.2" "mode: off"
check 1 "mode off without reason -> block (D-004: declaration needs its why)"

fixture 1.0.2 1.0.2 "## v1.0.2" "mode: banana"
check 1 "unknown mode -> block"

fixture 1.0.2 1.0.2 "## v1.0.2" "mode: configured"
check 1 "configured but version-file/changelog entries missing -> block"

fixture 1.0.2 1.0.3 "## v1.0.3 — entry"
rm "$DIR/.claude/release.txt"
check 1 "seam file missing -> block (a missing target never turns a gate green)"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
