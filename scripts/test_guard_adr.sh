#!/usr/bin/env bash
# Regression cases for .claude/hooks/guard-adr.sh — run after any change to
# the hook (and inside `make verify`, so it binds in CI; D-004). Asserts BOTH
# sides (deny and still-allowed) so a fix can't silently over-tighten. Fully
# hermetic: a throwaway CLAUDE_PROJECT_DIR with fixture ADRs and its own token
# file — no dependence on this repo's real ADR statuses, no touching the real
# .claude/working/UNLOCKED_ADRS.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../.claude/hooks/guard-adr.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/docs/decisions" "$TMP/docs/process" "$TMP/.claude/working"
DECIDED="docs/decisions/adr-0001-fixture.md"
PROPOSED="docs/decisions/adr-0007-fixture.md"
printf '# ADR-0001 — Fixture\n\n- **Status:** ✅ Decided\n' >"$TMP/$DECIDED"
# The Proposed fixture deliberately embeds "✅ Decided" inside a comment and
# prose, to prove the status parse keys on the VALUE, not mere presence of ✅.
printf '# ADR-0007 — Fixture\n\n- **Status:** 🟡 Proposed\n<!-- at bootstrap, flip Status to ✅ Decided -->\nThis page is live while 🟡; promotion to ✅ Decided is the owner call.\n' >"$TMP/$PROPOSED"
printf '# Contributing\n' >"$TMP/docs/process/contributing.md"
printf '# Decisions\n' >"$TMP/docs/decisions/index.md"
TOKENS="$TMP/.claude/working/UNLOCKED_ADRS"

J() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

expect() { # expect <rc> <label> <tool_name> <tool_input_json>
  printf '{"tool_name":%s,"tool_input":%s}' "$(J "$3")" "$4" \
    | CLAUDE_PROJECT_DIR="$TMP" bash "$HOOK" >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$1" ]; then echo "PASS (rc=$rc): $2"
  else echo "FAIL (rc=$rc, want $1): $2"; fails=$((fails + 1)); fi
}

rm -f "$TOKENS"

# ---- deny side --------------------------------------------------------
expect 2 "edit Decided ADR, no token -> blocked" \
  Edit "{\"file_path\":$(J "$DECIDED")}"
expect 2 "create new ADR stamped ✅ -> blocked" \
  Write "{\"file_path\":$(J docs/decisions/adr-0099-new.md),\"content\":$(J '# ADR-0099
- **Status:** ✅ Decided')}"
expect 2 "off-format ✅ status line (no bullet) -> blocked" \
  Write "{\"file_path\":$(J docs/decisions/adr-0099-new.md),\"content\":$(J '**Status:** ✅ Decided')}"
expect 2 "born-Decided, emoji AFTER word (Status: Decided ✅) -> blocked" \
  Write "{\"file_path\":$(J docs/decisions/adr-0099-new.md),\"content\":$(J '- **Status:** Decided ✅')}"
expect 2 "born-Decided, em-dash form (Status — ✅ Decided) -> blocked" \
  Write "{\"file_path\":$(J docs/decisions/adr-0099-new.md),\"content\":$(J '- **Status** — ✅ Decided')}"
# promotion that replaces only the status VALUE (new_string has no 'Status')
expect 2 "promote 🟡→✅ via value-only Edit (applied in-memory) -> blocked" \
  Edit "{\"file_path\":$(J "$PROPOSED"),\"old_string\":$(J '🟡 Proposed'),\"new_string\":$(J '✅ Decided')}"
expect 2 "promote to a bare ✅ value via Edit -> blocked" \
  Edit "{\"file_path\":$(J "$PROPOSED"),\"old_string\":$(J '🟡 Proposed'),\"new_string\":$(J '✅')}"
expect 0 "Edit adds ✅ in PROSE (no status change) -> allowed" \
  Edit "{\"file_path\":$(J "$PROPOSED"),\"old_string\":$(J 'Proposed'),\"new_string\":$(J 'Proposed — ✅ in prose')}"
expect 2 "promote 🟡→✅ via Edit -> blocked" \
  Edit "{\"file_path\":$(J "$PROPOSED"),\"new_string\":$(J '- **Status:** ✅ Decided')}"
expect 2 "promote 🟡→✅ via MultiEdit -> blocked" \
  MultiEdit "{\"file_path\":$(J "$PROPOSED"),\"edits\":[{\"old_string\":$(J '- **Status:** 🟡 Proposed'),\"new_string\":$(J '- **Status:** ✅ Decided')}]}"
expect 2 "Decided ADR via ../ path (normalization) -> blocked" \
  Edit "{\"file_path\":$(J docs/decisions/../decisions/adr-0001-fixture.md)}"
expect 2 "git rm Decided ADR (delete) -> blocked" \
  Bash "{\"command\":$(J "git rm $DECIDED")}"
