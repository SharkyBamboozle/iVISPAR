# Lessons

The distilled **"never again" list** — an append-only ledger of load-bearing
lessons this project has paid for. The [changelog](changelog.md) is the
chronological diary; this page keeps only what must change future behaviour.
**Read it before starting substantial work; append to it when a session
learns something expensive** (the `/session-close` reflection step proposes
candidates — entries land only on explicit approval).

## The contract

- **Append-only, newest first.** Entries are never deleted. A lesson that no
  longer applies is marked **(SUPERSEDED — see entry of YYYY-MM-DD)** in
  place, mirroring the ADR supersede rule.
- **One screen per entry.** Date + title, what happened, the rule that
  follows, and links to the PR / issue / session that carry the full story.
  Details live in their canonical homes — this page holds the lesson.
- **Real incidents only.** An entry records something that actually happened
  in this project — never a hypothetical.
- **Escalation path.** A lesson starts here. If it keeps being violated, it
  graduates to a one-line rule in `CLAUDE.md` or a skill card under
  `.claude/skills/`; if it still recurs, it becomes an automated check. Note
  the promotion in the entry when it happens — this keeps `CLAUDE.md` growth
  demand-driven, never default.

---

<!-- BLUEPRINT: entries accumulate below as the project earns them. Entry
skeleton (copy, fill, keep newest first):

## YYYY-MM-DD — <short title of the lesson>

**What happened:** 1–3 sentences, with links (PR #N, issue #N, Session N).

**The rule:** one or two sentences of "therefore, from now on …".

**Promoted:** (optional) where this lesson graduated to, and when.
-->
