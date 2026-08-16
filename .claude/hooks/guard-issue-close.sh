#!/usr/bin/env bash
# PreToolUse guard for issue-close authority. Registered in
# .claude/settings.json for Bash AND the GitHub MCP issue-write tools
# (matcher: Bash|mcp__.*issue_write) — one home for all close-gating logic.
# Exit 0 = allow · exit 2 = block (stderr is fed back to the agent).
#
# Enforces the CLAUDE.md hard rule "never manually close or delete an
# issue": a close rides the completing PR's `Closes #N` (fired when the
# OPERATOR merges) or is the operator's own click; the agent's job ends at
# the readout comment + ticked boxes + the close request. There is NO
# unlock ritual here BY DESIGN (contrast guard-adr.sh): any sanctioned
# manual close is one operator click, which costs less than an unlock —
# and a client-side unlock token could not be honored by the server-side
# backstop (issue-close-guard.yml) without trusting agent-postable markers.
#
# Blocked, per tool layer:
#   MCP  — any *issue_write call with state=closed (create or update);
#   Bash — `gh issue close` / `gh issue delete` (global flags like
#          `gh -R o/r issue close` included), and `gh api` calls that set
#          an issue's state to closed — via -f/-F/--field/--raw-field in
#          any spelling (including a `key=@file` value the guard reads) OR a
#          --input body file (the FILE is inspected, the flag alone never
#          blocks) — or invoke an issue-closing GraphQL mutation: closeIssue,
#          deleteIssue, or updateIssue with `state: CLOSED`. Endpoints are
#          matched whether given as a path, a full URL, or a GHES /api/v3 or
#          /api prefix. A body the hook CANNOT read at check time (missing
#          @file, stdin) fails CLOSED on close-capable endpoints: otherwise
#          writing the body and sending it in the same command would slip
#          through unread.
# Still allowed (anti-over-tighten): creating issues, commenting (the
# /comments endpoint is never close-capable), editing bodies/labels
# (box-ticking is expected tracker upkeep) — by field flags or --input —
# REOPENING (state=open — it is the guard's own remedy), and `gh pr close`
# (PRs are not issues and out of this guard's scope).
#
# The Bash branch parses commands with the shared guard parser (the marked
# region below is byte-identical across the three guard hooks and pinned
# by scripts/test_guardlib.py): one quote-aware lex of the whole command
# string — unquoted newlines separate commands, '#' comments only at word
# boundaries, operator runs (subshell parens included) separate by
# character membership, and gh flags are resolved positionally so global
# options can't hide the subcommand. The MCP check needs no parsing and
# runs FIRST, so it holds even if command parsing ever breaks.
#
# Named residuals (D-004): raw HTTPS calls bypass the token match — the
# server-side issue-close-guard.yml reverts app-mediated closes that slip
# through; issue DELETION is additionally admin-only at the GitHub layer
# and unexposed in the MCP toolset, so the gh-CLI match here is
# belt-and-suspenders on an already-narrow path. On Windows-Git-Bash, a
# `--input`/`@file` body given as an absolute MSYS path (`/tmp/...`) may be
# unreadable to a native-Windows python and is treated as unreadable — i.e.
# fail CLOSED (over-block) on a close-capable endpoint, the safe direction;
# a repo-relative or Windows-form path reads normally.
# Defaults to ALLOW on any parse failure: a broken guard must not brick
# every tool call.
set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

python3 - "$INPUT" <<'PY'
import json, os, posixpath, re, shlex, sys

try:
    data = json.loads(sys.argv[1])
    tool = data.get("tool_name", "") or ""
    ti = data.get("tool_input", {}) or {}
except Exception:
    sys.exit(0)  # never brick tool calls on parse failure

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

MSG = (
    "BLOCKED (CLAUDE.md hard rule): manually closing or deleting an "
    "issue is operator-only. The sanctioned paths: (1) the completing PR "
    "carries `Closes #N` and the close fires when the OPERATOR merges it; "
    "(2) for a readout-close, post the readout comment, tick the delivered "
    "boxes, and ASK THE OPERATOR to close the issue — do not close it "
    "yourself and do not route around this guard via other tools (the "
    "server-side issue-close-guard reverts app-mediated closes). Creating, "
    "commenting, labeling, body edits (box-ticking), and reopening all "
    "remain allowed. See docs/process/closing-issues.md."
)

INPUT_MSG = (
    "BLOCKED (CLAUDE.md hard rule, inconclusive body): this gh api call "
    "sends a --input request body the guard cannot read at check time "
    "(missing file or stdin) against an endpoint that can close an issue, "
    "and closing issues is operator-only — an unreadable close-shaped body "
    "fails closed. Instead: write the body file in its own PRIOR command "
    "so the guard can inspect it (and keep 'state' out of it), or pass "
    "fields via -f/--field flags. Comment posts (/comments) are never "
    "affected. See docs/process/closing-issues.md."
)

def block(msg=MSG):
    print(msg, file=sys.stderr)
    sys.exit(2)

# gh api endpoints able to close an issue: the issues collection or one
# issue — NEVER a sub-resource (/comments, /labels, /assignees, ...).
_CLOSEABLE_EP = re.compile(r"(repos/[^/]+/[^/]+/)?issues(/[^/]+)?")
_READ_CAP = 1 << 20  # cap body reads at 1 MiB — a guard must stay cheap

def _read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(_READ_CAP)
    except Exception:
        return None

