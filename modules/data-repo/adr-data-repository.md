# ADR-00NN — Run artifacts in a separate data repository

- **Status:** 🟡 Proposed
- **Decision ID:** D-0NN
- **Related requirements:** <!-- reproducibility R##, or "—" -->
- **Related questions:** —
- **Related decisions:** refines D-007 (binary hygiene — implements the strict/split posture's artifact side)

## Context

Runs produce a stream of artifacts — metrics, plots, videos, checkpoints —
that are numerous, often binary, and grow without bound. The code repo's
`data/` is gitignored (D-007), which keeps history clean but leaves kept
artifacts local-only and lost when an environment is reclaimed; committing
them to the code repo (even via LFS) would clutter history, hit quotas, and
couple artifact lifecycle to code review.

## Decision

**Run artifacts live in a separate, dedicated data repository
(`{{DATA_REPO}}`) — never committed to the code repo — organised one folder
per experiment.**

- **Layout:** one self-contained folder per experiment; runs keyed by
  `(experiment-id, seed, sweep-combo)` with a completion marker and a
  `config.resolved.yaml` snapshot (see the data repo's `runs/README.md`).
- **Code repo stays lean:** its `data/` is a gitignored local staging area
  only; nothing binary in its history.
- **Output roots are config:** tooling defaults to local staging and points
  at the data repo to publish; paths are never hard-coded.
- **Storage:** plain git blobs, no LFS; escalation trigger recorded in the
  data repo's README (~2 GB or painful clones → LFS or object storage).

## Consequences

- Code repo history stays small; CI and clones never fetch run outputs.
- A run is reproducible and shareable from its own folder (snapshot + seed).
- Experiments are additive and resumable — scaling is a parameter change,
  not a rerun.
- A second repo to manage — accepted ceremony cost.

## Reversibility / notes

- Artifact paths are config, so redirecting storage (different repo, object
  store, artifact service) touches configuration, not code.
- This refines the blueprint's binary-hygiene rule; it does not alter it.

## References

- Related docs: the data repo's `README.md` and `runs/README.md`
- Related decisions: [ADR-0007](adr-0007-binary-hygiene.md)
