# Requirements

Hard constraints the project must satisfy, each with a stable `R##` ID — never
renumbered. Requirements are **derived from the [vision](vision.md)** and
serve as the evaluation criteria for architecture and tooling decisions
(see the [decisions registry](../decisions/index.md)); the traceability chain runs
vision → `P#` principles → `R##` requirements → analysis → `D-xxx` decisions.

When a requirement's premise weakens, **annotate it** with a note admonition
naming the gating question and session — the row stands as written.

| # | Requirement | Driven by |
|---|-------------|-----------|

<!-- BLUEPRINT: add rows as requirements are established. Example:

| R1 | Any published result is re-runnable from its own artifacts (config snapshot + seed) | Vision — credibility of results |
| R2 | The stack runs end-to-end on a single dev machine | P2 — keep the loop tight |

Annotation example, appended below the table when a premise weakens:

!!! note "R1's force is contingent on Q3 (Session 8)"
    If Q3 resolves to <X>, R1 relaxes to <Y>. The row stands as written until then.
-->