expect 2 "git mv Decided ADR (rename) -> blocked" \
  Bash "{\"command\":$(J "git mv $DECIDED docs/decisions/adr-0001-renamed.md")}"

# ---- hardened parsing: global options, subshells, magic, parent dirs ---
expect 2 "git -C . rm Decided ADR -> blocked" \
  Bash "{\"command\":$(J "git -C . rm $DECIDED")}"
expect 2 "git -C docs/decisions rm bare Decided name -> blocked (path resolves against -C)" \
  Bash "{\"command\":$(J 'git -C docs/decisions rm adr-0001-fixture.md')}"
expect 0 "git -C docs/decisions rm bare Proposed name -> allowed (partner)" \
  Bash "{\"command\":$(J 'git -C docs/decisions rm adr-0007-fixture.md')}"
expect 2 "(git rm Decided ADR) subshell -> blocked" \
  Bash "{\"command\":$(J "(git rm $DECIDED)")}"
expect 0 "(git rm Proposed ADR) subshell -> allowed (partner)" \
  Bash "{\"command\":$(J "(git rm $PROPOSED)")}"
expect 2 "newline-joined rm of Decided ADR -> blocked" \
  Bash "{\"command\":$(J "$(printf 'echo x\ngit rm %s' "$DECIDED")")}"
expect 0 "commented-out rm of Decided ADR -> allowed (word-boundary comment)" \
  Bash "{\"command\":$(J "echo hi # git rm $DECIDED")}"
expect 2 "rm of Decided ADR with trailing comment -> blocked (partner)" \
  Bash "{\"command\":$(J "git rm $DECIDED # cleanup")}"
expect 2 "git rm :/ magic pathspec on Decided ADR -> blocked" \
  Bash "{\"command\":$(J "git rm :/$DECIDED")}"
expect 2 "absolute-path git rm of Decided ADR -> blocked" \
  Bash "{\"command\":$(J "$(command -v git) rm $DECIDED")}"
