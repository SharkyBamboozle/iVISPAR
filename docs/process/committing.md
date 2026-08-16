# Committing

You are writing a commit message. *Enforcement (D-004): advisory — no gate
inspects a commit message; each rule's exact status is in its label below.*

- **The body of a non-trivial commit tells the story** in four short parts:
  symptom (what was wrong or missing) → cause → fix → and, where a test now
  guards the behaviour, a closing `Pin: <test path>` line naming it. For a
  change to anything load-bearing, add one sentence on why the guarantee still
  holds (e.g. "the check now fires in more cases, never fewer"). *(Advisory —
  no gate inspects commit-body quality; upheld by review, per D-004.)*
- **Exceptions are trailers.** A deliberate bypass of a convention is declared
  as a **git trailer** — a labelled line at the very end of the commit
  message, e.g. `Skip-Registry-Sync: typo-only fix in the ADR page`. The
  reason is mandatory. Trailers are permanent, searchable, and
  machine-checkable — a PR label or a chat-only approval is none of those.
  Any automated check added later verifies exactly these trailers, so the
  convention costs nothing now and becomes enforcement-ready. *(Advisory for
  now — only the `Unlock-ADR` and `Skip-Registry-Sync` trailers are gated
  today, by `adr-gates.yml`; the general "declare bypasses as trailers"
  convention is review-upheld until a trailer-checking gate exists, per D-004.)*

The trailer machinery is the exception channel the other rules point at —
the fourth [enforcement layer](enforcement.md), the `Test-Adjusted` trailer
([Testing changes](testing-changes.md)), and the ADR gates
([Writing ADRs](writing-adrs.md)) all declare their bypasses here.
