# Decisions Registry

This page is the canonical list of **Architecture Decision Records (ADRs)** for
{{PROJECT_NAME}}. Each row corresponds to a decision with a stable `D-xxx` ID,
its one-line statement, and its current status.

Every decision has its own ADR page (Context / Decision / Consequences /
Alternatives where meaningful / Reversibility / References), reached from
the **ADR** column. This registry
holds the canonical statement + status; the topic pages hold the reasoning —
each fact has exactly one canonical home
(see [Records & canon](../process/records-and-canon.md#canonicality-convention)).

When a decision's status changes, update its ADR **and** this registry row
together. New decision → next free ID, page from
`docs/.templates/adr-template.md`, row here, `nav` entry in `mkdocs.yml`.

**Status legend:** ✅ Decided · 🟡 Proposed · 🔴 Open · 🧊 Deferred/Superseded.

| ID | Decision | Status | ADR |
|----|----------|--------|-----|
| D-001 | Documentation & decision records: the docs site is the single source of truth (strict build as a merge gate); stable typed IDs with one status legend; decisions live as ADRs + registry rows, superseded never rewritten; every record type has exactly one home | ✅ | [ADR-0001](adr-0001-documentation-and-records.md) |
| D-002 | Work tracking: issues track work while docs hold truth — epics group native sub-issues (build tasks); findings are `note`-labelled issues, never sub-issues; notes are triaged at epic closeout; outcomes are written back as readouts | ✅ | [ADR-0002](adr-0002-work-tracking.md) |
| D-003 | Branch model: feature branch → PR into `development` (the integration branch and default) → promotion PR into `main`; no direct pushes to the long-lived branches, no self-merges, no force-pushes or history rewrites; the bootstrap birth commit is the single sanctioned direct push | ✅ | [ADR-0003](adr-0003-branch-model.md) |
| D-004 | Enforcement doctrine: every process rule names its enforcer or is explicitly advisory with a reason; enforcement layers prose → hooks → CI, and every layer declares which way it fails — deny-hooks fall through when broken, approve-hooks defer and never block, server gates fail closed, bind admins (bypass = a temporary visible settings edit), and catch the deferred client tail (each deferral names its catcher, auditably); exceptions are reasoned commit trailers; exception lists are four-rule ledgers; no silent gate lanes | ✅ | [ADR-0004](adr-0004-enforcement-doctrine.md) |
| D-005 | Testing policy: scaffolding ships binding hermetic self-tests inside `make verify`; test-writing is event-driven (bugfix → regression test named on the `Pin:` line), placement follows the project's layout; weakening a test takes a `Test-Adjusted:` trailer; no coverage thresholds | ✅ | [ADR-0005](adr-0005-testing-policy.md) |
| D-006 | Verification & honesty: `make verify` plus exercising the change is the bar for "done"; reporting is honest — a ticked box was actually run, numbers name source and `n=`, capability claims state where they exist; load-bearing claims get risk-proportional adversarial verification | ✅ | [ADR-0006](adr-0006-verification-and-honesty.md) |
| D-007 | Binary hygiene: posture finalized at bootstrap — default strict/split (no binaries in source history; durable artifacts live outside it; LFS only where declared), wired through the single `.claude/asset-dirs.txt` seam so hook and CI can never disagree | 🟡 | [ADR-0007](adr-0007-binary-hygiene.md) |
