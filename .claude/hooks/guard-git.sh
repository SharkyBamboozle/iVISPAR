#!/usr/bin/env bash
# PreToolUse guard for Bash commands (registered in .claude/settings.json).
# Exit 0 = allow · exit 2 = block (stderr is fed back to the agent).
#
# Guards CLAUDE.md's hard rules at the Bash layer — push to main (including
# broad pushes that carry main: --all/--branches/--mirror), force-push in
# every spelling (-f, bundled short clusters like -fu, --force-with-lease
# with or without a value, leading-+ refspecs), remote branch deletion,
# staging un-LFS'd binaries (named files, bulk adds, AND directory adds —
# scanned scoped to the added directory), self-merging PRs (gh pr merge,
# gh api .../merge, the mergePullRequest GraphQL mutation, and the MCP
# merge tools — matched by tool NAME before any command parsing, so a
# parser failure can never disarm that branch), and zombie
# pushes to a branch whose PR is already merged/closed. It normalizes each
# command to its INTENT before matching (refspec forms, quoting, global
# options, bulk adds) rather than pattern-matching one literal form, and
# FAILS CLOSED when repo state is inconclusive (D-004) — except the
# zombie-push check, which fails OPEN by design: blocking every push on a
# gh/network error would brick normal work, and a wrongly-allowed zombie
# push wastes effort but destroys nothing. The thorough net is
# repo-hygiene CI + branch protection: enforcement is layered by design.
#
# Command parsing is the shared guard parser (the marked region below is
# byte-identical across the three guard hooks and pinned by
# scripts/test_guardlib.py): one quote-aware lex of the whole command
# string — unquoted newlines separate commands, '#' starts a comment only
# at a word boundary, operator runs ('&&', '|', ';', subshell parens,
# redirects) separate by character membership, and git/gh global options
# (git -C/-c/--git-dir ..., gh -R/--repo ...) are skipped — with -C
# directories surfaced — before the subcommand is read.
#
# Known residuals (deliberate, documented — not silently implied covered):
# here-document bodies still parse as live commands (a body line that looks
# like a push can false-BLOCK — an inconvenience, never a hole); POSIX
# lexing mangles Windows backslash paths (C:\...) and backslash program
# dirs; `git add --pathspec-from-file` contents are not inspected; and — per
# the issue's explicit non-scope — nested interpreters (`sh -c '<cmd>'`,
# `eval`, `bash -c`), string-built/base64 obfuscation, and command-name
# wrappers (`env`, `xargs`, `find -delete`) are NOT unwrapped: branch
# protection, the repo-hygiene / CI gates, and the session-start PR verdict
# (D-004) are the layered net for that tail. Command substitutions ARE
# surfaced (top-level and inside "..", both `...` and $(..)); a `cd` inside a
# ( ) subshell does not persist in a real shell, and the guards that resolve
# paths (guard-adr) check both the cd-context AND the no-cd baseline so a
# leaked subshell-cd can only ADD coverage, never cause a miss.
#
# Every block message says WHAT TO DO INSTEAD — a blocked agent with no
# alternative starts improvising workarounds.
#
# Defaults to ALLOW on any parse failure: a broken guard must not brick
# every Bash call.
set -uo pipefail

INPUT=$(cat 2>/dev/null || true)

python3 - "$INPUT" <<'PY'
import json, os, posixpath, re, shlex, subprocess, sys

try:
    data = json.loads(sys.argv[1])
    cmd = data.get("tool_input", {}).get("command", "") or ""
except Exception:
    sys.exit(0)  # never brick Bash on parse failure

def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)

# The no-self-merge rule on the MCP surface: merge tools are blocked
# outright, BEFORE the parser — this branch must never sit behind it, so
# a parsing failure cannot disarm it (ADR-0004 failure directions). The
# settings.json matcher routes these tool names here; the permission
# deny-list carries a secondary copy for prompt-mode sessions.
tool_name = data.get("tool_name", "") or ""
if re.search(r"mcp__.*(merge_pull_request|enable_pr_auto_merge)", tool_name):
    block(
        "BLOCKED: merging a PR is the operator's act, never the agent's "
        "(CLAUDE.md hard rule). Auto-merge counts as merging. Instead: "
        "push the branch, open the PR into development, and ask the "
        "operator to review and merge it in the GitHub UI."
    )

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

