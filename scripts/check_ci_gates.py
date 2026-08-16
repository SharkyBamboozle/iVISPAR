#!/usr/bin/env python3
"""Meta-gate: pins the verification configuration itself (D-004).

Two layers of wiring, both of which decay silently if unpinned:

1. **CI gates** — parses .github/workflows/*.yml and asserts the gates
   actually fire where work lands, and that nobody has quietly neutered a
   required job with `continue-on-error`. The failure mode this prevents is
   real: a gate filtered to `branches: [main]` while all PRs target the
   integration branch runs never — a checker whose fatal tier never executes
   isn't a gate.
2. **Scaffolding suites** — asserts D-005's "every hook ships a suite,
   every checker ships a --self-test" holds for the *next* one too: every
   PreToolUse hook in .claude/settings.json — deny or approve, .sh or .py —
   has a matching scripts/test_*.sh wired into `make verify`, and every
   scripts/check_* checker has its --self-test wired there. Without this,
   adding a new guard with no suite passes `make verify` unnoticed — the
   very gap it plugs.

Runs inside `make verify` (PyYAML ships with the docs toolchain) and
therefore also in CI on every PR. Failure messages say exactly what to
widen. Deliberate exemption: docs.yml's `deploy` job uses continue-on-error
as a retry ladder for GitHub Pages transients — that is its design, not a
neutered gate.

Self-test: `check_ci_gates.py --self-test` runs both-ways fixtures (each
check proven to fail on bad wiring AND to pass on good) against synthetic
workflow dicts and synthetic scaffolding inventories — no filesystem, no
network (D-005).
"""

import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit(
        "check_ci_gates: PyYAML missing — install the docs toolchain first: "
        "pip install -r docs/requirements.txt"
    )

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF_DIR = os.path.join(ROOT, ".github", "workflows")
SETTINGS_PATH = os.path.join(ROOT, ".claude", "settings.json")
HOOKS_DIR = os.path.join(ROOT, ".claude", "hooks")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
MAKEFILE_PATH = os.path.join(ROOT, "Makefile")

# The gates the template ships (required-presence). A seeded project that
# renames or adds gates updates this list in the same diff — it IS the pin.
REQUIRED_GATES = (
    "docs.yml", "repo-hygiene.yml", "adr-gates.yml", "security.yml",
    "issue-link-guard.yml", "branch-flow-guard.yml", "issue-close-guard.yml",
)

# Workflows whose pull_request `types:` list is load-bearing: GitHub's
# default types omit `edited`, so a gate that must re-check PR-body edits
# (a closing keyword can be added after the first CI run) silently stops
# firing on them if its list is narrowed — or never written.
REQUIRED_PR_TYPES = {
    "issue-link-guard.yml": ("opened", "edited", "reopened", "synchronize"),
}

# Workflows whose `issues:` trigger types are load-bearing: the
# issue-close guard only sees a close if `closed` is in its list — a
# narrowed list (or a dropped trigger) silently kills the gate. An absent
# `types:` means GitHub's default (all types), which includes `closed`.
REQUIRED_ISSUE_TYPES = {
    "issue-close-guard.yml": ("closed",),
}

# (workflow, job) allowed to carry continue-on-error — a first-class D-003
# ledger: a reason per entry, a ceiling, staleness fails loud (an entry whose
# job no longer has continue-on-error is removed, checked in scan()).
CONTINUE_ON_ERROR_EXEMPT = {
    ("docs.yml", "deploy"): "Pages retry ladder — see docs.yml header",
}
CONTINUE_ON_ERROR_CEILING = 3

failures = []


def fail(msg: str) -> None:
    failures.append(msg)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def triggers(wf: dict) -> dict:
    # YAML 1.1 parses the bare key `on` as boolean True.
    raw = wf.get("on", wf.get(True, {}))
    return raw if isinstance(raw, dict) else {name: None for name in (raw or [])}


