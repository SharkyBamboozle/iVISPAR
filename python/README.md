# python/

The installable package `ivispar` (src layout). Subpackages mirror
the architecture seams — the future package/service boundaries — each created
as a docstring-only stub pointing at its docs page, and each imported by the
smoke test (`tests/test_package.py`).

| Subpackage | Component | Docs |
|---|---|---|
| `agent` | agent policies: VLM adapters, scripted baselines, human | agents section (docs wave) |
| `configuration` | puzzle configuration & dataset generation | experiments section (docs wave) |
| `environment` | environment state & game logic | environments section (docs wave) |
| `evaluation` | metrics, error analysis, plotting | evaluation section (docs wave) |
| `experiment` | runner & action-perception loop | experiments section (docs wave) |
| `models` | episode & data models / formats | data-formats section (docs wave) |
| `utility` | shared helpers | development section (docs wave) |

## Setup

```bash
pip install -e "python[dev]"
```

## Verify — exactly what CI runs (from `python/`)

```bash
python3 -m ruff check .
python3 -m pytest -q
```