BINARY_EXT = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".avi",
    ".pdf", ".zip", ".tar", ".gz", ".7z",
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".npy", ".npz",
    ".uasset", ".umap", ".fbx", ".glb", ".blend", ".exr", ".psd",
    ".wav", ".mp3",
)

# Sanctioned asset-dir prefixes come from ONE data file shared with the CI
# backstop (.github/workflows/repo-hygiene.yml) so the two layers can never
# disagree — .claude/asset-dirs.txt is the single source (D-004). Missing or
# unreadable file = strict posture (empty).
def _allowed_binary_prefixes():
    path = os.path.join(
        os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "asset-dirs.txt"
    )
    try:
        with open(path, encoding="utf-8") as f:
            return tuple(
                line.strip() for line in f
                if line.strip() and not line.lstrip().startswith("#")
            )
    except Exception:
        return ()

ALLOWED_BINARY_DIR_PREFIXES = _allowed_binary_prefixes()

# Repo-state helpers take the surfaced `git -C` directory (chdir) so a
# command that addresses ANOTHER repo is judged against THAT repo's state;
# a missing/invalid chdir lands in each helper's except-path default.

def lfs_tracked(path, chdir=None):
    try:
        out = subprocess.run(
            ["git", "check-attr", "filter", "--", path],
            capture_output=True, text=True, timeout=5, cwd=chdir or None,
        ).stdout
        return "filter: lfs" in out
    except Exception:
        return False

_CUR_BRANCH = {}

def current_branch(chdir=None):
    key = chdir or ""
    if key not in _CUR_BRANCH:
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5, cwd=chdir or None)
            _CUR_BRANCH[key] = r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            _CUR_BRANCH[key] = ""
    return _CUR_BRANCH[key]

def push_to_main_is_birth(chdir=None):
    # Sanctioned direct push (BOOTSTRAP.md step 8): allowed only while the
    # repo is demonstrably un-bootstrapped —
    #   (a) origin/main is exactly the template's SINGLE initial commit and
    #       still carries BOOTSTRAP.md, or
    #   (b) the remote definitively has no main at all.
    # ANY inconclusive signal (no origin, network error, ls-remote exit != 2)
    # fails closed → treated as armed → push blocked.
    try:
        have_local = subprocess.run(
            ["git", "rev-parse", "--verify", "-q", "origin/main"],
            capture_output=True, timeout=5, cwd=chdir or None).returncode == 0
        if have_local:
            has_bootstrap = subprocess.run(
                ["git", "cat-file", "-e", "origin/main:BOOTSTRAP.md"],
                capture_output=True, timeout=5, cwd=chdir or None
            ).returncode == 0
            count = subprocess.run(
                ["git", "rev-list", "--count", "origin/main"],
                capture_output=True, text=True, timeout=10, cwd=chdir or None
            ).stdout.strip()
            return has_bootstrap and count == "1"
        # No local origin/main: birth ONLY if ls-remote definitively reports
        # main absent (its documented --exit-code value is 2). A single-branch
        # clone lacks origin/main even when the remote has it, so we must ask
        # the remote — but a missing/renamed origin or a network error returns
        # a DIFFERENT non-zero code, which must NOT disarm the guard.
        r = subprocess.run(
            ["git", "ls-remote", "--exit-code", "--heads", "origin", "main"],
            capture_output=True, timeout=15, cwd=chdir or None)
        return r.returncode == 2
    except Exception:
        return False  # fail closed: treat as armed

def norm_branch(ref, cur):
    # Reduce a push refspec token to its destination branch name:
    # +src:dst (force form) -> dst · src:dst -> dst · refs/heads/main ->
    # main · HEAD -> current branch. A branch legitimately NAMED 'foo/main'
    # stays 'foo/main' — only the refs/heads/ prefix is stripped, never
    # arbitrary leading path segments.
    if ref.startswith("+"):
        ref = ref[1:]
    dst = ref.split(":")[-1]
    if dst == "HEAD":
        return cur
    if dst.startswith("refs/heads/"):
        dst = dst[len("refs/heads/"):]
    return dst

