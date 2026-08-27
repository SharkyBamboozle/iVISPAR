<!-- Epic issue body skeleton — use with:
gh issue create --label epic --title "<Epic name>" --body-file <this file>
Sub-issues are attached as GitHub NATIVE sub-issues, added incrementally.
Only build tasks become sub-issues; findings become `note` issues. -->

**<Bold one-sentence thesis of the epic.>** <Relation sentence, e.g. "Direct
successor to #NN — reuses X, changes exactly one thing: Y.">

🟡 **Proposed.** <Status sentence; add "No decisions are made here" if true.>

> **Living scope.** This body is reconciled with the sub-issues as they land.

> **Boundary with #NN.** <If a peer epic runs concurrently, draw the explicit
> line: which sub-issues belong to which side. Delete if N/A.>

## Why this epic exists

<The forcing problem, citing the triggering `note` issues by number.>

## Strands

<2–4 lettered workstreams, one line each.>

## Build order & dependencies

```
#A → #B → {#C, #D} → #E
```

<Phase/keystone annotations as needed.>

## Related notes & findings

Durable index: `label:note`. Notes are listed here as they are filed — one
line each, never as sub-issues:

- (none yet)

## Explicit non-goals (deferred)

<Named exclusions, each with a pointer to where the deferred item lives —
keeps the slice honest.>

## Home & relation

<Where the code lives (directory / governing D-xxx); predecessor / peer /
successor epics.>

---
*Sub-issues are added incrementally; findings tracked in Related notes above;
the story page lives under `docs/records/epics/`.*
