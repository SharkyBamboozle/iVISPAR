#!/usr/bin/env bash
# Regression cases for scripts/issue_link_decision.sh (the issue-link guard
# logic). Runs inside `make verify`, so it binds in CI (D-004). Hermetic:
# a mocked `gh` on PATH serves canned issue records and closing-reference
# lists — no network. Asserts BOTH sides (block and allow) so a fix can't
# silently over/under-tighten.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/issue_link_decision.sh"
fails=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Mock gh, dispatching on the call shape:
#   api graphql …                     -> $MOCK_LINKED numbers (one per line), rc $MOCK_LINKED_RC
#   api repos/*/issues/N (counters)   -> $MOCK_ISSUE_<N> ("<epic|-> <total> <completed>"),
#                                        rc $MOCK_ISSUE_<N>_RC, stderr $MOCK_ISSUE_<N>_ERR
#   api repos/*/issues/N --jq .body   -> $MOCK_BODY_<N> (raw multi-line body)
cat >"$TMP/gh" <<'MOCK'
#!/usr/bin/env bash
args="$*"
case "$args" in
  *graphql*)
    if [ "${MOCK_LINKED_RC:-0}" -ne 0 ]; then
      printf '%s\n' "${MOCK_LINKED_ERR:-gh: HTTP 500 backend error}" >&2
      exit "${MOCK_LINKED_RC}"
    fi
    for n in ${MOCK_LINKED:-}; do printf '%s\n' "$n"; done
    exit 0 ;;
  *issues/*)
    num=$(printf '%s' "$args" | sed -n 's|.*issues/\([0-9][0-9]*\).*|\1|p')
    if printf '%s' "$args" | grep -q 'sub_issues_summary'; then
      rc_var="MOCK_ISSUE_${num}_RC"; out_var="MOCK_ISSUE_${num}"; err_var="MOCK_ISSUE_${num}_ERR"
      if [ "${!rc_var:-0}" -ne 0 ]; then
        printf '%s\n' "${!err_var:-gh: Not Found (HTTP 404)}" >&2
        exit "${!rc_var}"
      fi
      out="${!out_var:-}"; [ -z "$out" ] && out="- 0 0"
      printf '%s\n' "$out"
    else
      bvar="MOCK_BODY_${num}"
      printf '%s\n' "${!bvar:-}"
    fi
    exit 0 ;;
esac
exit 0
MOCK
chmod +x "$TMP/gh"

# Standing fixtures: #61 an epic mid-flight, #45 an epic fully complete
# (with leftover unchecked body boxes — the epic path judges sub-issues,
# never boxes), #65 an ordinary issue with all boxes ticked, #50 an epic
# with no sub-issues yet, #70 an ordinary issue with unchecked deliverables
# (one indented/nested), #72 an ordinary issue whose body merely QUOTES the
# checkbox syntax mid-line — the false-positive regression shape.
export MOCK_ISSUE_61="epic 16 4"
export MOCK_ISSUE_45="epic 16 16"
export MOCK_ISSUE_65="- 0 0"
export MOCK_ISSUE_50="epic 0 0"
export MOCK_ISSUE_70="- 0 0"
export MOCK_ISSUE_72="- 0 0"
export MOCK_BODY_45="## Exit criteria
- [ ] leftover box the epic path must ignore"
export MOCK_BODY_65="## Deliverables
- [x] code landed
* [x] readout posted"
export MOCK_BODY_70="## Deliverables
- [x] code landed
- [ ] readout pending
  - [ ] nested follow-through"
export MOCK_BODY_72="Switch plain bullets to task-list items (\`- [ ]\`) per the template.
- [x] shipped"
# #73 box-less prose, #74 a note (checklist-exempt), #75 fenced-sample-only
# (a sample is not a checkbox), #76 fenced sample + one real ticked box.
export MOCK_ISSUE_73="- 0 0"
export MOCK_BODY_73="Prose only — deliverables described in sentences, no checklist anywhere."
export MOCK_ISSUE_74="note 0 0"
export MOCK_ISSUE_75="- 0 0"
export MOCK_BODY_75='Template snippet for illustration:

```
- [ ] sample box inside a fence
- [ ] another sample line
```
'
export MOCK_ISSUE_76="- 0 0"
export MOCK_BODY_76='Fenced sample:

```
- [ ] sample box inside a fence
```

- [x] the real deliverable, ticked'

check() { # check <want_rc> <label> — uses the currently-exported case vars
  PATH="$TMP:$PATH" REPO="org/repo" PR_NUMBER=1 \
  PR_BODY="${PR_BODY:-}" PR_TITLE="${PR_TITLE:-}" COMMITS="${COMMITS:-}" \
    bash "$SCRIPT" >/dev/null 2>&1
  local rc=$?
  if [ "$rc" -eq "$1" ]; then echo "PASS (rc=$rc): $2"
  else echo "FAIL (rc=$rc, want $1): $2"; fails=$((fails + 1)); fi
  unset PR_BODY PR_TITLE COMMITS \
    MOCK_LINKED MOCK_LINKED_RC MOCK_LINKED_ERR \
    MOCK_ISSUE_999_RC MOCK_ISSUE_61_RC MOCK_ISSUE_61_ERR
}

# check_out <want_rc> <must_match_ERE> <must_NOT_match_ERE|-> <label> —
# like check(), but also asserts the combined output, pinning WHICH path
# decided the run: "passed on merits" vs the ::warning:: waiver
# annunciation must be distinguishable in the log, not just the exit code.
check_out() {
  local out rc ok=1 why=""
  out=$(PATH="$TMP:$PATH" REPO="org/repo" PR_NUMBER=1 \
    PR_BODY="${PR_BODY:-}" PR_TITLE="${PR_TITLE:-}" COMMITS="${COMMITS:-}" \
    bash "$SCRIPT" 2>&1)
  rc=$?
  [ "$rc" -eq "$1" ] || { ok=0; why="rc=$rc want $1"; }
  printf '%s\n' "$out" | grep -qE "$2" || { ok=0; why="$why; missing /$2/"; }
  if [ "$3" != "-" ] && printf '%s\n' "$out" | grep -qE "$3"; then
    ok=0; why="$why; forbidden /$3/ present"
  fi
  if [ "$ok" -eq 1 ]; then echo "PASS (rc=$rc): $4"
  else echo "FAIL ($why): $4"; fails=$((fails + 1)); fi
  unset PR_BODY PR_TITLE COMMITS \
    MOCK_LINKED MOCK_LINKED_RC MOCK_LINKED_ERR \
    MOCK_ISSUE_999_RC MOCK_ISSUE_61_RC MOCK_ISSUE_61_ERR
}

export PR_BODY="Closes #61 (partial — the qualifier changes nothing) (epic: #61)"
check 1 "closing keyword on an epic with open sub-issues -> block"

export PR_BODY="Closes — · Part of #61 (epic)"
check 0 "progress idiom (no keyword-adjacent number) -> allow"

export PR_BODY="Closes #65 (epic: #61)"
check 0 "closes a non-epic sub-issue, epic referenced without keyword -> allow"

export PR_BODY="Closes #45 (epic) — closes atomically when this retrospective lands"
check 0 "closeout PR: epic with every sub-issue complete -> allow (body boxes ignored on the epic path)"

export PR_BODY="Closes #70"
check 1 "ordinary issue with unchecked deliverable boxes (incl. nested) -> block"

export PR_BODY="Closes #72"
check 0 "body only QUOTES checkbox syntax mid-line, boxes ticked -> allow (the false-positive regression)"

export PR_BODY="Closes #73"
check 1 "box-less ordinary issue -> block (faith-based close)"

export PR_BODY="Closes #73"
export COMMITS="fix: tiny thing

Skip-Issue-Link-Guard: trivial one-line fix, no deliverable structure"
check 0 "box-less issue + declared trailer -> allow (argued exception)"

export PR_BODY="Closes #74"
check 0 "note-labeled issue without boxes -> allow (notes are checklist-exempt)"

export PR_BODY="Closes #75"
check 1 "only fenced checkbox SAMPLES in the body -> block as box-less (fences stripped)"

export PR_BODY="Closes #76"
check 0 "fenced sample plus one real ticked box -> allow (fence stripped, presence satisfied)"

export PR_BODY="Closes #70 (deliverables re-homed)"
export COMMITS="fix: final slice

Skip-Issue-Link-Guard: remaining deliverables deferred to a follow-up issue"
check 0 "unchecked deliverables + declared trailer -> allow (argued exception)"

export PR_BODY="closes #50"
check 0 "epic with zero sub-issues -> allow (nothing open to orphan)"

export PR_TITLE="fix #61 for real this time"
check 1 "closing keyword in the PR title (squash-merge surface) -> block"

export COMMITS="feat: partial views

Fixes #61"
check 1 "closing keyword in a commit message -> block"

export PR_BODY="Resolves: org/repo#61"
check 1 "explicit same-repo owner/repo#N form -> block"

export PR_BODY="Fixes https://github.com/org/repo/issues/61"
check 1 "full-URL form -> block"

export PR_BODY="Closes other/repo#61 and https://github.com/other/repo/issues/61"
check 0 "cross-repo closing references -> allow (another repo's policy)"

export PR_BODY="Closes #61 (epic closeout follows atomically)"
export COMMITS="docs: closeout

Skip-Issue-Link-Guard: deliberate atomic closeout, sub-issues close in this train"
check 0 "Skip-Issue-Link-Guard trailer with reason -> allow (declared exception)"

export MOCK_LINKED="61"
check 1 "sidebar-linked epic with a clean body -> block (GraphQL set caught it)"

export MOCK_LINKED_RC=1
check 1 "closing-reference listing fails -> block (fail closed)"

export PR_BODY="Closes #999"
export MOCK_ISSUE_999_RC=1
check 0 "reference to a nonexistent issue (definitive 404) -> allow with note"

export PR_BODY="Closes #61"
export MOCK_ISSUE_61_RC=1 MOCK_ISSUE_61_ERR="gh: HTTP 500 backend error"
check 1 "issue lookup transient error -> block (fail closed)"

export PR_BODY="The unfixed #61 backlog and prefixes #61 must not trip the guard"
check 0 "keyword substring inside a word -> allow (no false positive)"

# ---- Merits-first, waiver-second, loud waiver — output-asserting
# cases pinning WHICH path passed, both ways: the order (a trailer never
# masks a merits pass), the annunciation (a waiver-pass is a ::warning::,
# never silent), and the unchanged deny side (no trailer still blocks).

export PR_BODY="Closes #65"
check_out 0 "passed on merits" "passed on WAIVER" \
  "all boxes ticked, no trailer -> logged as a merits pass"

export PR_BODY="Closes #65"
export COMMITS="chore: tidy

Skip-Issue-Link-Guard: stale reason from an earlier state of the issue"
check_out 0 "trailer is present but was not consulted" "passed on WAIVER" \
  "ticked boxes + leftover trailer -> merits pass, trailer NOT consulted (the order pin)"

export PR_BODY="Closes #70"
check_out 1 "::error::" "passed on" \
  "unchecked boxes, no trailer -> still blocks with ::error:: annotations"

export PR_BODY="Closes #70 (deliverables re-homed)"
export COMMITS="fix: final slice

Skip-Issue-Link-Guard: remaining deliverables deferred to a follow-up issue"
check_out 0 "::warning::.*passed on WAIVER.*deferred to a follow-up issue" "::error::" \
  "unchecked boxes + trailer -> loud ::warning:: quoting the reason, no ::error::"

export PR_BODY="Closes #70"
export COMMITS="fix: x

Skip-Issue-Link-Guard: argued reason"
check_out 0 "waived: This PR would close #70" "-" \
  "waiver-pass lists each waived finding in the job log"

export MOCK_LINKED_RC=1
export COMMITS="chore: y

Skip-Issue-Link-Guard: gate outage, change reviewed by owner"
check_out 0 "passed on WAIVER.*could not be fully evaluated" "::error::" \
  "gh failure + trailer -> declared exception stands in, announced"

# ---- Two-trailer regression: a promotion-shaped range holds every commit
# since the last release, so several trailers can be in range at once — some
# arguing findings that no longer exist. Selecting one and quoting it as THE
# declared exception announced a false reason. The guard cannot match a
# trailer to a finding, so a waiver-pass must carry EVERY reason inside the
# ::warning:: annotation itself (the checks summary shows the annotation,
# not the job log) and present none of them as the single reason — pinned
# both negatively (the retired single-reason phrasing is forbidden) and
# positively (the plural count framing must be on the annotation line).
# check_out matches line-wise, so "::warning::.*<reason>" proves the reason
# sits on the annotation line itself; each reason gets its own call, and
# BOTH reasons are asserted at BOTH waiver exits (asserting only one lets a
# single-reason fix from either end of the list pass). The infra cases use
# a MULTI-LINE gh error: a raw newline in the interpolated details would
# end the annotation early and evict every reason from it.
# The helper unsets the case env, hence the re-exports.

TWO_TRAILER_COMMITS="fix: newest slice

Skip-Issue-Link-Guard: newest trailer, argues an unrelated finding that is already fixed

fix: older slice

Skip-Issue-Link-Guard: older trailer, argues the real unchecked box"
MULTILINE_GH_ERR=$'gh: HTTP 502\nBad gateway from the GraphQL proxy'

export PR_BODY="Closes #70"
export COMMITS="$TWO_TRAILER_COMMITS"
check_out 0 "::warning::.*newest trailer, argues an unrelated finding" \
  "Declared exception \(commit trailer\):" \
  "two trailers, live finding -> annotation carries the newest reason; none presented as THE reason"

export PR_BODY="Closes #70"
export COMMITS="$TWO_TRAILER_COMMITS"
check_out 0 "::warning::.*2 declared exception\(s\) in range.*older trailer, argues the real unchecked box" "-" \
  "two trailers, live finding -> annotation carries the older reason too, under the plural count framing"

export MOCK_LINKED_RC=1
export MOCK_LINKED_ERR="$MULTILINE_GH_ERR"
export COMMITS="$TWO_TRAILER_COMMITS"
check_out 0 "::warning::.*could not be fully evaluated.*newest trailer, argues an unrelated finding" \
  "Declared exception \(commit trailer\):" \
  "gh failure (multi-line error) + two trailers -> infra annotation carries the newest reason"

export MOCK_LINKED_RC=1
export MOCK_LINKED_ERR="$MULTILINE_GH_ERR"
export COMMITS="$TWO_TRAILER_COMMITS"
check_out 0 "::warning::.*could not be fully evaluated.*older trailer, argues the real unchecked box" "-" \
  "gh failure (multi-line error) + two trailers -> infra annotation carries the older reason too"

# ---- The fail-closed exit keeps its details inside the annotation too:
# with NO trailer, a multi-line gh error must not end the ::error::
# annotation at its first newline — the checks summary would then show a
# truncated policy message, with the rest of the details as plain log
# lines (the same eviction the waiver exit guards against). The run still
# blocks; the exit code is unchanged.
export MOCK_LINKED_RC=1
export MOCK_LINKED_ERR="$MULTILINE_GH_ERR"
check_out 1 "::error::.*Failing CLOSED.*Bad gateway from the GraphQL proxy" "passed on" \
  "gh failure (multi-line error), no trailer -> fail-closed ::error:: carries the full details"

[ "$fails" -eq 0 ] && echo "all asserted cases pass" || echo "$fails case(s) FAILED"
exit "$fails"
