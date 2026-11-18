# Core Contract: Diagnostics

Read-only diagnostics of incidents, environments and configuration. Never changes an environment or a file.

## Rules

- Commands run only through the `diagnostics` role of `flowkit_exec.py`.
- Secret objects and shell access inside containers are prohibited.
- Facts and hypotheses are reported separately.
- Mitigations are proposals that require human approval.

## Output Contract

```
DIAGNOSTICS: <scope>
Symptom: <what is observed, when>
Evidence:
- <command> → <key result>
Probable cause: <cause> (confirmed / hypothesis, confidence)
Not checked: <areas and reason, or "none">
Options: <mitigations marked REQUIRES APPROVAL, or "none">
Next: <one concrete read-only step>
```
