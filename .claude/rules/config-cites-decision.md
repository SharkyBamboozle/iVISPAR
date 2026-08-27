---
paths:
  - ".github/**"
  - ".gitignore"
  - ".gitattributes"
  - "mkdocs.yml"
  - ".claude/settings.json"
  - "docs/requirements.txt"
---

# Config files cite their governing decision

You are editing CI or repo config. Non-obvious lines carry a rationale
comment naming the `D-###` decision or `#issue` that put them there, so the
file explains itself. Canonical rule: `docs/process/writing-adrs.md`;
rationale: `docs/process/enforcement.md` → *Enforcement layering (D-004)*.

Files that can't carry inline comments (JSON) cite their rationale here or in
the governing doc — e.g. `.claude/settings.json`'s permission deny-list
(`git push --force`/`-f`, `gh pr merge`, `git reset --hard`, `gh repo delete`,
the MCP merge tools `merge_pull_request`/`enable_pr_auto_merge`)
mirrors the CLAUDE.md hard rules (no force-push, no self-merge) and the
irreversible-operation guardrails. The guard-git hook's matcher routes the
same MCP merge tools into its parser-independent block; the deny-list
entries are the secondary layer (ADR-0004 → failure directions: deny rules
may not bind in prompt-free permission modes, hooks fire everywhere).

The same file's allow-list is prefix-only — a rule matches the literal head
of the command string, nothing more. The approve path for everything those
prefixes miss (`git -C … status`, env-prefixed reads, read-only pipelines)
is the checked-in approve-hook `.claude/hooks/guard-command-policy.py` on
the `Bash` matcher: per ADR-0004's failure directions it approves only what
it can prove read-only, defers everything else, and never blocks — so it
never contends with the deny layers above, and widening the allow-list is
rarely the right fix.

Advisory salience only — the enforcers remain the hooks and CI gates named
there.
