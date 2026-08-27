#!/usr/bin/env bash
# Decision logic for the issue-link guard (.github/workflows/issue-link-guard.yml).
# A GitHub closing keyword (close/closes/closed/fix/fixes/fixed/resolve/
# resolves/resolved) auto-closes its target when the PR merges into the
# default branch — and GitHub ignores qualifiers: "Closes #7 (partial)" still
# closes #7. The rule (docs/process/opening-a-pr.md): a closing keyword
# may only target an issue the PR fully completes. This script blocks any closing reference — in the PR body, PR
# title, a commit message, or GitHub's own resolved link set (which
# includes sidebar-linked issues) — whose target is not completion-ready:
#   epic-labeled issue  -> blocked while it has open sub-issues (only its
#                          closeout PR, every sub-issue closed, passes);
#   note-labeled issue  -> exempt: a note never reaches "done" — its
#                          completion semantics are the triage verbs;
#   any other issue     -> blocked while its body carries unchecked
#                          task-list deliverable boxes (- [ ] / * [ ]) —
#                          tick what is done, re-home what is deferred, or
#                          declare the exception — AND blocked when it
#                          carries no checklist at all: a box-less
#                          close is a faith-based close; state the
#                          deliverables (retroactively is sanctioned: one
#                          ticked box per delivered artifact) or declare
#                          the exception. Fenced code blocks are stripped
#                          before counting — samples never count.
#
# Extracted into a script so the decision is unit-testable with a mocked `gh`
# (scripts/test_issue_link_guard.sh) — the workflow just supplies the inputs.
#
# Exit 0 = allow · exit 1 = block.
# Env: REPO (owner/name), PR_NUMBER, PR_TITLE, PR_BODY, COMMITS (concatenated
#      commit messages over the PR range), GH_TOKEN (for `gh api`).
#
# Inconclusive `gh` outcomes fail CLOSED (house rule — same as the
# branch-flow guard: a transient error must not silently drop the policy).
# The one exception: a definitive 404 on a referenced issue number, which
# nothing can close, is allowed through with a note.
#
# Override — evaluated SECOND, announced loudly: a
# `Skip-Issue-Link-Guard: <reason>` commit trailer (D-004 — exceptions are
# declared, never silent). The merits path always runs first; the trailer is
# consulted only when merits fail (or cannot be evaluated), so a re-run of a
# PR whose targets have since become completion-ready passes on merits and a
# stale waiver never masks the real rule. A waiver-pass emits a ::warning::
# annotation quoting EVERY trailer in range — an exception must not be
# visually identical to a genuine pass, and the guard cannot match a
# trailer to a finding, so it never presents one trailer as THE reason: a
# promotion PR's range is everything since the last release and can hold
# several trailers, some arguing findings that no longer exist; quoting
# only the newest announced a false reason.
set -uo pipefail

REPO="${REPO:-}"
PR_NUMBER="${PR_NUMBER:-}"
PR_TITLE="${PR_TITLE:-}"
PR_BODY="${PR_BODY:-}"
COMMITS="${COMMITS:-}"

# Waiver trailers are parsed up front but consulted only at the exit
# points below — merits first, waiver second. Same per-trailer acceptance
# as the old presence grep: the reason must be non-empty. ALL reasons in
# range are kept, one per line, in `git log` order (newest commit first) —
# the guard cannot know which trailer argues which finding, so it
# announces every one.
WAIVER_REASONS="$(printf '%s\n' "$COMMITS" \
  | sed -n 's/^Skip-Issue-Link-Guard:[[:space:]]*\([^[:space:]].*\)$/\1/p')"
WAIVER_COUNT="$(printf '%s\n' "$WAIVER_REASONS" | grep -c '.')"

# The reasons as one ::warning::-embeddable block. An annotation is a
# single line and GitHub shows it in the checks summary, where a reviewer
# may never open the job log — so the reasons travel inside the annotation,
# newlines escaped as %0A (rendered as line breaks).
waiver_block() {
  printf '%s\n' "$WAIVER_REASONS" \
    | sed 's/^/%0A  - Skip-Issue-Link-Guard: /' \
    | tr -d '\n'
}

# Blocking findings are collected during the merits evaluation and flushed
# at the exits — as ::error:: when the run blocks, as plain "waived:" lines
# when a trailer overrides them: an annotation's severity must match the
# run's outcome.
problems=()

