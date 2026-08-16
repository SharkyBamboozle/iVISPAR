#!/usr/bin/env python3
"""Docs truth-checker: fails when docs claim things that are no longer true.

Part of `make verify` (D-004; the no-silent-lanes doctrine — a dormant lane owns its
activation condition). The strict mkdocs build validates markdown *links*; this checks
the mechanically verifiable *claims* docs make, in seven lanes:

  A. Dead path citations (always on) — a backtick-cited repo path in the
     docs must exist on disk. Docs rot is usually introduced by NON-doc
     changes (a rename in a code PR); since this runs inside `make verify`
     on every PR of any kind, the renaming PR itself goes red.
  B. Issue-state drift (on when GitHub is reachable; NEVER guesses) — a
     doc line citing an issue as open fails once that issue is closed.
     Offline / no-`gh` degrades to a silent skip; CI arms it by exporting
     GH_TOKEN in docs.yml's verify step, so the lane is CI-strength there.
  C. Flag / env-var citations (config seam, self-arming) — cited `--flags`
     and PREFIX_* env vars must exist in the project's code. A template
     has no code, so this lane reads .claude/docs-truth.txt. THE LANE OWNS
     ITS ACTIVATION CONDITION: while unconfigured, it fails loudly the
     moment project code manifestly exists (root manifest or src/ dir) —
     "silently unconfigured forever" is not a reachable state. `mode: off`
     requires a written reason (D-004 advisory declaration).
  D. Cross-artifact registry consistency (always on; dormant only when the
     tree has no decisions system, e.g. self-test fixtures) — the docs must
     agree with EACH OTHER about the typed-ID structure: registry row and
     ADR page carry the same status; every ADR page has a registry row, an
     existing link target, and an mkdocs nav entry (and vice versa);
     `D-###` IDs and ADR file numbers are unique (stable IDs are never
     reused — two branches claiming the same number must fail loud, not
     merge into a collision); IDs cited in ADR "Related ..." headers exist
     in their registries; a `Q##` marked ✅ names what resolved it.
     Deliberately mechanical-only: whether a claim is still semantically
     true is judgment work and stays out of the merge gate. HTML comments
     are stripped before parsing (templates embed example rows in them).
  E. Epic-page status vs issue state (same reachability posture as
     lane B — NEVER guesses) — an epic page under docs/records/epics/
     whose status line says in-progress (🟡/🔴) must cite an OPEN epic
     issue. A closed issue behind an in-progress page means the epic was
     wrongly closed (e.g. a PR's closing keyword slipped past the
     issue-link guard via a path no PR event covers — a sidebar link added
     after CI, a direct push) or the page went stale; either way the docs
     no longer tell the truth, and this lane surfaces it on the next run.
  F. Built-but-open sub-issues (same posture — NEVER guesses) — a
     bullet under an epic page's "What has been built" section leads with
     its sub-issue number (epic-page-template); a bullet-leading #N whose
     issue is still OPEN means the page claims done work the tracker
     denies — the mirror of lane E, catching the under-closing direction
     (close the issue with its readout, or don't list it as built yet).
     Bullet-leading refs only: mid-line refs may legitimately cite PRs.
  G. Blueprint-only: session records written into shipped stubs (armed
     only while blueprint/ exists — i.e. in the template repo, and in a
     seed until bootstrap deletes the machinery). docs/records/changelog.md
     and docs/records/lessons.md ship to seeded projects as EMPTY STUBS;
     while the template is being authored they are not its diary, so a
     session entry or a dated lesson written there reaches every seed as
     false history — a diary of a project the reader never worked on. The
     bootstrap gate cannot see it (the text carries neither an unfilled
     placeholder token nor an unresolved judgment marker), hence this lane.
     Same posture as lane C: the lane owns its activation condition, and it
     self-disarms permanently once blueprint/ is deleted — a bootstrapped
     project's records are its own. Rule + rationale: CONTRIBUTING.md ->
     Two hats.

Exemptions live in KNOWN_EXEMPT below and follow the ledger rules (D-004):
a reason per entry, a ceiling, itemized matching, and STALE ENTRIES FAIL —
an exemption that no longer matches anything must be removed.

Self-test: `check_docs_truth.py --self-test` runs both-ways fixtures
(each lane proven to fail AND to pass) without touching the network.
"""

import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- config --

# Doc surfaces scanned. docs/.templates/ is excluded below via the ledger.
DOC_GLOBS_DIRS = ["docs"]
# AGENTS.md joins CLAUDE.md as an agent entry point (it points other agents at
# CLAUDE.md), so its path citations are truth-checked like its siblings.
DOC_ROOT_FILES = [
    "CLAUDE.md", "AGENTS.md", "README.md", "BOOTSTRAP.md", "HARVEST.md",
    "UPDATE.md", "ADOPT.md", "CONTRIBUTING.md",
]

# A citation is treated as a repo path only if it starts with one of these
# directories or exactly names one of these root files.
TOP_DIRS = {"docs", "scripts", "modules", "blueprint", ".claude", ".github"}
ROOT_FILES = {
    "CLAUDE.md", "AGENTS.md", "README.md", "BOOTSTRAP.md", "HARVEST.md",
    "UPDATE.md", "ADOPT.md", "CONTRIBUTING.md", "LICENSE",
    "Makefile", "mkdocs.yml", ".gitignore", ".gitleaks.toml",
}

# Placeholder fragments that mark a citation as illustrative, not a claim.
PLACEHOLDER_FRAGMENTS = ("NN", "XX", "xxx", "###", "...", "…")

