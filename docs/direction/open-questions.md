# Open questions

The registry of open design and engineering questions, each with a stable
`Q##` ID — never renumbered, **rows never deleted**.

**Lifecycle.** A question enters 🔴 with a summary and pointers to (a) the
topic page holding the analysis and (b) the roadmap spike or epic that will
answer it. When resolved, the row **stays**: status flips to ✅, the summary
gains `**Resolved (Session N):** <one-line outcome>`, and Pointers becomes
`Resolved by [ADR-00NN]` — the resolving ADR reciprocally records "resolves
Q##". Deferred questions go 🧊 with their **reactivation trigger inline**.
Questions may gate other questions or requirements; write that dependency into
the row.

**Status legend:** ✅ Resolved · 🟡 Tentatively answered · 🔴 Open ·
🧊 Deferred.

| ID | Status | Summary | Pointers |
|----|--------|---------|----------|

<!-- BLUEPRINT: add rows as questions arise. One example per lifecycle state:

| Q1 | 🔴 | Which storage backend fits the access pattern? | analysis: <topic page> · answered by Spike A |
| Q2 | ✅ | Is X fast enough at scale? **Resolved (Session 4):** yes, 10× headroom. | Resolved by [ADR-0003](../decisions/adr-0003-slug.md) |
| Q3 | 🧊 | Do we need multi-region? | Deferred — reactivate when the first non-EU user appears. |
-->
