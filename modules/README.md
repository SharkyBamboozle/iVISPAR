# modules/ — optional payloads, applied per project at bootstrap

Each module is a `MODULE.md` (instructions the bootstrap session executes:
what to copy, which tokens to fill, which judgment calls to make) plus
payload files mirroring their destination paths. There is no templating
engine — the bootstrap Claude session is the module engine. This directory
is deleted at instantiation.

| Module | Apply when |
|---|---|
| `python-package` | the project has a Python product/library side |
| `data-repo` | binary policy is **strict/split** (below) and runs produce artifacts worth keeping |
| `lfs-assets` | the project authors/vendors large binary assets in-repo |

## Binary policy — a per-project decision made at bootstrap

Not every project wants the same posture toward binaries. A research platform
must keep run artifacts out of source history; a static website legitimately
ships images and is too small to split in two. **Pick ONE posture at
bootstrap** and wire it in two places — the CLAUDE.md hard rule, and
`.claude/asset-dirs.txt`, the single data file that both enforcement points
(the `guard-git.sh` hook and repo-hygiene CI) read, so hook and CI can never
disagree (D-004). Each carries a `BLUEPRINT:` marker, so the completion gate
blocks until the choice is made.

**1. Strict / split (default).** No binaries in the code repo, ever; durable
run artifacts live in the paired data repo. Apply the `data-repo` module;
fill `{{DATA_REPO}}`; leave the hook/CI allowlists empty. Right for research
platforms, experiment-producing projects, anything long-lived.

**2. In-repo assets.** The project's binaries are part of the product
(website images, game assets, design files). Name the sanctioned asset
directories (e.g. `assets/`, `static/`) and list them, one per line, in
`.claude/asset-dirs.txt`; rewrite the
CLAUDE.md bullet to say binaries live **only** under those directories and
generated artifacts still stay out. Apply `lfs-assets` for large/authored
types; small web images can stay plain git. Files under asset dirs skip the
hygiene checks entirely — size discipline there is a review concern.
Skip the `data-repo` module — or combine postures: in-repo website assets
AND a data repo for run outputs are not mutually exclusive.

**3. Keep the default when unsure.** For small projects with no clear binary
story, posture 1 without the data-repo module (strict rule, no split) is the
cheapest safe choice — the `allow-binaries` PR label remains the explicit
per-case exception, and the posture can be revisited via a superseding ADR.

Record the chosen posture by finalizing **ADR-0007 (binary hygiene)**:
rewrite its Decision section to the chosen posture, flip its status to
✅ Decided, and update its registry row — promotion to ✅ is hook-gated
like every other path to Decided (`guard-adr.sh`): run
`/unlock-adr adr-0007` first — see `BOOTSTRAP.md` step 4.
