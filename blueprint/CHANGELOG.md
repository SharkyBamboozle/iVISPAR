# Blueprint changelog

What each blueprint version changed. Bumped by the harvest ritual
(`HARVEST.md`); each seeded project records the version it started from in
its init commit.

## v1.2.0 — A read-only approve-hook, admin-bound server rules, bypass-hardened guards

Eight merged PRs since v1.1.0, in eight changes. The second minor of the 1.x
line: two changes add machinery — a checked-in approve-hook that auto-approves
provably read-only Bash commands, and server rules that now bind
administrators with the shipped gates pinned to their producing app — and the
largest change hardens the three PreToolUse guards against argv-parsing
bypasses. Nothing is removed or renamed and every seam holds, so the
`UPDATE.md` pull carries no breaking change — but two items are worth a look
before you pull, both flagged in their bullets: re-running `github_setup.sh`
now binds administrators to the protected-branch rules, and the new
approve-hook changes which Bash commands run without a permission prompt.

- **A read-only Bash approve-hook joins the harness** (#119):
  `.claude/hooks/guard-command-policy.py` adopts the upstream Breakwater
  auto-approver with its newline defect fixed — `normalise()` turns an
  unquoted newline into a command separator before lexing, so a safe first
  line can no longer launder a mutating second line (`git status` followed by
  a newline-smuggled `git push` now defers; the tested all-read-only
  multi-line commands still auto-approve). The upstream policy tables are adopted byte-unchanged,
  and the docstring's *Known residuals* note names what they still permit (a
  bounded set of local git ref ops; best-effort sed/find/awk write
  detection). The CI meta-gate now discovers `.py` PreToolUse hooks, a new
  hermetic suite pins hook and gate in `make verify`, and `.gitattributes`
  pins `*.sh`/`*.py` to LF so CRLF checkouts cannot break shebangs or the
  pinned parser region. Per ADR-0004's failure directions the hook approves
  or defers, never blocks. **On update:** the hook changes prompting only —
  commands it cannot prove read-only fall through to the normal permission
  flow.