SEAM_FILE = os.path.join(".claude", "docs-truth.txt")

# Evidence that the project now has real code (lane C's self-arming
# condition). Extend deliberately, not casually — false arming annoys,
# but a missed manifest means a silent lane.
CODE_MANIFESTS = (
    "pyproject.toml", "setup.py", "package.json", "Cargo.toml",
    "go.mod", "CMakeLists.txt", "pom.xml", "build.gradle",
)
CODE_DIRS = ("src", "lib", "app", "pkg")

# ------------------------------------------------- exemption ledger (D-004)

# Itemized entries: (lane, file fragment, citation fragment, reason).
# Ceiling + staleness ratchet enforced in main(). NEVER add a blanket
# directory/category pass here — restructure the doc instead.
KNOWN_EXEMPT = [
    ("path", "docs/.templates/", "*", "reusable skeletons: their citations are placeholders by design"),
]
KNOWN_EXEMPT_CEILING = 15


def exempt(lane: str, path: str, citation: str):
    # Ledger fragments are POSIX-style; callers pass os.path.relpath output,
    # which renders with os.sep — normalize so exemptions match on Windows
    # too. Backslashes are replaced unconditionally, not via os.sep: os.sep
    # is "/" where CI runs, so an os.sep-based replace would be a no-op there
    # and no self-test fixture could catch its removal.
    path = path.replace("\\", "/")
    for i, (l, file_frag, cite_frag, _reason) in enumerate(KNOWN_EXEMPT):
        if l != lane:
            continue
        if file_frag not in path:
            continue
        if cite_frag != "*" and cite_frag not in citation:
            continue
        return i
    return None


# ----------------------------------------------------------------- helpers

def doc_files(root: str):
    out = []
    for d in DOC_GLOBS_DIRS:
        base = os.path.join(root, d)
        for dirpath, _dirnames, filenames in os.walk(base):
            for f in filenames:
                if f.endswith(".md"):
                    out.append(os.path.join(dirpath, f))
    for f in DOC_ROOT_FILES:
        p = os.path.join(root, f)
        if os.path.isfile(p):
            out.append(p)
    return sorted(out)


CITATION_RE = re.compile(r"`([^`\n]+)`")
PATH_TOKEN_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")


def path_citations(text: str):
    """Backtick tokens that read as repo-path claims."""
    for m in CITATION_RE.finditer(text):
        tok = m.group(1).strip()
        if not PATH_TOKEN_RE.match(tok):
            continue  # spaces, <angle>, {{token}}, → arrows: illustrative
        if any(frag in tok for frag in PLACEHOLDER_FRAGMENTS):
            continue
        if "/" in tok:
            head = tok.split("/", 1)[0]
            if head in TOP_DIRS:
                yield tok
        elif tok in ROOT_FILES:
            yield tok


ISSUE_OPEN_CLAIM_RE = re.compile(
    r"(?i)(?:TODO\(#(\d+)\)"
    r"|(?:issue\s+)?#(\d+)[^\n]{0,40}?\b(?:still open|remains open|\(open\))"
    r"|\bopen issue\s+#(\d+))"
)


def issue_open_claims(text: str):
    for m in ISSUE_OPEN_CLAIM_RE.finditer(text):
        num = next(g for g in m.groups() if g)
        yield int(num), m.group(0).strip()


def gh_issue_state(number: int):
    """Real resolver: None = unknown (offline / not an issue) — NEVER guess."""
    fake = os.environ.get("DOCS_TRUTH_FAKE_ISSUES")
    if fake is not None:  # deterministic self-test injection
        table = dict(p.split(":") for p in fake.split(",") if p)
        return table.get(str(number))
    try:
        out = subprocess.run(
            ["gh", "issue", "view", str(number), "--json", "state", "-q", ".state"],
            capture_output=True, text=True, timeout=15, cwd=ROOT,
        )
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


# ------------------------------------------------------------ lane C seam

def parse_seam(root: str):
    """Returns dict: mode, reason, code_roots, env_prefix, commands."""
    cfg = {"mode": "unconfigured", "reason": "", "code_roots": [],
           "env_prefix": "", "commands": []}
    path = os.path.join(root, SEAM_FILE)
    if not os.path.isfile(path):
        return cfg
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, val = (s.strip() for s in line.split(":", 1))
            if key == "mode":
                parts = val.split(None, 1)
                cfg["mode"] = parts[0]
                cfg["reason"] = parts[1] if len(parts) > 1 else ""
            elif key == "code-root":
                cfg["code_roots"].append(val)
            elif key == "env-prefix":
                cfg["env_prefix"] = val
            elif key == "command":
                cfg["commands"].append(val)
    return cfg


# Immediate subdirs never counted as project code: repo machinery, docs, and
# blueprint scaffolding (the last two deleted at bootstrap). Everything else
# one level down IS scanned, so a module that installs code under a subdir
# (python-package: python/pyproject.toml + python/src/) still self-arms.
NON_CODE_SUBDIRS = frozenset({
    "docs", "site", "scripts", "modules", "blueprint",
    "node_modules", "__pycache__",
})