def dead_pr(branch, src_ref, chdir=None):
    """Zombie-push detection: returns (state, number) when the branch's
    PR history is terminal (latest PR MERGED/CLOSED, none open) AND the
    commits being pushed still sit on the old pre-merge line; None otherwise.
    A branch legitimately RESTARTED from the integration line (its history
    contains current origin/development) is fresh follow-up work headed for
    a fresh PR — allowed. FAILS OPEN (None) on any gh/network error: see the
    header. MCP/API pushes bypass this hook entirely — the session-start
    PR verdict and the PR-lifecycle rule are that net
    (docs/process/pushing.md)."""
    try:
        # gh is reached through an explicit seam: GUARD_GH_BIN (POSIX
        # shlex-split) replaces the leading "gh" so the regression suite
        # can substitute its hermetic mock on every platform. Use ABSOLUTE
        # forward-slash program paths, e.g. "/usr/bin/bash /tmp/m/gh" or
        # "'C:/Program Files/Git/usr/bin/bash.exe' /tmp/m/gh": a
        # Windows-native Python resolves this spawn via CreateProcess,
        # which cannot execute an extensionless shebang script (so PATH
        # interception falls through to the real gh) and for BARE names
        # searches System32 — where bash.exe is the WSL launcher — before
        # PATH. Unset or empty -> exactly ["gh"], byte-identical
        # production behavior.
        gh_argv = shlex.split(os.environ.get("GUARD_GH_BIN", "")) or ["gh"]
        r = subprocess.run(
            gh_argv + ["pr", "list", "--head", branch, "--state", "all",
                       "--json", "number,state", "--limit", "20"],
            capture_output=True, text=True, timeout=15, cwd=chdir or None)
        if r.returncode != 0:
            return None
        prs = json.loads(r.stdout or "[]")
        if not prs or any(p.get("state") == "OPEN" for p in prs):
            return None
        latest = max(prs, key=lambda p: p.get("number", 0))
        if latest.get("state") not in ("MERGED", "CLOSED"):
            return None
        # Best-effort fetch so a stale local origin/development ref cannot
        # hide a moved integration line; ignore failures (offline degrades
        # to the local ref, still better than memory).
        subprocess.run(["git", "fetch", "origin", "development"],
                       capture_output=True, timeout=20, cwd=chdir or None)
        anc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "origin/development",
             src_ref], capture_output=True, timeout=10, cwd=chdir or None)
        if anc.returncode == 0:
            return None  # restarted on the current integration line
        return (latest.get("state"), latest.get("number"))
    except Exception:
        return None

def repo_toplevel(chdir=None):
    # The worktree root git resolves against. `git add -A`/`--all` and the
    # root-anchored pathspecs (`:/`, `:(top)`) stage the WHOLE tree
    # regardless of cwd, so the binary scan must run from the root — a scan
    # scoped to a `git -C sub` subdir (or a session cwd inside a subdir)
    # misses the repo-root files those forms actually stage.
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5, cwd=chdir or None)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def pathspec_new_binaries(pathspec, chdir=None):
    # Un-LFS'd binaries a `git add <pathspec>` would stage — git resolves
    # the pathspec (globs, magic, subtrees) exactly as `add` does, so a
    # quoted wildcard like '*' or 'sub/*' is matched by git, not guessed.
    # --full-name yields repo-root-relative paths regardless of cwd. Fail
    # open (empty) on error.
    try:
        out = subprocess.run(
            ["git", "ls-files", "--others", "--modified", "--exclude-standard",
             "--full-name", "--", pathspec],
            capture_output=True, text=True, timeout=10, cwd=chdir or None
        ).stdout
    except Exception:
        return []
    bad = []
    for f in out.splitlines():
        f = f.strip()
        if not f or f.startswith(ALLOWED_BINARY_DIR_PREFIXES):
            continue
        if f.lower().endswith(BINARY_EXT) and not lfs_tracked(f, chdir):
            bad.append(f)
    return bad

