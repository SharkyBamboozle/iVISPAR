# runs/ — the run-folder contract

One folder per **experiment**: `runs/<experiment-id>/`, self-contained and
shareable on its own. Inside, one sub-folder per **run**, keyed by identity
`(experiment-id, seed, sweep-combo)`.

Each run folder contains:

- **`config.resolved.yaml`** — the **fully-resolved** config that actually
  ran (CLI/dict overrides + the per-run seed/sweep applied), snapshotted at
  launch. The run is reproducible from its own folder; diffing two snapshots
  shows exactly what changed. Every parameter is single-sourced in the config
  — one home per knob.
- **Metrics** — machine-readable (`metrics.jsonl` or equivalent). Durable
  artifacts are the record; live dashboards are off-by-default conveniences
  that must not change results.
- **Checkpoints / outputs** — full-state, so `--resume` can extend a run.
- **A completion marker** (`COMPLETE.json` / `DONE`) — lets any fresh session
  *check* a run instead of watching it.

Experiment-level `aggregate/` holds cross-run plots/videos, re-derived from
whatever runs are present.

**Rules:** runs are **additive and resumable, never destructive** — adding
seeds must not discard prior runs; scaling an experiment is a parameter
change, not a rerun. Evaluation aggregates over what exists.

<!-- BLUEPRINT: name this project's concrete artifact types and any standard
artifact pack per change-class (canonical list lives on one docs page in the
code repo). -->