def pr_branches(wf: dict):
    """None = pull_request trigger absent; [] = unfiltered (all branches)."""
    trig = triggers(wf)
    if "pull_request" not in trig:
        return None
    pr = trig.get("pull_request") or {}
    if not isinstance(pr, dict):
        return []
    return pr.get("branches") or []


def pr_paths(wf: dict):
    """The pull_request `paths:` filter, or None if unfiltered/absent."""
    trig = triggers(wf)
    pr = trig.get("pull_request")
    if not isinstance(pr, dict):
        return None
    return pr.get("paths")


def check_fires_on_integration(name: str, wf: dict) -> None:
    branches = pr_branches(wf)
    if branches is None:
        fail(f"{name}: no pull_request trigger — the gate never runs on PRs.")
    elif branches and "development" not in branches:
        fail(
            f"{name}: pull_request.branches={branches} excludes 'development', "
            "where all feature work lands — widen it (or drop the filter)."
        )


def check_pr_types(name: str, wf: dict) -> None:
    """A workflow in REQUIRED_PR_TYPES must list every required pull_request
    event type — absence of `types:` means GitHub's default set, which drops
    `edited`."""
    required = REQUIRED_PR_TYPES.get(name)
    if not required:
        return
    pr = triggers(wf).get("pull_request")
    types = pr.get("types") if isinstance(pr, dict) else None
    missing = [t for t in required if t not in (types or [])]
    if missing:
        fail(
            f"{name}: pull_request 'types:' must include {list(required)} — "
            f"missing {missing}. GitHub's default types omit 'edited', so a "
            "narrowed (or absent) list silently stops re-checking PR-body "
            "edits."
        )


def check_issue_types(name: str, wf: dict) -> None:
    """A workflow in REQUIRED_ISSUE_TYPES must trigger on `issues` and, if it
    narrows `types:`, keep every required type — else the gate never
    fires. No `types:` list = GitHub's default = all types = fine."""
    required = REQUIRED_ISSUE_TYPES.get(name)
    if not required:
        return
    trig = triggers(wf)
    if "issues" not in trig:
        fail(
            f"{name}: no `issues:` trigger — the issue-close gate never runs. "
            "Restore `on: issues: types: [closed]`."
        )
        return
    iss = trig.get("issues")
    types = iss.get("types") if isinstance(iss, dict) else None
    if types is None:
        return  # default types include every required one
    missing = [t for t in required if t not in types]
    if missing:
        fail(
            f"{name}: `issues:` 'types:' must include {list(required)} — "
            f"missing {missing}; a narrowed list silently kills the gate."
        )


def check_not_paths_neutered(name: str, wf: dict) -> None:
    # A required gate must run on EVERY PR into the integration branch; a
    # pull_request `paths:` filter silently skips it on PRs that don't touch
    # those paths — the paths-filter neutering this catch guards against.
    if pr_paths(wf):
        fail(
            f"{name}: a required gate carries a pull_request 'paths:' filter, so "
            "it skips PRs that don't touch those paths — a gate that can be "
            "path-filtered off checks nothing on the PRs it misses. Drop the "
            "paths filter (optional/module workflows may keep one; required "
            "gates may not)."
        )


