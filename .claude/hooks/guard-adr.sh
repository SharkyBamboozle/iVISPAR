#!/usr/bin/env bash
# PreToolUse guard for ADR governance (D-004). Registered in
# .claude/settings.json for Edit|Write|MultiEdit AND Bash — one home for all
# ADR-lock logic.
# Exit 0 = allow · exit 2 = block (stderr is fed back to the agent).
#
# Enforces the CLAUDE.md hard rule "never change a ✅ Decided ADR", widened to
# every path TO a Decided state: editing a Decided page, creating one already
# stamped ✅, promoting 🟡→✅, and deleting/renaming a Decided page via
# `git rm`/`git mv` OR plain coreutils `rm`/`mv` (the lock protects the
# DECISION, not the git spelling of the deletion) — including removes/renames
# of a PARENT directory (`git rm -r docs/decisions`, `rm -rf docs/decisions`),
# pathspec magic and root-anchored/empty/glob forms (`:/`, `:`, `:(top)`,
# `:/*`, `docs/deci*`), brace expansion (`rm docs/decisions/adr-{0001,0007}.md`),
# and `git -C <dir>` forms (targets resolve against the -C directory, the way
# git itself would). Any of these needs a fresh /unlock-adr token (≤1h).
# Creating or editing a 🟡/🔴/🧊 page is always allowed — the lock protects
# decisions, not authoring or proposing. CI closes the loop: adr-gates.yml
# requires an 'Unlock-ADR: <id> — <reason>' commit trailer.
#
# The Bash branch parses commands with the shared guard parser (the marked
# region below is byte-identical across the three guard hooks and pinned by
# scripts/test_guardlib.py): one quote-aware lex of the whole command
# string — unquoted newlines separate commands, '#' comments only at word
# boundaries, operator runs (subshell parens included) separate by
# character membership, and git global options are skipped — with -C
# directories surfaced — before the subcommand is read.
#
# Paths are normalized before matching (defeats `../`//`//` bypasses); the
# status parse tolerates format variants. Known residual (documented):
# `git rm --pathspec-from-file` contents are not inspected — the adr-gates
# CI trailer check is the net there. Every block says WHAT TO DO INSTEAD.
# Defaults to ALLOW on parse failure: a broken guard must not brick edits.
set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

python3 - "$INPUT" <<'PY'
import fnmatch, json, os, posixpath, re, shlex, sys, time

try:
    data = json.loads(sys.argv[1])
    tool = data.get("tool_name", "") or ""
    ti = data.get("tool_input", {}) or {}
except Exception:
    sys.exit(0)  # never brick edits on parse failure

# ---8<--- shared guard command-parser — byte-identical in guard-git.sh,
# guard-adr.sh, and guard-issue-close.sh; pinned (identity + syntax + unit
# tests) by scripts/test_guardlib.py. Edit ONE copy, then mirror it to the
# other two hooks verbatim.
#
# Contract: turn a raw shell command string into simple-command token
# lists, then surface git/gh invocations with global options resolved.
# Guarantees (each closes a live false-allow or false-block class):
#   - ONE quote-aware lex of the whole string (posix shlex,
#     whitespace_split, punctuation_chars): a quoted ';', '#', or newline
#     never splits or comments-out a command;
#   - unquoted newlines separate commands (handled in the quote-aware
#     pre-pass, never a raw newline split), so a following line's tokens
#     cannot bleed into the previous command's arguments;
#   - '#' starts a comment only at a word boundary, exactly like the
#     shell — shlex's own commenters would eat a mid-word or quoted '#';
#   - separators are recognized by CHARACTER MEMBERSHIP over the operator
#     set '();<>|&', so runs like '&&(' still separate and '(git ...)',
#     '$(git ...)' parse as git commands instead of hiding them;
#   - git/gh global options before the subcommand are skipped,
#     value-taking ones consume their value, and git -C directories are
#     surfaced so path arguments resolve the way git itself would;
#   - a lex error (unbalanced quote, trailing escape) raises out of _lex
#     and split_commands degrades to a naive whitespace split — matching
#     MORE, never silently matching nothing.

