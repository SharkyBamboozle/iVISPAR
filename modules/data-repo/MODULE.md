# Module: data-repo

The paired data repository — durable home for run artifacts (metrics, plots,
videos, checkpoints), keeping the code repo's history free of binaries. This
is the one module a template mechanism can't deliver: it creates a **second
repo**, which only the bootstrap session can do.

**Apply when:** the project's **binary policy** (decided at bootstrap — see
`modules/README.md` → *Binary policy*) is the strict/split posture AND runs
produce artifacts worth keeping. A small project that ships its binaries as
part of the product (e.g. a static website) takes the in-repo-assets posture
instead and skips this module — the two-repo split is a decision, not a
default. Postures can combine: in-repo website assets and a data repo for
run outputs are not mutually exclusive.

## How to apply (the bootstrap session executes this)

1. **Prepare the seed fully — always, before anything else** — fill
   `{{TOKENS}}` AND resolve the seed's `BLUEPRINT:` judgment markers (the
   artifact-types judgment of step 4 happens NOW): the code repo's
   completion gate never sees the data repo, so an unresolved marker pushed
   here is permanent.
2. **If `gh` is available — create and push now.** Create the repo (name =
   the interviewed `{{DATA_REPO}}` value; default `<slug>-data`):
   `gh repo create {{GITHUB_OWNER}}/{{DATA_REPO}} --private`; push `seed/`
   as its initial commit; then run
   `scripts/github_setup.sh -R {{GITHUB_OWNER}}/{{DATA_REPO}} --profile data`
   (labels + anti-force-push protection; no development branch, no Pages —
   data repos take direct pushes from tooling).
3. **If `gh` is NOT available — defer, but rescue the seed first.**
   BOOTSTRAP step 7 runs `git rm -rf modules/`, which deletes this
   directory — including the prepared `seed/`. Before that happens, move the
   prepared seed out of the delete path:
   `git mv modules/data-repo/seed data-repo-seed` (a root directory step 7
   leaves untouched). Then record in `POST_INIT_CHECKLIST.md` the deferred
   create-and-push, operating on `data-repo-seed/` and ending with
   `git rm -r data-repo-seed` once the push succeeds. Skipping this loses
   the resolved seed permanently — the deferred data repo would have
   nothing to push.
4. **Judgment (Tier 2):** name the project's artifact types in the seed
   README and the ADR (plots? videos? checkpoints?), and decide whether the
   project needs a standard artifact pack per change-class
   (docs/process/records-and-canon.md → *Standard artifact packs & figures*).
5. In the **code repo**:
   - copy `code/data/README.md` to `data/README.md` (the `.gitignore` already
     carries `data/*` + `!data/README.md`);
   - fill the `{{DATA_REPO}}` token wherever it appears (CLAUDE.md hard
     rules, etc.);
   - create the split ADR: next free `D-0NN` from `adr-data-repository.md`
     (this directory), registry row + nav entry per `/adr-new` — the
     payload ships 🟡 Proposed; promote to ✅ later via the normal
     `/unlock-adr` ritual.
6. Post-init checklist items: grant any CI/session integrations access to
   the data repo when runs start publishing.

## Storage decision (already made — blueprint default)

**Plain git blobs, no LFS.** A data repo is mostly binaries; GitHub's free
LFS quota (~1 GiB storage/bandwidth) is a trap for exactly that shape, while
ordinary blobs in a dedicated append-mostly, rarely-cloned repo are fine.
The escalation trigger is written into the seed README: repo > ~2 GB or
clone times hurt → move to LFS or object storage behind the same
configured-output-root seam (paths are config, not code — the move touches
configuration only).
