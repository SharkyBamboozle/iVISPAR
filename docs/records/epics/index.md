# Epics

Work on {{PROJECT_NAME}} is organised into **epics** — coherent bodies of
work, each tracked by a GitHub epic issue with build tasks as **sub-issues**
and findings as **`note`** issues
([Filing work](../../process/filing-work.md)). This section
gives each epic a **page that tells its story**: what it set out to do, what
was built, what was found, what was decided, and what it carried forward —
curated to skip the intermediate steps that don't matter to the story.

An epic page is deliberately a *different lens* from the other records, so
nothing is duplicated (the full lens table lives in
[Records & canon](../../process/records-and-canon.md#the-record-lenses)):

| Surface | Lens |
|---|---|
| **This epic page** | the epic's **curated story / retrospective** — the clean arc, dead-ends dropped |
| [Changelog](../changelog.md) | the **chronological diary** — every session, cross-epic |
| The **GitHub epic issue** | the **live plan + tracker** — scope, sub-issue DAG, notes index |
| [Decisions](../../decisions/index.md) + topic docs | the **canonical decisions & current system state** |
| [Agent-Research](../agent-research/index.md) | the curated output of a **fan-out research pass** — proposes and rates, never decides |

**Lifecycle.** A page is created as a short stub with a status when its epic
starts (template: `docs/.templates/epic-page-template.md`) and filled in as
the epic progresses. At **closeout** it is finalised into the retrospective,
and the epic issue is closed with a short pointer comment
(`docs/.templates/epic-closeout-comment.md`) plus the note triage the
[note convention](../../process/running-epics.md) requires.

## The epics

| Epic | Status | Page | Issue |
|---|---|---|---|

<!-- BLUEPRINT: one row per epic, e.g.
| **First vertical slice** | 🟡 In progress | [First slice](first-slice.md) | [#12](https://github.com/{{GITHUB_OWNER}}/{{PROJECT_SLUG}}/issues/12) |
-->

*Status legend:* ✅ Done · 🟡 In progress · 🔴 Open · 🧊 Deferred/Superseded.
