#!/usr/bin/env bash
# Decision logic for the issue-close guard (.github/workflows/issue-close-guard.yml).
# CLAUDE.md hard rule: manual issue closes are operator-only. GitHub
# cannot express that as a role — closing needs only Triage, and coding
# agents act with the OPERATOR'S OWN identity via a GitHub App
# user-to-server token — so the one structural boundary GitHub records is
# used instead: an app-mediated action carries `performed_via_github_app`
# on the issue's `closed` event. This script reads the LAST `closed` event
# and rules:
#
#   closed by a commit / merged PR    -> stands (the PR path is the gated,
#                                        operator-merged close surface —
#                                        this also keeps merge-queue /
#                                        auto-merge projects safe);
#   performed via a GitHub App,       -> REVERTED (reopen + explanatory
#   or by a Bot actor                    comment) unless the app is in the
#                                        ALLOWED_APPS ledger below;
#   plain human close (no app)        -> stands (the operator's own click —
#                                        the only actor GitHub can
#                                        distinguish from an agent).
#
# FAILS OPEN on gh/API read errors: a wrongly-standing close is an
# inconvenience the /session-close reconciliation sweep catches, while
# auto-reopening legitimately-closed issues on transient errors would be
# worse. Every run logs the raw event line it judged, so live runs
# self-document the payloads (the authoring sandbox could not read live
# event data — a live-fire probe is owed after activation).
#
# Exit 0 = close stands (incl. fail-open) or revert succeeded ·
# exit 1 = a revert was required but could not be completed (loud red run).
# Env: REPO (owner/name), ISSUE_NUMBER, GH_TOKEN (for `gh api`).
# Unit-testable with a mocked `gh` (scripts/test_issue_close_guard.sh).
set -uo pipefail

REPO="${REPO:-}"
ISSUE_NUMBER="${ISSUE_NUMBER:-}"

# ALLOWED_APPS — a D-004 four-rule ledger of app slugs whose closes stand.
# Reason per entry, inline; ceiling: 4 (raising it is a deliberate,
# reviewed diff); itemized slugs, never patterns. Staleness has no
# mechanical signal here (an app that stops closing issues leaves no trace),
# so entries are re-justified whenever this script changes — noted per D-004.
#   github-actions : the repo's own workflow automation — anything it closes
#                    got its close logic through a merged, PR-gated workflow
#   github-mobile  : GitHub's first-party mobile client — an operator
#                    surface, not an agent (best-effort slug seed; if a
#                    revert comment ever names a different first-party slug,
#                    extend this ledger in a reviewed diff)
ALLOWED_APPS=("github-actions" "github-mobile")

# One line per `closed` event, oldest to newest, fields |-separated:
#   <actor login>|<actor type>|<commit|->|<app slug|->
# The compact projection happens in gh's --jq so the mocked suite can serve
# canned lines without a jq dependency.
events=$(gh api "repos/$REPO/issues/$ISSUE_NUMBER/events" --paginate --jq \
  '.[] | select(.event == "closed") | ((.actor.login // "?") + "|" + (.actor.type // "?") + "|" + (if .commit_id then "commit" else "-" end) + "|" + (.performed_via_github_app.slug // "-"))' 2>&1)
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "::warning::issue-close-guard: could not read #$ISSUE_NUMBER's events ('gh api' failed) — guard SKIPPED, close stands (fail-open by design; see script header). Details: $events"
  exit 0
fi

last=$(printf '%s\n' "$events" | grep -v '^[[:space:]]*$' | tail -n 1)
if [ -z "$last" ]; then
  echo "issue-close-guard: no closed event found on #$ISSUE_NUMBER — nothing to judge."
  exit 0
fi
IFS='|' read -r actor actor_type commit app <<<"$last"
echo "issue-close-guard: judging last close of #$ISSUE_NUMBER — actor=$actor type=$actor_type commit=$commit app=$app"

# 1) A commit-driven close (merged PR / commit keyword) is the sanctioned
#    PR path, whoever performed the merge.
if [ "$commit" = "commit" ]; then
  echo "issue-close-guard: closed via commit/merged PR — the gated close path. Close stands."
  exit 0
fi

# 2) App- or bot-mediated manual close -> revert, unless ledgered.
mediated=""
if [ "$app" != "-" ]; then mediated="app '$app'"; fi
case "$actor_type" in Bot|bot) mediated="${mediated:-bot actor '$actor'}";; esac
if [ -n "$mediated" ] && [ "$app" != "-" ]; then
  for allowed in "${ALLOWED_APPS[@]}"; do
    if [ "$app" = "$allowed" ]; then
      echo "issue-close-guard: close performed via ledgered app '$app' — close stands (see ALLOWED_APPS)."
      exit 0
    fi
  done
fi
if [ -z "$mediated" ]; then
  echo "issue-close-guard: plain human close by '$actor' — the operator's own action. Close stands."
  exit 0
fi

echo "issue-close-guard: manual close was $mediated — operator-only rule violated. Reverting."
comment="**Reopened by the issue-close-guard** (CLAUDE.md hard rule): this issue was closed manually via \`$mediated\`, and manual closes are **operator-only** — at the GitHub layer an agent acts with the operator's own identity, so the app marker on the close event is the only enforceable boundary.

Sanctioned close paths:
- the completing PR carries \`Closes #$ISSUE_NUMBER\` and the close fires when the **operator merges** it, or
- the completing session posts the readout comment, ticks the deliverable boxes, and **asks the operator** to close.

If this revert is wrong (a legitimate first-party surface), the app slug above is the ledger key — extend \`ALLOWED_APPS\` in \`scripts/issue_close_decision.sh\` in a reviewed diff."

out=$(gh api -X PATCH "repos/$REPO/issues/$ISSUE_NUMBER" -f state=open 2>&1)
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "::error::issue-close-guard: REVERT FAILED — could not reopen #$ISSUE_NUMBER ($out). The unauthorized close stands until the operator intervenes."
  exit 1
fi
out=$(gh api "repos/$REPO/issues/$ISSUE_NUMBER/comments" -f body="$comment" 2>&1)
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "::error::issue-close-guard: reopened #$ISSUE_NUMBER but could not post the explanatory comment ($out) — a silent revert is half a gate; treat this run as failed."
  exit 1
fi
echo "issue-close-guard: #$ISSUE_NUMBER reopened and annotated."
exit 0
