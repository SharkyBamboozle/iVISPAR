# Enforcement

The doctrine of how rules get their teeth — and how exceptions stay honest.
Decision home: [ADR-0004](../decisions/adr-0004-enforcement-doctrine.md).

## Enforcement layering (D-004)

**Every process rule names what enforces it — or is explicitly advisory.**
A rule added to `CLAUDE.md` or the process pages states the hook, CI gate,
test, or template section that catches violations; a rule nobody catches carries
the honest label *"advisory — deliberately unenforced because ⟨reason⟩"*.
*(This meta-rule is itself advisory — no gate can check whether a newly added
rule named its enforcer; PR review is the backstop, per D-004.)*
The enforcing artifact cites the rule back (the config-cites-decision
convention) — *advisory itself: the back-citation is a practiced
convention, not mechanically checked (D-004)*. The layers, from cheap to
binding:

1. **Prose** (`CLAUDE.md`, the process pages) states the rule and points at
   its enforcer.
2. **Local hooks** (`.claude/hooks/`) nudge or deny at edit time; every
   block message says what to do instead. Hooks are code — each ships a
   regression suite asserting both the deny and the still-allowed side,
   bound in CI via `make verify`; that rule's home is
   [Testing changes](testing-changes.md) (D-005).
3. **CI gates** (`.github/workflows/`) are the binding layer — they
   survive every client configuration. The meta-gate
   (`scripts/check_ci_gates.py`, part of `make verify`) pins the gate
   wiring itself: gates must fire on PRs into `development` and must not
   carry `continue-on-error`; it also pins the scaffolding wiring — the
   suite-per-hook rule in [Testing changes](testing-changes.md) (D-005).
4. **Exceptions are commit trailers** with a mandatory reason (see
   [Committing](committing.md)) — permanent, searchable, machine-checked;
   never PR labels or chat-only approvals.

House conventions that follow from the same principle: an allowed-to-fail
CI job ends with an explicit **failure beacon** (otherwise a green check
list hides a red lane); a file-targeted gate **fails loud when its target
file is missing** (a moved file may never turn a gate green); fake secrets
in tests follow the **canary naming convention** in `.gitleaks.toml`; and
**a dormant gate lane owns its activation condition** — it detects when it
becomes needed and fails until configured or explicitly declared off with
a reason, never relying on a human to remember the switch (the flag/env
citation lane of `scripts/check_docs_truth.py` and its seam
`.claude/docs-truth.txt` are the reference implementation).

Of these house conventions the dormant-gate-lane one names its reference
implementation above; the other three — the failure beacon, a file-targeted
gate failing loud when its target file is missing, and the canary naming
convention — are *advisory: convention-strength, with no meta-gate verifying
them (D-004)*.

## Failure directions (D-004)

**Every layer declares which way it fails.** The doctrine's home is
[ADR-0004](../decisions/adr-0004-enforcement-doctrine.md); this is the map:

1. **Deny-hooks** block proven intent. Broken machinery falls through — a
   broken guard must never brick every tool call — but an ambiguous
   *resolved* target blocks: uncertain evidence over-blocks safely.
2. **Approve-hooks** approve only what they can prove safe, defer the
   rest, and never block — a gap costs a prompt, never a mistake. They
   never contend with a deny-hook. Implemented by
   `.claude/hooks/guard-command-policy.py` (read-only Bash auto-approval;
   suite: `scripts/test_guard_command_policy.sh`).
3. **The permission prompt counts for nothing.** Sessions legitimately
   run prompt-free; hooks and server gates are the layers that fire
   everywhere.
4. **CI gates and branch protection fail closed and are the authority.**
   Server rules bind administrators (`enforce_admins: true` is the
   shipped default; the escape hatch is a temporary, visible settings
   edit — relax, act, restore). Every bypass class a client guard defers
   (nested interpreters, command wrappers, time-of-check races) names the
   server layer that catches it, and that claim is auditable (D-006) —
   re-audit it after material changes to the gates or the protection
   rules.

## Exception lists are ledgers (D-004)

Every allowlist / skip-list / tolerated-issues list any gate grows is a
first-class ledger:

1. **A reason per entry** — inline, next to the entry.
2. **A ceiling** — the list states its maximum size; exceeding it is a
   visible, deliberate diff, never silent accretion.
3. **Staleness fails loud** — an entry that is no longer needed fails the
   gate until removed; the frontier only moves one way.
4. **Itemized, never blanket** — entries name specific items, never a
   whole directory or category.

*These four are advisory construction discipline — the reference ledgers
(`KNOWN_EXEMPT` in `check_docs_truth.py`, the gitleaks/ci-gates allowlists)
follow them, but no meta-gate verifies that every ledger a gate grows obeys
all four; upheld by review, per D-004.*

Honesty- and security-critical findings (a real secret, a fabricated
claim) are **never ledgerable**. *(Advisory — no gate prevents an entry being
added to an allowlist; this is honesty discipline, per D-004.)*
