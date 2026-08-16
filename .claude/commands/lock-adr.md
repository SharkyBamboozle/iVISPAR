---
description: Revoke a previously issued /unlock-adr token
disable-model-invocation: true
---

Re-lock a Decided ADR page by revoking its unlock token. The ADR id is:
$ARGUMENTS (short form, e.g. `adr-0002`; empty = revoke ALL tokens).

```bash
# Revoke one id (or delete the whole file to revoke all):
sed -i "/^<adr-id> /d" .claude/working/UNLOCKED_ADRS 2>/dev/null || true
```

Report which tokens were revoked and which (if any) remain.
