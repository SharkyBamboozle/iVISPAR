# HARVEST.md — pull process improvements back from live projects

**Who runs this:** a Claude session **in this blueprint repo**, pointed at
one or more live projects (local clones or added repos), invoked as *"Run
HARVEST.md against <projects>."* Improvements flow **blueprint-ward,
manually, batched** — live projects are the R&D lab; the blueprint is the
distillation, not a dependency. Downstream projects never auto-receive
updates: new projects get them at birth; an existing project adopts a
specific change by hand only when wanted.

## 1 · Collect candidates

- **Diff the literal process files** against each live project's copy —
  they started byte-identical, so every delta is a candidate. Do not
  enumerate the literal set — it grows every release, so an enumerated list
  goes stale silently. Instead diff **every tracked file EXCEPT** the
  per-project set and the machinery below — what remains is literal by
  construction, so a newly added literal file (a gate, a skill card, a data
  file) is caught without editing this step. Skip, by the tiers in
  `blueprint/TOKENS.md` (the one canonical home for the file-treatment
  rule):
    - **Identity / generated files** (Tier 2) — `CLAUDE.md`,
      `docs/index.md`, `README.md`, the decisions registry and ADR pages,
      the filled `docs/direction/` registries, and the `docs/records/` diary
      (changelog, lessons, epics, research). These diverge by design; a
      byte-diff is pure noise.
    - **Tokenized config** (Tier 1) — `mkdocs.yml`, `pyproject.toml`, any
      config carrying the project's name / owner / branch tokens.
    - **Machinery deleted at bootstrap** — `blueprint/`, `modules/`,
      `BOOTSTRAP.md`, `HARVEST.md`, `UPDATE.md`, `ADOPT.md`, `LICENSE`,
      `scripts/check_bootstrap_complete.sh`.
- **Sweep each project's CLAUDE.md** for sections/conventions that grew
  there but are actually generic — CLAUDE.md is skipped by the diff above,
  so this sweep is how its generic growth still reaches the harvest.
- **Check flagged candidates**: `note` issues in live projects mentioning
  the blueprint, and any issues in this repo. *Offline / no tracker
  reachable:* fall back to scanning each project's `.claude/working/` and
  `.claude/archive/` — a session that flagged an improvement often leaves
  the note there even when it never filed an issue. The `label:note`
  sub-lane is **best-effort**: it needs a reachable GitHub tracker, and its
  absence narrows the net but never blocks a harvest.

## 2 · Judge

- **Discard the never-harvestable deltas first** — they differ by
  construction, not by improvement, and are noise rather than candidates:
    - a **filled Tier-2 block** — the project wrote its identity into a
      `<!-- BLUEPRINT: -->` judgment spot;
    - a **module-applied delta** — a file the project gained by applying an
      optional module (`modules/*`) it chose at bootstrap;
    - a **bootstrap cleanup** — machinery the project deleted at
      instantiation.
- **Then, for each remaining delta:** generic (belongs in the blueprint) vs
  project-specific (stays downstream)? When unsure, leave it downstream —
  the blueprint stays minimal; a delta can always be harvested next round.
- List the verdicts for the user before applying.

## 3 · Apply

- Apply accepted deltas to the blueprint (keep literal files literal —
  re-parameterize anything project-specific that leaked in).
- **Placement of a harvested CLAUDE.md convention:** it lands in its
  canonical home, not verbatim where it grew downstream. A process rule
  goes to its act page under `docs/process/` (routed via the contributing
  hub's *Find your act* table) with its enforcer named (D-004),
  and `CLAUDE.md` gets only a thin pointer; a genuinely CLAUDE.md-shaped
  rule (a hard rule, an autonomy-contract line) joins the matching section
  of the blueprint's own `CLAUDE.md` template. One home per fact — never
  both.
- Bump `blueprint/VERSION`; append a `blueprint/CHANGELOG.md` entry naming
  each harvested change and its source project. The release train itself —
  operator-decided bump class, caboose PR, promotion PR, tag — follows the
  `/promote` ritual (`.claude/commands/promote.md`); the bullets below
  state the harvest-specific details.
- `make verify` + `bash -n` any touched scripts; run the matching hook
  suite if a guard changed (e.g. `scripts/test_guard_git.sh`).
- Feature branch → PR (this repo follows its own branch model).
- **After the PR merges, tag the merge commit on `main`** — not the
  feature-branch tip, not an arbitrary commit:
  `git checkout main && git pull && git tag v<VERSION> && git push origin v<VERSION>`.
  `UPDATE.md` takes a seeded project's merge base directly from these tags
  and reads the FROM→TO delta between them as a `main`-line diff; a
  feature-branch tip sits off `main`'s first-parent line, so a tag there
  puts the base off the mainline and silently corrupts the next update's
  diff. An untagged version cannot be diffed against at all.
- Close any harvest-candidate issues with a pointer to the version.
