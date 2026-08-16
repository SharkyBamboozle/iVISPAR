# <Report title> — <scope> (<YYYY-MM>)

<!-- A report is a SNAPSHOT IN TIME: it proposes and rates — it does not
decide. Load-bearing findings graduate into an ADR / epic / topic page / open
question; the report stays as the record of how the direction was found. Add
the report's row to docs/records/agent-research/index.md. -->

!!! note "Reconciliation (<date>)"
    <!-- If the codebase moved while the scan ran: what changed, which
    findings it affects, and how they were re-checked. Delete if N/A. -->

## How to read this

Each direction is rated **novelty 1–5** (<define the levels against prior
art: 1 = well-trodden … 5 = no published precedent found>) × **trajectory
S/M/L** (<define: how far the direction could carry — a spike, an epic, a
research program>).

## Start here — the map

| ★ | Direction | Novelty | Trajectory | One-line pitch |
|---|-----------|---------|------------|----------------|

## Directions

### <Direction name>

- **Question:** <the precise question this direction answers>
- **Why it's close:** <what in the codebase/state makes it reachable now>
- **Novelty & prior art:** <rating + the closest existing work>
- **Metric:** <how success would be measured>
- **The catch:** <the honest blocker, risk, or hidden cost>
- **Start with:** <the first concrete step — issue-sized>

## Cross-cutting findings

<Code/system observations surfaced along the way — file each as a `note`
issue and link it here; they are handed off, not owned by this report.>

## How this was produced

<Method, honestly: fan-out shape (how many agents, which lenses) →
literature/novelty pass → code-grounded feasibility → **adversarial
verification** (what got downgraded or cut, and why). Silent caps (top-N,
sampling) must be stated.>
