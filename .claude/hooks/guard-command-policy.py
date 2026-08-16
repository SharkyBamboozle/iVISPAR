#!/usr/bin/env python3
"""PreToolUse auto-approver for read-only Bash commands.

Registered on the Bash matcher in .claude/settings.json alongside
guard-git.sh. Where guard-git.sh answers "must this be BLOCKED?", this
answers the complementary question "can this be approved WITHOUT asking?"
— the prompt-fatigue problem. Anything it cannot positively prove safe is
left to the normal permission flow (exit 0, no output), so a gap here costs
a prompt, never a mistake.

Protocol
  exit 0, no stdout      -> defer to normal permission matching (ask)
  exit 0, JSON on stdout -> auto-approve, no prompt
  This hook NEVER blocks. Blocking stays with guard-git.sh / guard-adr.sh /
  guard-issue-close.sh, which run on the same matcher and are unaffected by
  an approve decision from here.

Scope (deliberately narrow)
  Read-only investigation verbs only: the git plumbing, grep/awk/sed/find
  pipelines and gh read subcommands that made up 100% of the observed
  prompt flood. Mutating verbs — mkdir, cp, mv, rm, git add/commit/push,
  gh pr create — are NOT auto-approved and keep prompting. That is the
  point: the flood is reconnaissance, and reconnaissance is provably safe.

Why it catches what the allow-list misses
  Prefix rules match the literal head of a string, so `git -C /repo
  status`, `(make verify || true) | tail -50`, `MSYS_NO_PATHCONV=1 git show`
  and `a; b; c` all fall through even when `git status` and `make verify`
  are allow-listed. This walks each shell segment, strips env-assignment
  prefixes and git global flags, and judges the real verb.

Posture: TRUST_REPO_SCRIPTS = True (a deliberate choice, not a detail)
  With it, `bash scripts/...` / `bash .claude/hooks/...` runs are
  auto-approved for ANY checked-in script — including ones a future PR
  adds. The trust boundary is review of the repo's own tooling: the same
  review that protects this hook and the deny-hooks. Projects wanting the
  stricter posture flip it to False and pay a prompt per suite run.

Fails toward asking on every uncertainty: lexer error, command
substitution, heredoc, process substitution, unresolvable redirect target,
or any verb not on the list.

Known residuals (adopted as-is; this hook does NOT prove every approved
command read-only)
  The policy tables approve a bounded set of LOCAL, reversible git ref
  operations that do change refs: `git branch NAME` / `git tag NAME`
  (create), `git fetch <refspec>` (write a local ref), `git branch -f`
  (force-move). File-write detection for sed/find/awk is best-effort and
  has gaps — e.g. `sed --in-place=SUFFIX`, `find -fprint0`, and
  `awk '{print EXPR > FILE}'` are not recognised as writes (a regex cannot
  fully parse awk). A redirect INTO the project dir or /tmp is approved by
  design. These are inherited from the upstream tables and left unchanged
  on adoption; whether any of them SHOULD prompt is a per-project policy
  call, not a defect this file decides. The two properties it does
  guarantee, both pinned by the suite: it never contends with a deny-hook
  (nothing a deny-hook blocks is ever auto-approved), and it never blocks.
"""

import json
import os
import re
import shlex
import sys

# ---------------------------------------------------------------------------
# Policy tables
# ---------------------------------------------------------------------------

# Verbs that cannot modify state. Note the deliberate omissions:
#   env     - `env FOO=1 rm -rf x` runs an arbitrary program
#   xargs   - same, one level of indirection
#   tee     - writes files
#   tar     - extraction writes
#   make    - runs a Makefile target, i.e. arbitrary code
SAFE_VERBS = {
    "ls", "cat", "head", "tail", "wc", "echo", "printf", "pwd",
    "dirname", "basename", "realpath", "readlink", "stat", "file",
    "du", "df", "sort", "uniq", "cut", "tr", "nl", "seq", "column",
    "diff", "cmp", "comm", "grep", "egrep", "fgrep", "rg", "jq",
    "date", "whoami", "hostname", "uname", "which", "type",
    "md5sum", "sha1sum", "sha256sum", "true", "false", "test",
    "cd", "mktemp",
}

# Shell keywords that carry no action themselves. Safe to skip because every
# segment of a loop or conditional body is split out and judged separately —
# `for f in *; do rm $f; done` still stops at the `rm` segment.
STRUCTURAL = {
    "for", "do", "done", "if", "then", "else", "elif", "fi",
    "while", "until", "case", "esac", "in", "{", "}", "!",
}