def worktree_new_binaries(top=None, prefix=""):
    # Files a bulk/dir `git add` would stage: untracked + modified,
    # .gitignore respected. Scanned from the repo TOP-LEVEL (`top`) so
    # tree-wide forms see the entire worktree; optionally scoped to one
    # repo-root-relative directory prefix so `git add docs/` is judged on
    # docs/ alone. Fail-open (empty) on error — repo-hygiene CI is the
    # backstop.
    try:
        out = subprocess.run(
            ["git", "ls-files", "--others", "--modified", "--exclude-standard"],
            capture_output=True, text=True, timeout=10, cwd=top or None
        ).stdout
    except Exception:
        return []
    bad = []
    for f in out.splitlines():
        f = f.strip()
        if not f:
            continue
        if prefix and not (f == prefix or f.startswith(prefix + "/")):
            continue
        if f.startswith(ALLOWED_BINARY_DIR_PREFIXES):
            continue
        if f.lower().endswith(BINARY_EXT) and not lfs_tracked(f, top):
            bad.append(f)
    return bad

PUSH_MAIN_MSG = (
    "BLOCKED (CLAUDE.md hard rule): never push to main. Instead: push the "
    "feature branch and open a PR into development — main is promoted via PR "
    "only. If this IS a fresh un-bootstrapped template clone, ask the user to "
    "approve this push explicitly."
)
FORCE_MSG = (
    "BLOCKED (CLAUDE.md hard rule): no force-pushes or history rewrites. "
    "Rebase or merge onto the moved remote instead; if a force-push is "
    "genuinely required, ask the user explicitly first."
)
DELETE_MSG = (
    "BLOCKED (CLAUDE.md hard rule): remote branch deletion is guarded — you "
    "may delete only branches you created in this session. If that is the "
    "case here, ask the user to confirm and run the deletion themselves."
)
MERGE_MSG = (
    "BLOCKED (CLAUDE.md hard rule): never merge your own PR (this includes "
    "`gh pr merge`, `gh api .../merge`, and the mergePullRequest GraphQL "
    "mutation). Leave the PR for the user to review and merge."
)

def binary_msg(arg):
    return (
        f"BLOCKED (CLAUDE.md hard rule): '{arg}' is a binary-type file not "
        "covered by LFS. Never commit binaries — run artifacts go to the data "
        "repo; for a genuinely-needed authored asset, add an LFS pattern to "
        ".gitattributes and ask the user first."
    )

# git push options that take a separate value (their value must not be
# mistaken for a refspec).
_PUSH_VALUE_OPTS = frozenset(
    ("-o", "--push-option", "--receive-pack", "--exec", "--repo"))
# git push single-letter boolean options, and the single value-taking short
# (-o, --push-option). A short cluster is read letter by letter UNTIL a
# value-taking short, whose remainder is that option's value, not more
# flags — so `-fu` activates {f,u} but `-of` is -o with value "f" (no
# force) and `-fo x` still activates {f} (force, then -o consumes "x").
_PUSH_BOOL_SHORTS = frozenset("fdnqvu46")
_PUSH_VALUE_SHORTS = frozenset("o")

def _cluster_shorts(flag):
    # The set of boolean short options a single-dash cluster activates.
    # Walk stops at the first value-taking short (its remainder is a value);
    # an unknown short letter yields the empty set — never guess a cluster
    # we don't fully understand into a force/delete verdict.
    if not (len(flag) > 1 and flag[0] == "-" and flag[1] != "-"):
        return set()
    active = set()
    for ch in flag[1:]:
        if ch in _PUSH_VALUE_SHORTS:
            break
        if ch not in _PUSH_BOOL_SHORTS:
            return set()
        active.add(ch)
    return active

def _long_abbrev_of(flag, full, min_len):
    # True when `flag` (its name, before any '=') is a git-accepted
    # abbreviation of the long option `full`: a prefix of `full` at least
    # `min_len` chars long (the shortest UNAMBIGUOUS prefix among git push's
    # options). git resolves unambiguous prefixes to the full option, so
    # `--force-with-lea` == `--force-with-lease`, `--dry` == `--dry-run`.
    name = flag.split("=", 1)[0]
    return name.startswith("--") and len(name) >= min_len \
        and full.startswith(name)