def project_code_evidence(root: str):
    # Root-level manifest or src-style directory.
    for m in CODE_MANIFESTS:
        if os.path.isfile(os.path.join(root, m)):
            return m
    for d in CODE_DIRS:
        if os.path.isdir(os.path.join(root, d)):
            return d + "/"
    # One level down: the blueprint's reference module layout installs code
    # under a subdir, so a root-only check leaves the self-arming lane dormant
    # under the very layout the blueprint ships.
    try:
        subs = sorted(os.listdir(root))
    except OSError:
        return None
    for sub in subs:
        p = os.path.join(root, sub)
        if sub.startswith(".") or sub in NON_CODE_SUBDIRS or not os.path.isdir(p):
            continue
        for m in CODE_MANIFESTS:
            if os.path.isfile(os.path.join(p, m)):
                return f"{sub}/{m}"
        for d in CODE_DIRS:
            if os.path.isdir(os.path.join(p, d)):
                return f"{sub}/{d}/"
    return None


def code_corpus(root: str, code_roots):
    chunks = []
    for cr in code_roots:
        base = os.path.join(root, cr)
        for dirpath, _dirnames, filenames in os.walk(base):
            for f in filenames:
                p = os.path.join(dirpath, f)
                try:
                    if os.path.getsize(p) > 1_000_000:
                        continue
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        chunks.append(fh.read())
                except OSError:
                    continue
    return "\n".join(chunks)


FLAG_RE = re.compile(r"--[a-z0-9][a-z0-9-]*")


# ------------------------------------------- lane D: registry consistency

STATUS_EMOJI = ("✅", "🟡", "🔴", "🧊")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _first_status_emoji(s: str):
    for ch in s:
        if ch in STATUS_EMOJI:
            return ch
    return None


def _read_stripped(path: str) -> str:
    """File text with HTML comments removed — templates and registries embed
    example rows inside comments; those are illustrations, never claims."""
    with open(path, encoding="utf-8") as f:
        return HTML_COMMENT_RE.sub("", f.read())


def lane_d_consistency(root: str, issues: list):
    dec_dir = os.path.join(root, "docs", "decisions")
    index_p = os.path.join(dec_dir, "index.md")
    adr_files = []
    if os.path.isdir(dec_dir):
        adr_files = sorted(
            f for f in os.listdir(dec_dir) if re.match(r"adr-\d+.*\.md$", f)
        )
    if not os.path.isfile(index_p):
        if adr_files:  # pages without their registry: fail loud, never green
            issues.append(
                "[consistency] docs/decisions/ has ADR pages but no index.md "
                "registry — restore the registry; pages and registry are a pair."
            )
        return  # dormant: this tree has no decisions system (e.g. fixtures)

    # Registry rows: | D-### | statement | status | [ADR-…](file.md) |
    rows = []
    seen_ids = {}
    for ln, line in enumerate(_read_stripped(index_p).splitlines(), 1):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not re.fullmatch(r"D-\d+", cells[0]):
            continue
        rid = cells[0]
        if rid in seen_ids:
            issues.append(
                f"[consistency] docs/decisions/index.md: duplicate registry ID "
                f"{rid} (rows {seen_ids[rid]} and {ln}) — stable IDs are never "
                "reused; renumber the newer decision to the next free ID."
            )
        seen_ids[rid] = ln
        emoji = _first_status_emoji(cells[2])
        link = re.search(r"\(([^)]+\.md)\)", cells[3])
        rows.append((rid, emoji, link.group(1) if link else None, ln))

    # ADR file-number uniqueness (adr-0007-a.md vs adr-0007-b.md collide).
    nums = {}
    for f in adr_files:
        n = re.match(r"adr-(\d+)", f).group(1)
        if n in nums:
            issues.append(
                f"[consistency] docs/decisions/: duplicate ADR number {n} "
                f"({nums[n]} and {f}) — two branches claimed the same number; "
                "renumber one to the next free number and fix its registry row."
            )
        nums[n] = f

    # Row ↔ page agreement + bijection.
    linked = set()
    for rid, emoji, link, ln in rows:
        if emoji is None or link is None:
            issues.append(
                f"[consistency] docs/decisions/index.md row {ln} ({rid}): "
                "cannot parse status emoji + ADR link — keep rows in the "
                "'ID | statement | status | [ADR-…](file.md)' shape."
            )
            continue
        linked.add(link)
        page = os.path.join(dec_dir, link)
        if not os.path.isfile(page):
            issues.append(
                f"[consistency] docs/decisions/index.md: {rid} links {link}, "
                "which does not exist."
            )
            continue
        text = _read_stripped(page)
        sm = re.search(r"^\s*-\s*\*\*Status:\*\*(.*)$", text, re.M)
        p_emoji = _first_status_emoji(sm.group(1)) if sm else None
        if p_emoji is None:
            issues.append(
                f"[consistency] docs/decisions/{link}: no parsable "
                "'- **Status:**' line — the registry cannot be checked against it."
            )
        elif p_emoji != emoji:
            issues.append(
                f"[consistency] status drift: the registry says {rid} is "
                f"{emoji} but docs/decisions/{link} says {p_emoji} — update the "
                "ADR page AND the registry row together "
                "(docs/process/writing-adrs.md)."
            )
        dm = re.search(r"^\s*-\s*\*\*Decision ID:\*\*\s*(D-\d+)", text, re.M)
        if dm and dm.group(1) != rid:
            issues.append(
                f"[consistency] docs/decisions/{link}: page header says "
                f"Decision ID {dm.group(1)} but its registry row says {rid}."
            )
    for f in adr_files:
        if f not in linked:
            issues.append(
                f"[consistency] docs/decisions/{f} has no row in "
                "docs/decisions/index.md — every ADR page gets a registry row "
                "(ID · statement · status · link)."
            )

    # Nav presence, both directions. The strict build now gates both for
    # every page (nav entries pointing nowhere; orphan pages, via
    # validation.nav.omitted_files in mkdocs.yml) — this stays for the
    # ADR-specific message that names the /adr-new step to fix it.
    mk = os.path.join(root, "mkdocs.yml")
    if os.path.isfile(mk) and adr_files:
        with open(mk, encoding="utf-8") as f:
            nav_text = f.read()
        for f_ in adr_files:
            if f"decisions/{f_}" not in nav_text:
                issues.append(
                    f"[consistency] mkdocs.yml nav has no entry for "
                    f"decisions/{f_} — add it under Decisions (/adr-new step 4)."
                )
        for nf in re.findall(r"decisions/(adr-[^\s\"']+\.md)", nav_text):
            if nf not in adr_files:
                issues.append(
                    f"[consistency] mkdocs.yml nav lists decisions/{nf}, "
                    "which does not exist."
                )

    # Structured cross-refs in ADR headers cite existing registry entries.
    req_ids, q_rows = set(), []
    req_p = os.path.join(root, "docs", "direction", "requirements.md")
    q_p = os.path.join(root, "docs", "direction", "open-questions.md")
    if os.path.isfile(req_p):
        for line in _read_stripped(req_p).splitlines():
            m = re.match(r"\|\s*(R\d+)\s*\|", line)
            if m:
                req_ids.add(m.group(1))
    if os.path.isfile(q_p):
        for line in _read_stripped(q_p).splitlines():
            m = re.match(r"\|\s*(Q\d+)\s*\|(.*)", line)
            if m:
                q_rows.append((m.group(1), m.group(2)))
    q_ids = {q for q, _rest in q_rows}
    reg_ids = set(seen_ids)
    for f in adr_files:
        text = _read_stripped(os.path.join(dec_dir, f))
        for label, pat, known, reg_name in (
            ("requirements", r"R\d+", req_ids, "docs/direction/requirements.md"),
            ("questions", r"Q\d+", q_ids, "docs/direction/open-questions.md"),
            ("decisions", r"D-\d+", reg_ids, "docs/decisions/index.md"),
        ):
            hm = re.search(rf"^\s*-\s*\*\*Related {label}:\*\*(.*)$", text, re.M)
            if not hm:
                continue
            for tok in sorted(set(re.findall(pat, hm.group(1)))):
                if tok not in known:
                    issues.append(
                        f"[consistency] docs/decisions/{f}: header cites {tok} "
                        f"but {reg_name} has no such entry — fix the reference "
                        "or add the registry row."
                    )

    # A resolved question names its resolution.
    for q, rest in q_rows:
        if _first_status_emoji(rest) == "✅" and "Resolved" not in rest:
            issues.append(
                f"[consistency] docs/direction/open-questions.md: {q} is marked "
                "✅ without a 'Resolved …' outcome/pointer — record what "
                "resolved it (see the lifecycle note atop the file)."
            )


