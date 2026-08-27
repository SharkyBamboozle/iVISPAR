# Requirements

Hard constraints the project must satisfy, each with a stable `R##` ID — never
renumbered. Requirements are **derived from the [vision](vision.md)** and
serve as the evaluation criteria for architecture and tooling decisions
(see the [decisions registry](../decisions/index.md)); the traceability chain runs
vision → `P#` principles → `R##` requirements → analysis → `D-xxx` decisions.

When a requirement's premise weakens, **annotate it** with a note admonition
naming the gating question and session — the row stands as written.

| # | Requirement | Driven by |
|---|-------------|-----------|
| R1 | Any published result is re-runnable from its own artifacts (episode config + seed + app-build generation) | Vision — credibility; P3 |
| R2 | The full action–perception loop runs end-to-end on a single dev machine (Python runner + served WebGL app, no cloud dependency) | Vision — accessible benchmark |
| R3 | The EMNLP 2025 paper state stays reachable and byte-stable at tag `emnlp25` | P4 — immutable paper record |
| R4 | Every VLM provider integrates through one adapter interface; adding a provider touches no runner code | P2 — comparable evaluation |
