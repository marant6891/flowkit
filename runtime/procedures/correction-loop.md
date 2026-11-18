## Correction loop — Verify → Fix → re-Verify

When Verifier returns `Overall: FAIL` on a scope that Implementer (or a direct Orchestrator edit) just touched:

- `Next:` in that iteration's checkpoint includes the option **"Fix via Implementer + re-Verify (attempt 1/2)"** alongside the normal retry/skip/rollback options — the user still chooses it, this is not auto-continue.
- If chosen: Implementer is invoked with the exact `[FAIL]` lines from Verifier as its step description (not a vague "fix it"). After Implementer returns `DONE`/`PARTIAL`, Verifier re-checks **only the same scope + same dimensions** that failed — not a full re-scan.
- Counts as attempt 1. If it fails again, the same option is offered once more, labeled **"attempt 2/2"**.
- After a second consecutive `FAIL` on the same scope+dimension, the loop stops automatically — Orchestrator does not offer a third automatic attempt. It presents both failed attempts side by side and asks the user to decide manually (adjust the plan, escalate to `ANALYZE:`, or accept as known issue).
- Each attempt gets its own condensed entry in `AGENT_CONTEXT` (see below) so the trail of what was tried is preserved.