_OP_CHARS = frozenset("();<>|&")

def _presplit(cmd):
    # Quote-aware pre-pass: strip word-boundary comments, drop
    # backslash-newline line continuations, turn unquoted newlines into ';',
    # and surface command substitutions so a hidden git/gh becomes its own
    # command — a top-level (unquoted) backtick becomes ';', and a
    # substitution INSIDE double quotes (`...` via the 'bq' state, $(...) via
    # the depth-tracked 'dqs' state) closes the quote, breaks the command,
    # lexes the body bare, and reopens the quote at the close. (An unquoted
    # $(...) is already split by the '(' / ')' operator chars.)
    out = []
    state = ""       # '', "'", '"', 'bq'/'dqs' (`..`/$(..) subst in a "..")
    boundary = True  # at a word boundary (start / after whitespace/operator)
    dqs_depth = 0    # paren depth inside a double-quoted $( ) substitution
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if state == "'":
            out.append(c)
            if c == "'":
                state = ""
            i += 1
        elif state == '"':
            if c == "\\" and i + 1 < n:
                if cmd[i + 1] == "\n":
                    i += 2
                    continue
                out.append(c)
                out.append(cmd[i + 1])
                i += 2
                continue
            if c == "$" and i + 1 < n and cmd[i + 1] == "(":
                # $(...) inside "..." is command substitution: close the
                # quote, break the command, and lex the body bare (tracking
                # paren depth) so a hidden git/gh surfaces; the matching ')'
                # reopens the quote.
                out.append('"')
                out.append(";")
                state = "dqs"
                dqs_depth = 1
                boundary = True
                i += 2
                continue
            if c == "`":
                # A `...` substitution inside "..." runs a command: close the
                # quote, break the command, and lex the body bare so a hidden
                # git/gh surfaces; the closing backtick reopens the quote.
                out.append('"')
                out.append(";")
                state = "bq"
                boundary = True
                i += 1
                continue
            out.append(c)
            if c == '"':
                state = ""
            i += 1
        elif state == "bq":
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(cmd[i + 1])
                boundary = False
                i += 2
                continue
            if c == "`":
                out.append(";")
                out.append('"')
                state = '"'
                boundary = False
                i += 1
                continue
            out.append(c)
            boundary = c in " \t\r" or c in _OP_CHARS
            i += 1
        elif state == "dqs":
            if c == "\\" and i + 1 < n:
                out.append(c)
                out.append(cmd[i + 1])
                boundary = False
                i += 2
                continue
            if c == "(":
                dqs_depth += 1
                out.append(c)
                boundary = True
                i += 1
                continue
            if c == ")":
                dqs_depth -= 1
                if dqs_depth == 0:
                    out.append(";")
                    out.append('"')
                    state = '"'
                    boundary = False
                else:
                    out.append(c)
                    boundary = True
                i += 1
                continue
            out.append(c)
            boundary = c in " \t\r" or c in _OP_CHARS
            i += 1
        elif c == "\\" and i + 1 < n:
            if cmd[i + 1] == "\n":
                i += 2
                continue
            out.append(c)
            out.append(cmd[i + 1])
            boundary = False
            i += 2
        elif c in ("'", '"'):
            state = c
            out.append(c)
            boundary = False
            i += 1
        elif c == "#" and boundary:
            while i < n and cmd[i] != "\n":
                i += 1
        elif c == "`":
            out.append(";")
            boundary = True
            i += 1
        elif c == "\n":
            out.append(";")
            boundary = True
            i += 1
        else:
            out.append(c)
            boundary = c in " \t\r" or c in _OP_CHARS
            i += 1
    # An unterminated bq (dangling backtick in a "..") never reopened the
    # quote; the shlex pass will still see the surfaced body command.
    return "".join(out)

