# {{PROJECT_NAME}} — data repository

Durable home for run artifacts: metrics, plots, videos, checkpoints, and
anything else a run produces that is worth keeping. Paired with the code repo
[`{{GITHUB_OWNER}}/{{PROJECT_SLUG}}`](https://github.com/{{GITHUB_OWNER}}/{{PROJECT_SLUG}})
— see its data-repository ADR for the decision record.

**The split:** nothing binary is ever committed to the code repo; its `data/`
directory is a gitignored local staging area only. This repo is the durable,
shareable home — organised **one folder per experiment** (see
`runs/README.md` for the run-folder contract). Cross-repo references go by
folder name + decision ID, never by committed artifact.

**Storage:** plain git blobs, deliberately no LFS (GitHub's free LFS quota is
a trap for a mostly-binary repo). **Escalation trigger:** when this repo
passes ~2 GB or clone times hurt, move artifacts to LFS or object storage —
artifact *paths are config* in the code repo's tooling, so the move touches
configuration, not code.

**Workflow:** tooling pushes directly to `main` (no PR flow here — this repo
records outputs, it doesn't review them). Force-pushes are blocked; history
is append-only.