# -------------------------------------- lane G: blueprint-only records rule

# The blueprint machinery, deleted wholesale at bootstrap. Its presence is
# what arms this lane; its absence disarms it forever.
BLUEPRINT_DIR = "blueprint"

# A changelog entry per the grammar the stub documents:
#   ### Session N (YYYY-MM-DD) — title
SESSION_HEADING_RE = re.compile(r"^###\s+Session\b.*$", re.M)
# A lessons entry: a dated H2. The skeleton in the stub lives inside an HTML
# comment (stripped before matching) and carries no real date anyway.
DATED_LESSON_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\b.*$", re.M)


def lane_g_blueprint_records(root: str, issues: list):
    """While the blueprint machinery is present, docs/records/ holds the
    SHIPPED STUBS of a downstream project's diary, not this repo's records."""
    if not os.path.isdir(os.path.join(root, BLUEPRINT_DIR)):
        return  # dormant: bootstrapped project — its records are its own

    changelog = os.path.join(root, "docs", "records", "changelog.md")
    if os.path.isfile(changelog):
        with open(changelog, encoding="utf-8") as f:
            text = f.read()
        for m in SESSION_HEADING_RE.finditer(text):
            head = m.group(0).strip()
            # The shipped stub's heading still carries its unresolved
            # placeholder comment where the date goes; a real entry never
            # does. (Matched as a bare comment opener on purpose: spelling
            # the judgment-block marker out here would make this file trip
            # the bootstrap gate's own Tier-2 grep.)
            if "<!--" in head:
                continue
            issues.append(
                f"[blueprint-records] docs/records/changelog.md: '{head}' is a "
                "real session entry, but the blueprint keeps no per-session "
                "records — this file ships to seeded projects as a stub, so "
                "the entry reaches every seed as false history. Remove it; "
                "the blueprint's only log is blueprint/CHANGELOG.md, written "
                "once per release in the promotion caboose (CONTRIBUTING.md "
                "-> Two hats)."
            )

    lessons = os.path.join(root, "docs", "records", "lessons.md")
    if os.path.isfile(lessons):
        for m in DATED_LESSON_RE.finditer(_read_stripped(lessons)):
            issues.append(
                f"[blueprint-records] docs/records/lessons.md: '{m.group(0).strip()}' "
                "is a dated lesson entry, but this file ships to seeded "
                "projects as a stub — a blueprint-internal incident recorded "
                "here becomes false history in every seed. Put the durable "
                "form where it stays true downstream (a regression case in "
                "the matching scripts/test_*.sh suite, a rule on a ritual "
                "card, a docs/process/ page) and drop the entry "
                "(CONTRIBUTING.md -> Two hats)."
            )


