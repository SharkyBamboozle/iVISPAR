# iVISPAR

Interactive multi-modal benchmark for evaluating the visual-spatial
reasoning of vision-language models acting as agents.

> **🚧 v2 rebuild in progress.** This line (`development`) carries the
> re-seeded benchmark: process scaffolding first, the refactored framework
> landing in staged waves — it is not yet runnable. For the working, citable
> state behind the EMNLP 2025 paper, use the frozen tag
> [`emnlp25`](https://github.com/SharkyBamboozle/iVISPAR/tree/emnlp25) or the
> [EMNLP25 Release](https://github.com/SharkyBamboozle/iVISPAR/releases/tag/emnlp25).

## What is iVISPAR?

iVISPAR evaluates VLMs as *agents*: a Python experiment runner drives a
Unity WebGL simulator over a WebSocket bridge, and the model solves sliding
geom-board, sliding-tile, and Rubik's-Cube puzzles it observes in 3D, 2D,
or text — a closed action–perception loop, not single-shot QA.

- 📄 Paper (EMNLP 2025): <https://aclanthology.org/2025.emnlp-main.1359/>
- 📄 Preprint: <https://arxiv.org/abs/2502.03214>
- 🌐 Project page: <http://ivispar.ai/>
- 🎬 Demo: <https://www.youtube.com/watch?v=Djis_xkgtW8>

## Reproducing the paper

Use the frozen snapshot — it preserves the exact code, configurations, and
playable WebGL build behind the published results:

```bash
git clone --branch emnlp25 https://github.com/SharkyBamboozle/iVISPAR.git
```

## Documentation

The `docs/` site (MkDocs Material) is the single source of truth — start at
`docs/index.md`, or build it locally:

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

The hosted docs site goes live with release 2.0.0.

## Citation

Mayer, J., Ballout, M., Jassim, S., Nosrat Nezami, F., & Bruni, E. (2025).
*iVISPAR — An Interactive Visual-Spatial Reasoning Benchmark for VLMs.* In
Proceedings of EMNLP 2025, pages 26757–26781.
<https://aclanthology.org/2025.emnlp-main.1359/>

```bibtex
@inproceedings{mayer-etal-2025-ivispar,
    title = "i{VISPAR} {---} An Interactive Visual-Spatial Reasoning Benchmark for {VLM}s",
    author = "Mayer, Julius  and
      Ballout, Mohamad  and
      Jassim, Serwan  and
      Nezami, Farbod Nosrat  and
      Bruni, Elia",
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-main.1359/",
    doi = "10.18653/v1/2025.emnlp-main.1359",
    pages = "26757--26781",
    ISBN = "979-8-89176-332-6"
}
```

## License

MIT © 2024 Julius Mayer — see [LICENSE](LICENSE).

---

Initialized from [Project Blueprint](https://github.com/SharkyBamboozle/CLAUDE_blueprint) v1.2.0
