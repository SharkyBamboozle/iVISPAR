# ADR-0007 — Binary hygiene

- **Status:** ✅ Decided
- **Decision ID:** D-007
- **Related requirements:** R3
- **Related questions:** Q2 (texture redistribution — scopes *which* assets ship, not the posture)
- **Related decisions:** enforced through the seams named by D-004
  (enforcement doctrine); no paired data repository is adopted (see
  Reversibility for the named reactivation trigger)


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

**Posture — in-repo assets, narrowly sanctioned; plain git, no LFS; no
paired data repository.**

- **Two sanctioned asset prefixes, nothing else:** `unity/` (authored Unity
  project assets: textures, models, fonts) and `docs/assets/` (docs-site
  media, kept small — advisory budget, single-digit MB). Both listed in
  `.claude/asset-dirs.txt`.
- **Plain git, no LFS — a measured choice, not an omission:** the authored
  binary payload is ~18 MB and write-once — measured over the private dev
  repository's Unity tree (du/find, 2026-08-15, n=1) — and the Unity
  project serializes Force-Text, so scenes/prefabs/materials are diffable
  YAML, not binaries;
  LFS's churn benefit does not apply to write-once assets, while its
  metered bandwidth quota on a public repository is a documented
  failure mode (every external clone bills the owner's free quota).
- **Generated artifacts never enter history, anywhere:** WebGL app builds
  ship as GitHub Release assets (the runner fetches them); run outputs,
  datasets, and model weights stay out of git entirely. This is the clause
  that ended the pre-v2 era's repeated build commits — the dominant weight
  in both historical repositories.
- **No paired data repository** — nothing durable needs one yet; the
  reactivation trigger is named under Reversibility.

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
time; both read the one seam file. The "configure LFS before the first binary" ordering is
advisory — upheld by review, since no gate can see a pattern that doesn't
exist yet.

## Consequences

- Clones stay lean indefinitely; history never needs a rewrite to shed
  weight — which keeps the append-only history rule (D-003) affordable.
- Publishable artifacts (app builds) get a real distribution channel —
  Release assets — instead of a tolerated corner of source history; run
  outputs have deliberately no in-repo home.
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

- **Named reactivation triggers:** adopt LFS only if a single needed asset
  exceeds ~50 MB or authored-asset churn becomes sustained; propose a
  data-repo ADR when the first durable dataset/results drop must be
  publicly versioned (roughly >10 MB). Until a trigger fires, revisiting
  this posture is out of scope.

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