# git subcommands that only read. Anything touching the index, the worktree,
# refs, config or the remote's state is absent on purpose.
GIT_READ_SUBCOMMANDS = {
    "status", "log", "diff", "show", "shortlog", "blame", "describe",
    "rev-list", "rev-parse", "ls-files", "ls-tree", "ls-remote",
    "cat-file", "check-ignore", "check-attr", "merge-base", "grep",
    "reflog", "for-each-ref", "count-objects", "var", "symbolic-ref",
    "verify-commit", "verify-tag", "diff-tree", "diff-index", "name-rev",
    "whatchanged", "fetch",  # network, but does not alter local worktree
}

# git subcommands that read only when they are not passed a mutating flag.
GIT_CONDITIONAL = {
    "branch": {"-d", "-D", "-m", "-M", "-c", "-C", "--delete", "--move",
               "--copy", "--edit-description", "--set-upstream-to",
               "--unset-upstream", "-u"},
    "tag": {"-d", "-D", "--delete", "-a", "-s", "-f", "--force"},
    "stash": set(),          # bare/list only; see _git_ok
    "worktree": set(),       # list only; see _git_ok
    "remote": set(),         # -v / show only; see _git_ok
    "config": set(),         # --get* / --list only; see _git_ok
    "notes": set(),
}

# gh subcommand paths that only read.
GH_READ = {
    ("pr", "list"), ("pr", "view"), ("pr", "checks"), ("pr", "diff"),
    ("pr", "status"),
    ("issue", "list"), ("issue", "view"), ("issue", "status"),
    ("run", "list"), ("run", "view"),
    ("label", "list"),
    ("repo", "view"),
    ("release", "list"), ("release", "view"),
    ("auth", "status"),
    ("workflow", "list"), ("workflow", "view"),
}

# Per-verb flags that turn a reader into a writer.
FIND_WRITE_FLAGS = {"-exec", "-execdir", "-ok", "-okdir", "-delete",
                    "-fprint", "-fprintf", "-fls"}
SED_WRITE_FLAGS = {"-i", "--in-place"}

# awk program text that writes files, pipes to a shell, or shells out.
AWK_WRITE_RE = re.compile(r"print[f]?\s*>|system\s*\(|\|\s*[\"']|>>")

# Redirections that discard or merge streams rather than writing a file.
NOOP_REDIRECTS = [
    r"2>&1", r"1>&2", r"&>\s*/dev/null", r"2>\s*/dev/null",
    r">\s*/dev/null", r"<\s*/dev/null",
]

# Trust the repo's own checked-in scripts — a recorded posture decision;
# see "Posture" in the module docstring before flipping it.
TRUST_REPO_SCRIPTS = True
REPO_SCRIPT_DIRS = ("scripts/", ".claude/hooks/")

OPERATORS = {";", "&&", "||", "|", "\n", "&"}

ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Constructs whose contents this hook cannot see into. Presence of any of
# these anywhere in the command means defer, no exceptions.
OPAQUE_RE = re.compile(r"\$\(|`|<<|>\(|<\(")


# ---------------------------------------------------------------------------
# Decision helpers
# ---------------------------------------------------------------------------

def approve(reason):
    """Emit the PreToolUse allow decision and stop."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def defer():
    """Say nothing; the normal permission flow decides."""
    sys.exit(0)


# ---------------------------------------------------------------------------
# Path handling
# ---------------------------------------------------------------------------

def _writable_roots():
    roots = []
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    if proj:
        roots.append(os.path.realpath(proj))
    for var in ("TMPDIR", "TEMP", "TMP"):
        val = os.environ.get(var)
        if val:
            roots.append(os.path.realpath(val))
    roots.append(os.path.realpath("/tmp"))
    return roots


def redirect_target_ok(path):
    """True when a literal redirect target sits inside the project or temp."""
    if "$" in path or "*" in path or "?" in path:
        return False  # unresolvable at inspection time
    proj = os.environ.get("CLAUDE_PROJECT_DIR") or "."
    resolved = os.path.realpath(os.path.join(proj, os.path.expanduser(path)))
    for root in _writable_roots():
        if resolved == root or resolved.startswith(root + os.sep):
            return True
    return False


# ---------------------------------------------------------------------------
# Lexing
# ---------------------------------------------------------------------------

def normalise(cmd):
    """Drop stream-merging redirects so any surviving '>' is a real write."""
    out = cmd
    for pat in NOOP_REDIRECTS:
        out = re.sub(pat, " ", out)
    out = out.replace("\n", " ; ")     # newline is a command separator, and
    return out                         # shlex would otherwise eat it as whitespace


def lex(cmd):
    """Tokenise, keeping shell operators as their own tokens.

    Returns None on any lexing failure (unbalanced quotes and the like),
    which the caller treats as 'defer'.
    """
    try:
        lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""      # '#' is data here (branch names, regexes)
        return list(lexer)
    except Exception:
        return None


def segments(tokens):
    """Split a token list on shell operators."""
    segs, cur = [], []
    for tok in tokens:
        if tok in OPERATORS or set(tok) <= {"&", ";", "|"} and tok:
            if cur:
                segs.append(cur)
                cur = []
        else:
            cur.append(tok)
    if cur:
        segs.append(cur)
    return segs


def strip_prefixes(tokens):
    """Remove env assignments and structural keywords from the head."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        # `for x in a b c` executes nothing — it is a word list. (A
        # `for x in $(...)` form never reaches here: OPAQUE_RE rejects the
        # whole command first.) The loop BODY arrives as its own segment
        # and is judged on its own merits.
        if t == "for":
            return []
        if ENV_ASSIGN_RE.match(t) or t in STRUCTURAL:
            i += 1
            continue
        break
    return tokens[i:]


