## Procedure: Diagnostics → DevOps → Validator → verification

Use for infrastructure problems and configuration changes. Each step passes the handoff block below; never re-derive context that the block already holds.

1. **Diagnostics** collects evidence (read-only) and fills Symptoms, Evidence, Impact, Hypotheses, Cause.
2. **DevOps** prepares the change in files and fills Proposed change, Validation plan, Risk and rollback.
3. **Validator** runs the static checks from the validation plan and fills Result per check.
4. A `FAIL` goes back to DevOps with the exact failing lines (correction loop, at most 2 attempts).
5. `Apply:` commands are never run by an agent. Show them to the user as `WAIT_FOR_APPROVAL`; a person or an approved pipeline applies them.
6. After the user reports the change applied, **Diagnostics** re-checks the original symptom.
7. Final report: the handoff block with every field filled or marked `UNKNOWN`.

```
HANDOFF: <task or incident id>
Symptoms: <what is observed, when>
Evidence: <command or file → key result>
Impact: <users, services, environments>
Hypotheses: <hypothesis — confidence high/medium/low>
Cause: <confirmed cause with evidence, or "unconfirmed">
Proposed change: <files and one-line purpose>
Validation plan: <static checks for Validator>
Result: <check — PASS/FAIL/NOT_RUN/UNKNOWN/BLOCKED>
Risk and rollback: <risk, how to revert>
After change: <re-check result, or NOT_RUN>
```

No access to the environment does not block the plan: prepare the change and the validation, and mark live checks `NOT_RUN`.
