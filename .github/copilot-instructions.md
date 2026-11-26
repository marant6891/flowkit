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

**Agents** are located under `agents/`. Each `*_agent.md` file is a Claude Code agent definition with YAML frontmatter. The main orchestrator is `flowkit-orchestrator_agent.md`.

## When to Activate a Skill

Activate a skill when the user requests an output that matches the skill's `description`. Key triggers:
- User has an **idea, concept or problem** and wants a **guided requirements workshop** up to the target document, or asks to resume a workshop → `flowkit-requirements-workshop` (always interactive, ask and wait at every gate)
- User asks for a **PT, PRD, change spec, or requirements document** → `flowkit-client-pt-prd-writer`
- User provides a **meeting transcript (.vtt, .docx)** and asks for a **summary or email** → `flowkit-client-meeting-recap`
- User asks for **documentation of an existing solution** — **end-user help, user guide, manual, quick start, FAQ, admin guide or technical documentation** — based on its **source code**, for a given audience and Word template → `flowkit-client-solution-docs-writer`
- User pastes a **draft e-mail or chat message to a client** and asks to **improve, soften, shorten or turn it into a written confirmation ("dupokrytka")** → `flowkit-client-message-editor`
- User asks for a **postmortem, RCA, incident report** → `flowkit-devops-incident-postmortem`
- User asks for a **reliability or SRE review, SLO, alerts, probes, resource limits, scaling or backup** → `flowkit-devops-sre-review`
- User asks for a **SQL query, database or analytical report (KPI, trends, period comparison, ranking, cohorts), data check, INSERT, UPDATE or DELETE** → `flowkit-sql-data-assistant`

When activating a skill, read the full `SKILL.md` and all files referenced inside it before generating output.

## Main agent — flowkit-orchestrator

The `flowkit-orchestrator` agent is the single entry point. It coordinates subagents using a strict 3-step iteration loop:
- Each iteration: ≤3 steps → summarize → ask user → repeat
- Supported prefixes: `ANALYZE:` `VERIFY:` `PLAN:` `SPEC:` `DRY:` `LOG:` `DEVOPS:` `DIAG:` `BA:` `SQL:` `SHIP:` `AUTO:` `FAST:` `STRICT:` (whole task on recommendations, no checkpoint stops except high-risk actions). Prefixes are optional: without one the orchestrator selects the action from the request
- Subagents (hidden from the agent picker, called by the orchestrator): `flowkit-code-analyzer`, `flowkit-verifier`, `flowkit-planner`, `flowkit-implementer`, `flowkit-devops`, `flowkit-product-owner`, `flowkit-diagnostics`, `flowkit-analyst`, `flowkit-validator`

See [`agents/flowkit-orchestrator_agent.md`](../agents/flowkit-orchestrator_agent.md) for full protocol.

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
