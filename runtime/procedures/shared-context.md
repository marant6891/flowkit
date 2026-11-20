## Shared context — AGENT_CONTEXT file (token/cost optimization)

Purpose: let subagents skip re-reading/re-analyzing what an earlier subagent in the same task already found, without inflating prompts with verbatim history. Reduces duplicate `read`/`search` work across Analyzer → Planner → Implementer → Verifier chains. Files double as an Obsidian-vault-ready knowledge trail across tasks.

**Location**
- Dedicated folder at the **workspace/repo root**: `agent-context/` (no leading dot — kept visible/discoverable, e.g. for later use as an Obsidian vault).
- If `agent-context/` does not exist yet, create it on first use.
- These files may contain client data. In a git repository, before the first write run `git check-ignore -q agent-context/`; if it is not ignored, add `agent-context/` and `AGENT_LOG.md` to `.git/info/exclude` with the `edit` tool (local only, no tracked file changes). Never commit these files.

**Creation**
- Created lazily on the task's **first** subagent call — not for single-shot direct edits with no subagent involved.
- Filename: `agent-context/AGENT_CONTEXT_{YYYYMMDD}_{HHMMSS}_{XXXX}.md`, where `XXXX` is a random 4-character alphanumeric id generated once at creation (e.g. `agent-context/AGENT_CONTEXT_20260923_141207_a93f.md`).
- The timestamp + random id makes the filename effectively unique per session — this is what allows **two or more chats to run different tasks in parallel in the same workspace** without colliding or overwriting each other's context.
- One file per task/session. Do not reuse an existing `AGENT_CONTEXT_*` file for an unrelated task in the same long-running chat — if scope changes materially, create a new one.

**File template (Obsidian-friendly frontmatter)**
```yaml
---
title: "<short task title>"
date: <YYYY-MM-DD>
tags: [agent-context, flowkit-orchestrator]
task: "<one-line task description>"
status: in-progress
related: []
---
```
- `related:` holds `[[AGENT_CONTEXT_...]]` wikilinks to other context files in this repo that cover the same module/feature (checked via `agent-context/` listing at task start). Left as `[]` if none found. This is what keeps the eventual Obsidian graph connected instead of a flat pile of isolated notes.

followed by appended entries below the frontmatter.

**Writing**
- Orchestrator **appends** (never overwrites, frontmatter stays at top) after every subagent call:
```
