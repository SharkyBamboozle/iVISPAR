# scripts/

Repo tooling and one-off utilities — bootstrap and maintenance scripts that
operate **on** the repo, not code that ships **in** the product. Anything with
lasting product value belongs in the installable package (python-package
module), not here.

| Script | Purpose |
|---|---|
| `github_setup.sh` | Idempotent GitHub setup — everything a template can't carry (labels, `development` branch + default, protection, Pages + environment policy, merge settings). `--profile data` for a paired data repo. |
| `bootstrap_labels.sh` | Sync the label taxonomy from `.github/labels.yml` (create-or-update; safe to re-run). |
| `check_bootstrap_complete.sh` | The objective bootstrap-finished gate: no unfilled placeholder tokens, no unresolved judgment blocks (see `blueprint/TOKENS.md`). Deleted at bootstrap — drop this row then. |
| `check_ci_gates.py` | The CI meta-gate: pins the gate wiring so a gate can't be silently unwired (no `continue-on-error`; must fire on PRs into the integration branch) and the scaffolding wiring (every deny-hook has a wired suite, every checker a wired `--self-test`). Runs in `make verify`; ships with `--self-test`. |
| `check_docs_truth.py` | The docs truth-checker: dead path citations, closed-issues-cited-as-open, flag/env citations, and cross-artifact registry consistency. Runs in `make verify`; ships with `--self-test`. |
| `branch_flow_decision.sh` | The branch-flow-guard decision logic (extracted from `branch-flow-guard.yml` so it is hermetically testable): allow a same-repo `development`→`main` promotion, block a fork branch named `development`, fail **closed** on an inconclusive `gh` result. Called by the workflow. |
| `adr_unlock_decision.sh` | The ADR-lock decision logic (extracted from `adr-gates.yml` so it is hermetically testable): every path to a `✅ Decided` page — create-as-Decided, promote, edit, delete, rename — must carry an `Unlock-ADR:` trailer. Called by the workflow. |
| `test_guard_git.sh` | Regression suite for the `guard-git.sh` hook — asserts both the blocked and the still-allowed cases. Runs in `make verify`. |
| `test_guard_adr.sh` | Regression suite for the `guard-adr.sh` hook — asserts both the blocked and the still-allowed cases. Runs in `make verify`. |
| `test_guard_command_policy.sh` | Regression suite for the `.claude/hooks/guard-command-policy.py` approve-hook — python syntax pin (`bash -n` can't see a `.py` hook), the embedded self-test, the newline defect table and its still-approved partners through the hook's real JSON-on-stdin channel, the deny-surface non-contention check (nothing the deny layers block is ever auto-approved), and the never-blocks property (exit 0 on every input). Runs in `make verify`. |
| `test_guardlib.py` | Pin + unit suite for the shared guard command-parser embedded (deliberately triplicated) in the three guard hooks: 3-way byte-identity of the marked region, python-syntax compile of each hook's heredoc (`bash -n` can't see python), and parser unit tests including the fail-open contract. Runs in `make verify`. |
| `verify_guards_windows.sh` | Manual Windows verification helper for the three guard hooks (no Windows CI runner exists). Runs the guard suites, prints the interpreter/bash fingerprint, asserts a forbidden command still BLOCKS through the hooks' real JSON-on-stdin channel, and probes the MSYS-path vs `cygpath` gap **via stdin only** — never a bare path argument, which MSYS would auto-translate into a false green. Not wired into `make verify` (platform-specific manual gate); runs on Linux too as a smoke test. |
| `test_branch_flow_guard.sh` | Regression suite for `branch_flow_decision.sh` (mocked `gh`, both-ways). Runs in `make verify`. |
| `test_adr_unlock_decision.sh` | Regression suite for `adr_unlock_decision.sh` (fixture git repos, both-ways across all five Decided paths). Runs in `make verify`. |
| `test_stale_working_docs.sh` | Regression suite for the `stale-working-docs.sh` Stop nudge — the fired message carries the closed action set (above all the never-a-git-action sentence), live tasks (recent writes) stay unflagged, README-only and missing dirs stay silent, every path exits 0 (print-only pin). Runs in `make verify`, wired by hand: the CI meta-gate binds suites only for PreToolUse hooks, so the Makefile line is this suite's only wiring pin. |
