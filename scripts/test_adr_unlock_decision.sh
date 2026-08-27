#!/usr/bin/env bash
# Regression cases for scripts/adr_unlock_decision.sh (the CI decided-ADR lock).
# Runs inside `make verify`, so it binds in CI (D-004/D-005). Hermetic:
# each case builds a throwaway git repo with a BASE and a HEAD commit — no
# network. Asserts BOTH sides (blocked / allowed) so a fix can't silently
# over- or under-tighten. Covers all five paths to a ✅ Decided page plus the
# freely-allowed 🟡 Proposed drafting paths.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/adr_unlock_decision.sh"
fails=0
B=""; H=""

adr() { # adr <repo> <file> <status-glyph+words>
  mkdir -p "$1/docs/decisions"
  printf '# %s\n\n- **Status:** %s\n\nbody\n' "$2" "$3" >"$1/docs/decisions/$2"
}
ci() { git -C "$1" add -A; git -C "$1" commit -q "${@:2}"; }

_case() { # _case <expect_rc> <label> <build-fn>
  local want="$1" label="$2" build="$3" tmp rc
  tmp="$(mktemp -d)"
  git init -q "$tmp"; git -C "$tmp" config user.email t@t.t; git -C "$tmp" config user.name t
  git -C "$tmp" commit -q --allow-empty -m root
  "$build" "$tmp"
  ( cd "$tmp" && BASE="$B" HEAD="$H" bash "$SCRIPT" >/dev/null 2>&1 ); rc=$?
  if [ "$rc" -eq "$want" ]; then echo "PASS (rc=$rc): $label"
  else echo "FAIL (rc=$rc, want $want): $label"; fails=$((fails + 1)); fi
  rm -rf "$tmp"
}

D="✅ Decided"; P="🟡 Proposed"
UNLOCK="feat

Unlock-ADR: adr-0001 — deliberate maintenance edit"

b_edit_decided_no_trailer() { adr "$1" adr-0001-x.md "$D"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  printf 'more\n' >>"$1/docs/decisions/adr-0001-x.md"; ci "$1" -m edit; H=$(git -C "$1" rev-parse HEAD); }
b_edit_decided_trailer() { adr "$1" adr-0001-x.md "$D"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  printf 'more\n' >>"$1/docs/decisions/adr-0001-x.md"; ci "$1" -m "$UNLOCK"; H=$(git -C "$1" rev-parse HEAD); }
b_add_decided_no_trailer() { ci "$1" --allow-empty -m base; B=$(git -C "$1" rev-parse HEAD)
  adr "$1" adr-0002-y.md "$D"; ci "$1" -m add; H=$(git -C "$1" rev-parse HEAD); }
b_add_decided_trailer() { ci "$1" --allow-empty -m base; B=$(git -C "$1" rev-parse HEAD)
  adr "$1" adr-0002-y.md "$D"; ci "$1" -m "feat

Unlock-ADR: adr-0002 — seed decision born Decided"; H=$(git -C "$1" rev-parse HEAD); }
b_add_proposed() { ci "$1" --allow-empty -m base; B=$(git -C "$1" rev-parse HEAD)
  adr "$1" adr-0003-z.md "$P"; ci "$1" -m add; H=$(git -C "$1" rev-parse HEAD); }
b_promote_no_trailer() { adr "$1" adr-0004-w.md "$P"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  adr "$1" adr-0004-w.md "$D"; ci "$1" -m promote; H=$(git -C "$1" rev-parse HEAD); }
b_edit_proposed() { adr "$1" adr-0005-p.md "$P"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  printf 'more\n' >>"$1/docs/decisions/adr-0005-p.md"; ci "$1" -m edit; H=$(git -C "$1" rev-parse HEAD); }
b_delete_decided_no_trailer() { adr "$1" adr-0006-d.md "$D"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  git -C "$1" rm -q docs/decisions/adr-0006-d.md; ci "$1" -m delete; H=$(git -C "$1" rev-parse HEAD); }
b_rename_decided_no_trailer() { adr "$1" adr-0007-old.md "$D"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  git -C "$1" mv docs/decisions/adr-0007-old.md docs/decisions/adr-0007-new.md; ci "$1" -m rename; H=$(git -C "$1" rev-parse HEAD); }
b_no_adr_change() { adr "$1" adr-0008-k.md "$D"; printf 'x\n' >"$1/README.md"; ci "$1" -m base; B=$(git -C "$1" rev-parse HEAD)
  printf 'y\n' >>"$1/README.md"; ci "$1" -m docs; H=$(git -C "$1" rev-parse HEAD); }

_case 1 "edit a Decided page, no trailer -> blocked"        b_edit_decided_no_trailer
_case 0 "edit a Decided page, Unlock-ADR trailer -> allowed" b_edit_decided_trailer
_case 1 "create a page already Decided, no trailer -> blocked" b_add_decided_no_trailer
_case 0 "create a Decided page with trailer -> allowed"      b_add_decided_trailer
_case 0 "create a Proposed page, no trailer -> allowed"      b_add_proposed
_case 1 "promote Proposed -> Decided, no trailer -> blocked" b_promote_no_trailer
_case 0 "edit a Proposed page, no trailer -> allowed"        b_edit_proposed
_case 1 "delete a Decided page, no trailer -> blocked"       b_delete_decided_no_trailer
_case 1 "rename a Decided page, no trailer -> blocked"       b_rename_decided_no_trailer
_case 0 "no ADR page changed -> allowed"                     b_no_adr_change

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