def _lex(cmd):
    # One shlex pass. Raises ValueError on malformed input (unbalanced
    # quote / trailing escape): the error must SURFACE — a parser that
    # silently yields nothing would fail open on exactly the inputs an
    # evasion would use.
    lx = shlex.shlex(_presplit(cmd), posix=True, punctuation_chars=True)
    lx.whitespace_split = True
    lx.commenters = ""  # comments were already handled, at word boundaries
    return list(lx)

def _brace_expand_once(s):
    # Expand the first brace group carrying a top-level comma into its
    # alternatives (prefix+opt+suffix). Returns None when the token has no
    # such group. Nested braces are tracked so only top-level commas split.
    start = s.find("{")
    while start != -1:
        depth, parts, cur, end = 0, [], [], -1
        i = start
        while i < len(s):
            ch = s[i]
            if ch == "{":
                depth += 1
                if depth == 1:
                    i += 1
                    continue
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            elif ch == "," and depth == 1:
                parts.append("".join(cur))
                cur = []
                i += 1
                continue
            cur.append(ch)
            i += 1
        if end != -1:
            pre, suf = s[:start], s[end + 1:]
            if parts:
                parts.append("".join(cur))
                return [pre + p + suf for p in parts]
            # No top-level comma: a `{m..n}` numeric/alpha sequence?
            seq = _brace_range("".join(cur))
            if seq is not None:
                return [pre + p + suf for p in seq]
        start = s.find("{", start + 1)
    return None

def _brace_range(interior):
    # Expand a bash sequence `m..n` (optional `..step`): numeric with
    # zero-pad width preserved, or single-char alpha. Returns a list, or
    # None when it is not a range. Bounded to keep the guard cheap.
    m = re.fullmatch(r"(-?\d+)\.\.(-?\d+)(?:\.\.(-?\d+))?", interior)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        step = abs(int(m.group(3))) if m.group(3) else 1
        if step == 0 or abs(hi - lo) // step > 1024:
            return None
        width = max(len(m.group(1).lstrip("-")), len(m.group(2).lstrip("-"))) \
            if (m.group(1).startswith("0") or m.group(2).startswith("0")) else 0
        rng = range(lo, hi + 1, step) if hi >= lo else range(lo, hi - 1, -step)
        return [("-" if v < 0 else "") + str(abs(v)).zfill(width) for v in rng]
    m = re.fullmatch(r"([A-Za-z])\.\.([A-Za-z])", interior)
    if m:
        a, b = ord(m.group(1)), ord(m.group(2))
        rng = range(a, b + 1) if b >= a else range(a, b - 1, -1)
        return [chr(v) for v in rng]
    return None

def expand_braces(token, cap=64):
    # Bash brace expansion of comma-lists (`a{x,y}` -> ['ax','ay']) and
    # `{m..n}` ranges, so every real path a command would touch is surfaced
    # to the matchers. Quoting is not tracked here (lost at lex) — expanding
    # a quoted brace only ADDS candidate paths, i.e. matches MORE, the safe
    # direction. Bounded by `cap`; on overflow the partial set is returned
    # WITH the original braced token appended, so a scope-based guard
    # (guard-adr's rm_scope keys on '{') still sees the '{' and scans the
    # dropped tail rather than silently missing it — a truncated expansion
    # must never read as "fully enumerated".
    results, changed = [token], True
    while changed:
        changed = False
        out = []
        for s in results:
            exp = _brace_expand_once(s)
            if exp is None:
                out.append(s)
            else:
                out.extend(exp)
                changed = True
            if len(out) >= cap:
                return out[:cap] + [token]
        results = out
    return results

def split_commands(cmd):
    # Raw command string -> list of simple-command token lists, split at
    # operator-run tokens ('&&', '|', ';', '(', ')', '&&(', ...). Each
    # surviving word is brace-expanded so `rm a-{1,2}.md` surfaces both paths.
    try:
        tokens = _lex(cmd)
    except ValueError:
        tokens = _presplit(cmd).split()  # degrade toward MORE matching
    cmds, cur = [], []
    for t in tokens:
        if t and frozenset(t) <= _OP_CHARS:
            if cur:
                cmds.append(cur)
            cur = []
        else:
            cur.extend(expand_braces(t))
    if cur:
        cmds.append(cur)
    return cmds

