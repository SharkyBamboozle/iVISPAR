---
paths:
  - ".claude/commands/**"
  - ".claude/hooks/**"
  - ".claude/skills/**"
  - ".claude/rules/**"
  - ".claude/settings.json"
  - ".github/**"
  - "docs/process/**"
  - "docs/.templates/**"
  - "scripts/**"
  - "Makefile"
---

# Flag harvest candidates

You are touching a process file (contributing, templates, hooks, workflows,
commands, scripts). When you improve one in a way that isn't specific to
this project, flag it as a **harvest candidate** — a `note` issue mentioning
the blueprint — so the next blueprint harvest pass picks it up.

*(Advisory — no gate detects a forgotten harvest note; upheld by review at
harvest time, per D-004.)*
