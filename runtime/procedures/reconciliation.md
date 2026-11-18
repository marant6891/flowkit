## Reconciliation — conflicting subagent results

If two subagent calls in the same task produce contradictory findings on the same scope (e.g. Analyzer reports "clean" on a file, Verifier later reports `[FAIL]` on the same file/area; or Planner assumes a pattern Analyzer's findings contradict):

- Orchestrator does **not** silently pick one result or discard the other.
- Both results are surfaced together at the top of the next checkpoint (`REPORT_PROGRESS` / `ASK_USER`), labeled `CONFLICT:`, with a one-line note on the likely cause (e.g. "code changed between calls", "different scope/dimensions checked", "stale AGENT_CONTEXT entry").
- Orchestrator proposes re-running the more specific/recent subagent on the narrowed scope as one of the `Next:` options — never resolves the conflict by assumption.
- The `AGENT_CONTEXT` entry for the stale finding is not deleted — a new entry is appended noting the correction, so the file keeps an honest trail.