def prog_name(tok):
    # The program a command token invokes, reduced for matching: strip any
    # directory ('/usr/bin/git' -> 'git') and a trailing '.exe'/'.com'
    # ('git.exe' -> 'git', for Windows), so an absolute- or relative-path
    # invocation is recognized, not just the bare name. Backslash directory
    # separators are a documented residual (POSIX lexing eats them upstream).
    base = tok.rsplit("/", 1)[-1]
    low = base.lower()
    for ext in (".exe", ".com"):
        if low.endswith(ext):
            return base[: -len(ext)]
    return base

def strip_magic(arg):
    # Peel git pathspec magic: returns (path, from_root) — path is None for
    # exclude pathspecs (':!x', ':(exclude)x'), from_root is True for
    # root-anchored ones (':/x', ':(top)x').
    if not arg.startswith(":"):
        return arg, False
    if arg.startswith(":("):
        m = re.match(r":\(([^)]*)\)(.*)", arg, re.S)
        if not m:
            return arg[1:], False
        magics = m.group(1).split(",")
        if "exclude" in magics:
            return None, False
        return m.group(2), "top" in magics
    body = arg[1:]
    from_root = False
    while body and body[:1] in ("/", "!", "^"):
        if body[0] in "!^":
            return None, False
        from_root = True
        body = body[1:]
    if body[:1] == ":":
        body = body[1:]
    return body, from_root

def normalize_endpoint(word):
    # Reduce a `gh api` endpoint argument to the bare path used for matching.
    # gh accepts a path ('repos/o/r/issues/5', '/repos/...'), a full URL
    # ('https://api.github.com/repos/o/r/issues/5'), and GHES hosts with an
    # '/api/v3' (REST) or '/api' (GraphQL) prefix — all of which must match
    # the same rules as the bare path. Drops scheme://host, the api/v3|api
    # prefix, the query/fragment, and surrounding slashes.
    ep = word.split("?", 1)[0].split("#", 1)[0]
    m = re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^/]+(/.*)?$", ep)
    if m:
        ep = m.group(1) or ""
    ep = ep.strip("/")
    for pfx in ("api/v3/", "api/"):
        if ep.startswith(pfx):
            ep = ep[len(pfx):]
            break
    return ep

def at_file_ref(value):
    # gh field values (-f/-F/--field/--raw-field key=VALUE) support VALUE of
    # the form '@file' (read from that file) and '@-' (read from stdin).
    # Returns ('literal'|'file'|'stdin', target): the guards resolve 'file'
    # by reading it and fail closed on 'stdin' where a hard rule is at stake.
    if value == "@-":
        return ("stdin", None)
    if value.startswith("@"):
        return ("file", value[1:])
    return ("literal", value)

# git global options that consume the NEXT token as their value ('=' forms
# like --git-dir=x are self-contained). Listing a boolean option here would
# swallow the subcommand — keep it to options that are value-taking in git.
_GIT_VALUE_OPTS = frozenset((
    "-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env",
    "--attr-source",
))

def git_calls(tokens):
    # Yield (subcommand, args, chdir) for each git invocation in one simple
    # command; chdir is the accumulated -C value (None when absent) so
    # callers can resolve relative paths the way git itself would.
    for i, t in enumerate(tokens):
        if prog_name(t) != "git":
            continue
        j = i + 1
        chdir = None
        while j < len(tokens):
            a = tokens[j]
            if a.startswith("-"):
                if a in _GIT_VALUE_OPTS and j + 1 < len(tokens):
                    if a == "-C":
                        v = tokens[j + 1]
                        chdir = v if chdir is None else os.path.join(chdir, v)
                    j += 2
                else:
                    j += 1
                continue
            break
        if j < len(tokens):
            yield tokens[j], tokens[j + 1:], chdir