expect 2 "top-level backtick git rm of Decided ADR -> blocked" \
  Bash "{\"command\":$(J "\`git rm $DECIDED\`")}"
expect 2 "git rm -r docs/decisions (parent dir) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r docs/decisions')}"
expect 2 "git rm -r docs (grandparent dir) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r docs')}"
expect 2 "git rm -r :/ (root-anchored, whole repo) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r :/')}"
expect 2 "git rm -r : (empty pathspec = repo root) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r :')}"
expect 2 "git rm -r :(top) (root-anchored magic) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r :(top)')}"
expect 2 "git rm -r :/* (root glob) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r :/*')}"
expect 2 "git rm docs/deci* (glob prefix under docs) -> blocked" \
  Bash "{\"command\":$(J 'git rm -r docs/deci*')}"
expect 0 "git rm -r other* (glob prefix, no ADRs) -> allowed (partner)" \
  Bash "{\"command\":$(J 'git rm -r other*')}"
expect 2 "git rm brace-expansion incl. Decided ADR -> blocked" \
  Bash "{\"command\":$(J "git rm docs/decisions/adr-{0001-fixture,0007-fixture}.md")}"

# ---- coreutils rm/mv reach the same file (lock protects the decision) --
expect 2 "coreutils rm of Decided ADR -> blocked" \
  Bash "{\"command\":$(J "rm $DECIDED")}"
expect 2 "coreutils rm -rf docs/decisions (parent dir) -> blocked" \
  Bash "{\"command\":$(J 'rm -rf docs/decisions')}"
expect 2 "coreutils mv of Decided ADR out of repo -> blocked" \
  Bash "{\"command\":$(J "mv $DECIDED /tmp/somewhere.md")}"
expect 2 "coreutils rm brace-expansion incl. Decided ADR -> blocked" \
  Bash "{\"command\":$(J "rm docs/decisions/adr-{0001-fixture,0007-fixture}.md")}"
expect 2 "git rm brace-RANGE incl. Decided ADR -> blocked" \
  Bash "{\"command\":$(J 'git rm docs/decisions/adr-{0001..0001}-fixture.md')}"
expect 2 "git rm over-cap brace-range under decisions -> blocked (scope scan)" \
  Bash "{\"command\":$(J 'git rm docs/decisions/adr-000{1..2000}-fixture.md')}"
expect 2 "git rm DESCENDING brace-range past cap -> blocked (scope scan)" \
  Bash "{\"command\":$(J 'git rm docs/decisions/adr-{0065..0001}-fixture.md')}"
expect 0 "over-cap brace-range OUTSIDE the ADR tree -> allowed (no false-block)" \
  Bash "{\"command\":$(J 'rm docs/process/note-{1..2000}.md')}"

# ---- cd context is tracked across && / ; lists -------------------------
expect 2 "cd docs/decisions && git rm bare Decided name -> blocked" \
  Bash "{\"command\":$(J 'cd docs/decisions && git rm adr-0001-fixture.md')}"
expect 2 "cd docs/decisions && rm bare Decided name -> blocked" \
  Bash "{\"command\":$(J 'cd docs/decisions && rm adr-0001-fixture.md')}"
expect 2 "cd docs && rm -r decisions (parent dir via cd) -> blocked" \
  Bash "{\"command\":$(J 'cd docs && rm -r decisions')}"
expect 0 "cd docs/process && rm contributing.md (not an ADR) -> allowed (partner)" \
  Bash "{\"command\":$(J 'cd docs/process && rm contributing.md')}"
# subshell cd does NOT persist in a real shell — the running-cd must not leak
# out of ( ) and cause a MISS relative to the no-cd baseline (both contexts
# are checked, so the full-path form is still caught).
expect 2 "(cd sub) ; git rm <full-path Decided> -> blocked (no subshell-cd leak miss)" \
  Bash "{\"command\":$(J '(cd sub) ; git rm docs/decisions/adr-0001-fixture.md')}"
expect 2 "(cd docs) ; rm decisions/<Decided> -> blocked (cd-context catches it)" \
  Bash "{\"command\":$(J '(cd docs) ; rm decisions/adr-0001-fixture.md')}"
expect 0 "(cd docs/decisions) ; git rm docs/process/<non-ADR> -> allowed (partner)" \
  Bash "{\"command\":$(J '(cd docs/decisions) ; git rm docs/process/contributing.md')}"
expect 0 "coreutils rm of Proposed ADR -> allowed (partner)" \
  Bash "{\"command\":$(J "rm $PROPOSED")}"
expect 0 "coreutils rm of a non-ADR file -> allowed" \
  Bash "{\"command\":$(J 'rm docs/process/contributing.md')}"
expect 0 "coreutils mv INTO docs/decisions -> allowed (creates, not destroys)" \
  Bash "{\"command\":$(J 'mv docs/process/contributing.md docs/decisions/')}"
expect 2 "git mv docs/decisions archive (parent dir rename) -> blocked" \
  Bash "{\"command\":$(J 'git mv docs/decisions archive')}"
expect 0 "git rm -r docs/process (no ADRs beneath) -> allowed (partner)" \
  Bash "{\"command\":$(J 'git rm -r docs/process')}"
expect 0 "git mv INTO docs/decisions -> allowed (creates, not destroys)" \
  Bash "{\"command\":$(J 'git mv docs/process/contributing.md docs/decisions/')}"

# ---- allow side (anti-over-tighten) -----------------------------------
expect 0 "edit Proposed ADR, no token -> allowed" \
  Edit "{\"file_path\":$(J "$PROPOSED")}"
expect 0 "create new ADR stamped 🟡 -> allowed" \
  Write "{\"file_path\":$(J docs/decisions/adr-0099-new.md),\"content\":$(J '# ADR-0099
- **Status:** 🟡 Proposed')}"
expect 0 "edit Proposed ADR body (non-status) -> allowed" \
  Edit "{\"file_path\":$(J "$PROPOSED"),\"new_string\":$(J 'some prose change')}"
expect 0 "git rm Proposed ADR -> allowed" \
  Bash "{\"command\":$(J "git rm $PROPOSED")}"
expect 0 "git rm a non-ADR file -> allowed" \
  Bash "{\"command\":$(J 'git rm README.md')}"
expect 0 "git status (not rm/mv) -> allowed" \
  Bash "{\"command\":$(J 'git status && git diff')}"
expect 0 "registry index.md (not an ADR) -> allowed" \
  Edit "{\"file_path\":$(J docs/decisions/index.md)}"
expect 0 "unrelated docs page -> allowed" \
  Edit "{\"file_path\":$(J docs/process/contributing.md)}"
expect 0 "garbage input -> allowed (fail-open)" \
  Edit "{\"file_path\":$(J 'not even a path')}"

# ---- token unlocks exactly the named ADR ------------------------------
mkdir -p "$TMP/.claude/working"
echo "adr-0001 $(date +%s)" >"$TOKENS"
expect 0 "edit Decided ADR with fresh token -> allowed" \
  Edit "{\"file_path\":$(J "$DECIDED")}"
expect 0 "git rm Decided ADR with fresh token -> allowed" \
  Bash "{\"command\":$(J "git rm $DECIDED")}"
expect 0 "git -C . rm Decided ADR with fresh token -> allowed" \
  Bash "{\"command\":$(J "git -C . rm $DECIDED")}"
expect 0 "git rm -r docs/decisions, its only Decided ADR unlocked -> allowed" \
  Bash "{\"command\":$(J 'git rm -r docs/decisions')}"
echo "adr-0001 $(( $(date +%s) - 7200 ))" >"$TOKENS"
expect 2 "edit Decided ADR with expired token -> blocked" \
  Edit "{\"file_path\":$(J "$DECIDED")}"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
