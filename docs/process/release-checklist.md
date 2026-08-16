# Release checklist

The single canonical release path — a promotion of `development` into
`main`, run via the `/promote` ritual (`.claude/commands/promote.md`).
Every step is mandatory unless explicitly marked optional — the person (or
agent) running this checklist **is** the release engineer; do not skip a
step by deferring it to someone else. Conventions and enforcers:
[Releases](releases.md).

<!-- BLUEPRINT: the promotion skeleton below is the shipped standard —
extend the placeholder steps (build/publish) with the project's real ones
as its release process takes shape. If this project never cuts releases,
delete this page (plus its nav entry in mkdocs.yml, its *Find your act* row
in `docs/process/contributing.md`, and the release mention in CLAUDE.md →
"Where to read, by task") and declare `mode: off <reason>` in
`.claude/release.txt` — the release-gate then passes with a note. -->

## 0. Pre-flight

- [ ] `development` green, ahead of `main`; working tree clean.
- [ ] Release contents listed from
      `git log --first-parent --oneline main..development` — that list
      **is** the release; the changelog entry and the promotion PR's
      contents table are both derived from it, never from memory.
- [ ] No open blocker issues against this release.

## 1. Bump decision — the operator's call

- [ ] Per-change bump class proposed with one-line reasoning (breaking
      change to shipped machinery → major; new machinery → minor;
      fixes/docs → patch); overall proposal = the highest class present.
- [ ] **Operator approved patch / minor / major** — a hard STOP in
      `/promote`; a failed or unanswered question blocks, it never
      defaults. *(Advisory — the approval is judgment; the `release-gate`
      checks the increment's arithmetic, per D-004.)*

## 2. Caboose — version & log land on `development` first

- [ ] Version bumped in the seam-named file and the release-log entry
      prepended (both named by `.claude/release.txt`), bundling **every**
      promoted change from step 0's list.
- [ ] Caboose PR merged to `development` before the promotion PR opens.

## 3. Verify

- [ ] `make verify` green on the release commit.
- [ ] *(project-specific test / benchmark gates go here)*

## 4. Promotion PR

- [ ] Head `development` → base `main`, body from
      `.github/PULL_REQUEST_TEMPLATE/promotion.md`.
- [ ] `Closes #N` restated for every issue the train completed — on a
      main-default repo this is what closes them; on a dev-default repo a
      harmless manifest (the `issue-link-guard` gate vets the list either
      way).
- [ ] Required checks green: `flow-guard` · `release-gate` ·
      `issue-link-guard` · `build` · `no-binaries` · `secret-scan` ·
      `registry-sync` · `decided-adr-unlock`.
- [ ] If `issue-link-guard` passed on a **waiver** (a `::warning::` run,
      not a merits pass): the PR body names each waived finding with its
      true reason. *(Advisory per D-004 — nothing checks a promotion PR
      body; the guard announces every `Skip-Issue-Link-Guard` trailer in
      range but cannot match a trailer to a finding, so a human states
      the match. Rule: [Releases](releases.md).)*

## 5. Merge, tag — operator-only

- [ ] Operator merges (never the agent, never self-merge).
- [ ] Annotated tag cut on the **`main` merge commit** — not a branch tip
      that may have moved since verification; downstream version-span
      tooling reads deltas along `main`'s first-parent line from these
      tags, so a tag off that line silently corrupts later diffs.

## 6. Build, package & publish

- [ ] *(build/package/publish steps go here — delete the section with a
      note if the promotion itself is the release)*
- [ ] Post-publish smoke check: *(the one command or URL that proves it's
      live)*.

## 7. Post-check

- [ ] Every restated issue verified closed; stragglers have a one-line
      pointer comment + an operator close request (the close itself is
      operator-only — CLAUDE.md hard rule).
- [ ] Session changelog entry for the release
      ([changelog](../records/changelog.md)).

## Rollback plan

If the release is bad: *(how to roll back goes here)*. A rollback is followed
by a post-mortem note naming **the check that failed to catch the problem**,
and the fix ships as a new release through this same checklist — never as a
hot patch outside it.

## Checklist meta

- This checklist is the **single source of truth** for releases. If a step is
  skipped, the release is non-conforming and must be marked as such in the
  changelog.
- When you find a step that was missed in a past release, **add it here** —
  not in a separate doc.
- When a step becomes reliably automated, mark it `(automated)` but **keep it
  in the list**, so the release engineer still verifies the automation ran.