def split_flags(args, value_opts):
    # (flags, positional) for one subcommand's args: '--' ends flag
    # parsing; flags in value_opts consume their separate value ('=' forms
    # are self-contained); a lone '-' is positional (stdin).
    flags, positional = [], []
    k = 0
    while k < len(args):
        a = args[k]
        if a == "--":
            positional.extend(args[k + 1:])
            break
        if a.startswith("-") and a != "-":
            flags.append(a)
            if a in value_opts and k + 1 < len(args):
                k += 2
                continue
        else:
            positional.append(a)
        k += 1
    return flags, positional

# gh flags that always take a separate value wherever they exist in gh
# ('--flag=v' and attached '-Xv' forms are self-contained). Same rule as
# above: over-listing a boolean flag could swallow a subcommand word and
# hide a close/merge — when unsure, leave it out; an unconsumed value only
# adds a TRAILING word, and the matchers key on leading word positions.
_GH_VALUE_FLAGS = frozenset((
    "-R", "--repo", "--hostname", "-X", "--method", "-f", "--raw-field",
    "-F", "--field", "-H", "--header", "-q", "--jq", "-t", "--template",
    "--input", "-b", "--body", "--body-file", "--comment", "--milestone",
    "--cache",
))
_GH_FIELD_FLAGS = ("-f", "--raw-field", "-F", "--field")

def gh_calls(tokens):
    # Yield (words, fields, inputs, raw) for each gh invocation in one
    # simple command: words = subcommand path + positional args with flags
    # (and their values) removed — so `gh -R o/r issue close 5` and
    # `gh issue close 5 -R o/r` both yield words starting ('issue',
    # 'close'); fields = -f/-F/--field/--raw-field values in every
    # spelling; inputs = --input values; raw = every token after 'gh'.
    for i, t in enumerate(tokens):
        if prog_name(t) != "gh":
            continue
        words, fields, inputs = [], [], []
        raw = tokens[i + 1:]
        j = 0
        while j < len(raw):
            a = raw[j]
            if a == "--":
                words.extend(raw[j + 1:])
                break
            if a.startswith("--") and "=" in a:
                flag, _, val = a.partition("=")
                if flag in _GH_FIELD_FLAGS:
                    fields.append(val)
                elif flag == "--input":
                    inputs.append(val)
            elif a.startswith("-") and not a.startswith("--") and len(a) > 2:
                if a[:2] in _GH_FIELD_FLAGS:
                    fields.append(a[2:])
            elif a.startswith("-") and a != "-":
                if a in _GH_VALUE_FLAGS and j + 1 < len(raw):
                    val = raw[j + 1]
                    if a in _GH_FIELD_FLAGS:
                        fields.append(val)
                    elif a == "--input":
                        inputs.append(val)
                    j += 2
                    continue
            else:
                words.append(a)
            j += 1
        yield words, fields, inputs, raw

def advance_cd(run_cd, tokens):
    # Track the shell's working directory across a `cmd && cmd` / `cmd; cmd`
    # list so `cd docs/decisions && rm adr-...` resolves the way bash would.
    # `run_cd` is relative to the Bash tool's start cwd (assumed repo root);
    # a `cd` to an absolute path or ~ makes it unknowable -> None. Returns
    # the (possibly updated) run_cd; non-cd commands leave it unchanged. This
    # models sequential `&&`/`;`; a cd inside a ( ) subshell does not persist
    # in a real shell — a documented imprecision, and only ever toward
    # MORE matching.
    #
    # These are POSIX SHELL paths (always '/'-separated), so they are joined
    # and normalized with `posixpath`, NEVER `os.path`: on Windows os.path is
    # ntpath, which would emit '\'-separated output and (Python 3.13) stop
    # treating a rooted '/abs' as absolute — both platform quirks, neither
    # correct for a shell path. posixpath is identical to os.path on POSIX.
    if not tokens or prog_name(tokens[0]) != "cd":
        return run_cd
    args = [t for t in tokens[1:] if not t.startswith("-")]
    if not args:
        return None  # `cd` with no arg -> HOME, unknowable
    tgt = args[0]
    if tgt == "-" or posixpath.isabs(tgt) or tgt.startswith("~"):
        return None
    base = run_cd or ""
    return posixpath.normpath(posixpath.join(base, tgt)) if base \
        else posixpath.normpath(tgt)

