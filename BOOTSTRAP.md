# BOOTSTRAP.md — initialize this repository from the blueprint

**Who runs this:** a Claude session in a fresh clone seeded from the
Project Blueprint template, invoked as *"Run BOOTSTRAP.md."* Execute the
steps in order; do not skip the gate. This file (and all blueprint
machinery) deletes itself at the end — a live project never carries it.

Read first: `blueprint/TOKENS.md` (placeholder tiers), `modules/README.md`
(module list + the binary-policy postures), `blueprint/VERSION` (note the
version — it goes into the init commit message).

## 1 · Interview

Ask the user (skip anything already answered in their invoking message):

1. **Identity** — project name, one-liner. → `{{PROJECT_NAME}}`,
   `{{ONE_LINER}}`.
2. **GitHub coordinates** — owner and repo slug (default: parse
   `git remote get-url origin`). → `{{GITHUB_OWNER}}`, `{{PROJECT_SLUG}}`.
3. **Domain areas** — which topic sections the docs will grow
   (architecture? design? content?): used for the CLAUDE.md routing rows,
   `area:*` labels, and mkdocs nav pruning.
4. **Binary policy** — one posture from `modules/README.md` → *Binary
   policy*; if in-repo assets: the sanctioned asset directories.
5. **Modules** — `python-package`? (then: package name → `{{PACKAGE_NAME}}`,
   and the architecture seams), `data-repo`? (then: artifact kinds;
   `{{DATA_REPO}}` = `<slug>-data` unless told otherwise), `lfs-assets`?
   (then: asset types/dirs).
6. **Docs publishing** — publish docs to GitHub Pages on each merge to
   `development`/`main`? **(default: no.)** For **private** projects, keep
   this **off** — a published Pages site can be publicly reachable and would
   leak sensitive project information. Enable only if the docs are meant to be
   public, understanding that every merge then publishes them. → drives the
   `--deploy-docs` flag on `scripts/github_setup.sh` (see step 8).

## 2 · Apply the core

1. Fill every **Tier-1 token** — contents AND file/directory names
   (`git grep -lE '\{\{[A-Z_]+\}\}'` finds them — this regex, not a bare
   `'{{'`, which false-hits GitHub Actions' `${{ }}` syntax; unused tokens
   like `{{DATA_REPO}}` in a no-data-repo project: remove the referencing
   clause, don't leave the token).
2. Resolve every **Tier-2 `<!-- BLUEPRINT: ... -->` block** with real
   content or an explicit "none yet" statement — never leave the marker.
   This includes: CLAUDE.md identity + commands/code-style slots + routing
   rows + repo-layout bullets (the three describing `modules/`, `blueprint/`,
   and `LICENSE` resolve by deletion, marker and bullets together — step 7
   removes the machinery they describe),
   `docs/index.md`, vision seeds (principles may legitimately start as
   "none recorded yet — add P1 when a recurring argument appears"),
   registry example comments, the changelog's Session 1 entry (today's
   date; note "Initialized from Project Blueprint v<VERSION>"; which
   modules were applied).
3. Prune the mkdocs `nav` to the pages that exist; add each domain area as
   its own top-level nav tab (`docs/<area>/`, a sibling of Home and Project).
   **Every `nav` entry must point at a file
   that exists** — adding a domain-area tab means creating at least a
   one-line stub page for it in the same step, or the strict build (step 5)
   fails ("A reference to 'docs/…' is included in the 'nav' configuration,
   which is not found in the documentation files"). The reverse also fails
   under `--strict`: a page under `docs/` that no `nav` entry lists.
4. **Rewrite `README.md` as the project's README** (name, one-liner, docs
   pointer, setup + verify commands, and the footer
   `Initialized from [Project Blueprint](https://github.com/SharkyBamboozle/CLAUDE_blueprint) vN`)
   — the shipped README describes the blueprint, not your project. Linking
   the name turns every kept stamp into a backlink (attribution +
   provenance); the version stays bare text right after the link. The
   footer is machine-read: the blueprint's `UPDATE.md` ritual uses it to
   establish the project's version span — keep the canonical (linked) form
   above (the version bare, so it reads the same whether or not the link
   survives).
5. **`site/` is reserved** — it is the MkDocs build output directory
   (gitignored, clobbered on every docs build). Never place project sources
   there; pick another name (`web/`, `content/`, `assets/`).

## 3 · Apply the chosen modules

Execute each selected module's `MODULE.md` exactly (copy payload, fill
tokens, make its judgment calls, extend `Makefile`/`CLAUDE.md`/nav as it
instructs). Skip unselected modules entirely — their payloads die with
`modules/` in step 7.

## 4 · Wire the binary policy

