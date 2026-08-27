---
description: Archive .claude/working/ contents to .claude/archive/YYYY-MM-DD/<slug>/
disable-model-invocation: true
---

Archive the current working docs. The task slug is: $ARGUMENTS (if empty,
derive a short kebab-case slug from this session's main task and say which
you chose).

Steps, in order:

1. **Check for still-running work.** If any file in `.claude/working/` is the
   live state of an unfinished task (loop state, checkpoints, resume docs),
   leave it in place and say so — never archive a running task's state files.
2. **Move everything else** (except `README.md`) into the dated archive
   folder:

   ```bash
   DEST=".claude/archive/$(date +%F)/<slug>"
   mkdir -p "$DEST"
   find .claude/working -mindepth 1 -maxdepth 1 -not -name 'README*' \
     -exec mv {} "$DEST/" \;
   ```

3. **Report** what was archived and what was deliberately left behind. Do not
   delete anything — purging requires explicit user instruction
   (`.claude/archive/README.md`).