def combine_chdir(run_cd, chdir):
    # Merge the running `cd` context with a command's own `git -C` value into
    # one directory. None run_cd (unknown) = the start cwd. POSIX shell paths
    # -> posixpath (see advance_cd on why not os.path).
    parts = [p for p in (run_cd, chdir) if p]
    if not parts:
        return None
    d = parts[0]
    for p in parts[1:]:
        d = p if posixpath.isabs(p) else posixpath.join(d, p)
    return d

# ---8<--- end shared guard command-parser

ROOT_ABS = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR", "."))
ADR_DIR = "docs/decisions"

# A Status field whose VALUE is Decided — tolerant of markup/bullet variants
# (`- **Status:** ✅`, `**Status**: ✅`, `Status: ✅`, and the emoji-last /
# em-dash forms `Status: Decided ✅`, `- **Status** — ✅ Decided`). Anchored
# so only markup/space/colon/dash — and optionally the word "Decided" — sits
# between "Status" and the ✅: a legend line ("Status legend: ✅ Decided · 🟡
# …") has "legend" in the gap and does NOT match, nor does prose like "flip
# Status to ✅" ("to" in the gap).
STATUS_DECIDED = re.compile(
    r"\bStatus\b[*_:\s—-]*(?:Decided[*_:\s—-]*)?✅", re.IGNORECASE)

def block(rel, short, action):
    print(
        f"BLOCKED (CLAUDE.md hard rule): {rel} is (or would become) a "
        f"✅ Decided ADR, and {action} a Decided decision is gated. A changed "
        "decision is a NEW superseding ADR (docs/process/writing-adrs.md, "
        "/adr-new). For a legitimate governance action "
        "(maintenance edit, create-as-Decided, 🟡→✅ promotion, delete, "
        f"rename), first run:\n\n    /unlock-adr {short or '<adr-id>'}\n\n"
        "(1h token; the commit must then carry an 'Unlock-ADR: "
        f"{short or '<adr-id>'} — <reason>' trailer, checked by adr-gates.yml). "
        "Reading an ADR never needs an unlock.",
        file=sys.stderr,
    )
    sys.exit(2)

def norm_rel(path):
    if not path:
        return ""
    ap = path if os.path.isabs(path) else os.path.join(ROOT_ABS, path)
    ap = os.path.normpath(ap)  # collapses .. and //
    try:
        return os.path.relpath(ap, ROOT_ABS).replace(os.sep, "/")
    except Exception:
        return ""

def is_adr(rel):
    return rel.startswith(ADR_DIR + "/adr-") and rel.endswith(".md")

def adr_short(rel):
    m = re.search(r"adr-\d+", os.path.basename(rel))
    return m.group(0) if m else ""

def on_disk_decided(rel):
    try:
        with open(os.path.join(ROOT_ABS, rel), encoding="utf-8") as f:
            return any(STATUS_DECIDED.search(line) for line in f)
    except Exception:
        return False

def content_decides(text):
    return bool(text) and any(STATUS_DECIDED.search(l) for l in text.splitlines())

def fresh_token(short):
    try:
        now = int(time.time())
        path = os.path.join(ROOT_ABS, ".claude", "working", "UNLOCKED_ADRS")
        with open(path, encoding="utf-8") as f:
            for line in f:
                p = line.split()
                if len(p) >= 2 and p[0] == short and p[1].isdigit() \
                        and now - int(p[1]) < 3600:
                    return True
    except Exception:
        pass
    return False

def enforce(rel, incoming_decided, action):
    if not is_adr(rel):
        return
    # Locked when the target IS a Decided ADR on disk, or the action WOULD make
    # it one (create-as-✅ / 🟡→✅). Authoring/editing a non-Decided page: free.
    if not (on_disk_decided(rel) or incoming_decided):
        return
    short = adr_short(rel)
    if short and fresh_token(short):
        return
    block(rel, short, action)