- **Server rules bind administrators, required checks pin their producer, and
  MCP self-merge is blocked** (#124): `scripts/github_setup.sh` ships
  `enforce_admins: true` in all three protection payloads — an admin
  exemption is an agent exemption, since agents act with the operator's
  identity; the escape hatch is a temporary, visible settings edit. Required
  checks move to the modern `checks` field with the shipped Actions gates
  pinned to the GitHub Actions app, so a same-named check from another app
  cannot satisfy them (`--require-check` entries stay any-source).
  `guard-git.sh` gains a parser-independent branch denying the MCP
  `merge_pull_request` / `enable_pr_auto_merge` tools by name — the
  never-self-merge rule now holds on the MCP path too. **On update:**
  re-running the script applies `enforce_admins` to both protected branches —
  administrators, and agents carrying their identity, are bound by the same
  rules from then on.
- **One hardened argv parser across the three PreToolUse guards** (#118): a
  global option, newline, subshell, comment, or unusual force/pathspec form
  before the subcommand could silently disarm `guard-git`, `guard-adr`, and
  `guard-issue-close`. The fragile per-hook parsing is replaced by one
  quote-aware argv parser, triplicated byte-for-byte so each hook stays a
  self-contained heredoc (no import path to fail on Windows) and
  identity-pinned by `scripts/test_guardlib.py` in `make verify`. Per-guard
  matcher hardening lands with it — force/broad push forms, add-scope,
  GraphQL merge, `:/`, parent-dir and `-C`/`cd` ADR resolution, `--input`
  file inspection — plus paired allow/deny hermetic fixtures; the 49-case
  bypass catalog now returns the correct verdict on every row, confirmed on
  native Windows. Residual classes the parser does not chase
  (nested interpreters, command-name wrappers, TOCTOU) are named in the hook
  headers and backstopped by branch protection and CI (D-004).
- **stale-working-docs nudge: bounded action set, live-task suppression**
  (#115): the Stop nudge fired every turn, flagged a live task's own state
  files, and asked for cleanup without bounding the action — sessions read it
  as "commit and push the working docs" and published mid-task scratch. The
  message now carries the closed action set (finished → `/handoff`; still
  running → do nothing; never a git action), a 6-hour recent-write
  suppression trims the live-task false positives, and a new hermetic suite
  pins both. Where task-end records land is now canon — `pushing.md`,
  `records-and-canon.md`, and `/session-close` name the records path.
- **ADR-0004 states each layer's failure direction** (#122): additive
  in-place refinement — deny-hooks fall through when broken, approve-hooks
  defer and never block, the prompt layer counts for nothing, server gates
  fail closed and are the authority; a deferred bypass class must name its
  auditable catcher; server rules bind administrators. The registry row
  extends to match and `enforcement.md` gains the failure-directions map.
- **guard-git's suite reaches `gh` through an explicit seam** (#114): on
  Windows, `CreateProcess` resolution bypassed the suite's hermetic `gh`
  mock, so the zombie-push cases silently exercised the live `gh`. The hook
  now resolves `gh` via the `GUARD_GH_BIN` seam (unset/empty → exactly
  `["gh"]`, byte-identical production behavior); the suite delivers its mock
  through the seam with a `PATH` decoy that turns any seam revert red on
  Linux, where CI runs.
- **Two-hats rule 4 sharpened — the PR ritual runs unchanged here**: three PR
  rounds in a row downgraded a completing PR's `Closes #NN` to `Part of
  #NN`, reading "issues do not auto-close at integration" as "no closing
  keyword on integration PRs". The rule now opens "run the PR ritual
  unchanged anyway" and names the downgrade as the anti-pattern; only the
  close's firing moment moves, to promotion. Blueprint-only files — nothing a
  seed receives changes.
- **A dangling tracker ID leaves `.gitignore`**: the archive block cited this
  repo's issue number, which a seed cannot resolve; comment text only, both
  ignore rules byte-identical.

## v1.1.0 — Gates that block, path-scoped rules, a leaner CLAUDE.md

Sixteen merged PRs since v1.0.5, in twelve changes. The first minor of the
1.x line: three of them add machinery rather than fix it — a new
strict-build gate on orphan docs pages, four shipped gate jobs promoted to
merge-blocking in the provisioning script, and two new path-scoped rule files.
Nothing is removed or renamed and every seam holds, so the `UPDATE.md` pull
carries no breaking change — but two items are worth a look before you pull,
both flagged in their bullets: the orphan-page gate can turn a project red on
`make verify` that was green, and re-running `github_setup.sh` now requires
four more status contexts on both protected branches.

- **Orphan docs pages fail the strict build** (#25, epic #20): `mkdocs.yml`
  gains `validation: nav: omitted_files: warn`, so a page under `docs/` that no
  nav entry lists now fails `mkdocs build --strict` — `make verify` and
  `docs.yml` gate **both** directions of the nav↔file pairing, where before
  only nav entries pointing at missing files failed. BOOTSTRAP step 2.3 already
  claimed this behavior; the config is what makes the claim true (D-004 — a
  convention names its gate). Dot-directories (`docs/.templates/`) are excluded
  by MkDocs before the check, so the shipped skeletons need no exemption.
  **On update:** a project carrying an unlisted page under `docs/` goes red
  until the page is added to the nav or removed.
- **The diff-scoped gates block merges** (#87): `scripts/github_setup.sh`
  required only 4 of 9 shipped gate jobs on `main` and 2 of 9 on `development`
  — a leaked secret, a committed binary, an un-synced ADR registry row, or an
  edit to a locked ✅ Decided ADR went red in CI yet stayed mergeable. The
  defaults become 8 contexts on `main` (adding `no-binaries`, `secret-scan`,
  `registry-sync`, `decided-adr-unlock`) and 6 on `development` (the same four,
  minus the `main`-only promotion pair). The selection principle is now stated
  where the list lives: a check may block merges only if it is a verdict on the
  PR's own change. `dependency-audit` is excluded on purpose — its verdict
  tracks external CVE feeds, so merge-blocking it would let a third-party
  disclosure freeze every open PR, including the one bumping the vulnerable
  pin; it stays the weekly sweep. `flow-guard`/`release-gate` stay `main`-only
  because that workflow never reports on PRs into `development`, and a required
  context that never reports blocks merges forever. `enforce_admins: false` now
  says in the script why it is the template default. **On update:** re-running
  the script applies the wider list, so a project that deleted
  `repo-hygiene.yml`, `security.yml`, or `adr-gates.yml` must pass
  `--require-check` explicitly or its merges will block on contexts that never
  report.
- **Instruction-file meta-docs demoted to path-scoped rules** (#88): guidance
  that only applies while editing a particular file no longer sits in the
  always-loaded `CLAUDE.md`. Two new rules ship — `claude-md-stays-thin.md`
  (scoped to `CLAUDE.md`) and `harvest-candidates.md` (scoped to the process
  surfaces: `.claude/`, `.github/`, `docs/process/`, `docs/.templates/`,
  `scripts/`, `Makefile`) — and `.claude/rules/README.md` gains its own
  `paths:` scope plus permission for a rule to *be* the canonical home of a
  purely path-local convention, not only a pointer. The README's trigger
  caveat is now measured rather than reported: on Claude Code v2.1.224, a
  path-scoped rule fires when an existing match is read or edited, does **not**
  fire when Claude creates a new matching file, and a rule created mid-session
  does not fire in that session; one SDK-driven remote worker session type
  injected nothing on touch. The stale claim that an `InstructionsLoaded` hook
  reports rule loading is replaced by the check that actually works — inspect
  the context.
- **`issue-link-guard` announces every waiver trailer in range** (#82): a
  waiver-pass quoted only the newest `Skip-Issue-Link-Guard` trailer as *the*
  reason. The guard cannot match a trailer to a finding, and a promotion PR's
  range is everything since the last release — several trailers, some arguing
  findings that no longer exist — so quoting one announced a false reason. All
  reasons in range now travel inside the `::warning::` annotation itself
  (newlines escaped `%0A`, so they survive where a reviewer actually reads
  them), the merits-path note counts them, and `/promote` step 4 plus
  `docs/process/releases.md` require the promotion PR body to name each waived
  finding with its true reason — advisory, and stated as such (D-004).
- **Fail-closed guard details stop truncating** (#106): the `::error::` exit of
  `infra_fail_or_waive` embedded raw `gh` output, and a workflow-command
  annotation ends at its first newline — so a multi-line error showed one line
  in the checks summary and spilled the rest into plain log lines. Both exits
  now escape the details identically. Cosmetic only: exit codes and the
  blocking behavior are unchanged.
- **`check_docs_truth` exemptions match on Windows** (#109): `exempt()`
  compared POSIX ledger fragments against `os.path.relpath` output, which
  renders with `os.sep` — so on Windows no exemption ever applied and the
  ledger falsely reported every entry stale. Paths are normalized
  unconditionally (not via `os.sep`, which is `/` where CI runs and would make
  the fix a no-op there), pinned by four self-test cases whose backslash paths
  fail on POSIX if the normalization is ever removed.
- **`CLAUDE.md` diet — slice 2** (#91, #93, #96, #99): 2,531 → 2,005 words
  (`wc -w`; 526 removed, 323 → 269 lines) across the Repo workflow,
  Conventions, Repo layout and docs-router sections, each bullet compressed to
  its obligation core plus the pointer that carries the detail. The router's
  gated-act bullets fold into the *Find your act* table, and the three bullets
  bootstrap deletes are marked as such. Deduplication only — no rule weakened,
  no new always-loaded text.
- **Standing pointers aim at act pages, not redirect stubs** (#83, #84): the
  v1.0.5 split left pointers landing on the dispatch hub and on section arrows
  that no longer resolve. Hooks, commands, workflows, decision scripts, issue
  and PR templates, the ADR pages and the module payloads now cite the act page
  that answers them — `pushing.md`, `opening-a-pr.md`, `closing-issues.md`,
  `writing-adrs.md`, `adding-docs-pages.md` — and the dead `→ section` arrows
  are gone.
- **Three stale enforcement statements corrected** (#100): ADR-0002, ADR-0003
  and ADR-0004 described enforcement that had since changed. The pages are
  rewritten to read as if always written that way — an ADR records the decision
  that holds, not its edit history. Carries a
  `Skip-Registry-Sync: registry rows carry none of the corrected claims`
  trailer: the corrections touch page prose only, no registry row changes.
- **Citations that outlive bootstrap dropped from the seed** (#24, epic #20):
  `AGENTS.md` and the `docs/records/changelog.md` stub cited machinery that
  `BOOTSTRAP.md` deletes, so a seeded project's docs-truth checker broke on
  first run at pointers to files that no longer existed.
- **Two hats gains rule 4 — issues do not auto-close at integration here**: a
  closing keyword fires only on PRs into the repo's *default* branch. Seeded
  projects make `development` the default, so the shipped premise holds
  downstream; it cannot hold in this repo, where `main` must stay default
  because a template is seeded from its default branch. The issues close at
  promotion via the restated `Closes` lines instead, which makes a merged PR
  whose target issue is still open the normal between-releases state here —
  not drift to flag, and never cause for a manual close.
- **Release checklist carries the waiver-reason rule** (#105): step 4 had only
  a "required checks green" box while `/promote` and `docs/process/releases.md`
  required the promotion PR body to name each waived finding — a release
  engineer running the checklist alone had nothing to remind them.

## v1.0.5 — Act-shaped process docs, a leaner CLAUDE.md, seed-hygiene fixes

Seven backward-compatible changes since v1.0.4 — the process manual split into
act-shaped pages behind a dispatch hub, a deduplication pass on the
always-loaded `CLAUDE.md`, the two-hats authoring contract with a checker lane
behind its records rule, a faithful-read protocol for `/tick`, and three
hygiene fixes to what a seeded project inherits. A clean `UPDATE.md` pull for
downstream projects: no breaking changes, and the one new checker lane is
blueprint-only — it self-disarms permanently at bootstrap.

- **`contributing.md` split into act-shaped pages** (#66): the 636-line process
  manual becomes a 126-line dispatch hub plus thirteen pages named for the act
  they govern — filing work, committing, pushing, opening a PR, closing issues,
  running epics, writing ADRs, adding docs pages, testing changes, releases,
  records and canon, ending a session, enforcement — each wired into the nav
  and reachable from the hub. Anchor-preserving: content moved, not rewritten,
  so existing citations still resolve.
- **`CLAUDE.md` diet — slice 1** (#59): 2,702 → 2,351 words (`wc -w`; 351
  removed) by cutting standing instruction text whose substance already reaches
  the agent at its moment of need — the honest-reporting and
  adversarial-verification paragraphs (both skills' triggers are always
  loaded), reproduce-before-you-fix and know-when-to-stop (the
  `reproduce-first` card), the config-cites-decision bullet (its path-scoped
  rule), and per-rule detail the guard hooks' block messages already teach at
  the blocked call. Two enabling moves landed first: the three-strikes
  escalation rule into `reproduce-first` → *Hard rules*, and
  `config-cites-decision.md`'s canonical pointer re-aimed at the act pages.
  Pure deduplication — no new machinery, and zero words added to any
  always-loaded surface.
- **The two-hats authoring contract, and a lane behind its records rule**
  (#75): `CONTRIBUTING.md` gains *Two hats* — authoring the template is not
  working in a seeded project, so the blueprint's own session records must
  never land in the stubs it ships — restated as three rules in `CLAUDE.md`'s
  blueprint admonition. Lane G of `check_docs_truth.py` enforces the records
  half: a session entry in `docs/records/changelog.md` or a dated lesson in
  `docs/records/lessons.md` fails `make verify` while `blueprint/` exists, with
  four both-ways self-test scenarios. The lane arms on the machinery's
  presence and disarms forever once bootstrap deletes it — a seeded project's
  records are its own.
- **`/tick` composes its write from a faithful read** (#72): a tick is a
  full-body rewrite, and issue-body reads are not equally faithful — the GitHub
  MCP `issue_read`/`list_issues` tools strip HTML comments and `<angle-tokens>`
  (even inside code fences) and escape quotes, so a body composed from one
  silently and permanently deletes content. Step 1 of the card is now a channel
  choice (`gh api`, or MCP `search_issues` with a number assertion — never the
  lossy pair), followed by an `updated_at` staleness check so a write never
  lands across a newer edit. The tick also moves to PR-open, where
  `issue-link-guard` counts the boxes, so the guard starts green instead of
  being waived.
- **Blueprint session scratch stops shipping into seeded projects** (#70, epic
  #20): `.claude/archive/` carried two dated reproduction entries from this
  repo's own sessions into every seed — issue IDs and citations to machinery
  bootstrap deletes. Both are removed, `.gitignore` keeps this repo's agent
  scratch untracked (a bootstrap-deleted block: seeded projects *do* track
  their archive, which `HARVEST.md` scans), and `CONTRIBUTING.md` states the
  rule.
- **Tracker IDs swept out of seed-inherited content** (#74): an issue or PR
  number from this repo points at nothing downstream — in a seeded project it
  resolves to an unrelated issue. Twenty-three files lose their `(#NN)`
  citations: the guard hooks and their block messages, the gate workflows and
  decision scripts, the issue and PR templates, the labels manifest, the
  Makefile, and the release seam. Comments and messages only — no behavior
  change, and every test suite's assertions are untouched.
- **Close instructions reworded to the operator-close protocol** (#63, #60):
  eight shipped process texts still instructed an agent-performed manual close
  — against the v1.0.4 hard rule, denied at the source by
  `guard-issue-close.sh` and reverted server-side by `issue-close-guard.yml`.
  Every manual branch now reads *post the comment → tick → request the operator
  close*, citing portable homes rather than this repo's tracker IDs; the
  PR-carried `Closes #N` branches are byte-identical.

## v1.0.4 — Operator-only issue closing, the /tick ritual, gate & bootstrap fixes

Seven backward-compatible changes since v1.0.3 — an enforcement pair making
manual issue closes operator-only, a ritual command for deliverable-box
ticking, a hardening pass on `issue-link-guard`, a fail-safe fix to the
lfs-assets module, two bootstrap-hardening fixes from the epic #20 audit,
and a dependency bump. A clean `UPDATE.md` pull for downstream projects: no
breaking changes.

- **Operator-only issue closing** (#54): agents can no longer manually close
  or delete issues — the `guard-issue-close.sh` PreToolUse hook denies MCP
  `state=closed` writes and `gh issue close`/`delete` at the source, and the
  `issue-close-guard.yml` workflow reverts app-/bot-mediated manual closes
  server-side (commit/PR-merge closes and the operator's own clicks stand;
  allowlisted first-party apps; fail-open on read errors). Both suites wired
  into `make verify`; new CLAUDE.md hard-rule bullet + contributing.md
  paragraph. The `issues:`-triggered workflow arms on the default branch at
  this promotion; the live-fire probe is tracked in #57.
- **The `/tick` ritual** (#52): attestation-first deliverable box ticking —
  per box, *did I deliver this?* answered with named evidence or no tick —
  then the anchored body edit and a verify re-read; five pointer edits put
  the affordance at the work-time sites (CLAUDE.md, contributing.md, the
  task skeleton, the PR template). An affordance for the existing
  `issue-link-guard` rule (#37, #41), not a new gate.
- **`issue-link-guard` evaluates merits before waivers, loudly** (#47): the
  decision script now counts deliverable boxes first, consults the
  `Skip-Issue-Link-Guard` trailer only when merits fail, logs which path
  passed, and announces waiver-passes with per-finding `waived:` lines plus
  a `::warning::` quoting the reason; the tick-your-boxes duty becomes
  visible work-time instruction text. Exit codes unchanged for every input.
- **lfs-assets applies fail-safe** (#22): the module now instructs
  uncommenting the chosen menu lines (not appending them as comments) into
  the repo's root `.gitattributes`, creating the file if absent, with a
  mandatory `git check-attr filter` proof step — verbatim application
  previously yielded zero LFS coverage, silently.
- **Bootstrap names the ADR unlock it triggers** (#21): the three sites
  claiming ADR-0007's 🟡→✅ finalization "needs no ADR unlock" now instruct
  `/unlock-adr adr-0007` plus the `Unlock-ADR:` trailer in the birth
  commit's body, and the data-repo module's ADR payload ships 🟡 Proposed —
  the hook and gates themselves are untouched.
- **Tier-1 gate false positive removed** (#23): the illustrative literal
  `{{TOKEN}}` in a `scripts/github_setup.sh` comment — a pre-baked
  completion-gate failure shipped to every seed — reworded to "unresolved
  placeholders".
- **Dependency bump** (#55): `actions/setup-python` 6 → 7 in the GitHub
  Actions group (Dependabot).

## v1.0.3 — Lifecycle guardrails: issue-link guard, promotion train, zombie-push

Five changes hardening how issues close and how releases are cut, plus
push-time protection against stacking commits on an already-merged PR. Each
lands or extends enforcement machinery — CI gates, a ritual command, a push
hook — carrying its own both-ways test suite in `make verify`.

- **`issue-link-guard` — closing keywords may only target issues a PR
  completes** (#18): a required CI gate that blocks a closing reference to an
  `epic`-labeled issue with open sub-issues (closeout PRs pass; the
  `Skip-Issue-Link-Guard:` trailer is the declared exception; an inconclusive
  `gh` fails closed). Adds the forced-choice linking block to the PR template,
  the canonical *PR ↔ issue linking* section in `contributing.md`, and the
  docs-truth `epic-state` lane covering the residual paths.
- **Standardized promotion train** (#35): the `/promote` ritual — contents
  derived from `main..development`, a per-change bump proposal, a hard operator
  STOP on patch/minor/major, caboose PR, promotion PR, operator-only merge +
  tag — plus a promotion PR template and the `release-gate` job (the seam-named
  version file bumped by exactly one semver step and a release-log entry for
  it; seam `.claude/release.txt`). Fills the release checklist and the
  surrounding process prose.
- **Close-at-completion guardrails** (#37): the symmetric rule that an issue
  closes when its deliverables are met. Deliverables become task-list
  checkboxes in the task template; `issue-link-guard` gains the general-issue
  check (a `Closes` at any issue with unchecked boxes fails, the trailer
  excepted); `/session-close` gains the per-issue `n/m` reconciliation sweep;
  the docs-truth `built-state` lane mirrors `epic-state` for the under-closing
  case.
- **Zombie-push guardrails** (#39): `guard-git.sh` now reads the destination
  branch's PR state at push time — terminal (merged or closed) history blocks
  with state-specific recovery instructions, unless the push carries the
  current `origin/development` restart line — and fails open on `gh`/network
  errors. The session-start orientation prints the branch's PR verdict, and the
  canonical *PR lifecycle* section is added.
- **Mandatory deliverable checklist at close time** (#41): a `Closes` at a
  box-less non-epic, non-`note` issue now fails unless a `Skip-Issue-Link-Guard`
  trailer is present — absence no longer reads as compliance — and checkbox
  counting is fence-aware, so a fenced *sample* of `- [ ]` syntax is not
  miscounted as a real deliverable box.

## v1.0.2 — Multi-agent entry point (AGENTS.md)

Two backward-compatible changes since v1.0.1: a tool-neutral entry point
(`AGENTS.md`) so agents that aren't Claude Code can find the contract, and a
fix flipping the seeded changelog convention to newest-first. A clean
`UPDATE.md` pull for downstream projects — no new machinery, no breaking
changes.

- **`AGENTS.md` routes non-Claude agents to `CLAUDE.md`**: a thin pointer file
  (no duplicated rules) so tools following the `AGENTS.md` convention (e.g.
  Codex) are sent to the one maintained contract. It names which rules are
  tool-neutral and CI-enforced for any agent, and which `.claude/` machinery
  is Claude Code-specific and safe for other agents to ignore. No ADR —
  additive entry point, consistent with D-001 (docs canonical) and D-004 (CI
  is the cross-agent enforcer).
- **`AGENTS.md` is truth-checked like its siblings**: added to
  `check_docs_truth.py`'s `DOC_ROOT_FILES` and `ROOT_FILES`, so its
  backtick-cited paths are validated in `make verify`/CI alongside `CLAUDE.md`
  and `README.md` (D-004 — a new entry point names its enforcer).
- **README documents the agent-agnostic posture**: a note that the process and
  its enforcement are tool-neutral while the agent-facing ergonomics
  (`CLAUDE.md`, `.claude/`) are tuned for Claude Code, other agents routed
  through `AGENTS.md`.
- **Seeded changelog convention flips to newest-first** (#12): the seeded
  `docs/records/changelog.md` grew oldest-first while its sibling logs
  (`docs/records/lessons.md`, `blueprint/CHANGELOG.md`) are newest-first, so
  the session-start orientation hook (`grep -m1 '^### '`) surfaced the *oldest*
  entry mislabeled "Last" in multi-session projects. The convention is flipped
  to newest-first across `docs/records/changelog.md`,
  `.claude/commands/session-close.md`, `docs/process/contributing.md`, and
  `CLAUDE.md`; no code change — the hook's existing grep becomes correct. No
  ADR — ADR-0001 (D-001) calls the changelog a "chronological diary" without
  fixing a direction.

## v1.0.1 — Post-launch dogfooding fixes

First patch after the public release — five changes surfaced by using the
template, all backward-compatible (a clean `UPDATE.md` pull for downstream
projects): no new machinery, no breaking changes.

- **Domain areas become top-level nav tabs** (#2): BOOTSTRAP placed chosen
  domain areas as sections *inside* the `Project` tab, reading as
  project-meta. Each area is now its own top-level tab; `Project` keeps only
  the four meta sections. Four editable sources brought into agreement
  (`BOOTSTRAP.md`, both `mkdocs.yml` comments, `contributing.md`,
  `docs/index.md`). No ADR — nav topology isn't ADR-governed.
- **Docs-to-Pages publishing is opt-in, default off** (#3):
  `scripts/github_setup.sh` set `DEPLOY_DOCS=true` unconditionally, so a
  freshly-seeded (often `--private`) project published placeholder-filled
  docs to a public URL on the first merge. Now gated behind `--deploy-docs`,
  with the choice and its public-exposure risk surfaced in BOOTSTRAP. Only
  publishing changes — the strict-build merge gate runs regardless.
- **Seeded README footer links to the blueprint** (#5): the
  `Initialized from Project Blueprint vN` stamp now links "Project Blueprint"
  to the blueprint repo (attribution / backlink). The machine-read anchors
  (birth commit message, changelog Session 1 entry) stay plain, so `UPDATE.md`
  still reads the version whether the footer is bare or linked.
- **README documents the GitHub UI instantiation route** (#6): the "Use this
  template" flow is now a first-class option (badge CTA to `/generate` plus a
  link to GitHub's official guide) alongside the `gh` CLI; the "run
  BOOTSTRAP" step is location-agnostic.
- **Dependency bump** (#1): `pyyaml` requirement `>=6` → `>=6.0.3` in
  `docs/requirements.txt` (Dependabot).

## v1.0.0 — First release

The template is complete and validated end-to-end: the core documentation
skeleton, the GitHub layer (labels, issue forms, PR template, gate workflows),
the Claude harness layer (guard hooks, ritual commands, skill cards), the
optional modules (python-package, data-repo, lfs-assets), and the bootstrap /
harvest / update / adopt lifecycle rituals. A full end-to-end BOOTSTRAP
dry-run — driven through machinery deletion to a green first `make verify` on
the seeded-repo state — validates the seeding path. Seeded projects record
"Initialized from Project Blueprint v1.0.0".
