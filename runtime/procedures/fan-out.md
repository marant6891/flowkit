## Parallel fan-out (conditional)

If the current platform's `agent` tool supports issuing multiple subagent calls within a single turn, Orchestrator MAY fan out **independent, read-only** subagent calls (Analyzer/Verifier/PM only — never Implementer/DevOps edits) when their scopes do not overlap and do not depend on each other's output — e.g. Analyzer on module A + Analyzer on module B, or Analyzer + PM on unrelated concerns.

- All calls in one fan-out count together as **one `[SUB]` step** toward the 3-step iteration cap, not one each.
- Each call still follows its own Delegation rule (scoped input, optional `AGENT_CONTEXT` filename).
- Results from all calls in the fan-out are merged into a single checkpoint summary (`REPORT_PROGRESS`) — one block per subagent, not interleaved.
- If the platform does not support multi-call turns, Orchestrator silently falls back to sequential calls — this is not reported as a limitation to the user, just handled.
- Never fan out calls that write files (Implementer, DevOps `edit` steps) — those stay strictly sequential to avoid conflicting edits.
