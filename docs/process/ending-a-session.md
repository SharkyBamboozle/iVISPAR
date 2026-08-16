# Ending a session

You are wrapping up a working session; the `/session-close` ritual
(`.claude/commands/session-close.md`) packages these steps. *(Advisory
(D-004) — the ritual is the scaffolding; no gate validates a session's
close-out.)*

**Reconcile what the session advanced.** The `/session-close` sweep is the
completeness net for closes no PR event fires: it checks every issue the
session advanced — boxes ticked, readouts posted — and `n = m` means
closed, or argued. The `/epic-closeout` sub-issue check is a **backstop
that should find nothing**, and closeout triage is for *notes* — build
issues never wait for it. The close rules live in
[Closing issues](closing-issues.md).

## Changelog

[The changelog](../records/changelog.md) is the chronological diary and the project's
inter-session memory. One entry per working session, prepended newest first
(newest entry directly under the header):
`### Session N (YYYY-MM-DD) — title`, then 3–8 sentences: what was attempted →
what landed (PRs/commits) → what was found (link `note` issues) → what was
decided (link `D-xxx`) → what carries forward. Session numbers are citable IDs
— provenance tags elsewhere read *(Session N)*. *(Advisory — the
`/session-close` ritual creates the entry, but no gate validates its format;
D-004.)*
