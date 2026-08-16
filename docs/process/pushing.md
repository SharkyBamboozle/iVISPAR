# Pushing

You are about to push — possibly to a branch that had a PR before.
*Enforcement (D-004): the `guard-git.sh` hook at push time (fail-open) +
the session-start verdict line — detailed at the end of this page.*

## Branch model

Develop on a **feature branch** → PR into **`development`** (the integration
branch, the repo default). **`main` is the promoted branch** — it advances
only by PR from `development`, never by direct push (branch protection +
the git guard hook enforce this; the single exception is the repo's birth
commit during bootstrap). Never merge your own PR.

## PR lifecycle

**A PR is append-only while OPEN — and git will not tell you when it no
longer is.** Pushing to a branch whose PR was merged or closed succeeds at
the git layer (with delete-on-merge it even *recreates* the pruned branch),
GitHub attaches the commits to nothing, and "the changes landed on the PR"
becomes a false report backed only by a local exit code. Hence two rules:

1. **Before pushing to any branch with PR history, read the PR's state
   from the API** — a `git fetch` inspects refs, not PRs, and cannot
   distinguish the two terminal states, which demand different responses:
   - **Merged** → the branch is dead history. Restart it from the
     integration line (`git fetch origin development &&
     git checkout -B <branch> origin/development`), re-apply the follow-up
     work, and open a **fresh PR** — never stack new commits on merged
     history.
   - **Closed without merging** → the operator *rejected* that line of
     work; more commits do not reverse the decision. **Stop and ask.**
2. **Remote state is read in the same turn it is asserted, never
   recalled.** "Landed on PR #N" may only be claimed after reading the PR
   and seeing the pushed head on it. This is the operational form: a
   statement about a PR's or issue's state is backed by a fresh read made
   in the same turn — session memory is never a source for remote state.
   *(This half is advisory by nature and demonstrably the weakest layer —
   the session that authored this rule itself asserted a stale PR state
   from memory within an hour of writing it; that incident is why the
   mechanical layers below sit at action moments, per D-004.)*

Enforcement (D-004): the git guard hook checks the branch's PR state at
push time (`.claude/hooks/guard-git.sh`; suite:
`scripts/test_guard_git.sh`) — blocking pushes to terminal-PR branches
still on the pre-merge line, while a branch restarted onto current
`origin/development` passes (that IS the recovery). The check **fails
open** on gh/network errors — blocking every push offline would brick
normal work, and a wrongly-allowed zombie push wastes effort but destroys
nothing. The session-start hook prints the current branch's PR verdict at
the highest-risk moment (a fresh session on a stale branch). Named
residuals: MCP/API pushes bypass the Bash hook, and **no CI gate can exist
here** — a push to a dead branch fires no PR event; the verdict line,
this rule, and review are that net. PR watching/subscription (where a
harness offers it) remains a **per-PR operator choice, never a standing
default**: subscriptions are session-bound where this failure is
cross-session, merge events are not reliably delivered, and the blueprint's
conventions bind any agent — a harness-specific habit no gate can verify
is not a rule (D-004).

### Where task-end records land

**Task-end records — the session changelog entry and the `/handoff`
archive — are ordinary commits on the session's own feature branch, and
ride its open PR.** The two moments they trade on: *push* is the
durability moment — once records sit on any remote branch, container
reclamation and branch deletion cannot lose them; *merge* is the
integration moment, where operator burden lives. The changelog entry is
tiny but conflict-prone (every session prepends to one file — integrate
promptly); archive files are bulky but inert (a new dated folder, never
edited — they can wait once pushed). The `/session-close` card carries the
records commit as an explicit step.

Recovery, when the branch's PR has already **merged**: the restart rule
above applies to records too — restart the branch from `development`; the
records ride the follow-up PR, or a small **records-only PR** when the
session is fully done. A records PR closes nothing, its body names the
merged PR it trails, and its content is inert, so review is a skim. Rare
by construction: the rule covers every case except a merge that lands
mid-session.

**If unsure: push first, then ask.** A pushed branch is durable, so the
question can safely fail without losing what it protects — ask-then-push
is the wrong order. Discarding records is a legitimate operator *answer*,
never a default (the archive contract: purge only on explicit
instruction). This guidance lives in the rituals deliberately: a
context-blind hook cannot know whether a task is finished, so **no hook or
nudge ever asks for a git action on working docs** — only the rituals
speak about git (`.claude/working/README.md`). *(Advisory (D-004): no gate
can read a session's intent; the `/session-close` step and review are the
net.)*