# Single allow exit for a run the real rule permits. A present-but-unneeded
# trailer is noted, never consulted — the job log stays honest about WHICH
# rule passed the PR, and a stale waiver ages out visibly.
pass_on_merits() {
  if [ "$WAIVER_COUNT" -eq 1 ]; then
    echo "note: a Skip-Issue-Link-Guard trailer is present but was not consulted — the merits path passed on its own."
  elif [ "$WAIVER_COUNT" -gt 1 ]; then
    echo "note: $WAIVER_COUNT Skip-Issue-Link-Guard trailers are present but were not consulted — the merits path passed on its own."
  fi
  echo "issue-link-guard: passed on merits."
  exit 0
}

# Single exit for a `gh` failure: the merits path could not be evaluated.
# Without a trailer this fails CLOSED (house rule); with one, the declared
# exception stands in for the unevaluable merits — loudly.
# $1 = what failed, $2 = captured gh output.
infra_fail_or_waive() {
  # $2 is raw gh output and routinely multi-line; a raw newline would end
  # an annotation at that point and push everything after it — the waiver
  # reasons, or the fail-closed details tail — out into plain log lines,
  # so its newlines are escaped like the reasons' (%0A) on both exits.
  local details="${2//$'\n'/%0A}"
  if [ -n "$WAIVER_REASONS" ]; then
    for p in ${problems[@]+"${problems[@]}"}; do echo "waived: $p"; done
    echo "::warning::issue-link-guard: passed on WAIVER, not on merits — $1, so the merits path could not be fully evaluated. Details: ${details}. ${WAIVER_COUNT} declared exception(s) in range stand in — the guard does not match a trailer to a finding, so read them all:$(waiver_block)"
    exit 0
  fi
  for p in ${problems[@]+"${problems[@]}"}; do echo "::error::$p"; done
  echo "::error::issue-link-guard: $1 (transient / auth / network). Failing CLOSED to avoid a silent policy bypass. Details: ${details}"
  exit 1
}

# The nine closing keywords. (^|[^[:alnum:]_]) instead of \b so the pattern
# is portable ERE ("unfixed #7" must not match).
KW='(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)'
TEXT="$PR_BODY
$PR_TITLE
$COMMITS"
# Only '.' in an owner/name is regex-special (allowed chars: [A-Za-z0-9_.-]).
REPO_RE=$(printf '%s' "$REPO" | sed 's/\./\\./g')

# Closing references in the supplied text: same-repo shorthand (#N), the
# explicit owner/repo#N form, and the full-URL form — each only when it
# targets THIS repo (cross-repo closes are another repo's policy).
refs=$(
  {
    printf '%s' "$TEXT" | grep -oiE "(^|[^[:alnum:]_])${KW}:?[[:space:]]*#[0-9]+" | sed 's/.*#//'
    printf '%s' "$TEXT" | grep -oiE "(^|[^[:alnum:]_])${KW}:?[[:space:]]*${REPO_RE}#[0-9]+" | sed 's/.*#//'
    printf '%s' "$TEXT" | grep -oiE "(^|[^[:alnum:]_])${KW}:?[[:space:]]*https://github\.com/${REPO_RE}/issues/[0-9]+" | sed 's|.*/||'
  } | sort -un
)

# GitHub's own resolved link set for this PR: body keywords as GitHub parsed
# them, plus manually-linked (Development sidebar) issues as of this run.
linked=$(gh api graphql \
  -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){closingIssuesReferences(first:100){nodes{number}}}}}' \
  -f o="${REPO%%/*}" -f r="${REPO#*/}" -F n="${PR_NUMBER:-0}" \
  --jq '.data.repository.pullRequest.closingIssuesReferences.nodes[].number' 2>&1)
rc=$?
if [ "$rc" -ne 0 ]; then
  infra_fail_or_waive "could not list this PR's closing references — 'gh api graphql' failed" "$linked"
fi

candidates=$(printf '%s\n%s\n' "$refs" "$linked" | grep -E '^[0-9]+$' | sort -un)
if [ -z "$candidates" ]; then
  echo "OK: no closing references to this repo's issues."
  pass_on_merits
fi

