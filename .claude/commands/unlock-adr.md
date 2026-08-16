---
description: Unlock a ✅ Decided ADR for maintenance edits in this session (1h token)
disable-model-invocation: true
---

Unlock a Decided ADR page for a legitimate **maintenance** edit — a typo
fix, an annotation admonition, or the 🧊 supersession marker. The ADR id is:
$ARGUMENTS (short form, e.g. `adr-0002`).

Steps, in order:

1. **Confirm this is maintenance, not a decision change.** A changed
   decision is a NEW superseding ADR (`/adr-new`) — never an edit. If in
   doubt, stop and ask the user.
2. **Write the token** (read-time TTL — stale lines expire on their own):

   ```bash
   mkdir -p .claude/working
   echo "<adr-id> $(date +%s)" >> .claude/working/UNLOCKED_ADRS
   ```

3. **Remember the trailer.** Any commit touching the unlocked page must
   carry `Unlock-ADR: <adr-id> — <one-line reason>` — the `adr-gates.yml`
   CI check fails otherwise. `/lock-adr <adr-id>` revokes the token early.