def check_no_continue_on_error(name: str, wf: dict) -> set:
    """Fail on any un-exempted continue-on-error. Returns the set of exempt
    (name, job) keys actually hit — scan() uses it to catch stale exemptions."""
    hits = set()
    for job_name, job in (wf.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        if (name, job_name) in CONTINUE_ON_ERROR_EXEMPT:
            # The exemption covers continue-on-error at the job OR step level
            # (docs.yml's deploy retry ladder is step-level); either counts as
            # the exemption being used, so it isn't flagged stale.
            steps_coe = any(
                isinstance(s, dict) and s.get("continue-on-error")
                for s in (job.get("steps") or [])
            )
            if job.get("continue-on-error") or steps_coe:
                hits.add((name, job_name))
            continue
        if job.get("continue-on-error"):
            fail(
                f"{name}: job '{job_name}' has continue-on-error — a gate that "
                "cannot fail checks nothing. Remove it, or add a documented "
                "exemption to CONTINUE_ON_ERROR_EXEMPT with its reason."
            )
        for step in job.get("steps") or []:
            if isinstance(step, dict) and step.get("continue-on-error"):
                label = step.get("name", "<unnamed step>")
                fail(
                    f"{name}: step '{label}' in job '{job_name}' has "
                    "continue-on-error — same rule as above."
                )
    return hits


def validate_coe_ledger(ledger=None, ceiling=CONTINUE_ON_ERROR_CEILING) -> list:
    """Static D-003 checks on the continue-on-error ledger: a non-empty reason
    per entry, and a ceiling. (Staleness is checked in scan() against the
    actual workflows.)"""
    ledger = CONTINUE_ON_ERROR_EXEMPT if ledger is None else ledger
    problems = []
    if len(ledger) > ceiling:
        problems.append(
            f"CONTINUE_ON_ERROR_EXEMPT has {len(ledger)} entries, ceiling is "
            f"{ceiling} — raising it is a deliberate diff with a reason (D-004)."
        )
    for key, reason in ledger.items():
        if not (reason or "").strip():
            problems.append(f"{key}: continue-on-error exemption has no reason (D-004).")
    return problems


# --------------------------------------------------- scaffolding suite wiring

def pretooluse_hooks_from_settings(settings: dict) -> list:
    """Basenames of hook scripts registered under PreToolUse — the tier that
    can deny OR auto-approve a tool call. Keying off registration (not the
    guard-* name) catches a hook whatever it is called; matching .sh and .py
    catches it whatever it is written in (an unpinned approve-hook decays as
    silently as an unpinned deny-hook)."""
    names = []
    for entry in settings.get("hooks", {}).get("PreToolUse") or []:
        for hook in entry.get("hooks") or []:
            m = re.search(r"/hooks/([A-Za-z0-9_.-]+\.(?:sh|py))", hook.get("command", ""))
            if m:
                names.append(m.group(1))
    return sorted(set(names))


def expected_suite(hook_basename: str) -> str:
    """guard-git.sh -> test_guard_git.sh (hyphens become underscores). A .py
    hook maps the same way — its suite is still a bash script, driving the
    hook through its real JSON-on-stdin channel."""
    stem = re.sub(r"\.(?:sh|py)$", "", hook_basename)
    return "test_" + stem.replace("-", "_") + ".sh"


def check_scaffolding_wired(hooks, checkers, script_files, makefile_text) -> list:
    """Pure D-005 wiring check (plain data in, problems out, for hermetic
    self-testing): every PreToolUse hook (deny or approve) has a suite that
    exists AND runs in `make verify`; every checker's --self-test runs there
    too."""
    problems = []
    have = set(script_files)
    for hook in hooks:
        suite = expected_suite(hook)
        if suite not in have:
            problems.append(
                f"PreToolUse hook '{hook}' has no regression suite: expected "
                f"scripts/{suite} asserting both sides — deny/still-allowed "
                "for a deny-hook, approve/defer for an approve-hook (D-005)."
            )
        elif suite not in makefile_text:
            problems.append(
                f"hook suite scripts/{suite} exists but is not wired into "
                "`make verify` — a suite that never runs guards nothing (D-005)."
            )
    for checker in checkers:
        if f"{checker} --self-test" not in makefile_text:
            problems.append(
                f"checker scripts/{checker} has no --self-test wired into "
                "`make verify` (D-005: every checker ships a --self-test that "
                "runs in the gate)."
            )
    # Every scripts/test_* file must run inside `make verify` — a suite that
    # never runs guards nothing (D-005). This widens the deny-hook rule to
    # ALL test scripts, whatever their language: e.g. the shared
    # guard-parser pin (test_guardlib.py) is not derivable from any hook
    # basename, so only this pin keeps it wired.
    for test in sorted(f for f in script_files if f.startswith("test_")):
        if test not in makefile_text:
            problems.append(
                f"test script scripts/{test} is not wired into `make verify` "
                "— a suite that never runs guards nothing (D-005)."
            )
    return problems


def scan_scaffolding() -> list:
    """Gather the real inventory from disk and run check_scaffolding_wired."""
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            settings = json.load(f)
    except (OSError, ValueError) as e:
        return [f".claude/settings.json unreadable ({e}) — cannot pin hook suites."]
    hooks = pretooluse_hooks_from_settings(settings)
    script_files = (
        {os.path.basename(p) for p in glob.glob(os.path.join(SCRIPTS_DIR, "*.sh"))}
        | {os.path.basename(p) for p in glob.glob(os.path.join(SCRIPTS_DIR, "*.py"))}
    )
    checkers = sorted(
        f for f in script_files if f.startswith("check_") and f.endswith((".py", ".sh"))
    )
    try:
        with open(MAKEFILE_PATH, encoding="utf-8") as f:
            makefile_text = f.read()
    except OSError as e:
        return [f"Makefile unreadable ({e}) — cannot pin scaffolding wiring."]
    return check_scaffolding_wired(hooks, checkers, script_files, makefile_text)


# -------------------------------------------------------------- self-test

def self_test() -> int:
    """Both-ways fixtures per check — a checker that cannot fail checks
    nothing, and one that always fails gates nothing (D-005)."""
    problems = []

    def scenario(label: str, expect_fail: bool, run) -> None:
        failures.clear()
        run()
        if expect_fail and not failures:
            problems.append(f"{label}: expected a failure, got a clean pass")
        if not expect_fail and failures:
            problems.append(f"{label}: expected a clean pass, got {failures}")

    # Parsing: YAML 1.1 reads a bare `on:` key as boolean True — triggers()
    # must find the pull_request block behind that trap.
    wf = yaml.safe_load("on:\n  pull_request:\n    branches: [main]\njobs: {}\n")
    if pr_branches(wf) != ["main"]:
        problems.append("parse: YAML-1.1 `on:`-as-True key not handled by triggers()")
    if pr_branches({"on": {"push": None}}) is not None:
        problems.append("parse: absent pull_request trigger must read as None")

    scenario("fires/deny: no pull_request trigger", True,
             lambda: check_fires_on_integration("t.yml", {"on": {"push": None}}))
    scenario("fires/deny: branch filter excludes development", True,
             lambda: check_fires_on_integration(
                 "t.yml", {"on": {"pull_request": {"branches": ["main"]}}}))
    scenario("fires/allow: unfiltered pull_request", False,
             lambda: check_fires_on_integration("t.yml", {"on": {"pull_request": None}}))
    scenario("fires/allow: filter includes development", False,
             lambda: check_fires_on_integration(
                 "t.yml", {"on": {"pull_request": {"branches": ["development"]}}}))

    scenario("types/deny: pinned workflow with no types list", True,
             lambda: check_pr_types(
                 "issue-link-guard.yml", {"on": {"pull_request": None}}))
    scenario("types/deny: pinned workflow missing 'edited'", True,
             lambda: check_pr_types(
                 "issue-link-guard.yml",
                 {"on": {"pull_request": {"types": ["opened", "synchronize"]}}}))
    scenario("types/allow: pinned workflow with the full list", False,
             lambda: check_pr_types(
                 "issue-link-guard.yml",
                 {"on": {"pull_request": {"types":
                     ["opened", "edited", "reopened", "synchronize"]}}}))
    scenario("types/allow: unpinned workflow ignored", False,
             lambda: check_pr_types("docs.yml", {"on": {"pull_request": None}}))

    scenario("issue-types/deny: pinned workflow with no issues trigger", True,
             lambda: check_issue_types(
                 "issue-close-guard.yml", {"on": {"push": None}}))
    scenario("issue-types/deny: types list missing 'closed'", True,
             lambda: check_issue_types(
                 "issue-close-guard.yml",
                 {"on": {"issues": {"types": ["opened", "labeled"]}}}))
    scenario("issue-types/allow: types list carries 'closed'", False,
             lambda: check_issue_types(
                 "issue-close-guard.yml", {"on": {"issues": {"types": ["closed"]}}}))
    scenario("issue-types/allow: bare issues trigger (default types)", False,
             lambda: check_issue_types(
                 "issue-close-guard.yml", {"on": {"issues": None}}))
    scenario("issue-types/allow: unpinned workflow ignored", False,
             lambda: check_issue_types("docs.yml", {"on": {"push": None}}))

    scenario("coe/deny: job-level continue-on-error", True,
             lambda: check_no_continue_on_error(
                 "t.yml", {"jobs": {"j": {"continue-on-error": True}}}))
    scenario("coe/deny: step-level continue-on-error", True,
             lambda: check_no_continue_on_error(
                 "t.yml", {"jobs": {"j": {"steps": [
                     {"name": "s", "continue-on-error": True}]}}}))
    scenario("coe/allow: clean job", False,
             lambda: check_no_continue_on_error(
                 "t.yml", {"jobs": {"j": {"steps": [{"run": "true"}]}}}))
    scenario("coe/allow: documented exemption honored", False,
             lambda: check_no_continue_on_error(
                 "docs.yml", {"jobs": {"deploy": {"continue-on-error": True}}}))

    # A required gate must not be paths-neutered.
    scenario("paths/deny: required gate paths-filtered", True,
             lambda: check_not_paths_neutered(
                 "docs.yml", {"on": {"pull_request": {"paths": ["docs/**"]}}}))
    scenario("paths/allow: no paths filter", False,
             lambda: check_not_paths_neutered("docs.yml", {"on": {"pull_request": None}}))

    # The continue-on-error exemption is a D-003 ledger.
    if not validate_coe_ledger({("a.yml", "j"): ""}):
        problems.append("coe-ledger/deny: empty reason not rejected")
    if not validate_coe_ledger({("a.yml", "1"): "r", ("b.yml", "2"): "r"}, ceiling=1):
        problems.append("coe-ledger/deny: ceiling not enforced")
    if validate_coe_ledger({("a.yml", "j"): "a real reason"}):
        problems.append("coe-ledger/allow: valid entry rejected")

    # Scaffolding-suite wiring: every PreToolUse hook (deny or approve, .sh
    # or .py) has a wired suite, every checker a wired --self-test. Pure
    # function, so synthetic inventories.
    _settings = {"hooks": {"PreToolUse": [
        {"hooks": [{"command": 'bash "$D/.claude/hooks/guard-git.sh"'}]},
        {"hooks": [{"command": 'bash "$D/.claude/hooks/guard-adr.sh"'}]},
        {"hooks": [{"command": 'python3 "$D/.claude/hooks/guard-command-policy.py"'}]},
    ]}}
    if pretooluse_hooks_from_settings(_settings) != [
            "guard-adr.sh", "guard-command-policy.py", "guard-git.sh"]:
        problems.append("scaffold: hooks not extracted from PreToolUse registration (.sh + .py)")
    _good_mk = ("bash scripts/test_guard_git.sh\nbash scripts/test_guard_adr.sh\n"
                "python3 scripts/check_ci_gates.py --self-test\n")
    _scripts = {"test_guard_git.sh", "test_guard_adr.sh", "check_ci_gates.py"}
    if check_scaffolding_wired(["guard-git.sh", "guard-adr.sh"], ["check_ci_gates.py"],
                               _scripts, _good_mk):
        problems.append("scaffold/allow: fully-wired inventory rejected")
    if not any("no regression suite" in p for p in check_scaffolding_wired(
            ["guard-new.sh"], [], _scripts, _good_mk)):
        problems.append("scaffold/deny: new deny-hook with no suite escaped")
    if not any("no regression suite" in p for p in check_scaffolding_wired(
            ["guard-command-policy.py"], [], _scripts, _good_mk)):
        problems.append("scaffold/deny: .py PreToolUse hook with no suite escaped")
    if check_scaffolding_wired(
            ["guard-command-policy.py"], [],
            _scripts | {"test_guard_command_policy.sh"},
            _good_mk + "bash scripts/test_guard_command_policy.sh\n"):
        problems.append("scaffold/allow: wired .py hook suite rejected")
    if not any("not wired" in p for p in check_scaffolding_wired(
            ["guard-git.sh"], [], _scripts | {"test_guard_git.sh"},
            "python3 scripts/check_ci_gates.py --self-test\n")):
        problems.append("scaffold/deny: unwired existing suite escaped")
    if not any("self-test" in p for p in check_scaffolding_wired(
            [], ["check_new.py"], _scripts, _good_mk)):
        problems.append("scaffold/deny: checker with no wired --self-test escaped")
    if not any("not wired" in p for p in check_scaffolding_wired(
            [], [], _scripts | {"test_guardlib.py"}, _good_mk)):
        problems.append("scaffold/deny: unwired non-hook test script escaped")
    if check_scaffolding_wired(
            [], [], _scripts | {"test_guardlib.py"},
            _good_mk + "python3 scripts/test_guardlib.py\n"):
        problems.append("scaffold/allow: wired non-hook test script rejected")

    # scan() applies the checks to EVERY workflow, not a hardcoded list.
    import tempfile
    ok = "on:\n  pull_request:\njobs:\n  j:\n    steps:\n      - run: 'true'\n"
    sec = ("on:\n  pull_request:\n  schedule:\n    - cron: '0 0 * * 0'\n"
           "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
    bfg = ("on:\n  pull_request:\n    branches: [main]\n"
           "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
    ilg = ("on:\n  pull_request:\n    types: [opened, edited, reopened, synchronize]\n"
           "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
    icg = ("on:\n  issues:\n    types: [closed]\n"
           "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
    # docs.yml carries the exempted deploy job so the ledger entry isn't stale.
    docs = ("on:\n  pull_request:\njobs:\n  build:\n    steps:\n      - run: 'true'\n"
            "  deploy:\n    continue-on-error: true\n    steps:\n      - run: 'true'\n")
    with tempfile.TemporaryDirectory() as d:
        wfd = os.path.join(d, ".github", "workflows")
        os.makedirs(wfd)
        def w(n, c):
            with open(os.path.join(wfd, n), "w", encoding="utf-8") as fh:
                fh.write(c)
        w("docs.yml", docs); w("repo-hygiene.yml", ok); w("adr-gates.yml", ok)
        w("security.yml", sec); w("branch-flow-guard.yml", bfg)
        w("issue-link-guard.yml", ilg); w("issue-close-guard.yml", icg)
        failures.clear(); scan(wfd)
        if failures:
            problems.append(f"scan/allow: clean fixture set failed: {list(failures)}")
        # A narrowed issues-types pinned gate must fail the live scan too.
        w("issue-close-guard.yml", "on:\n  issues:\n    types: [opened]\n"
          "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
        failures.clear(); scan(wfd)
        if not any("issues" in f and "types" in f for f in failures):
            problems.append("scan/deny: a types-narrowed issue-close gate escaped")
        w("issue-close-guard.yml", icg)
        # A types-narrowed pinned gate must fail the live scan, not just the
        # unit check.
        w("issue-link-guard.yml", "on:\n  pull_request:\n    types: [opened]\n"
          "jobs:\n  j:\n    steps:\n      - run: 'true'\n")
        failures.clear(); scan(wfd)
        if not any("types" in f for f in failures):
            problems.append("scan/deny: a types-narrowed pinned gate escaped")
        w("issue-link-guard.yml", ilg)
        w("throwaway.yml", "on:\n  pull_request:\njobs:\n  j:\n    "
          "continue-on-error: true\n    steps:\n      - run: 'true'\n")
        failures.clear(); scan(wfd)
        if not any("throwaway" in f for f in failures):
            problems.append("scan/deny: a new workflow's continue-on-error escaped")
        os.remove(os.path.join(wfd, "throwaway.yml"))
        w("docs.yml", "on:\n  pull_request:\n    paths: [docs/**]\njobs:\n  "
          "build:\n    steps:\n      - run: 'true'\n  deploy:\n    "
          "continue-on-error: true\n    steps:\n      - run: 'true'\n")
        failures.clear(); scan(wfd)
        if not any("docs.yml" in f and "paths" in f for f in failures):
            problems.append("scan/deny: paths-neutered required gate escaped")
        w("docs.yml", ok)  # remove the exempted deploy job -> exemption goes stale
        failures.clear(); scan(wfd)
        if not any("stale" in f for f in failures):
            problems.append("scan/deny: stale continue-on-error exemption not caught")

    failures.clear()
    if problems:
        print("check_ci_gates --self-test: FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("check_ci_gates --self-test: OK (all scenarios pass, both ways per check)")
    return 0


# ------------------------------------------------------------------- scan

def scan(wf_dir: str) -> int:
    """Audit every workflow in wf_dir; append to `failures`. Returns the count
    of workflows scanned (0 = none found, itself a failure)."""
    wf_paths = sorted(glob.glob(os.path.join(wf_dir, "*.yml")))
    if not wf_paths:
        fail("no workflows found — nothing to pin.")
        return 0
    names = {os.path.basename(p) for p in wf_paths}

    for required in REQUIRED_GATES:
        if required not in names:
            fail(f"{required}: workflow missing — the template ships this gate.")

    coe_hits = set()
    for path in wf_paths:
        name = os.path.basename(path)
        wf = load(path)

        # continue-on-error is forbidden in EVERY workflow (a new gate can't
        # escape by being unknown to this checker) — closing the unknown-workflow escape.
        coe_hits |= check_no_continue_on_error(name, wf)

        if name == "branch-flow-guard.yml":
            # The promotion guard fires on PRs into main, not development.
            branches = pr_branches(wf)
            if branches is None or (branches and "main" not in branches):
                fail(
                    "branch-flow-guard.yml: must trigger on pull_request into "
                    "'main' — that is the promotion rule it guards."
                )
            continue

        # Every other pull_request-triggered workflow must fire on integration
        # PRs; required gates must additionally not be paths-neutered. Optional
        # module workflows (e.g. python.yml) may be path-filtered.
        if "pull_request" in triggers(wf):
            check_fires_on_integration(name, wf)
        check_pr_types(name, wf)
        check_issue_types(name, wf)
        if name in REQUIRED_GATES:
            check_not_paths_neutered(name, wf)
        if name == "security.yml" and "schedule" not in triggers(wf):
            fail(
                "security.yml: no schedule trigger — advisories arrive on their "
                "own clock; keep the weekly cron."
            )

    # D-003 ledger: continue-on-error exemptions carry reasons + a ceiling, and
    # a stale exemption (its job no longer has continue-on-error) fails loud.
    for problem in validate_coe_ledger():
        fail(problem)
    for key in CONTINUE_ON_ERROR_EXEMPT:
        if key not in coe_hits:
            fail(
                f"continue-on-error exemption {key} is stale — that job no "
                "longer has continue-on-error; remove the exemption (D-004 "
                "ledger: the frontier only moves one way)."
            )
    return len(wf_paths)


# ------------------------------------------------------------------- main

def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    count = scan(WF_DIR)
    for problem in scan_scaffolding():
        fail(problem)
    if failures:
        print("check_ci_gates: FAIL")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    print(f"check_ci_gates: OK ({count} workflows + scaffolding wiring pinned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
