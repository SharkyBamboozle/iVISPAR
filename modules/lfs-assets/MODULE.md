# Module: lfs-assets

Git LFS for **authored binary assets** (3D models, textures, audio, design
files) that genuinely belong in the code repo — as opposed to run artifacts,
which go to the data repo (data-repo module) and are never committed here.

**Apply when:** the project will hand-author or vendor large binary assets
(game/graphics/audio projects). Skip for pure code/docs projects.

## The rule this module enforces

**Configure LFS patterns BEFORE any binaries exist** — the first binary
committed as a plain blob is the point of no return for git history.
Patterns are **scoped per directory** (e.g. `assets/**/*.glb`), never global
(`*.glb`), so a stray binary outside the sanctioned directory is still
caught by the repo-hygiene CI check instead of being silently LFS'd.

## How to apply (the bootstrap session executes this)

1. **Judgment (Tier 2):** pick the asset directories and file types from the
   menu in `.gitattributes` (this directory). The menu ships every line
   commented out — **uncomment the chosen lines** (strip the leading `# `)
   and append them to the repo's **root** `.gitattributes`, **creating the
   file if it does not exist** (the template ships none). Patterns may name
   directories that don't exist yet. Start the created file with a one-line
   comment citing D-007 (binary hygiene), per the config-cites-decision rule
   (`.claude/rules/config-cites-decision.md`).
2. **Verify (mandatory):** for one representative chosen pattern, run
   `git check-attr filter -- <path matching it>` — e.g.
   `git check-attr filter -- assets/example.glb` for the `.glb` line. It
   must print `filter: lfs` before you continue; `filter: unspecified`
   means the chosen lines are still comments, or the file is not at the
   repo root.
3. Reserve LFS for these authored assets only; keep the quota away from run
   outputs (data-repo module) and generated files (`.gitignore`).
4. Post-init checklist items:
   - `git lfs install` — once per machine, before touching LFS paths.
   - Watch the GitHub LFS quota (~1 GiB free storage/bandwidth); budget or
     escalate if asset volume approaches it.
5. Add to `CLAUDE.md` → Repo layout: the asset directory bullet + the
   "Git LFS preconfigured, `git lfs install` once per machine" note.
