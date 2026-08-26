# Changelog

Per-session narrative — the **chronological diary** of the project and its
inter-session memory. One entry per working session, **prepended newest first**
(newest entry directly under the header, `Session N` down to `Session 1` at
the bottom — mirroring `lessons.md`); session numbers are citable IDs
(provenance tags elsewhere read *(Session N)*).

**Entry grammar:** `### Session N (YYYY-MM-DD) — title`, then 3–8 sentences:
what was attempted → what landed (PRs/commits) → what was found (link `note`
issues) → what was decided (link `D-xxx`) → what carries forward.

### Session 1 (2026-08-26) — Re-seeded from Project Blueprint v1.2.0

The repository was re-seeded in place: the EMNLP 2025 tree was retired to the
frozen tag `emnlp25` (with a GitHub Release and a protecting ruleset), and
the Project Blueprint v1.2.0 scaffolding was instantiated on `development`.
Module applied: python-package (package `ivispar`). Binary posture finalized
as D-007: in-repo assets under `unity/` and `docs/assets/` only, plain git, no LFS; generated
artifacts (WebGL app builds) ship as Release assets. First design
principles, requirements, and open questions seeded — see the registries.
The refactored framework migrates from the private dev repository in staged
waves, to be tracked by the migration epic (filed right after this PR
merges — this PR installs the tracker substrate it will use).