Three places, consistently (they carry the `BLUEPRINT:` markers): the
CLAUDE.md hard-rule bullet; `.claude/asset-dirs.txt` — the single data
file both enforcement points (the `guard-git.sh` hook and the repo-hygiene
CI) read, so they can never disagree; and **ADR-0007 (binary hygiene)**,
which is *finalized* here: rewrite its Decision section to the chosen
posture, flip its status to ✅ Decided, and update its registry row in the
same commit. Flipping 🟡→✅ is itself a gated path to Decided — the
`guard-adr.sh` hook blocks the promotion edit like any other. First run
`/unlock-adr adr-0007` (mints a 1h token), then make the finalization
edit, and give the step-8 init commit an
`Unlock-ADR: adr-0007 — bootstrap binary-policy finalization` trailer in
its **body** — the subject stays exactly
`Initialize from Project Blueprint v<VERSION>` (step 8's version anchor).
(`adr-gates.yml` runs only on pull requests, so the direct birth push is
never CI-checked — the trailer keeps the birth commit consistent with the
hook's own contract.)

## 5 · Gate — must pass before anything is deleted

```bash
git add -A                              # git grep sees tracked files only — stage first
./scripts/check_bootstrap_complete.sh   # both tiers + filenames: clean
make verify                             # strict docs build (+ module lint/tests)
```

Fix and re-run until green. Do not rationalize a red gate.

## 6 · Write POST_INIT_CHECKLIST.md

Everything that couldn't be done here, as a checklist the user works
through: `scripts/github_setup.sh` invocation (with `--areas`, and
`--deploy-docs` only if Pages publishing was chosen in the interview;
required checks default to the template's own shipped gates) **if `gh` was
unavailable in this session — write the exact command**; `git lfs install` (per machine, if lfs-assets);
data-repo creation steps (if that module was chosen but `gh` unavailable —
create the repo and push the **preserved `data-repo-seed/`** the module
staged, then delete that directory; see `modules/data-repo/MODULE.md`);
**the project's own LICENSE decision** — the template's `LICENSE` is
deleted in step 7 (the blueprint is MIT with a template-use waiver, so a
seeded project owes nothing and starts license-free); add the project's
chosen license, or record the deferral with a written trigger;
secrets/integrations; verify the repo is NOT marked as a template.

## 7 · Delete the machinery

**First, if data-repo creation was deferred** (the module was chosen but
`gh` was unavailable): confirm the prepared seed was already moved to
`data-repo-seed/` at the repo root (per `modules/data-repo/MODULE.md`).
The command below deletes `modules/` — the seed's *original* home — so a
seed left unrescued under `modules/data-repo/` is lost permanently and
the deferred data repo has nothing to push.

```bash
git rm -rf BOOTSTRAP.md HARVEST.md UPDATE.md ADOPT.md CONTRIBUTING.md LICENSE blueprint/ modules/ scripts/check_bootstrap_complete.sh
```

(`LICENSE` is the blueprint's own MIT license; its template-use waiver
explicitly permits this deletion. The seeded project adds its own per the
checklist above.)

(`-f` because machinery files may carry staged edits from earlier steps.
Read `blueprint/VERSION` before this — it's needed for the commit message.
Also drop the `check_bootstrap_complete.sh` row from `scripts/README.md` —
it points at a file that no longer exists.)

**Then re-run `make verify`.** The machinery is gone now, so any surviving
ADR or doc that still cites a deleted path — a layout bullet, an ADR that
mentions the blueprint scaffolding — fails here, on your machine, instead of
on the seeded repo's first CI run. Fix every citation the checker flags and
re-run until green before committing.

## 8 · Commit, push, GitHub setup

1. Commit everything as: `Initialize from Project Blueprint v<VERSION>`
   (plain text, never linked — this commit message is the format-proof
   version anchor `UPDATE.md` step 0 falls back to when the README footer is
   absent or reworded). The `Unlock-ADR: adr-0007 — <reason>` trailer from
   step 4 goes in the commit **body**, below this subject — never in the
   subject itself.
2. Push to `main` — **the one sanctioned direct push**: the guard hook
   permits it while the repo is demonstrably un-bootstrapped (remote `main`
   absent, or still the template's single initial commit carrying
   `BOOTSTRAP.md`). If it blocks anyway (e.g. extra commits landed on
   `main` before bootstrapping), stop and ask the user to run or approve
   the push — do not work around the hook.
3. If `gh` is available: run
   `scripts/github_setup.sh --areas "<areas>"` — append `--deploy-docs` only
   if the user opted into Pages publishing (interview Q6; default off, and off
   for private projects)
   (creates `development`, makes it default, protection with the shipped
   gates as required checks, labels; a Pages site + deploy only with
   `--deploy-docs`). Do not pass `--require-check` unless deliberately
   overriding the defaults — an explicit list replaces them. Otherwise it's
   the top item of POST_INIT_CHECKLIST.md.
4. Report to the user: what was applied, what's in the checklist, and a
   suggested first move (usually `/epic-kickoff` for the first slice of
   work).