# ------------------------------------------------------------- the checks

def run_checks(root: str, seam=None):
    """Returns (fatal_issues, notes, used_exempt_indices)."""
    issues, notes, used = [], [], set()
    seam = seam if seam is not None else parse_seam(root)

    files = doc_files(root)
    texts = {}
    for p in files:
        try:
            with open(p, encoding="utf-8") as f:
                texts[p] = f.read()
        except OSError:
            continue

    # Lane A — dead path citations.
    for p, text in texts.items():
        rel = os.path.relpath(p, root)
        for tok in path_citations(text):
            idx = exempt("path", rel, tok)
            if idx is not None:
                used.add(idx)
                continue
            target = os.path.join(root, tok)
            ok = os.path.isdir(target) if tok.endswith("/") else os.path.exists(target)
            if not ok:
                issues.append(
                    f"[path] {rel}: cites `{tok}` which does not exist — "
                    "fix the citation, or restore/rename the file it points at."
                )

    # Lane B — issues cited as open that are closed. Never guesses.
    lane_b_skipped = True
    for p, text in texts.items():
        rel = os.path.relpath(p, root)
        for num, claim in issue_open_claims(text):
            idx = exempt("issue", rel, f"#{num}")
            if idx is not None:
                used.add(idx)
                continue
            state = gh_issue_state(num)
            if state is None:
                continue  # unknown: offline / not an issue — skip, don't guess
            lane_b_skipped = False
            if state.upper() == "CLOSED":
                issues.append(
                    f"[issue-state] {rel}: cites #{num} as open ('{claim}') "
                    "but it is CLOSED — update the doc."
                )
    if lane_b_skipped:
        notes.append("issue-state lane: no verifiable open-claims (or GitHub unreachable — skipped, never guessed).")

    # Lane E — epic-page status vs issue state. Reuses lane B's
    # resolver: offline / unknown skips, never guesses.
    epics_dir = os.path.join(root, "docs", "records", "epics")
    for p, text in texts.items():
        rel = os.path.relpath(p, root)
        if not p.startswith(epics_dir + os.sep) or os.path.basename(p) == "index.md":
            continue
        status = re.search(r"^\*\*Status:\*\*.*$", text, re.MULTILINE)
        if not status or not ("🟡" in status.group(0) or "🔴" in status.group(0)):
            continue  # done/superseded pages may cite a closed issue
        cited = re.search(r"\[#(\d+)\]", status.group(0))
        if not cited:
            continue  # template placeholders ([#NN]) carry no digits
        state = gh_issue_state(int(cited.group(1)))
        if state is not None and state.upper() == "CLOSED":
            issues.append(
                f"[epic-state] {rel}: status line says in-progress but epic "
                f"issue #{cited.group(1)} is CLOSED — if the epic was closed "
                "by mistake (e.g. a PR closing keyword), reopen it; if the "
                "epic really finished, finalise the page and flip its status "
                "(/epic-closeout)."
            )

    # Lane F — built-but-open sub-issues. Bullet-leading #N under
    # "What has been built" only; same resolver: offline/unknown skips.
    for p, text in texts.items():
        rel = os.path.relpath(p, root)
        if not p.startswith(epics_dir + os.sep) or os.path.basename(p) == "index.md":
            continue
        built = re.search(r"^## What has been built$(.*?)(?=^## |\Z)",
                          text, re.MULTILINE | re.DOTALL)
        if not built:
            continue
        for ref in re.finditer(r"^\s*[-*]\s+(?:\*\*)?#(\d+)", built.group(1), re.MULTILINE):
            state = gh_issue_state(int(ref.group(1)))
            if state is not None and state.upper() == "OPEN":
                issues.append(
                    f"[built-state] {rel}: lists #{ref.group(1)} under 'What "
                    "has been built' but the issue is still OPEN — close it "
                    "with its readout comment (close-at-completion), or "
                    "don't list it as built yet."
                )

    # Lane C — flag / env-var citations, self-arming seam.
    if seam["mode"] == "unconfigured":
        evidence = project_code_evidence(root)
        if evidence:
            issues.append(
                f"[seam] project code detected ({evidence}) but {SEAM_FILE} is "
                "unconfigured — the flag/env citation lane cannot verify docs "
                "against code. Configure it (code-root/env-prefix/command), or "
                "set 'mode: off <reason>' as an explicit advisory declaration "
                "(D-004). Silently unconfigured is not an option."
            )
        else:
            notes.append("flag/env lane: dormant (no project code yet) — self-arms when a root manifest or src/ appears.")
    elif seam["mode"] == "off":
        if not seam["reason"]:
            issues.append(
                f"[seam] {SEAM_FILE} sets 'mode: off' without a reason — an "
                "advisory declaration needs its why (D-004). Write "
                "'mode: off <one-line reason>'."
            )
        else:
            notes.append(f"flag/env lane: off by declaration ({seam['reason']}).")
    elif seam["mode"] == "configured":
        roots_ok = [r for r in seam["code_roots"] if os.path.isdir(os.path.join(root, r))]
        if not roots_ok:
            issues.append(
                f"[seam] {SEAM_FILE} is 'configured' but no code-root exists on "
                "disk — fix the code-root entries."
            )
        else:
            corpus = code_corpus(root, roots_ok)
            for p, text in texts.items():
                rel = os.path.relpath(p, root)
                if seam["env_prefix"]:
                    for var in set(re.findall(rf"\b{re.escape(seam['env_prefix'])}[A-Z0-9_]+\b", text)):
                        idx = exempt("env", rel, var)
                        if idx is not None:
                            used.add(idx)
                            continue
                        if var not in corpus:
                            issues.append(
                                f"[env] {rel}: cites {var}, not found anywhere "
                                "under the configured code roots."
                            )
                # Flags are checked only inside the SAME backtick span as a
                # declared command — a line citing `myproj --x` and
                # `mkdocs build --strict` must not get mkdocs' flag checked
                # against the project corpus (self-test scenario C-live).
                for tok in CITATION_RE.findall(text):
                    if not any(cmd in tok for cmd in seam["commands"]):
                        continue
                    for flag in set(FLAG_RE.findall(tok)):
                        idx = exempt("flag", rel, flag)
                        if idx is not None:
                            used.add(idx)
                            continue
                        if flag not in corpus:
                            issues.append(
                                f"[flag] {rel}: cites {flag} in a project "
                                "command citation, not found under the code roots."
                            )
    else:
        issues.append(f"[seam] {SEAM_FILE}: unknown mode '{seam['mode']}' (use unconfigured/configured/off).")

    # Lane D — cross-artifact registry consistency.
    lane_d_consistency(root, issues)

    # Lane G — blueprint-only: no session records in the shipped stubs.
    # Silent when disarmed on purpose: unlike lane C's dormancy (a temporary
    # state that must self-arm), no-blueprint/ is this lane's terminal and
    # correct state, and a seeded project has no use for a note about
    # machinery it no longer carries.
    lane_g_blueprint_records(root, issues)

    return issues, notes, used


