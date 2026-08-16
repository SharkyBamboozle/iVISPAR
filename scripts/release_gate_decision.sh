#!/usr/bin/env bash
# Decision logic for the release-gate job (.github/workflows/branch-flow-guard.yml).
# A promotion PR into `main` must carry its release caboose
# (docs/process/release-checklist.md): the seam-named version file bumped by
# exactly one semver step — patch, minor, or major; WHICH one is the
# operator's decision, made at the /promote ritual's STOP, and this gate
# checks only the arithmetic, never the approval (advisory per D-004) —
# and the seam-named release log carrying an entry for the new version.
# Extracted into a script so the logic is testable against fixture git
# repos (scripts/test_release_gate.sh) — the workflow just supplies SHAs.
#
# Exit 0 = allow · exit 1 = block.
# Env: BASE, HEAD (PR base/head commit SHAs), SEAM (default .claude/release.txt).
#
# The seam declares the project's posture (mode: configured / off <reason>).
# A missing seam or a missing seam-named file fails LOUD — a moved file may
# never turn a gate green (house convention, D-004). Degenerate base states
# the PR cannot repair (version file absent or unparsable at base) degrade
# to a warning + head-side checks only, so a promotion can still fix them.
set -uo pipefail

BASE="${BASE:-}"
HEAD="${HEAD:-}"
SEAM="${SEAM:-.claude/release.txt}"

if [ -z "$BASE" ] || [ -z "$HEAD" ]; then
  echo "::error::release-gate: BASE/HEAD not supplied — failing closed."
  exit 1
fi
if [ ! -f "$SEAM" ]; then
  echo "::error::release-gate: seam file $SEAM is missing — restore it, or declare 'mode: off <one-line reason>' in it (D-004). A missing target never turns a gate green."
  exit 1
fi

mode_line="$(grep -E '^mode:' "$SEAM" | head -1 | sed 's/^mode:[[:space:]]*//')"
mode="${mode_line%% *}"
reason="$(printf '%s' "$mode_line" | sed 's/^[^[:space:]]*[[:space:]]*//')"

case "$mode" in
  off)
    if [ -z "$reason" ]; then
      echo "::error::release-gate: $SEAM sets 'mode: off' without a reason — an advisory declaration needs its why (D-004). Write 'mode: off <one-line reason>'."
      exit 1
    fi
    echo "release-gate: off by declaration ($reason)."
    exit 0
    ;;
  configured) ;;
  *)
    echo "::error::release-gate: $SEAM has unknown mode '$mode' (use 'configured', or 'off <reason>')."
    exit 1
    ;;
esac

vfile="$(grep -E '^version-file:' "$SEAM" | head -1 | sed 's/^version-file:[[:space:]]*//')"
clog="$(grep -E '^changelog:' "$SEAM" | head -1 | sed 's/^changelog:[[:space:]]*//')"
if [ -z "$vfile" ] || [ -z "$clog" ]; then
  echo "::error::release-gate: $SEAM is 'configured' but its version-file/changelog entries are missing — name both, or declare 'mode: off <reason>'."
  exit 1
fi

SEMVER='^[0-9]+\.[0-9]+\.[0-9]+$'

head_v="$(git show "$HEAD:$vfile" 2>/dev/null | head -1 | tr -d '[:space:]')"
if [ -z "$head_v" ]; then
  echo "::error::release-gate: $vfile is missing or empty at the PR head — the seam names it as this project's version file; restore it, or re-point $SEAM."
  exit 1
fi
if ! printf '%s' "$head_v" | grep -qE "$SEMVER"; then
  echo "::error::release-gate: head version '$head_v' is not MAJOR.MINOR.PATCH."
  exit 1
fi

base_v="$(git show "$BASE:$vfile" 2>/dev/null | head -1 | tr -d '[:space:]')"
if [ -z "$base_v" ]; then
  echo "::warning::release-gate: $vfile does not exist at the PR base — first versioned release; accepting $head_v as the starting version."
elif ! printf '%s' "$base_v" | grep -qE "$SEMVER"; then
  echo "::warning::release-gate: base version '$base_v' is not MAJOR.MINOR.PATCH — a state this PR cannot repair; checking the head side only."
else
  if [ "$base_v" = "$head_v" ]; then
    echo "::error::release-gate: version not bumped ($vfile reads '$head_v' on both sides). A promotion carries its release caboose — run /promote; the bump class is the operator's decision. See docs/process/release-checklist.md."
    exit 1
  fi
  IFS=. read -r bM bm bp <<<"$base_v"
  IFS=. read -r hM hm hp <<<"$head_v"
  legal=1
  [ "$hM" = "$bM" ] && [ "$hm" = "$bm" ] && [ "$hp" = "$((bp + 1))" ] && legal=0
  [ "$hM" = "$bM" ] && [ "$hm" = "$((bm + 1))" ] && [ "$hp" = "0" ] && legal=0
  [ "$hM" = "$((bM + 1))" ] && [ "$hm" = "0" ] && [ "$hp" = "0" ] && legal=0
  if [ "$legal" -ne 0 ]; then
    echo "::error::release-gate: '$base_v' → '$head_v' is not a single semver step (patch / minor / major). Pick exactly one bump class — the operator's decision at the /promote STOP."
    exit 1
  fi
fi

if ! git show "$HEAD:$clog" 2>/dev/null | grep -qF "$head_v"; then
  echo "::error::release-gate: $clog at the PR head has no entry mentioning $head_v — the caboose writes the release log, derived from the promoted delta (see /promote)."
  exit 1
fi

echo "release-gate: OK (${base_v:-<none>} → $head_v, entry present in $clog)."
exit 0
