# Module: python-package

The `python/` src-layout skeleton: one installable package whose subpackages
mirror the architecture seams, an import smoke test that makes the
decomposition an executable contract, and path-filtered CI.

**Apply when:** the project has a Python product/library side.

## How to apply (the bootstrap session executes this)

1. Copy the payload to the repo root, preserving paths:
   - `python/pyproject.toml`
   - `python/src/{{PACKAGE_NAME}}/__init__.py` — **rename the directory** to
     the real package name
   - `python/tests/test_package.py`
   - `python/README.md`
   - `.github/workflows/python.yml`
2. Fill the Tier-1 token `{{PACKAGE_NAME}}` everywhere (files AND the
   directory name). **Set `requires-python` to the floor the environment
   actually supports** — check `python3 --version` where the project will
   run (the shipped default 3.12 may exceed it; lower to e.g. `>=3.11`),
   and set the CI `python-version` to the same floor (test at the floor).
3. **Judgment (Tier 2):** create one docstring-only subpackage stub per
   architecture seam (`src/<pkg>/<seam>/__init__.py`, one line pointing at
   its docs page), list them in `SUBPACKAGES` in `tests/test_package.py`,
   and fill the subpackage↔docs table in `python/README.md`. Seams are the
   future package/service boundaries — record the layout decision as an ADR.
4. Run `pip install -e "python[dev]"` now — the gate's `make verify`
   (step 5 of BOOTSTRAP.md) runs ruff and pytest, which are not installed
   by anything else.
5. Extend the root `Makefile` verify target — **append** the lines below to
   the *existing* `verify:` recipe; do NOT replace it (the shipped guard
   suites, the `bash -n` pin, and the meta-gate / docs-truth checker steps
   must stay):

   ```make
   # Append to the existing `verify:` recipe. python3 -m binds to the
   # interpreter the package was installed into — bare `pytest`/`ruff` PATH
   # shims (e.g. uv tools) may point elsewhere.
   	cd python && python3 -m ruff check .
   	cd python && python3 -m pytest -q
   ```
   (`mkdocs build --strict` is already in the shipped `verify:` target — don't
   duplicate it.)

6. Add to `CLAUDE.md` → Repo layout: a `python/` bullet naming the package,
   the setup command (`pip install -e "python[dev]"`), and `pytest` /
   `ruff check` as the test/lint commands.
7. **Configure the docs-truth flag/env seam** — this module adds code under
   `python/`, which *arms* the flag/env citation lane of
   `scripts/check_docs_truth.py`. Leaving `.claude/docs-truth.txt` at
   `mode: unconfigured` now FAILS `make verify`. Set it: `mode: configured`
   with `code-root: python/src`, or `mode: off <reason>` if the docs cite no
   CLI flags or env vars yet (the honest early-seed choice — a package with
   no CLI has nothing for the lane to verify). See the seam file's header.
8. Post-init checklist item: none (CI activates on the next push — the
   workflow is path-filtered to `python/**` and itself).

**`python.yml` and the meta-gate / required checks.** The CI meta-gate
(`scripts/check_ci_gates.py`) globs *every* workflow, so once `python.yml`
exists it is validated like the rest — it must fire on PRs into
`development` (its unfiltered `pull_request` branch set already satisfies
this) and carry no `continue-on-error`. Do **not** add `python.yml` to the
meta-gate's required-*presence* list (the hardcoded `docs.yml` /
`repo-hygiene.yml` / `adr-gates.yml` / `security.yml` set): that list is
the always-shipped gates, and requiring an optional module's workflow would
break every seed that omits this module. For the same reason, do **not**
make `python.yml` a *required status check* in branch protection — it is
path-filtered, so on a docs-only PR it never runs and a required check that
never runs leaves the PR stuck pending. (Hardening the meta-gate's required
set so a new always-on gate can't silently escape it is a separate
concern, not addressed here.)