def _is_dry_run(flag):
    # --dry-run and its abbreviations (--dry, --dr — '--d' is ambiguous with
    # --delete). Abbreviation-aware so the ALLOW path matches the block path.
    return _long_abbrev_of(flag, "--dry-run", 4)

def _is_tags(flag):
    # --tags and its abbreviations (--tag, --ta — '--t' is ambiguous with
    # --thin).
    return _long_abbrev_of(flag, "--tags", 4)

def _is_delete(flag):
    # --delete and its abbreviations (--de … --delete — '--d' is ambiguous
    # with --dry-run). Keeps the delete guard abbreviation-aware like force.
    return _long_abbrev_of(flag, "--delete", 4)

def _is_broad_push(flag):
    # --all/--branches/--mirror push every branch (main included). git
    # accepts unambiguous long-option ABBREVIATIONS (`--al`, `--mir`,
    # `--branc`), so match any long flag whose body is a prefix of one of
    # these names. Over-matches a rare ambiguous stub (`--a`) toward
    # blocking — the safe direction for a push.
    if not flag.startswith("--"):
        return False
    body = flag[2:].split("=", 1)[0]
    return bool(body) and any(
        name.startswith(body) for name in ("all", "branches", "mirror"))

def _is_force_flag(flag):
    # Force in every long spelling: exact --force, and --force-with-lease
    # with or without a value, INCLUDING git's accepted abbreviations
    # (--force-w … --force-with-lease). '--force-if-includes' is a lease
    # modifier, not a force by itself, and is not matched here.
    name = flag.split("=", 1)[0]
    return name == "--force" or _long_abbrev_of(flag, "--force-with-lease", 9)

def check_git_push(args, chdir):
    flags, positional = split_flags(args, _PUSH_VALUE_OPTS)
    cluster_shorts = set().union(*(_cluster_shorts(f) for f in flags)) \
        if flags else set()
    # A --dry-run (or -n) push transmits NOTHING — it cannot violate any
    # hard rule, so it is always allowed (blocking it is a pure false-block).
    # Abbreviation-aware (--dry, --dr) so the ALLOW path recognizes the same
    # option spellings the block paths do (round-4 taught the block flags
    # abbreviations; the allow flags must keep pace or they false-block).
    if any(_is_dry_run(f) for f in flags) or "n" in cluster_shorts:
        return
    # Remote branch deletion: --delete/-d (bundled too, e.g. -qd), or a :dst
    # (empty source) refspec. Guarded regardless of branch — the hook can't
    # verify session-authorship, so it defers to the user.
    if "d" in cluster_shorts or any(_is_delete(f) for f in flags) or \
       any(p.lstrip("+").startswith(":") for p in positional):
        block(DELETE_MSG)
    cur = current_branch(chdir)
    # A broad push carries main along: --all/--branches push every branch,
    # --mirror pushes (and force-updates) every ref (abbreviations included).
    broad = any(_is_broad_push(f) for f in flags)
    # R1 — any explicit refspec destination names main/master (covers
    # `origin main`, `HEAD:main`, `refs/heads/main`, `feature:main`,
    # force forms `+main`/`+feature:main`).
    targets_main = broad or any(
        norm_branch(a, cur) in ("main", "master") for a in positional
    )
    # R2 — implicit push while checked out ON main (bare `git push`,
    # `git push origin`, `git push origin HEAD`): the first positional is
    # the remote, refspecs follow it; if none names a non-main branch, the
    # push lands on main. `--tags` restricts the push to tags (the current
    # branch is NOT pushed unless also named), so it is not an implicit
    # main push.
    refspecs = positional[1:]
    explicit_nonmain = any(
        norm_branch(a, cur) not in ("main", "master") for a in refspecs
    )
    tags_only = any(_is_tags(f) for f in flags)  # --tags and abbreviations
    implicit_to_main = (cur in ("main", "master")
                        and not explicit_nonmain and not tags_only)
    if (targets_main or implicit_to_main) and not push_to_main_is_birth(chdir):
        block(PUSH_MAIN_MSG)
    # Force in every spelling: exact flags, --force-with-lease[=...] and its
    # git-accepted abbreviations (--force-w…), bundled short clusters
    # activating f (e.g. -fu, -fo), and leading-+ refspecs.
    if "f" in cluster_shorts or any(_is_force_flag(f) for f in flags) or \
       any(p.startswith("+") for p in positional):
        block(FORCE_MSG)
    # R3 — zombie push: git happily pushes to a branch whose PR was already
    # merged or closed (delete-on-merge even recreates the pruned branch)
    # and GitHub attaches the commits to nothing; the agent then reports
    # "landed on the PR" off a local exit code. Verify the PR state before
    # the push. (Broad pushes were already blocked above.)
    if broad:
        return
    dests = {}
    for a in refspecs:
        dests[norm_branch(a, cur)] = a.lstrip("+").split(":")[0] or "HEAD"
    if not dests and cur:
        dests[cur] = "HEAD"
    for dest, src in dests.items():
        if not dest or dest in ("main", "master"):
            continue
        hit = dead_pr(dest, src, chdir)
        if hit and hit[0] == "MERGED":
            block(
                f"BLOCKED (PR lifecycle): PR #{hit[1]} for "
                f"branch '{dest}' is MERGED — this branch is dead "
                "history; pushing would strand commits on a zombie "
                "branch that no PR will ever merge. Instead: "
                "restart the branch from the integration line "
                "(git fetch origin development && git checkout -B "
                f"{dest} origin/development), re-apply the "
                "follow-up work, push, and open a FRESH PR. Never "
                "stack new commits on merged history."
            )
        if hit and hit[0] == "CLOSED":
            block(
                f"BLOCKED (PR lifecycle): PR #{hit[1]} for "
                f"branch '{dest}' was CLOSED without merging — the "
                "operator rejected that line of work; more commits "
                "do not reverse the decision. Ask the user how to "
                "proceed; if new work under this branch name is "
                "wanted, restart it from origin/development first."
            )