def resolve_target(arg, chdir):
    # One rm/mv argument -> repo-relative path, honoring pathspec magic and
    # the surfaced `git -C` directory. Returns "" for args that can't touch
    # an ADR (exclude pathspecs, unresolvable paths).
    path, from_root = strip_magic(arg)
    if path is None or not path:
        return ""
    if chdir and not from_root and not os.path.isabs(path):
        path = os.path.join(chdir, path)
    return norm_rel(path)

ADR_TOP = ADR_DIR.split("/")[0]  # 'docs' — the ADR tree's top segment

def _glob_scope(rel):
    # The directory a wildcard pathspec `rel` is anchored under, for the
    # parent-dir ADR check. Leading glob-free segments are kept verbatim; a
    # glob in the FIRST segment is scoped to repo root ('.') ONLY when that
    # glob could match the ADR tree's top segment ('docs') — otherwise it
    # matches unrelated top-level entries and cannot reach an ADR, so it is
    # scoped to itself (which holds no ADRs) rather than over-blocking.
    keep = []
    for seg in rel.split("/"):
        if any(c in seg for c in "*?[{"):
            if not keep:
                return "." if fnmatch.fnmatch(ADR_TOP, seg) else rel
            break
        keep.append(seg)
    return "/".join(keep) or "."

def rm_scope(arg, chdir):
    # The directory scope an rm/mv SOURCE argument would remove, for the
    # parent-directory ADR check. Unlike resolve_target (which yields a
    # single file path), this maps directory- and whole-tree-shaped
    # pathspecs to the dir they clear: an empty pathspec (':', ':/',
    # ':(top)') = "this dir and below" (repo root when root-anchored or no
    # -C), and a glob is scoped to its glob-free prefix. Returns None for
    # args that cannot remove a tree (exclude pathspecs).
    path, from_root = strip_magic(arg)
    if path is None:
        return None  # exclude pathspec
    norm = path.replace("\\", "/")
    if norm == "":
        if from_root or not chdir:
            return "."
        return norm_rel(chdir) or "."
    if chdir and not from_root and not os.path.isabs(path):
        path = os.path.join(chdir, path)
    rel = norm_rel(path)
    # '{' is treated like a glob char here so a brace token the shared
    # expander could not FULLY enumerate (a large/over-cap range left literal,
    # or a truncated expansion that re-appends the original) still scopes to
    # its brace-free prefix and scans for a Decided ADR — a truncated
    # expansion must never read as "nothing to remove here".
    if any(c in norm for c in "*?[{"):
        if from_root and "/" not in norm.lstrip("/"):
            return "."  # a root-anchored bare glob (':/*') = whole tree
        return _glob_scope(rel)
    return rel

def decided_adrs_under(rel):
    # Decided ADRs on disk beneath directory `rel` ('.' = repo root). ADR
    # pages live flat in docs/decisions, so listing that one directory is
    # the complete inventory.
    if rel not in (".", "docs") and rel != ADR_DIR \
            and not ADR_DIR.startswith(rel + "/") \
            and not rel.startswith(ADR_DIR + "/"):
        return []
    if not os.path.isdir(os.path.join(ROOT_ABS, rel)):
        return []
    try:
        names = sorted(os.listdir(os.path.join(ROOT_ABS, ADR_DIR)))
    except Exception:
        return []
    out = []
    for nm in names:
        r = ADR_DIR + "/" + nm
        if not is_adr(r):
            continue
        if rel.startswith(ADR_DIR + "/") and r != rel and not r.startswith(rel + "/"):
            continue
        if on_disk_decided(r):
            out.append(r)
    return out

