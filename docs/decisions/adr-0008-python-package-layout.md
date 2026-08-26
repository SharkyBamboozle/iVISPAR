# ADR-0008 — Python package layout

- **Status:** ✅ Decided
- **Decision ID:** D-008
- **Related requirements:** R2, R4
- **Related questions:** —
- **Related decisions:** refines D-001 (docs mirror the seams); constrained by D-007 (no binaries under `python/`)

## Context

The refactored experiment framework migrates here from the private dev
repository, which grew as loose scripts (`src_python/core/*`) with
hard-coded entry points and no installable package — the packaging gap is a
long-standing dev-tracker item. The migration is the natural moment to fix
the layout once: code should land in its final shape rather than move twice.

## Decision

**One installable src-layout package, `ivispar`, under `python/`, whose
subpackages mirror the runner's architecture seams.**

- Seams (one subpackage each): `agent`, `configuration`, `environment`,
  `evaluation`, `experiment`, `models`, `utility` — the decomposition the
  framework already uses; the smoke test imports every seam, making the
  decomposition an executable contract (enforcer:
  `python/tests/test_package.py` in `make verify` and the path-filtered
  `python.yml` CI).
- Build backend hatchling; `requires-python >= 3.11` (the floor the
  execution environments actually provide); dev extras `pytest` + `ruff`.
- Console entry points (`ivispar-configure` / `ivispar-run` /
  `ivispar-evaluate`) are declared **when the framework wave lands the code
  they call** — a stub entry point that imports nothing real would be a
  false capability claim (D-006).
- `python.yml` is path-filtered and therefore deliberately **not** a
  required status check and **not** in the CI meta-gate's presence list.

## Consequences

- The framework wave relocates dev code into a fixed, reviewed shape — no
  second migration later; `pip install -e "python[dev]"` becomes the one
  setup command.
- Renaming or deleting a seam breaks CI, forcing the ADR conversation
  instead of silent drift.
- Until the framework wave lands, the subpackages are docstring stubs — the
  package installs but does nothing (stated honestly in the README banner).

## Alternatives considered

- **Flat `src_python/` scripts as in the dev repo** — rejected: not
  installable, import-path fragility is the dev tracker's oldest complaint.
- **Package per seam (multi-distribution)** — rejected: one research
  codebase, one version, no independent release cadence to justify it.

## Reversibility / notes

Cheap to adjust until the framework wave lands code into the seams; after
that a seam change is a coordinated refactor (imports + smoke test + docs)
recorded by a superseding ADR. The seam list lives in exactly two places —
the package tree and `SUBPACKAGES` in the smoke test — which CI keeps
honest.

## References

- Related docs: `python/README.md` (subpackage ↔ component table)
- Related decisions: [ADR-0001](adr-0001-documentation-and-records.md), [ADR-0007](adr-0007-binary-hygiene.md)
