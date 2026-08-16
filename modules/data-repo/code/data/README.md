# Local data (gitignored)

Working directory for run outputs: results, checkpoints, bundles, downloaded
datasets. Everything here except this README is **gitignored** — nothing
under `data/` ever enters git history (see the data-repository ADR in
`docs/decisions/`). The durable home for kept artifacts is the external data
repo **{{DATA_REPO}}**, one folder per experiment; this directory is only a
local staging area. Tooling writes here by default and publishes to the data
repo via a configured output root — paths are config, never hard-coded.