def check_removal(positional, chdirs, is_move):
    # `chdirs` is the SET of base directories the targets might resolve
    # against — the running `cd` context AND the fallback where that cd did
    # NOT persist (e.g. a cd inside a ( ) subshell, whose effect a real shell
    # discards). A target is gated if it resolves to a Decided ADR under ANY
    # candidate: the cd-context catches `cd docs/decisions && rm <bare>`, the
    # fallback catches `(cd sub); rm docs/decisions/<adr>` — so cd-tracking
    # can never MISS relative to the no-cd baseline, only add coverage.
    action = "renaming/moving" if is_move else "deleting"
    # File-level check runs over EVERY argument — for mv that includes the
    # destination, so overwriting a Decided ADR via `mv other.md
    # docs/decisions/adr-....md` stays gated.
    for a in positional:
        for chdir in chdirs:
            rel = resolve_target(a, chdir)
            if is_adr(rel) and on_disk_decided(rel):
                short = adr_short(rel)
                if not (short and fresh_token(short)):
                    block(rel, short, action)
    # Parent-directory check runs over the SOURCES only (moving a file INTO
    # docs/decisions creates, not destroys): removing or renaming a
    # directory that contains a Decided ADR is gated like touching the ADR.
    sources = positional[:-1] if (is_move and len(positional) > 1) else positional
    for a in sources:
        for chdir in chdirs:
            scope = rm_scope(a, chdir)
            if scope is None or is_adr(scope):
                continue
            for r in decided_adrs_under(scope):
                short = adr_short(r)
                if not (short and fresh_token(short)):
                    block(r, short, action)

def result_decided(fp_rel, tool, ti):
    # Whether the file WOULD carry a Decided status after this edit — applied
    # in-memory, so a promotion that replaces only the status VALUE
    # (old='🟡 Proposed', new='✅ Decided', or even new='✅') is caught even
    # though new_string alone has no 'Status' token. Falls back to scanning
    # the incoming text when the current file can't be read.
    if tool == "Write":
        return content_decides(ti.get("content", "") or "")
    try:
        with open(os.path.join(ROOT_ABS, fp_rel), encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = None
    if content is None:
        if tool == "Edit":
            return content_decides(ti.get("new_string", "") or "")
        return content_decides("\n".join(
            (e.get("new_string", "") or "") for e in (ti.get("edits") or [])))
    if tool == "Edit":
        result = content.replace(
            ti.get("old_string", "") or "", ti.get("new_string", "") or "", 1)
    else:  # MultiEdit
        result = content
        for e in ti.get("edits") or []:
            result = result.replace(
                e.get("old_string", "") or "", e.get("new_string", "") or "", 1)
    return content_decides(result)

if tool in ("Edit", "Write", "MultiEdit"):
    rel = norm_rel(ti.get("file_path", "") or "")
    enforce(rel, result_decided(rel, tool, ti), "editing")

elif tool == "Bash":
    cmd = ti.get("command", "") or ""
    run_cd = ""  # working dir relative to the Bash tool's start cwd (repo root)

    def candidate_dirs(git_c):
        # The base dirs a target might resolve against: the cd-context
        # (combined with any git -C) AND the fallback where the running cd did
        # NOT persist (git -C alone, and repo root). Deduped, order-stable.
        cands, seen = [], set()
        for d in (combine_chdir(run_cd, git_c), git_c, None):
            key = d or ""
            if key not in seen:
                seen.add(key)
                cands.append(d)
        return cands

    for tokens in split_commands(cmd):
        run_cd = advance_cd(run_cd, tokens)
        # git rm / git mv — targets resolve against the running `cd` context
        # combined with any `git -C` directory (and the no-cd fallback);
        # --pathspec-from-file's value is consumed (its CONTENTS are a
        # documented residual — adr-gates CI is the net there).
        for sub, args, git_c in git_calls(tokens):
            if sub in ("rm", "mv"):
                _, positional = split_flags(
                    args, frozenset(("--pathspec-from-file",)))
                check_removal(positional, candidate_dirs(git_c), sub == "mv")
        # Plain coreutils `rm`/`mv` reach the same working-tree file — the
        # lock protects the DECISION, not the `git` spelling of the deletion.
        if tokens and prog_name(tokens[0]) in ("rm", "mv"):
            _, positional = split_flags(tokens[1:], frozenset())
            check_removal(positional, candidate_dirs(None),
                          prog_name(tokens[0]) == "mv")

sys.exit(0)
PY
exit $?