def ledger_audit(used, ledger=None, ceiling=None) -> list:
    """All four D-004 ledger rules on the exemption list: a reason per entry,
    a ceiling, itemized (no blanket/empty scope), and staleness (an entry that
    no longer matches anything fails loud). `ledger`/`ceiling` default to the
    live KNOWN_EXEMPT — overridable so the self-test can drive fixtures."""
    ledger = KNOWN_EXEMPT if ledger is None else ledger
    ceiling = KNOWN_EXEMPT_CEILING if ceiling is None else ceiling
    problems = []
    if len(ledger) > ceiling:
        problems.append(
            f"[ledger] exemption list has {len(ledger)} entries, ceiling is "
            f"{ceiling} — raising the ceiling is a deliberate diff with a "
            "reason, never silent growth (D-004)."
        )
    for i, entry in enumerate(ledger):
        lane, file_frag, cite_frag, reason = entry
        if not (reason or "").strip():
            problems.append(
                f"[ledger] {entry!r} has no reason — every exemption states "
                "why (D-004)."
            )
        if not (file_frag or "").strip():
            problems.append(
                f"[ledger] {entry!r} has an empty file fragment — it would "
                "match every file (blanket); name specific items (D-004)."
            )
        elif cite_frag == "*" and "/" not in file_frag.rstrip("/"):
            problems.append(
                f"[ledger] {entry!r} is blanket — a '*' citation wildcard "
                "scoped only to a top-level path waives a whole category; "
                "restrict the file fragment to specific items (D-004)."
            )
        if i not in used:
            problems.append(
                f"[ledger] stale exemption no longer matches anything: {entry!r} "
                "— remove it (D-004: the frontier only moves one way)."
            )
    return problems


# -------------------------------------------------------------- self-test

