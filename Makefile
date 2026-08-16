# One canonical verification entrypoint — "done" means `make verify` passes
# (see CLAUDE.md → Definition of done). Modules extend this target as they
# land: the python-package module adds lint + tests, etc.
# Scaffolding is code (D-005): the hook regression suites and the bash -n
# syntax pin run here — and therefore in CI on every PR (docs.yml) — so a
# broken guard fails the gate instead of waiting for a manual invocation.
# check_ci_gates.py is the meta-gate: it pins the CI gate configuration
# itself so a gate can't be silently unwired (D-004), and pins scaffolding
# wiring so a new deny-hook with no suite (or a checker with no wired
# --self-test) fails the gate instead of passing unnoticed (D-005).
# check_docs_truth.py fails on docs claims that are no longer true (dead
# path citations, closed issues cited as open, dead flag/env citations via
# the self-arming seam in .claude/docs-truth.txt, cross-artifact
# registry consistency: status drift, page/row/nav bijection, duplicate
# D-### IDs, dead ID cross-refs, in-progress epic pages whose epic
# issue is closed — a wrongly-closed epic surfaces here — and
# built-listed sub-issues still open, the under-closing mirror) —
# ADR-0004.
# Each checker's --self-test
# runs first so the checker itself stays pinned both ways (D-005).
.PHONY: verify
verify:
	bash scripts/test_guard_git.sh
	bash scripts/test_guard_adr.sh
	bash scripts/test_branch_flow_guard.sh
	bash scripts/test_adr_unlock_decision.sh
	bash scripts/test_issue_link_guard.sh
	bash scripts/test_release_gate.sh
	bash scripts/test_guard_issue_close.sh
	bash scripts/test_issue_close_guard.sh
	bash scripts/test_guard_command_policy.sh
	bash scripts/test_stale_working_docs.sh
	@# Shared guard-parser pin: 3-way byte-identity of the parser region
	@# embedded in the three guard hooks, python-syntax compile of each
	@# hook's heredoc (bash -n cannot see python), and parser unit tests.
	python3 scripts/test_guardlib.py
	@# Blueprint-only gate: deleted at bootstrap, so no-op in seeded projects.
	@# Only the hermetic --self-test runs here — the live gate always trips in
	@# the blueprint itself (tokens present by design), so it belongs in CI's
	@# bootstrap lane, not the seed's verify (D-005).
	if [ -f scripts/check_bootstrap_complete.sh ]; then bash scripts/check_bootstrap_complete.sh --self-test; fi
	for f in scripts/*.sh .claude/hooks/*.sh; do bash -n "$$f" || exit 1; done
	mkdocs build --strict
	python3 scripts/check_ci_gates.py --self-test
	python3 scripts/check_ci_gates.py
	python3 scripts/check_docs_truth.py --self-test
	python3 scripts/check_docs_truth.py
