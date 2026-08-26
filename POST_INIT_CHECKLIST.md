# Post-init checklist

Operator items left over from the bootstrap (most GitHub-side setup already
ran — labels, `development` + default flip, branch protection, merge
settings, `DEPLOY_DOCS=false`). Delete this file when every box is ticked.

- [ ] **Confirm the repo is NOT marked as a template** (Settings → General).
- [x] **LICENSE decision** — recorded: the repository keeps its own MIT
      (© 2024 Julius Mayer); the template's LICENSE never entered the tree.
- [x] **git lfs install** — not applicable: D-007 chose plain git, no LFS.
- [ ] **Secrets / integrations** — none needed yet. Provider API keys were
      rotated out during migration Phase 0; replacements go into local env
      vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`,
      `XAI_API_KEY`) when experiments resume — never into tracked files
      (gitleaks CI enforces).
- [ ] **Docs site** — deliberately dark until cutover. At release 2.0.0:
      re-run `github_setup.sh -R SharkyBamboozle/iVISPAR --deploy-docs`
      (note: a re-run re-asserts development as default — harmless then).
