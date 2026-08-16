# Roadmap

The project is mid-migration: the refactored framework moves here from the
private dev repository in staged, gated waves.

- **Phase A — re-seed** *(this line)*: blueprint scaffolding instantiated on
  `development`; the EMNLP 2025 tree retired to tag `emnlp25`.
- **Phase B — content waves** *(one PR each)*: Python framework as the
  installable `ivispar` package · Unity project under `unity/` · app-build
  delivery via Release assets · configs & instructions · docs merge ·
  process reconciliation · tracker port.
- **Phase C — cutover**: promotion of `development` to `main` as release
  **2.0.0**.
- **Phase D — post-cutover**: full scripted-episode harness; HPC/Apptainer +
  local-models epic.

Work that de-risks 🟡 proposed decisions before they are promoted to ✅ is
organised as **validation spikes** — each proves one claim or answers one
question, in isolation, as the narrowest slice that forecloses nothing. A
spike is distinct from a **vertical slice / MVP**, which exercises all pillars
end-to-end while deferring every hard choice to its `Q##`.

## Phase 0 — validation spikes

### Spike A — headless transport smoke

**Answers Q3 / de-risks the Phase-C cutover gate.**

- **Scope:** serve the app build, open the WebSocket bridge under headless
  Chromium, send one action, receive its acknowledgement and a screenshot.
- **Exit criterion (green):** acknowledged action + non-empty screenshot
  payload. Measured but not gating: loop latency.
- **Explicitly deferred:** full scripted episode and episode-save fix
  (gated on Q1 — dataset regeneration).
- **Related:** Q1 · Q3 · the Phase-B build-delivery wave.

### Spike B — remote binary-push probe

**De-risks the Unity wave (its transport, not its content).**

- **Scope:** push one small binary blob from a remote agent session to a
  scratch branch through the session git proxy.
- **Exit criterion (green):** the blob is visible via the GitHub API at the
  pushed ref.
- **Explicitly deferred:** everything about *which* assets ship (gated on
  Q2 — texture licensing).
- **Related:** Q2 · the Phase-B Unity wave.

## Exit criteria

How spike outcomes flip registry statuses — promotion happens here, not
informally:

Spike A green + Phase-B waves merged → the promotion PR (release 2.0.0).
Spike A red → the cutover waits and Q3 escalates to the operator.
Spike B red → the Unity wave lands via operator-side push instead.