def self_test() -> int:
    """Both-ways fixtures per lane; no network (fake issue resolver)."""
    failures = []

    def scenario(name, expect_fragments, build):
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "docs"))
            build(td)
            issues, _notes, _used = run_checks(td)
            for frag in expect_fragments:
                if not any(frag in i for i in issues):
                    failures.append(f"{name}: expected an issue containing '{frag}', got {issues}")
            if not expect_fragments and issues:
                failures.append(f"{name}: expected clean, got {issues}")

    def write(td, rel, text):
        p = os.path.join(td, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    # Lane A: dead citation fails; live citation passes; placeholder ignored.
    scenario("A-dead-path", ["[path]"], lambda td: write(td, "docs/a.md", "see `scripts/gone.sh`"))
    scenario("A-live-path", [], lambda td: (
        write(td, "scripts/here.sh", "x"),
        write(td, "docs/a.md", "see `scripts/here.sh` and `docs/adr-00NN-x.md` and `docs/<area>/`"),
    ))

    # Lane B: closed-cited-as-open fails; open passes; unknown skips.
    os.environ["DOCS_TRUTH_FAKE_ISSUES"] = "42:CLOSED,43:OPEN"
    try:
        scenario("B-closed-as-open", ["[issue-state]"], lambda td: write(td, "docs/b.md", "TODO(#42) pending"))
        scenario("B-really-open", [], lambda td: write(td, "docs/b.md", "issue #43 still open"))
        scenario("B-unknown-skips", [], lambda td: write(td, "docs/b.md", "issue #99 still open"))

        # Lane E: in-progress epic page citing a closed issue fails; open,
        # finished-page, and unknown cases pass (never guesses).
        epic_line = "# E\n\n**Status:** {} · epic issue [#{}](https://example.test/{})\n"
        scenario("E-wrongly-closed-epic", ["[epic-state]"], lambda td: write(
            td, "docs/records/epics/e.md", epic_line.format("🟡 In progress", 42, 42)))
        scenario("E-open-epic", [], lambda td: write(
            td, "docs/records/epics/e.md", epic_line.format("🟡 In progress", 43, 43)))
        scenario("E-finished-page-closed-issue", [], lambda td: write(
            td, "docs/records/epics/e.md", epic_line.format("✅ Done", 42, 42)))
        scenario("E-unknown-skips", [], lambda td: write(
            td, "docs/records/epics/e.md", epic_line.format("🟡 In progress", 99, 99)))

        # Lane F: built-but-open fails; built-and-closed, unknown, and
        # mid-line refs pass (never guesses; bullet-leading refs only).
        built_page = "# F\n\n## What has been built\n\n- #{} vendor block landed\n"
        scenario("F-built-but-open", ["[built-state]"], lambda td: write(
            td, "docs/records/epics/f.md", built_page.format(43)))
        scenario("F-built-and-closed", [], lambda td: write(
            td, "docs/records/epics/f.md", built_page.format(42)))
        scenario("F-unknown-skips", [], lambda td: write(
            td, "docs/records/epics/f.md", built_page.format(99)))
        scenario("F-midline-ref-ignored", [], lambda td: write(
            td, "docs/records/epics/f.md",
            "# F\n\n## What has been built\n\n- #42 done (via PR #43)\n"))
    finally:
        del os.environ["DOCS_TRUTH_FAKE_ISSUES"]

    # Lane C: self-arms on code evidence; off-without-reason fails;
    # off-with-reason passes; configured verifies flags/env both ways.
    scenario("C-self-arm", ["[seam] project code detected"], lambda td: (
        write(td, "pyproject.toml", "[project]"),
        write(td, "docs/c.md", "hello"),
    ))
    scenario("C-off-needs-reason", ["without a reason"], lambda td: (
        write(td, "pyproject.toml", "[project]"),
        write(td, ".claude/docs-truth.txt", "mode: off"),
        write(td, "docs/c.md", "hello"),
    ))
    scenario("C-off-with-reason", [], lambda td: (
        write(td, "pyproject.toml", "[project]"),
        write(td, ".claude/docs-truth.txt", "mode: off docs cite no project flags yet"),
        write(td, "docs/c.md", "hello"),
    ))
    seam_cfg = "mode: configured\ncode-root: src\nenv-prefix: MYPROJ_\ncommand: myproj\n"
    scenario("C-dead-flag-and-env", ["[flag]", "[env]"], lambda td: (
        write(td, "pyproject.toml", "[project]"),
        write(td, ".claude/docs-truth.txt", seam_cfg),
        write(td, "src/cli.py", "parser.add_argument('--real')  # MYPROJ_HOME"),
        write(td, "docs/c.md", "run `myproj --gone` with MYPROJ_MISSING"),
    ))
    scenario("C-live-flag-and-env", [], lambda td: (
        write(td, "pyproject.toml", "[project]"),
        write(td, ".claude/docs-truth.txt", seam_cfg),
        write(td, "src/cli.py", "parser.add_argument('--real')  # MYPROJ_HOME"),
        write(td, "docs/c.md", "run `myproj --real` with MYPROJ_HOME; `mkdocs build --strict` is fine"),
    ))

    # Lane D: registry/page/nav consistency, both ways. A coherent minimal
    # decisions tree (page + row + nav, statuses agreeing) must pass; each
    # single defect must fail.
    def decisions_fixture(td, page_status="✅ Decided", row_status="✅",
                          in_nav=True, related_q="—", extra_registry="",
                          extra_files=(), questions=None):
        write(td, "docs/decisions/adr-0001-first.md",
              "# ADR-0001 — First\n\n- **Status:** " + page_status +
              "\n- **Decision ID:** D-001\n- **Related questions:** " +
              related_q + "\n")
        for name, body in extra_files:
            write(td, f"docs/decisions/{name}", body)
        write(td, "docs/decisions/index.md",
              "# Registry\n\n| ID | Decision | Status | ADR |\n"
              "|----|----------|--------|-----|\n"
              f"| D-001 | First | {row_status} | [ADR-0001](adr-0001-first.md) |\n"
              + extra_registry)
        nav_page = "      - decisions/adr-0001-first.md\n" if in_nav else ""
        write(td, "mkdocs.yml",
              "nav:\n  - Decisions:\n      - decisions/index.md\n" + nav_page)
        if questions is not None:
            write(td, "docs/direction/open-questions.md", questions)

    scenario("D-clean", [], lambda td: decisions_fixture(td))
    scenario("D-status-drift", ["status drift"],
             lambda td: decisions_fixture(td, page_status="🟡 Proposed"))
    scenario("D-missing-row", ["has no row"], lambda td: decisions_fixture(
        td, extra_files=[("adr-0002-second.md",
                          "- **Status:** 🟡 Proposed\n- **Decision ID:** D-002\n")]))
    scenario("D-missing-nav", ["nav has no entry"],
             lambda td: decisions_fixture(td, in_nav=False))
    scenario("D-duplicate-id", ["duplicate registry ID"],
             lambda td: decisions_fixture(
        td, extra_registry="| D-001 | Dup | ✅ | [ADR-0001](adr-0001-first.md) |\n"))
    scenario("D-dead-xref", ["cites Q9"],
             lambda td: decisions_fixture(td, related_q="Q9"))
    scenario("D-resolved-q-unpointered", ["marked ✅ without"],
             lambda td: decisions_fixture(
        td, questions="| ID | Status | Summary | Pointers |\n"
                      "|----|--------|---------|----------|\n"
                      "| Q1 | ✅ | fast enough? yes | no pointer here |\n"))

    # Lane G: while blueprint/ is present the shipped records stubs must
    # stay stubs; once bootstrap deletes it, the same tree passes (a
    # bootstrapped project's records are its own). The stub heading keeps
    # its unresolved placeholder comment where a real entry carries a date.
    stub_changelog = ("# Changelog\n\n### Session 1 (<!-- fill: date -->) "
                      "— Project start\n")
    real_changelog = "# Changelog\n\n### Session 2 (2026-01-02) — Did a thing\n"
    stub_lessons = "# Lessons\n\n<!--\n## YYYY-MM-DD — skeleton entry\n-->\n"
    real_lessons = "# Lessons\n\n## 2026-01-02 — A lesson\n\nWhat happened.\n"
    def records(td, changelog, lessons, seeded=False):
        if not seeded:
            write(td, "blueprint/VERSION", "1.0.0\n")
        write(td, "docs/records/changelog.md", changelog)
        write(td, "docs/records/lessons.md", lessons)
    scenario("G-stubs-pass", [], lambda td: records(td, stub_changelog, stub_lessons))
    scenario("G-session-entry", ["[blueprint-records] docs/records/changelog.md"],
             lambda td: records(td, real_changelog, stub_lessons))
    scenario("G-dated-lesson", ["[blueprint-records] docs/records/lessons.md"],
             lambda td: records(td, stub_changelog, real_lessons))
    scenario("G-disarmed-after-bootstrap", [], lambda td: records(
        td, real_changelog, real_lessons, seeded=True))

    # D-004 ledger rules on the exemption list itself: a reason per
    # entry, itemized (no empty/blanket scope), a ceiling, and staleness.
    def ledger_case(label, expect_substr, ledger, used, ceiling=2):
        probs = ledger_audit(used, ledger=ledger, ceiling=ceiling)
        if not any(expect_substr in p for p in probs):
            failures.append(f"ledger/{label}: expected {expect_substr!r}, got {probs}")
    ledger_case("empty-reason", "has no reason",
                [("path", "docs/x/", "*", "")], {0})
    ledger_case("blanket-empty-file", "empty file fragment",
                [("path", "", "y", "reason")], {0})
    ledger_case("blanket-toplevel-wildcard", "is blanket",
                [("path", "docs/", "*", "reason")], {0})
    ledger_case("ceiling", "ceiling is 2",
                [("path", "a/b/", "c", "r"), ("path", "d/e/", "f", "r"),
                 ("path", "g/h/", "i", "r")], {0, 1, 2})
    ledger_case("staleness", "stale exemption",
                [("path", "docs/x/", "y", "reason")], set())
    if ledger_audit({0}, ledger=[("path", "docs/.templates/", "*", "reusable skeletons")]):
        failures.append("ledger/allow: a valid itemized entry was rejected")

    # The exemption matcher itself, both ways per separator. Ledger file
    # fragments are POSIX-style while every caller passes os.path.relpath
    # output, which renders with os.sep — so before exempt() normalized
    # backslashes, no exemption ever applied on Windows and the ledger
    # falsely reported every entry stale there. The Windows-separator paths
    # are hard-coded backslash strings on purpose: they fail on POSIX (where
    # CI runs) if the unconditional normalization is ever removed.
    _live_ledger = KNOWN_EXEMPT[:]
    KNOWN_EXEMPT[:] = [("path", "docs/.templates/", "*", "reason")]
    try:
        for label, sep_path, want in (
            ("posix-sep-match", "docs/.templates/skeleton.md", 0),
            ("windows-sep-match", "docs\\.templates\\skeleton.md", 0),
            ("posix-sep-miss", "docs/elsewhere/page.md", None),
            ("windows-sep-miss", "docs\\elsewhere\\page.md", None),
        ):
            got = exempt("path", sep_path, "any citation")
            if got != want:
                failures.append(f"exempt/{label}: expected {want!r}, got {got!r}")
    finally:
        KNOWN_EXEMPT[:] = _live_ledger

    # The self-arm lane must detect code nested under a subdir (the
    # python-package module installs at python/pyproject.toml + python/src/),
    # not just at the repo root, while machinery subdirs stay dormant.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        if project_code_evidence(_d) is not None:
            failures.append("selfarm/allow: a bare tree wrongly reported project code")
        os.makedirs(os.path.join(_d, "python", "src", "pkg"))
        open(os.path.join(_d, "python", "pyproject.toml"), "w").close()
        if project_code_evidence(_d) is None:
            failures.append("selfarm/deny: python/ module layout not detected")
    with _tf.TemporaryDirectory() as _d:
        os.makedirs(os.path.join(_d, "modules", "python-package", "python"))
        open(os.path.join(_d, "modules", "python-package", "python",
                          "pyproject.toml"), "w").close()
        if project_code_evidence(_d) is not None:
            failures.append("selfarm/allow: a machinery subdir wrongly armed the lane")

    if failures:
        print("check_docs_truth --self-test: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("check_docs_truth --self-test: OK (all scenarios pass, both ways per lane)")
    return 0


# ------------------------------------------------------------------- main

def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    issues, notes, used = run_checks(ROOT)
    issues += ledger_audit(used)

    for n in notes:
        print(f"note: {n}")
    if issues:
        print("check_docs_truth: FAIL")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("check_docs_truth: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