# ---------------------------------------------------------------------------
# Per-verb judgement
# ---------------------------------------------------------------------------

def _git_ok(args):
    """args = everything after the literal 'git'."""
    i = 0
    # Skip git's global flags to reach the subcommand.
    while i < len(args):
        a = args[i]
        if a in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            i += 2
            continue
        if a.startswith("--git-dir=") or a.startswith("--work-tree=") \
           or a.startswith("--namespace="):
            i += 1
            continue
        if a in ("-P", "--no-pager", "--paginate", "--no-replace-objects",
                 "--literal-pathspecs", "--bare"):
            i += 1
            continue
        if a.startswith("-"):
            return False       # unrecognised global flag: be conservative
        break
    if i >= len(args):
        return False
    sub = args[i]
    rest = args[i + 1:]

    if sub in GIT_READ_SUBCOMMANDS:
        return True

    if sub == "branch":
        return not any(f in GIT_CONDITIONAL["branch"] for f in rest)
    if sub == "tag":
        return not any(f in GIT_CONDITIONAL["tag"] for f in rest)
    if sub == "stash":
        return bool(rest) and rest[0] in ("list", "show")
    if sub == "worktree":
        return bool(rest) and rest[0] == "list"
    if sub == "remote":
        return not rest or rest[0] in ("-v", "--verbose", "show", "get-url")
    if sub == "config":
        return any(f.startswith("--get") or f in ("-l", "--list")
                   for f in rest)
    return False


def _gh_ok(args):
    if len(args) < 2:
        return False
    if (args[0], args[1]) not in GH_READ:
        return False
    # A read subcommand can still mutate via an explicit method override.
    return not any(a in ("-X", "--method", "-f", "-F", "--input")
                   or a.startswith("--method=")
                   for a in args[2:])


def _script_ok(args):
    """bash/python running a checked-in repo script."""
    if not TRUST_REPO_SCRIPTS:
        return False
    for a in args:
        if a == "-c" or a.startswith("-c"):
            return False       # inline code is not a script
    targets = [a for a in args if not a.startswith("-")]
    if not targets:
        return False
    target = targets[0].replace("\\", "/").lstrip("./")
    return target.startswith(REPO_SCRIPT_DIRS)


def segment_ok(tokens):
    """True when this one segment is provably read-only."""
    tokens = strip_prefixes(tokens)
    if not tokens:
        return True            # bare `done`, `fi`, etc.

    # Real (non-merging) redirects must land somewhere writable.
    for idx, tok in enumerate(tokens):
        if tok in (">", ">>"):
            if idx + 1 >= len(tokens):
                return False
            if not redirect_target_ok(tokens[idx + 1]):
                return False
    tokens = [t for i, t in enumerate(tokens)
              if t not in (">", ">>", "<")
              and not (i > 0 and tokens[i - 1] in (">", ">>", "<"))]
    if not tokens:
        return True

    verb = tokens[0].replace("\\", "/").rsplit("/", 1)[-1]
    verb = verb[:-4] if verb.endswith(".exe") else verb
    args = tokens[1:]

    if verb == "git":
        return _git_ok(args)
    if verb == "gh":
        return _gh_ok(args)
    if verb in ("bash", "sh", "python", "python3", "py"):
        if verb in ("python", "python3", "py") and args[:2] == ["-m", "json.tool"]:
            return True
        return _script_ok(args)
    if verb == "find":
        return not any(a in FIND_WRITE_FLAGS for a in args)
    if verb == "sed":
        if any(a in SED_WRITE_FLAGS or a.startswith("-i") for a in args):
            return False
        return True
    if verb == "awk" or verb == "gawk":
        return not any(AWK_WRITE_RE.search(a) for a in args)
    if verb == "command":
        return bool(args) and args[0] in ("-v", "-V")
    if verb in SAFE_VERBS:
        return True
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def evaluate(cmd):
    """Return a reason string to approve, or None to defer."""
    if not cmd or not cmd.strip():
        return None
    if OPAQUE_RE.search(cmd):
        return None            # substitution / heredoc: contents unknown
    tokens = lex(normalise(cmd))
    if tokens is None:
        return None
    segs = segments(tokens)
    if not segs:
        return None
    for seg in segs:
        if not segment_ok(seg):
            return None
    return f"read-only: {len(segs)} segment(s) verified against policy"


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        defer()
    if data.get("tool_name") not in (None, "Bash"):
        defer()
    cmd = (data.get("tool_input") or {}).get("command") or ""
    reason = evaluate(cmd)
    if reason:
        approve(reason)
    defer()


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

