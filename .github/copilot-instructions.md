# GitHub Copilot Instructions for FlowKit

This repository provides reusable **Agent Skills** and **Agents** for Business/Systems Analysts and DevOps Engineers. All skills operate strictly on user-provided source materials and never invent facts, dates, or requirements.

## Repository Structure

**Skills** are located under `skills/<skill-name>/`. Each skill contains:
- `SKILL.md` — main instructions with YAML frontmatter (`name`, `version`, `tags`, `description`).
- `checklists/` — quality-gate checklists to run before delivering output.
- `examples/` — concrete input → output transformations.
- `references/` — supporting guides (formats, terminology, mapping rules).
- `templates/` — fallback output templates when the user has no custom template.
- `CHANGELOG.md` — version history of the skill.

**Agents** are located under `agents/`. Each `*_agent.md` file is a Claude Code agent definition with YAML frontmatter. The main orchestrator is `agent-3x3_agent.md`.

## When to Activate a Skill

Activate a skill when the user requests an output that matches the skill's `description`. Key triggers:
- User asks for a **PT, PRD, change spec, or requirements document** → `client-pt-prd-writer`
- User provides a **meeting transcript (.vtt, .docx)** and asks for a **summary or email** → `client-meeting-recap`
- User asks for a **postmortem, RCA, incident report** → `devops-incident-postmortem`

When activating a skill, read the full `SKILL.md` and all files referenced inside it before generating output.

## Agent 3x3 — Orchestrator

The `agent-3x3` orchestrator coordinates subagents using a strict 3-step iteration loop:
- Each iteration: ≤3 steps → summarize → ask user → repeat
- Supported prefixes: `ANALYZE:` `VERIFY:` `PLAN:` `SPEC:` `DRY:` `LOG:` `DEVOPS:` `SHIP:`
- Subagents: Analyzer, Verifier, Planner, Implementer, DevOps, PM

See [`agents/agent-3x3_agent.md`](../agents/agent-3x3_agent.md) for full protocol.

## Core Rules (All Skills & AI Agents)

- **No direct push to `main`:** All changes must be developed on feature branches (`feat/*`, `fix/*`, `docs/*`) and merged into `main` exclusively through Pull Requests after CI validation passes.
- **No hallucination:** Every fact in output must come from user-provided materials. Missing data → mark as `DO POTWIERDZENIA` (w skillach z rejestrem tematów także `OPEN-NNN`), or `Brak danych`.
- **User's template takes priority** over the skill's fallback template.
- **No sensitive data in commits:** No client names, credentials, tokens, or production hostnames.
- **Always validate before PR:** Run `python scripts/validate_skills.py` to ensure all skills meet structure and frontmatter requirements.

## Detailed Engineering Guidelines

See [`DEVELOPMENT.md`](../DEVELOPMENT.md) for full branch strategy, conventional commits, quality standards, and security policies.

## Contributing a New Skill

Copy `skills/_template/`, rename `SKILL.template.md` to `SKILL.md`, fill in its frontmatter, and add the skill to the catalog table in `README.md`. The CI pipeline validates frontmatter on every push and PR.
