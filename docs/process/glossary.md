# Glossary

Track new terminology here **as it enters the project**. Each term: a bold
name, a 1–3 sentence definition that links to the term's canonical page
(never duplicating the analysis), and an italic **provenance tag** —
*(Session N)*, *(Q##)*, or *(Session N + #issue)* — so you can trace when and
why the term arrived. Group terms under thematic headings as the list grows; a
heading may carry a scope disclaimer reusing the status legend (e.g. *"all 🟡
ideas, nothing decided"*).

## Core concepts

- **Episode** — one puzzle instance solved in a closed loop: configuration +
  seed → observations → actions → result log. *(Session 1)*
- **Environment** — a puzzle family the simulator implements: sliding geom
  board, sliding tile puzzle, Rubik's Cube. *(Session 1)*
- **Modality** — how an episode is observed: 3D render, 2D schematic, or
  text description. *(Session 1)*
- **Action–perception loop** — the runner↔app cycle: the agent acts, the app
  applies the action and returns the next observation. *(Session 1)*
- **WebGL bridge** — the local WebSocket link between the Python runner and
  the Unity WebGL app served in a browser. *(Session 1)*
- **Agent** — the policy under evaluation: a VLM behind the adapter layer, a
  scripted baseline (A*, random), or a human. *(Session 1)*
- **App build** — the compiled Unity WebGL artifact the runner serves;
  distributed as a GitHub Release asset, never committed. *(Session 1)*
