# Design principles

The **standing constraints** against which architecture and stack choices are
judged — derived from the [vision](vision.md). Keep the set small (3–6 — only
principles that actually constrain); reference them by bare ID ("that violates
P2") instead of re-litigating recurring arguments. IDs are stable — never
renumbered.

**P1 — Evaluate interaction, not description.**
:   The unit of evaluation is a closed-loop episode — observe, act, receive
    feedback, repeat. Static single-shot judgments about an image are out of
    scope. This rules out benchmark designs that collapse into captioning or
    one-turn VQA.

**P2 — One episode, many modalities.**
:   Every environment renders the same underlying episode as 3D vision, 2D
    schematic, and text, so modality is an experimental variable over an
    otherwise identical task. This rules out modality-specific task forks
    whose results cannot be compared.

**P3 — Results are re-runnable.**
:   An episode is fully determined by its configuration, seed, and app-build
    generation; a published number must be reproducible from those artifacts.
    This rules out hidden state, hand-run experiments, and results that
    cannot name their inputs.

**P4 — The paper record is immutable.**
:   A published paper's repository state is frozen (tag `emnlp25`) and never
    rewritten; the benchmark evolves forward only. This rules out history
    rewrites and retroactive edits to cited artifacts.
