<!-- Note issue body skeleton — use with:
gh issue create --label note --title "note: <finding>" --body-file <this file>
A note is NEVER a sub-issue (it would leave the epic perpetually unfinished).
Cross-link it to the epic AND add a one-line entry to the epic's
"Related notes & findings" section. Triage at epic closeout. -->

A <design finding / observation / run finding> from <#issue / run / session>
(Epic #NN). **Not a build task** — filing per the `note` convention.

## The finding

<What was observed, where (run/commit/doc), and the evidence. If a number is
involved, add a caveat section if it shouldn't be over-read.>

## Why it matters later

<What this might change — a D-xxx? a Q##? scope? List the options; note that
none is decided here.>

## Triage

Triage when <the successor epic / a named trigger> arrives.
