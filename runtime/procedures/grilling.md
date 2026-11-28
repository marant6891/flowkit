## Grilling: critical questioning of a plan, decision or document (`GRILL:` / `PRZEPYTAJ:`)

Goal: reach a shared understanding with the user before anyone acts. The result is a confirmed list of decisions
and open questions, not a document and not code. Orchestrator runs it itself and never delegates it: subagents
cannot ask the user.

Contents: 1. Decision tree · 2. Facts or decisions · 3. Rounds · 4. Recording answers · 5. Done condition · 6. Output.

### 1. Decision tree

- Read the plan, idea, decision or document the user points to, and the sources around it.
- List the decisions it depends on. A decision depends on another when its sensible options change with the other
  answer (e.g. "which database" depends on "do we host it ourselves").
- **Frontier** = open decisions whose prerequisites are all settled. Only frontier questions may be asked now. A
  question that depends on an unanswered one waits for a later round, even when it seems important.

### 2. Facts or decisions

- **Fact** (answer exists in code, files, configuration or delivered materials): look it up instead of asking. Use
  `read`/`search` or delegate a read-only Analyzer or Analyst call. Record the answer as `SRC-NNN` with its locator.
  The lookup does not block the round: only questions that depend on the fact wait for it.
- **Decision** (priorities, scope, trade-offs, ownership, acceptance, anything the sources do not settle): always
  ask the user. Never answer it yourself, never infer it from field or class names, never fill it with a "typical"
  value.
- A fact you could not find becomes a question to the user, phrased as "I did not find X in <where I looked>".

### 3. Rounds

- Ask the whole frontier in one round, blocking questions first. Each question has an ID `Q-NNN`, one sentence on
  why it matters, 2-4 options with the recommended one first and marked „(rekomendowane)", and a one-line reason for
  the recommendation. Word it so that accepting the recommendation is a short answer.
- Present the round through `ASK_USER` in the question window: at most 4 questions per window, the rest in the next
  window of the same round. Diagnostic line `Ask: window` or `Ask: text — <reason>`, as everywhere in FlowKit.
- At most 8 questions per round. More frontier questions: ask the 8 with the widest impact, keep the rest for the next
  round.
- Wait for the answers. Then recompute the frontier: new decisions opened by the answers join it, decisions that the
  answers made irrelevant are closed with a one-line reason.

### 4. Recording answers

- Accepted answer → `DEC-NNN: <decision> | <who decided> | <round>`.
- "I don't know" or no answer → `OPEN-NNN` with the decision owner if known. Do not keep re-asking the same question;
  continue with branches that do not depend on it.
- An answer that contradicts a source → show both (`CONTRADICTION:` with quotes) and ask which one wins. Never settle
  it silently.
- Keep the tree in the answer (or in `agent-context/` when the session uses subagents): decisions, open items and
  which questions are still waiting for which prerequisite.

### 5. Done condition

Stop questioning when all three hold:
1. the frontier is empty,
2. every branch ends in `DEC-NNN`, `SRC-NNN` or `OPEN-NNN`; nothing is assumed silently,
3. the user confirmed the summary from section 6.

The user can stop earlier ("wystarczy", "stop"): then mark the remaining branches as `OPEN-NNN` and show the summary.
Do not start implementation, a document or any change until the user confirms the summary; after confirmation,
offer the next step (e.g. `PLAN:`, the PT/PRD skill, `TEST:`) through `ASK_USER`.

### 6. Output

```
GRILL: <topic>
Decisions: DEC-001 … (decision | who | round)
Facts checked: SRC-001 … (fact | locator)
Open: OPEN-001 … (what is missing | owner | what it blocks)
Contradictions: <list or "none found">
Rounds: <number>
Next: <one recommended step after confirmation>
```

### Modes

- `AUTO:` is incompatible with grilling: decisions belong to the user. When both are given, say so in one line and
  ask which one to use (recommended: `GRILL:`).
- `FAST:` does not shorten grilling; it only skips subagent lookups when the facts are already in the conversation.
- Language: questions and the summary in the user's language, plain language per `plain-language.md`.