def check_git_add(args, chdir):
    _, positional = split_flags(
        args, frozenset(("--pathspec-from-file", "--chmod")))
    # Everything is judged against repo-root-relative paths and scanned from
    # the top-level, so a `git -C sub` (or a session cwd inside a subdir)
    # cannot shrink the scan below what git would actually stage.
    top = repo_toplevel(chdir)
    try:
        cwd = os.getcwd()
    except Exception:
        cwd = "."
    base_abs = os.path.abspath(os.path.join(cwd, chdir)) if chdir else cwd

    def rel_to_top(abs_path):
        if not top:
            return None
        try:
            return os.path.relpath(abs_path, top).replace(os.sep, "/")
        except Exception:
            return None

    def scan(prefix):
        # prefix repo-root-relative; "" = whole worktree.
        for f in worktree_new_binaries(top, prefix or ""):
            block(binary_msg(f))

    def sanctioned_dir(pfx):
        return (pfx + "/").startswith(ALLOWED_BINARY_DIR_PREFIXES)

    # `-A`/`--all` stage the WHOLE tree regardless of cwd (git 2.x); `.`
    # stages only the cwd subtree.
    if any(a in ("-A", "--all") for a in args):
        scan("")
    if "." in positional:
        p = rel_to_top(base_abs)
        scan("" if p in (None, "", ".") else p)

    for arg in positional:
        if arg == ".":
            continue  # handled above
        path, from_root = strip_magic(arg)
        if path is None:
            continue  # exclude pathspec stages nothing
        norm = path.replace("\\", "/").rstrip("/")
        # A wildcard pathspec ('*', 'sub/*', 'top.*') is matched by git, not
        # by a directory scan — hand the ORIGINAL arg to git ls-files so git
        # resolves exactly what it would stage.
        if any(c in norm for c in "*?["):
            for f in pathspec_new_binaries(arg, chdir):
                block(binary_msg(f))
            continue
        # Root-anchored (':/', ':(top)') or paths climbing out of the cwd
        # ('..') stage outside any subdir prefix — full worktree scan.
        if from_root or norm in ("", ".") or ".." in norm.split("/"):
            scan("")
            continue
        abs_path = path if os.path.isabs(path) else os.path.join(base_abs, path)
        rel = rel_to_top(abs_path)
        # Directory adds stage everything beneath — scan that subtree.
        if arg.endswith("/") or os.path.isdir(abs_path):
            pfx = rel if rel is not None else os.path.normpath(norm).replace(os.sep, "/")
            if sanctioned_dir(pfx):
                continue
            scan(pfx)
            continue
        check_path = rel if rel is not None else norm
        if check_path.startswith(ALLOWED_BINARY_DIR_PREFIXES):
            continue
        if check_path.lower().endswith(BINARY_EXT) and not lfs_tracked(abs_path, top):
            block(binary_msg(check_path))

