# UPDATE.md — bring a seeded project up to a newer blueprint version

**Who runs this:** a Claude session **in the seeded project**, with the
blueprint cloned alongside, invoked as *"Run <blueprint-clone>/UPDATE.md
against this project."* Updates flow **pull, manual, batched** — the
project chooses when; the blueprint never pushes (the converse of
`HARVEST.md`). Nothing here touches the project's identity: its README
body, its filled registries, its ADR contents, its history.

## 0 · Establish the version span

- **From:** the project's blueprint stamp — the README footer
  ("Initialized from Project Blueprint vN" / "updated to vM"), or the
  birth commit (`git log --grep "Initialize from Project Blueprint"`).
  The footer's name may be bare text or a Markdown link
  (`[Project Blueprint](…)`) — the version reads the same either way, and
  the birth-commit fallback is always plain text.
- **To:** the blueprint clone's `blueprint/VERSION`.
- When a merge base is needed, check out the FROM version in the blueprint
  clone by its **release tag** (the harvest ritual tags every release, on
  the merge commit on `main`). The FROM→TO diff is read along `main`'s
  first-parent line — which is why the tag must sit on that line; a tag on a
  feature-branch tip would put the base off it and skew the diff.
- Read the `blueprint/CHANGELOG.md` entries across the span and split the
  worklist: **mechanical** (file deltas) vs **judgment** (new decisions,
  new interview-grade choices). **Present the worklist to the owner before
  anything lands.** An autonomous run (no interactive owner) satisfies this
  by writing the worklist into a durable artifact the owner reviews before
  merge — the PR description, or a worklist note — never by applying unseen:
  the gate is owner sight before the change *lands*, not before it is
  drafted.

## 1 · Mechanical pass — merge by file tier (`blueprint/TOKENS.md`)

- **Literal files** (hooks, workflows, commands, skills, doc templates,
  the process manual) started byte-identical at seeding:
    - project copy still identical to FROM → apply the FROM→TO diff
      directly;
    - project copy diverged → **three-way merge** (base = FROM, ours =
      project, theirs = TO); every conflict is a judgment call surfaced to
      the owner — never auto-resolved, never union-merged.
- **Tokenized files** (mkdocs config, CI carrying branch names): three-way
  merge, then confirm no unfilled tokens re-entered —
  `git grep -nE '\{\{[A-Z_]+\}\}'` must stay clean (the bootstrap gate
  script does not exist downstream).
- **New files** from the blueprint (a new hook, gate, or skill card): copy
  in; resolve any `BLUEPRINT:` markers they carry as a mini-bootstrap —
  `git grep -n 'BLUEPRINT:'` must end clean.
- **Generated / identity files** (the project's README body, ADR pages,
  filled registries, changelog, lessons): **the mechanical pass never
  touches them** — no byte-merge, no diff applied. (The judgment pass, step
  2, may *append* a re-proposed row to a registry — a different act from
  rewriting one, reconciled there.) An update also does not repair a stale
  citation *inside* an identity file — an ADR that references a doc path a
  later blueprint version renamed stays as written, because identity is the
  project's to rewrite, not the update's. Flag such a citation for a
  separate refresh pass; it is out of scope here by design.

## 2 · Judgment pass — decisions are re-decided, never copied

- **ADR IDs are project-local.** A new blueprint convention arriving as a
  decision record is not copied verbatim: re-propose it into the project's
  own registry under its **next free ID**, status 🟡 Proposed, and let the
  project owner flip it — supersede-never-overwrite, applied downstream.
  This *appends* a row; it never rewrites an existing one — which is what
  reconciles it with step 1's "the mechanical pass never touches
  registries": a re-proposal is an additive, owner-approved decision, not a
  merge of blueprint content into the project's filled registry.
- A new convention that assumes machinery the project skipped: adopt,
  adapt, or record as 🧊 deferred with a written trigger — never silently
  drop. List every verdict for the owner (mirror of `HARVEST.md` step 2).

## 3 · Verify and land

- `make verify` green; run the hook suites the project carries
  (`scripts/test_guard_git.sh`, `scripts/test_guard_adr.sh`); any **new**
  guard gets a both-ways demonstration (blocked case + allowed case) in
  the PR body.
- Feature branch → PR into the project's integration branch, with a
  per-tier summary: applied clean / three-way merged / conflicts resolved /
  decisions re-proposed / deferred-with-trigger.
- Update the README footer to
  "updated to [Project Blueprint](https://github.com/SharkyBamboozle/CLAUDE_blueprint) vM (from vN)"
  — the stamp the next update reads; keep the name linked (matching the
  bootstrap footer) and the versions as bare text.
- A **settled kept-divergence** — a conflict the owner resolved by
  deliberately keeping the project's version — gets one line in the
  project's lessons page, so the next update (and the next harvest) reads it
  as deliberate, not drift. An **unresolved surfaced conflict** is not a
  lesson: it is a blocker to resolve before the PR lands, not a divergence
  to record. Only settled divergences reach the lessons page.
