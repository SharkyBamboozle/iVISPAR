# Vision

iVISPAR exists to measure how well vision-language models *act* in space —
not whether they can describe an image, but whether they can plan and execute
multi-step spatial manipulations under feedback. A Python runner drives a
Unity WebGL simulator through an action–perception loop; the same episode is
observable as a 3D render, a 2D schematic, or text, so modality itself is an
experimental variable rather than a fixed choice.

The benchmark serves two audiences at once: researchers comparing VLM agents
against scripted and human baselines on a controlled, reproducible task
family — and the project's own line of publications, from the EMNLP 2025
paper (frozen at tag `emnlp25`) to the Rubik's-Cube follow-up in
preparation. This public repository is the canonical, citable home of both.

The near-term direction is the v2 rebuild: the privately refactored
framework (installable `ivispar` package, provider-agnostic VLM adapters,
headless execution) migrates here in staged waves and cuts over as release
2.0.0.

The vision translates into [design principles](design-principles.md) — the
standing constraints — and [requirements](requirements.md) — the hard
criteria every architecture and tooling choice is judged against.

!!! info "Deliberately deferred strategic choices"
    A strategic fork kept open **on purpose** is recorded here with its
    rationale and the trigger that will force it — a deliberate non-decision,
    documented as such so it is never mistaken for an oversight.

    **Benchmark artifact vs. evaluation platform** — whether iVISPAR stays a
    paper-anchored benchmark or grows into a general platform for interactive
    spatial-reasoning evaluation stays open until the follow-up paper ships;
    keeping both ramps open is cheap because the framework rebuild is the
    same work either way.