_READ_CAP = 1 << 20  # cap body reads at 1 MiB — a guard must stay cheap

def _readable_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(_READ_CAP)
    except Exception:
        return None

def _gql_merges(text):
    # A GraphQL body that merges (or arranges to merge) the author's own PR:
    # mergePullRequest, or enablePullRequestAutoMerge (sets the PR to merge
    # automatically once checks pass — the same self-merge outcome).
    return "mergePullRequest" in text or "enablePullRequestAutoMerge" in text

MERGE_INPUT_MSG = (
    "BLOCKED (CLAUDE.md hard rule, inconclusive body): this `gh api graphql` "
    "call carries a request body the guard cannot read at check time "
    "(missing @file or stdin), and self-merging a PR is forbidden — an "
    "unreadable GraphQL body fails closed. Instead: write the query to a "
    "readable file first, or pass it inline via `-f query=...`; a legitimate "
    "read query is never affected once its body is inspectable."
)

def _graphql_body_texts(fields, inputs):
    # Every GraphQL body the call would send: -f/-F/--field/--raw-field
    # values of the form key=@file (or key=@- / literal) plus --input files.
    # Yields (text_or_None, is_stdin) — None text = a file that could not be
    # read, so the caller fails closed on a merge/close-capable endpoint.
    for f in fields:
        _, _, val = f.partition("=")
        kind, target = at_file_ref(val)
        if kind == "literal":
            yield (val, False)
        elif kind == "stdin":
            yield (None, True)
        else:
            yield (_readable_text(target), False)
    for path in inputs:
        if path == "-":
            yield (None, True)
        else:
            yield (_readable_text(path), False)

run_cd = ""  # working dir relative to the Bash tool's start cwd (repo root)
for tokens in split_commands(cmd):
    run_cd = advance_cd(run_cd, tokens)
    for sub, args, git_c in git_calls(tokens):
        chdir = combine_chdir(run_cd, git_c)
        if sub == "push":
            check_git_push(args, chdir)
        elif sub == "add":
            check_git_add(args, chdir)
        # `git rm`/`git mv` of a Decided ADR is guarded by guard-adr.sh,
        # which is also registered on Bash (single home for ADR logic).
    for words, fields, inputs, raw in gh_calls(tokens):
        if words[:2] == ["pr", "merge"]:
            block(MERGE_MSG)
        if len(words) >= 2 and words[0] == "api":
            endpoint = normalize_endpoint(words[1])
            # Self-merge via the REST API: `gh api .../pulls/N/merge`.
            if re.search(r"/merge$", endpoint):
                block(MERGE_MSG)
            # ... or via the GraphQL mergePullRequest mutation — inline in a
            # -f query=..., in a key=@file field body, or in a --input body.
            # An unreadable @file/stdin body on graphql fails closed (a
            # readable legitimate query is inspected and allowed).
            if endpoint == "graphql":
                if any(_gql_merges(a) for a in raw):
                    block(MERGE_MSG)
                for text, is_stdin in _graphql_body_texts(fields, inputs):
                    if text is None:
                        block(MERGE_INPUT_MSG)
                    if _gql_merges(text):
                        block(MERGE_MSG)

sys.exit(0)
PY
exit $?
