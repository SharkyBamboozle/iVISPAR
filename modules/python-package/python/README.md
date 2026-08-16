# python/

The installable package `{{PACKAGE_NAME}}` (src layout). Subpackages mirror
the architecture seams — the future package/service boundaries — each created
as a docstring-only stub pointing at its docs page, and each imported by the
smoke test (`tests/test_package.py`).

| Subpackage | Component | Docs |
|---|---|---|
<!-- BLUEPRINT: one row per seam, e.g.
| `schemas` | engine-neutral contracts | docs/schemas/ |
-->

## Setup

```bash
pip install -e "python[dev]"
```

## Verify — exactly what CI runs (from `python/`)

```bash
python3 -m ruff check .
python3 -m pytest -q
```
