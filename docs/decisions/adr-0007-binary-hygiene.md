# ADR-0007 — Binary hygiene

- **Status:** 🟡 Proposed
- **Decision ID:** D-007
- **Related requirements:** —
- **Related questions:** —
- **Related decisions:** enforced through the seams named by D-004
  (enforcement doctrine); where a paired data repository is adopted, its
  adoption ADR records the artifact-side implementation

<!-- BLUEPRINT: finalize this decision at bootstrap. Choose ONE posture per
modules/README.md → "Binary policy" (strict/split, in-repo assets, or
strict-without-split), rewrite the Decision section below to state the
chosen posture as decided (drop the alternative), reconcile the Context,
Consequences, and Related-decisions lines with the chosen posture (e.g.
the data-repo references, under a posture without one), flip Status to
✅ Decided, and update the registry row (docs/decisions/index.md) to match.
Wire the same choice into .claude/asset-dirs.txt and the CLAUDE.md
hard-rule bullet — all in the same commit. Flipping to ✅ is itself a
hook-gated path to Decided (guard-adr.sh): first run /unlock-adr adr-0007,
then make this finalization edit — see BOOTSTRAP.md step 4. -->

## Context

Source history is append-only in practice: one merged binary bloats every
future clone permanently, and no later cleanup is cheap or safe. At the
same time, the right posture toward binaries is genuinely per-project — a
research platform must keep run artifacts out of source history entirely,
while an asset-native project (a website, a game) legitimately ships
binaries as product. This decision therefore fixes the *invariant* and
records the *posture* chosen for this project.

The invariant: **no binary ever enters source history unmanaged** — every
binary is either excluded, LFS-tracked, or inside an explicitly sanctioned
asset directory. The posture decides which of those applies where.

## Decision

**Default posture — strict/split (🟡 until finalized at bootstrap):**

- **No binaries in this repository's history** — images, video, archives,
  model weights, notebooks with outputs. `data/` is gitignored staging
  only.
- **Durable artifacts live outside source history** — in the paired data
  repository where the data-repo module is applied (its adoption gets its
  own ADR), or they are not kept.
- **LFS patterns, where needed, are configured *before* any matching binary
  exists** — LFS-after-the-fact still leaves blobs in history.
- **The alternative posture — in-repo assets** — sanctions named asset
  directories (listed one per line in `.claude/asset-dirs.txt`, LFS for
  large or authored types) while generated artifacts still stay out. A
  project choosing it rewrites this section at bootstrap accordingly.

**Wiring (posture-independent):** the sanctioned-directory list lives in
exactly one data file, `.claude/asset-dirs.txt`, read by both enforcement
points — the git guard hook at edit time and the repo-hygiene CI gate at
merge time — so the two layers can never disagree (D-004). A deliberate
one-off exception is the `allow-binaries` PR label: explicit, per-PR, and
visible in the record — the one label-based exception to D-004's trailer
rule; its trailer-ization is a deferred item D-004 owns.

**Enforcement** (per [D-004](adr-0004-enforcement-doctrine.md)): the
repo-hygiene CI gate blocks binary-typed and oversized non-LFS files
outside sanctioned directories on every PR; the git guard hook denies the
common-extension subset of the same class (no size ceiling) at staging
time; both read the one seam file. This enforcement is live while the page
is 🟡 Proposed — the status marks only the pending posture choice, never a
dormant rule. The "configure LFS before the first binary" ordering is
advisory — upheld by review, since no gate can see a pattern that doesn't
exist yet.

## Consequences

- Clones stay lean indefinitely; history never needs a rewrite to shed
  weight — which keeps the append-only history rule (D-003) affordable.
- Run artifacts get a real home (the data repo) instead of a tolerated
  corner of source history.
- Asset-native projects pay one bootstrap decision (name the sanctioned
  directories) instead of fighting the gate per-PR.
- The occasional legitimate one-off costs an explicit `allow-binaries`
  label — friction by design, so exceptions stay visible and rare.

## Alternatives considered

- **Allow binaries with size limits only** — rejected: size is the wrong
  axis; a thousand small binaries bloat history as surely as one large
  one, and "small enough" invites drift.
- **LFS for everything binary, no exclusions** — rejected: LFS costs
  bandwidth quotas and server lock-in, and run artifacts don't belong in
  *any* form of source history — they belong with the runs.
- **Review-time judgment per binary** — rejected: reviewer memory doesn't
  scale, and one miss is permanent; the gate makes the default safe and
  the exception explicit.

## Reversibility / notes

- The posture is revisable by superseding ADR at any time; because both
  enforcement points read the single seam file, rewiring a posture change
  is a one-file edit plus the ADR.
- Tightening later is cheap (remove sanctioned dirs); loosening later is
  also cheap — but *cleaning up* after a period without the rule is not,
  which is why the decision ships armed with its default rather than
  waiting for the first incident.

## References

- Related docs: `CLAUDE.md` → *Hard rules* (the binary bullet this decision
  governs)
- Related decisions: [ADR-0003](adr-0003-branch-model.md),
  [ADR-0004](adr-0004-enforcement-doctrine.md)