for num in $candidates; do
  # One line per issue: "<epic|note|-> <total> <completed>" (label class +
  # sub-issue counters; epic wins over note if ever both).
  info=$(gh api "repos/$REPO/issues/$num" \
    --jq '([.labels[].name] | if index("epic") then "epic" elif index("note") then "note" else "-" end) + " " + ((.sub_issues_summary.total // 0) | tostring) + " " + ((.sub_issues_summary.completed // 0) | tostring)' 2>&1)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    if printf '%s' "$info" | grep -qiE 'HTTP 404|not found'; then
      echo "note: closing reference to #$num, which does not exist — nothing to close, not blocking."
      continue
    fi
    infra_fail_or_waive "could not read issue #$num — 'gh api' failed" "$info"
  fi
  read -r flag total completed <<<"$info"
  if [ "$flag" = "epic" ] && [ "${completed:-0}" -lt "${total:-0}" ]; then
    problems+=("This PR would close epic #$num, which has open sub-issues ($completed/$total complete). A closing keyword targets only an issue the PR fully completes; an epic closes only via its closeout PR. Reference progress as 'Closes — · Part of #$num (epic)' — or declare a deliberate exception with a 'Skip-Issue-Link-Guard: <reason>' commit trailer. See docs/process/opening-a-pr.md.")
    continue
  fi
  if [ "$flag" = "epic" ]; then
    echo "OK: closing reference to epic #$num — all $total sub-issues complete (closeout)."
    continue
  fi
  if [ "$flag" = "note" ]; then
    echo "OK: closing reference to note #$num — notes are checklist-exempt; triage verbs are their completion semantics."
    continue
  fi
  # Non-epic, non-note: count deliverable boxes LINE-ANCHORED, in the
  # script (not jq), so the counting seam is covered by the mocked suite.
  # GitHub renders a task item only at a list-item line start — prose
  # QUOTING the syntax ("… task-list items (\`- [ ]\`) …") must not count;
  # the gate's first live run false-positived on exactly that (an issue
  # whose own spec body quoted the syntax). Fenced code blocks are stripped
  # first — a fenced SAMPLE of checkbox syntax is not a checkbox (a
  # promotion PR restating 'Closes #NN' would otherwise trip on that
  # issue's fenced template snippet).
  body=$(gh api "repos/$REPO/issues/$num" --jq '.body // ""' 2>&1)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    infra_fail_or_waive "could not read issue #$num's body — 'gh api' failed" "$body"
  fi
  stripped=$(printf '%s\n' "$body" | awk '/^[[:space:]]*```/{f=!f; next} !f')
  unchecked=$(printf '%s\n' "$stripped" | grep -cE '^[[:space:]]*[-*][[:space:]]+\[ \]')
  checked=$(printf '%s\n' "$stripped" | grep -cE '^[[:space:]]*[-*][[:space:]]+\[[xX]\]')
  if [ "$unchecked" -gt 0 ]; then
    problems+=("This PR would close #$num, which still has $unchecked unchecked deliverable box(es). Close only what is complete: tick the boxes that are done (ticking is the completing session's job — do it at PR-open), re-home what is deferred (and say where), or declare the exception with a 'Skip-Issue-Link-Guard: <reason>' commit trailer. See docs/process/closing-issues.md.")
  elif [ "$checked" -eq 0 ]; then
    problems+=("This PR would close #$num, which carries no deliverable checklist — a box-less close is a faith-based close. State the issue's deliverables as task-list boxes (retroactively is sanctioned: one ticked box per delivered artifact is a completion record, not busywork), or declare the exception with a 'Skip-Issue-Link-Guard: <reason, e.g. trivial one-line fix>' commit trailer. See docs/process/closing-issues.md.")
  else
    echo "OK: closing reference to #$num — deliverables $checked/$checked ticked."
  fi
done

if [ "${#problems[@]}" -eq 0 ]; then
  pass_on_merits
fi

# The merits path failed — only NOW is the waiver consulted, so the
# trailer can never mask a rule that would have passed or hide WHY it did
# not.
if [ -n "$WAIVER_REASONS" ]; then
  for p in "${problems[@]}"; do echo "waived: $p"; done
  echo "::warning::issue-link-guard: passed on WAIVER, not on merits — ${#problems[@]} blocking finding(s) waived (listed in the job log). ${WAIVER_COUNT} declared exception(s) in range. The guard does not match a trailer to a finding, so read them all:$(waiver_block)"
  exit 0
fi
for p in "${problems[@]}"; do echo "::error::$p"; done
exit 1
