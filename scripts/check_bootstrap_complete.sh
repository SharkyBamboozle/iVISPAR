#!/usr/bin/env bash
# The objective "bootstrap finished" gate (blueprint/TOKENS.md):
#   Tier 1 — no unfilled {{TOKENS}} (GitHub Actions' own ${{ }} is excluded)
#   Tier 2 — no unresolved <!-- BLUEPRINT: ... --> judgment blocks
# Run from the repo root of a freshly seeded project. Exits non-zero with the
# offending locations until both greps are clean. blueprint/ itself (and this
# script) are excluded — they are deleted at the end of bootstrap anyway.
#
# Ships with `--self-test` (D-005) — hermetic, drives fixture git repos.
set -uo pipefail

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

# Blueprint machinery is excluded — it is deleted at the end of bootstrap
# anyway (modules/, BOOTSTRAP.md, HARVEST.md, UPDATE.md, ADOPT.md,
# CONTRIBUTING.md, blueprint/). CONTRIBUTING.md (the blueprint's own
# contributor guide) legitimately contains literal {{TOKEN}} and BLUEPRINT:
# strings while explaining them — same reason its sibling rituals are excluded.
EXCLUDE=(':!blueprint' ':!modules' ':!BOOTSTRAP.md' ':!HARVEST.md' ':!UPDATE.md' ':!ADOPT.md' ':!CONTRIBUTING.md' ':!scripts/check_bootstrap_complete.sh')

run_checks() {
  local fail=0

  echo "== Tier 1: unfilled {{TOKENS}} (file contents) =="
  if git grep -nE '\{\{[A-Z_]+\}\}' -- "${EXCLUDE[@]}"; then
    fail=1
  else
    echo "clean"
  fi

  echo "== Tier 1: unfilled {{TOKENS}} (file/directory names) =="
  if git ls-files | grep -vE '^(blueprint|modules)/' | grep -E '\{\{[A-Z_]+\}\}'; then
    fail=1
  else
    echo "clean"
  fi

  echo "== Tier 2: unresolved BLUEPRINT: judgment blocks =="
  if git grep -n 'BLUEPRINT:' -- "${EXCLUDE[@]}"; then
    fail=1
  else
    echo "clean"
  fi

  if [ "$fail" -ne 0 ]; then
    echo
    echo "Bootstrap incomplete — resolve the locations above (see blueprint/TOKENS.md)."
  fi
  return "$fail"
}

self_test() {
  local fails=0
  _case() { # _case <expect_rc> <label> <setup-fn>
    local want="$1" label="$2" setup="$3" tmp rc
    tmp="$(mktemp -d)"
    ( cd "$tmp" && git init -q && git config user.email t@t.t && git config user.name t )
    "$setup" "$tmp"
    ( cd "$tmp" && git add -A >/dev/null 2>&1 )
    ( cd "$tmp" && bash "$SELF" >/dev/null 2>&1 ); rc=$?
    if [ "$rc" -eq "$want" ]; then echo "PASS (rc=$rc): $label"
    else echo "FAIL (rc=$rc, want $want): $label"; fails=$((fails + 1)); fi
    rm -rf "$tmp"
  }
  s_clean()   { echo "nothing to fill here" >"$1/a.md"; }
  s_content() { printf '%s\n' '{{PROJECT_NAME}}' >"$1/a.md"; }
  s_name()    { echo hi >"$1/{{PKG}}.md"; }   # double-quoted: no brace expansion
  s_marker()  { printf '<!-- BLUEPRINT: decide this at bootstrap -->\n' >"$1/a.md"; }
  s_actions() { printf 'run: echo ${{ github.token }}\n' >"$1/wf.yml"; }

  _case 0 "clean tree -> pass"                         s_clean
  _case 1 "unfilled {{TOKEN}} in file contents -> fail" s_content
  _case 1 "unfilled {{TOKEN}} in a filename -> fail"    s_name
  _case 1 "unresolved BLUEPRINT: marker -> fail"        s_marker
  _case 0 "GitHub Actions \${{ }} not flagged -> pass"  s_actions

  if [ "$fails" -eq 0 ]; then
    echo "check_bootstrap_complete --self-test: OK (all scenarios, both ways)"
    return 0
  fi
  echo "check_bootstrap_complete --self-test: FAIL ($fails)"
  return 1
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
  exit $?
fi
run_checks
exit $?