def body_verdict(text, needles):
    # 'hit' when the readable body text matches a close signal, else 'clean'.
    if needles:
        return "hit" if any(n in text for n in needles) else "clean"
    try:
        body = json.loads(text)
        if isinstance(body, dict):
            return "hit" if body.get("state") == "closed" else "clean"
    except Exception:
        pass
    return "hit" if re.search(r'"state"\s*:\s*"closed"', text) else "clean"

def input_body_verdict(path, needles):
    # 'hit'/'clean'/None (unreadable) for a --input FILE path.
    if path == "-":
        return None
    text = _read_text(path)
    return None if text is None else body_verdict(text, needles)

# A GraphQL body that CLOSES an issue: the closeIssue/deleteIssue mutations
# by name, OR any mutation setting an issue's state to CLOSED — updateIssue
# (and the IssueStateUpdateInput variant) take `state: IssueState`, whose
# CLOSED value closes the issue just like closeIssue. `state:` is singular
# (the mutation input field); the plural `states:` READ filter — e.g.
# `issues(states: CLOSED)` — is not matched, so read queries stay allowed.
_GQL_CLOSE_STATE = re.compile(r"\bstate\s*:\s*CLOSED\b")

def gql_closes(text):
    return ("closeIssue" in text or "deleteIssue" in text
            or bool(_GQL_CLOSE_STATE.search(text)))

def field_state_closed(fields):
    # True when a -f/-F/--field/--raw-field sets the issue 'state' to
    # 'closed', literally OR via a '@file' value (read it); 'inconclusive'
    # when the referenced value is an unreadable @file/stdin — the caller
    # fails closed. The KEY must be exactly 'state'; a body/title field that
    # merely contains that text stays allowed.
    inconclusive = False
    for v in fields:
        key, _, val = v.partition("=")
        if key != "state":
            continue
        kind, target = at_file_ref(val)
        if kind == "literal":
            if val == "closed":
                return True
        elif kind == "stdin":
            inconclusive = True
        else:
            text = _read_text(target)
            if text is None:
                inconclusive = True
            elif text.strip() == "closed" or body_verdict(text, ()) == "hit":
                return True
    return "inconclusive" if inconclusive else False

def field_close_mutation(fields):
    # ('hit'|'inconclusive'|'clean') for a GraphQL issue-closing mutation
    # carried in a key=@file / key=@- / literal field value.
    inconclusive = False
    for v in fields:
        _, _, val = v.partition("=")
        kind, target = at_file_ref(val)
        if kind == "literal":
            if gql_closes(val):
                return "hit"
        elif kind == "stdin":
            inconclusive = True
        else:
            text = _read_text(target)
            if text is None:
                inconclusive = True
            elif gql_closes(text):
                return "hit"
    return "inconclusive" if inconclusive else "clean"

if tool != "Bash" and tool.endswith("issue_write"):
    # MCP issue-write tools, any server name (mcp__github__issue_write,
    # forks/renames included). A close is state=closed on create or update;
    # everything else — create, retitle, label, body edit, reopen — passes.
    # This check runs FIRST and needs no command parsing, so it holds even
    # if the parser above is ever broken.
    if (ti.get("state") or "") == "closed":
        block()

elif tool == "Bash":
    cmd = ti.get("command", "") or ""
    for tokens in split_commands(cmd):
        for words, fields, inputs, raw in gh_calls(tokens):
            if len(words) >= 2 and words[0] == "issue" \
                    and words[1] in ("close", "delete"):
                block()
            if len(words) >= 2 and words[0] == "api":
                endpoint = normalize_endpoint(words[1])
                if _CLOSEABLE_EP.fullmatch(endpoint):
                    # REST close: a state=closed FIELD in any spelling
                    # (-f state=closed, --field=state=closed, -fstate=closed,
                    # -F state=@file). The key must BE 'state' — a body/title
                    # field merely CONTAINING that text stays allowed.
                    sc = field_state_closed(fields)
                    if sc is True:
                        block()
                    if sc == "inconclusive":
                        block(INPUT_MSG)
                    # ... or a --input body: inspect the file, never block
                    # on the flag itself; unreadable fails closed.
                    for path in inputs:
                        verdict = input_body_verdict(path, ())
                        if verdict == "hit":
                            block()
                        if verdict is None:
                            block(INPUT_MSG)
                if endpoint == "graphql":
                    # GraphQL: an issue-closing mutation (closeIssue,
                    # deleteIssue, or updateIssue with state:CLOSED) — inline
                    # in raw tokens, in a key=@file field body, or in a
                    # --input body (unreadable body: fail closed).
                    if any(gql_closes(a) for a in raw):
                        block()
                    # updateIssue with the CLOSED enum passed via a GraphQL
                    # VARIABLE (query says `state: $s`; a field supplies the
                    # enum value CLOSED) evades the literal-text checks. Only
                    # block when the CLOSED-valued variable is the one BOUND TO
                    # `state:` — an updateIssue that sets a NON-state field
                    # (title/body/label) to the literal string 'CLOSED' via a
                    # variable changes no state and stays allowed.
                    query_text = " ".join(raw)
                    if "updateIssue" in query_text:
                        closed_vars = [v.partition("=")[0] for v in fields
                                       if v.partition("=")[2] == "CLOSED"]
                        if any(re.search(
                                r"state\s*:\s*\$" + re.escape(var) + r"\b",
                                query_text) for var in closed_vars if var):
                            block()
                    fm = field_close_mutation(fields)
                    if fm == "hit":
                        block()
                    if fm == "inconclusive":
                        block(INPUT_MSG)
                    for path in inputs:
                        if path == "-":
                            block(INPUT_MSG)
                        text = _read_text(path)
                        if text is None:
                            block(INPUT_MSG)
                        if gql_closes(text):
                            block()

sys.exit(0)
PY
exit $?
