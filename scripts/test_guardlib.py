#!/usr/bin/env python3
"""Pin + unit suite for the shared guard command-parser (D-005).

The three PreToolUse guard hooks (guard-git.sh, guard-adr.sh,
guard-issue-close.sh) each embed a byte-identical command-parser region,
marked by '# ---8<---' sentinels — triplicated deliberately instead of a
shared module, so every hook stays a self-contained stdin-fed heredoc with
no import path to break (a shared-module import that fails on one platform
would silently disarm all three guards at once). This suite is what makes
the triplication safe:

1. **Identity pin** — the marked region must be byte-identical across all
   three hooks; an edit to one copy without mirroring the others fails here.
2. **Syntax pin** — each hook's full embedded python heredoc must compile;
   `bash -n` in `make verify` cannot see python syntax errors, and a hook
   whose python cannot even parse exits 1 → the harness treats every call
   as an error, but nothing else pins it to a compile check.
3. **Unit tests** — the parser's load-bearing guarantees, both ways per
   behavior (deny-relevant parses produce the tokens the matchers key on;
   allow-relevant constructs stay unmangled), including the fail-open
   contract: malformed input must RAISE out of _lex (a parser that silently
   yields nothing would fail open on exactly the inputs an evasion would
   use), while split_commands degrades to an over-matching fallback.

Runs inside `make verify` (wired there explicitly; check_ci_gates.py pins
every scripts/test_* file into the verify recipe).
"""

import os
import posixpath
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = [
    os.path.join(HERE, "..", ".claude", "hooks", name)
    for name in ("guard-git.sh", "guard-adr.sh", "guard-issue-close.sh")
]
BEGIN = "# ---8<--- shared guard command-parser"
END = "# ---8<--- end shared guard command-parser"

fails = 0


def check(ok, label):
    global fails
    if ok:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        fails += 1


def heredoc_of(text, path):
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.endswith("<<'PY'"))
        stop = next(i for i in range(start + 1, len(lines))
                    if lines[i] == "PY")
    except StopIteration:
        return None
    return "\n".join(lines[start + 1:stop])


def region_of(text):
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith(BEGIN)]
    ends = [i for i, l in enumerate(lines) if l == END]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        return None
    return "\n".join(lines[starts[0]:ends[0] + 1])


