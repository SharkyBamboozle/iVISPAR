#!/usr/bin/env bash
# Decision logic for the adr-gates 'decided-adr-unlock' job (D-001/D-004).
#
# Every PATH to a ✅ Decided ADR page must carry an
# 'Unlock-ADR: <adr-id> — <reason>' trailer somewhere in the PR's commits:
#   - creating a page already ✅ Decided  (the new-file gap)
#   - promoting a page 🟡 Proposed → ✅ Decided
#   - a maintenance edit of a ✅ page      (typo, annotation, supersession mark)
#   - deleting or renaming a ✅ page
# This mirrors the edit-time lock (.claude/hooks/guard-adr.sh) at the CI layer,
# which binds every client — hooks or not. Freely allowed WITHOUT a trailer:
# creating or editing a 🟡 Proposed ADR — Decided is the human-gated state, so
# initial drafting is unblocked and only reaching/leaving Decided is challenged.
#
# Reads BASE and HEAD (git refs) from the environment; runs inside a checked-out
# repo (the workflow) or a fixture repo (scripts/test_adr_unlock_decision.sh).
# Exit 0 = allowed, 1 = a Decided-ADR path lacks its Unlock-ADR trailer.
# Logic lives here (not inline YAML) so it is hermetically testable (D-005),
# the same split as scripts/branch_flow_decision.sh.
set -uo pipefail

: "${BASE:?BASE ref required}"
: "${HEAD:?HEAD ref required}"

# 0 if <ref>:<path> exists and its Status line is ✅ Decided. Anchored to the
# '- **Status:** ✅' line so a status-legend comment elsewhere can't false-fire.
is_decided() { # is_decided <ref> <path>
  git show "$1:$2" 2>/dev/null \
    | grep -qE '^[[:space:]]*-[[:space:]]*\*\*Status:\*\*[[:space:]]*✅'
}

# --no-renames: a rename surfaces as delete(old)+add(new); judging each side on
# its own base/head status catches a renamed Decided page from both directions.
changed=$(git diff --no-renames --name-only "$BASE" "$HEAD" \
  | grep -E '^docs/decisions/adr-.*\.md$' || true)
if [ -z "$changed" ]; then
  echo "No ADR pages changed."
  exit 0
fi

log=$(git log --format=%B "$BASE".."$HEAD")
fail=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  # Locked iff the page is Decided at BASE (edit/delete/rename of a Decided
  # page) OR at HEAD (created-as-Decided / promoted to Decided).
  if is_decided "$BASE" "$f" || is_decided "$HEAD" "$f"; then
    short=$(basename "$f" .md | grep -oE '^adr-[0-9]+')
    if ! printf '%s\n' "$log" \
         | grep -qE "^Unlock-ADR:[[:space:]]*$short([^0-9]|$)"; then
      echo "::error file=$f::Decided ADR '$short' reached or left the Decided state without an 'Unlock-ADR: $short — <reason>' trailer in any commit of this PR. Run /unlock-adr $short and add the trailer — or, for a changed decision, supersede via a new ADR instead of editing."
      fail=1
    fi
  fi
done <<<"$changed"

if [ "$fail" -eq 0 ]; then
  echo "Decided-ADR paths properly unlocked."
fi
exit "$fail"