SELF_TEST = [
    # (command, should_auto_approve, note)
    # --- representative of the observed prompt flood, all should approve ---
    ("git -C /repo status --short --branch", True, "-C form"),
    ("git -C /repo fetch --all --prune 2>&1 | head -50", True, "-C + pipe"),
    ("git -C /repo branch -vv --all 2>&1 | head -60", True, "branch read"),
    ("git status; echo '--- ignored ---'; git check-ignore -v .claude/x", True, "chained"),
    ("cd /repo && git log --oneline -3", True, "cd then read"),
    ("MSYS_NO_PATHCONV=1 git show origin/development:README.md", True, "env prefix"),
    ("git diff --stat origin/development...origin/main -- | tail -20", True, "diff"),
    ("sed -n '/^## Usage/,/^## Notes/p' README.md", True, "sed -n"),
    ("awk 'NR>=100 && NR<=200 && /TODO/ {print NR\": \"$0}' notes.txt", True, "awk read"),
    ("grep -rn 'TODO' --include=*.md . | wc -l", True, "grep pipe"),
    ("gh issue list --limit 3", True, "gh read"),
    ("gh pr checks 42", True, "gh checks"),
    ("bash scripts/test_guard_git.sh", True, "repo script"),
    ("python3 -m json.tool .claude/settings.local.json", True, "json validate"),
    ("for b in main dev; do git log --oneline -1 $b; done", True, "loop, safe body"),
    ("ls -la .claude/ | grep -i settings", True, "ls pipe grep"),

    # --- must NOT auto-approve ---
    ("git push origin main", False, "push"),
    ("git -C /repo push --force", False, "push behind -C"),
    ("git add .", False, "index mutation"),
    ("git commit -m x", False, "commit"),
    ("git branch -D old", False, "branch delete flag"),
    ("git config user.email x@y.z", False, "config write"),
    ("rm -rf build", False, "rm"),
    ("mkdir -p out", False, "mkdir is out of scope"),
    ("gh pr merge 42", False, "merge"),
    ("gh api -X POST /repos/o/r/issues", False, "api write"),
    ("gh issue list --limit 3 && rm -rf x", False, "safe head, unsafe tail"),
    ("for f in *; do rm $f; done", False, "loop, unsafe body"),
    ("echo hi > /etc/passwd", False, "redirect outside project"),
    ("cat $(cat cmd.txt)", False, "command substitution"),
    ("cat `whoami`", False, "backticks"),
    ("git commit -F - <<'EOF'", False, "heredoc"),
    ("sed -i 's/a/b/' file.txt", False, "sed in-place"),
    ("awk '{print > \"out.txt\"}' f", False, "awk writes"),
    ("find . -name '*.pyc' -delete", False, "find -delete"),
    ("python3 -c 'import os; os.remove(\"x\")'", False, "inline python"),
    ("env FOO=1 rm -rf /", False, "env indirection"),
    ("make verify", False, "make runs arbitrary targets"),
    ("cat file | xargs rm", False, "xargs"),
    ("(make verify || true) | tail -50", False, "subshell + make"),

    # --- newlines are command separators; paired cases pin the fix both
    # --- ways (deny the second-line laundering, keep multi-line reads free)
    ("git status\ngit log --oneline -3", True, "newline-joined reads"),
    ("git fetch origin\ngit status --short", True, "newline fetch + status"),
    ("git status\ngit push origin main", False, "newline-laundered push"),
    ("ls\nrm -rf build", False, "newline-laundered rm"),
]


def self_test():
    os.environ.setdefault("CLAUDE_PROJECT_DIR", os.getcwd())
    failures = 0
    for cmd, expected, note in SELF_TEST:
        got = evaluate(cmd) is not None
        if got != expected:
            failures += 1
            want = "APPROVE" if expected else "DEFER"
            gots = "APPROVE" if got else "DEFER"
            print(f"FAIL [{note}] want={want} got={gots}\n      {cmd}")
    total = len(SELF_TEST)
    if failures:
        print(f"\n{failures}/{total} case(s) FAILED")
        return 1
    print(f"{total}/{total} case(s) passed")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    main()