def main():
    # The parser relies on shlex punctuation_chars + whitespace_split
    # working together, which Python supports from 3.8 — on an older
    # interpreter the guards would misparse, so fail LOUD here.
    check(sys.version_info >= (3, 8),
          "python >= 3.8 (shlex punctuation_chars + whitespace_split)")

    texts = {}
    for path in HOOKS:
        name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                texts[name] = f.read()
        except OSError as e:
            check(False, f"{name}: readable ({e})")
            return fails

    # --- syntax pin: every hook's embedded python compiles -------------
    for name, text in texts.items():
        source = heredoc_of(text, name)
        check(source is not None, f"{name}: python heredoc found")
        if source is None:
            continue
        try:
            compile(source, name, "exec")
            check(True, f"{name}: embedded python compiles")
        except SyntaxError as e:
            check(False, f"{name}: embedded python compiles ({e})")

    # --- identity pin: the shared region is byte-identical -------------
    regions = {}
    for name, text in texts.items():
        region = region_of(text)
        check(region is not None,
              f"{name}: exactly one marked shared-parser region")
        regions[name] = region
    ref_name = "guard-git.sh"
    ref = regions.get(ref_name)
    if ref:
        for name, region in regions.items():
            if name == ref_name or region is None:
                continue
            check(region == ref,
                  f"{name}: shared region byte-identical to {ref_name}")

    if not ref:
        return fails

    # --- unit tests against the pinned region --------------------------
    ns = {"os": os, "posixpath": posixpath, "re": re, "shlex": shlex}
    exec(compile(ref, "shared-guard-parser", "exec"), ns)
    split_commands = ns["split_commands"]
    _lex = ns["_lex"]
    git_calls = ns["git_calls"]
    gh_calls = ns["gh_calls"]
    strip_magic = ns["strip_magic"]
    split_flags = ns["split_flags"]
    prog_name = ns["prog_name"]

    def cmds(s):
        return split_commands(s)

    # separators: classic operators, newlines, subshells, operator runs
    check(cmds("git status && git diff") ==
          [["git", "status"], ["git", "diff"]],
          "split: '&&' separates")
    check(cmds("a; b | c || d & e") ==
          [["a"], ["b"], ["c"], ["d"], ["e"]],
          "split: ';' '|' '||' '&' all separate")
    check(cmds("git push\necho origin main") ==
          [["git", "push"], ["echo", "origin", "main"]],
          "split: unquoted newline separates (no token bleed)")
    check(cmds("(git push origin main)") ==
          [["git", "push", "origin", "main"]],
          "split: subshell parens do not hide the command")
    check(["git", "push", "origin", "main"] in cmds("$(git push origin main)"),
          "split: $() command substitution does not hide the command")
    check(["git", "push"] in cmds("true &&(git push)"),
          "split: mixed operator run '&&(' still separates")
    check(cmds("git push origin main > log")[0] ==
          ["git", "push", "origin", "main"],
          "split: redirect bounds the command's arguments")

    # comments: word-boundary only, to end of line, quotes stay live
    check(cmds("echo hi # git push origin main") == [["echo", "hi"]],
          "comment: word-boundary '#' comments out the rest of the line")
    check(cmds("echo hi#there") == [["echo", "hi#there"]],
          "comment: mid-word '#' stays part of the word")
    check(cmds("echo '#' ; git push") == [["echo", "#"], ["git", "push"]],
          "comment: quoted '#' does not comment out what follows")
    check(cmds("echo hi # note\ngit push") ==
          [["echo", "hi"], ["git", "push"]],
          "comment: runs to end of LINE, next line stays live")

    # quoting: quoted operators/newlines never split; continuations join
    check(cmds('git commit -m "a; b && c"') ==
          [["git", "commit", "-m", "a; b && c"]],
          "quote: quoted ';'/'&&' does not split")
    check(cmds('git commit -m "a\nb"') ==
          [["git", "commit", "-m", "a\nb"]],
          "quote: quoted newline stays inside the token")
    check(cmds("git push \\\n-u origin feat") ==
          [["git", "push", "-u", "origin", "feat"]],
          "quote: backslash-newline line continuation joins")

    # backtick: top-level command substitution is split out; quoted is literal
    check(["git", "push", "origin", "main"] in cmds("`git push origin main`"),
          "backtick: top-level `...` surfaces the substituted command")
    check(cmds("echo '`git push`'") == [["echo", "`git push`"]],
          "backtick: single-quoted backtick stays literal (not split)")

    # brace expansion: comma-lists become multiple words (bash-style)
    check(cmds("rm a-{1,2}.md") == [["rm", "a-1.md", "a-2.md"]],
          "brace: comma-list expands to multiple words")
    check(cmds("git rm docs/adr-{0001,0007}.md") ==
          [["git", "rm", "docs/adr-0001.md", "docs/adr-0007.md"]],
          "brace: expansion surfaces every path git would touch")
    check(cmds("echo a{b}c") == [["echo", "a{b}c"]],
          "brace: a group with no comma is left literal")
    expand_braces = ns["expand_braces"]
    check(set(expand_braces("x{a,b,c}y")) == {"xay", "xby", "xcy"},
          "brace: three-way comma-list")
    # On overflow the partial set is capped and the ORIGINAL braced token is
    # appended (so scope-based guards still see the '{' rather than a silently
    # truncated, brace-free list) — length is bounded by cap+1, and the
    # original token is present.
    _capped = expand_braces("{a,b}{c,d}{e,f}{g,h}", cap=8)
    check(len(_capped) <= 9 and "{a,b}{c,d}{e,f}{g,h}" in _capped,
          "brace: overflow is capped AND retains the original braced token")
    check(cmds("git rm adr-{0001..0003}.md") ==
          [["git", "rm", "adr-0001.md", "adr-0002.md", "adr-0003.md"]],
          "brace: numeric range with zero-pad width preserved")
    check(set(expand_braces("f{a..c}")) == {"fa", "fb", "fc"},
          "brace: single-char alpha range")
    check(cmds("echo {1..1000000}") != [] and
          all(len(c) <= 65 for c in cmds("echo {1..1000000}")),
          "brace: oversized range does not blow up (bounded/declined)")

    # double-quoted backtick command substitution surfaces the inner command
    check(any(c[:4] == ["git", "push", "origin", "main"]
              for c in cmds('echo "`git push origin main`"')),
          "backtick: `...` inside \"...\" surfaces the substituted command")
    check(cmds('echo "plain text"') == [["echo", "plain text"]],
          "backtick: a plain double-quoted string is untouched")
    # double-quoted $(...) command substitution, with paren-depth tracking
    check(any(c[:4] == ["git", "push", "origin", "main"]
              for c in cmds('echo "$(git push origin main)"')),
          "dqs: $(...) inside \"...\" surfaces the substituted command")
    check(any(c[:2] == ["git", "status"]
              for c in cmds('echo "wrap $(git status) end"')),
          "dqs: nested-paren body closes at the matching ')' only")
    check(cmds('echo "a $(echo hi) b"')[0][0] == "echo",
          "dqs: a benign $(...) still parses without error")

    # cd context tracking across && / ; lists. These are POSIX shell paths, so
    # the expected values are '/'-separated LITERALS, never os.path.join — on
    # Windows os.path.join would emit '\' and (Python 3.13) os.path.isabs
    # would misjudge '/abs', but advance_cd/combine_chdir use posixpath and so
    # return the same '/'-separated result on every platform. Asserting the
    # literal is what pins that platform-independence.
    advance_cd = ns["advance_cd"]
    combine_chdir = ns["combine_chdir"]
    check(advance_cd("", ["cd", "docs/decisions"]) == "docs/decisions",
          "cd: advance into a relative dir (POSIX separators on every OS)")
    check(advance_cd("docs", ["cd", "decisions"]) == "docs/decisions",
          "cd: advance accumulates (POSIX separators on every OS)")
    check(advance_cd("docs", ["git", "status"]) == "docs",
          "cd: a non-cd command leaves the context unchanged")
    check(advance_cd("docs", ["cd", "/abs"]) is None,
          "cd: an absolute /abs cd makes the context unknowable (None)")
    check(combine_chdir("docs", "sub") == "docs/sub",
          "cd: combine running-cd with a -C value (POSIX separators)")
    check(combine_chdir("", None) is None and combine_chdir(None, None) is None,
          "cd: empty/none context combines to None (start cwd)")

    # fail-open contract (T3): malformed input raises out of _lex, and
    # split_commands degrades to an over-matching fallback — never to [].
    try:
        _lex('git push "unclosed')
        check(False, "lex: unbalanced quote raises ValueError")
    except ValueError:
        check(True, "lex: unbalanced quote raises ValueError")
    fallback = cmds('git push origin main "unclosed')
    check(any(c[:4] == ["git", "push", "origin", "main"] for c in fallback),
          "fallback: malformed input still surfaces the git command")
    check(cmds("") == [], "split: empty input yields no commands")

    # git_calls: global options skipped, values consumed, -C surfaced
    def gcalls(s):
        out = []
        for c in cmds(s):
            out.extend(git_calls(c))
        return out

    check(gcalls("git -C . push origin main") ==
          [("push", ["origin", "main"], ".")],
          "git: -C skipped, value surfaced as chdir")
    check(gcalls("git --no-pager push origin main") ==
          [("push", ["origin", "main"], None)],
          "git: boolean global option skipped")
    check(gcalls("git --git-dir=.git push origin main") ==
          [("push", ["origin", "main"], None)],
          "git: '=' form global option skipped")
    check(gcalls("git -c k=v push origin main") ==
          [("push", ["origin", "main"], None)],
          "git: -c consumes its value (value not read as subcommand)")
    check(gcalls("git -C a -C b rm f") == [("rm", ["f"], os.path.join("a", "b"))],
          "git: repeated -C accumulates")
    check(gcalls("git -C .") == [],
          "git: options with no subcommand yield nothing")
    check(gcalls("env -u X git push") == [("push", [], None)],
          "git: wrapped invocation (env ... git) still found")
    check(gcalls("echo git-like") == [],
          "git: 'mygit'/'git-like' is not git")
    check(gcalls("/usr/bin/git push origin main") ==
          [("push", ["origin", "main"], None)],
          "git: absolute-path invocation recognized (prog_name)")
    check(gcalls("git.exe push origin main") ==
          [("push", ["origin", "main"], None)],
          "git: git.exe invocation recognized (Windows)")
    check(prog_name("/usr/local/bin/gh") == "gh"
          and prog_name("gh.exe") == "gh"
          and prog_name("mygit") == "mygit",
          "prog_name: strips dir and .exe, leaves other names intact")

    # gh_calls: flags resolved positionally in every spelling
    def ghcalls(s):
        out = []
        for c in cmds(s):
            out.extend(gh_calls(c))
        return out

    check(ghcalls("gh -R o/r issue close 5")[0][0] ==
          ["issue", "close", "5"],
          "gh: -R value skipped before the subcommand")
    check(ghcalls("gh --repo=o/r issue close 5")[0][0] ==
          ["issue", "close", "5"],
          "gh: --repo= form skipped")
    check(ghcalls("gh issue close 5 -R o/r")[0][0] ==
          ["issue", "close", "5"],
          "gh: trailing flags removed from words")
    check(ghcalls("gh --paginate issue close 5")[0][0] ==
          ["issue", "close", "5"],
          "gh: unknown boolean flag does not swallow the subcommand")
    check(ghcalls("gh issue close -- 5")[0][0] == ["issue", "close", "5"],
          "gh: '--' keeps the rest positional")
    w, f, i, _ = ghcalls("gh api -X PATCH repos/o/r/issues/5 -f state=closed")[0]
    check(w == ["api", "repos/o/r/issues/5"] and f == ["state=closed"],
          "gh: -X value skipped, -f field captured, endpoint at words[1]")
    check(ghcalls("gh api repos/o/r/issues/5 --field=state=closed")[0][1] ==
          ["state=closed"],
          "gh: --field= spelling captured")
    check(ghcalls("gh api repos/o/r/issues/5 -fstate=closed")[0][1] ==
          ["state=closed"],
          "gh: attached -fVALUE spelling captured")
    check(ghcalls("gh api repos/o/r/issues/5 --input body.json")[0][2] ==
          ["body.json"],
          "gh: --input value captured")
    check(ghcalls("gh api repos/o/r/issues/5 --input=body.json")[0][2] ==
          ["body.json"],
          "gh: --input= value captured")

    # normalize_endpoint: paths, full URLs, and GHES prefixes -> bare path
    normalize_endpoint = ns["normalize_endpoint"]
    check(normalize_endpoint("repos/o/r/issues/5") == "repos/o/r/issues/5",
          "endpoint: bare path unchanged")
    check(normalize_endpoint("/repos/o/r/issues/5") == "repos/o/r/issues/5",
          "endpoint: leading slash stripped")
    check(normalize_endpoint("https://api.github.com/repos/o/r/issues/5") ==
          "repos/o/r/issues/5",
          "endpoint: full URL host stripped")
    check(normalize_endpoint("https://api.github.com/graphql") == "graphql",
          "endpoint: dotcom graphql URL -> graphql")
    check(normalize_endpoint("https://ghe.example.com/api/v3/repos/o/r/issues/5")
          == "repos/o/r/issues/5",
          "endpoint: GHES /api/v3 REST prefix stripped")
    check(normalize_endpoint("https://ghe.example.com/api/graphql") == "graphql",
          "endpoint: GHES /api graphql prefix stripped")
    check(normalize_endpoint("repos/o/r/issues/5?foo=1") == "repos/o/r/issues/5",
          "endpoint: query string dropped")

    # at_file_ref: gh field value @file / @- / literal
    at_file_ref = ns["at_file_ref"]
    check(at_file_ref("closed") == ("literal", "closed"),
          "at_file: literal value")
    check(at_file_ref("@body.json") == ("file", "body.json"),
          "at_file: @file reference")
    check(at_file_ref("@-") == ("stdin", None),
          "at_file: @- is stdin")

    # strip_magic: pathspec magic peeled, excludes dropped
    check(strip_magic(":/docs/x") == ("docs/x", True),
          "magic: ':/x' is root-anchored")
    check(strip_magic(":(top)docs/x") == ("docs/x", True),
          "magic: ':(top)x' is root-anchored")
    check(strip_magic(":!x") == (None, False),
          "magic: ':!x' exclude drops the arg")
    check(strip_magic(":(exclude)x") == (None, False),
          "magic: ':(exclude)x' drops the arg")
    check(strip_magic("::x") == ("x", False),
          "magic: '::x' bare magic terminator peeled")
    check(strip_magic("plain/path.md") == ("plain/path.md", False),
          "magic: plain paths pass through")

    # split_flags: '--' ends flags, value opts consume exactly one token
    check(split_flags(["-u", "origin", "feat"], frozenset()) ==
          (["-u"], ["origin", "feat"]),
          "flags: boolean flag separated from positionals")
    check(split_flags(["-o", "main", "origin", "feat"], frozenset(("-o",))) ==
          (["-o"], ["origin", "feat"]),
          "flags: value option consumes its value")
    check(split_flags(["--", "-f", "x"], frozenset()) == ([], ["-f", "x"]),
          "flags: '--' makes the rest positional")

    return fails


if __name__ == "__main__":
    n = main()
    if n == 0:
        print("all asserted cases pass")
    else:
        print(f"{n} case(s) FAILED")
    sys.exit(n)
