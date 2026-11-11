# GitHub Copilot Instructions for FlowKit

This repository provides reusable **Agent Skills** for Business/Systems Analysts and DevOps Engineers. All skills operate strictly on user-provided source materials and never invent facts, dates, or requirements.

## Repository Structure

Skills are located under `skills/<skill-name>/`. Each skill contains:
- `SKILL.md` — main instructions with YAML frontmatter (`name`, `version`, `tags`, `description`).
- `checklists/` — quality-gate checklists to run before delivering output.
- `examples/` — concrete input → output transformations.
- `references/` — supporting guides (formats, terminology, mapping rules).
- `templates/` — fallback output templates when the user has no custom template.
- `CHANGELOG.md` — version history of the skill.

## When to Activate a Skill

Activate a skill when the user requests an output that matches the skill's `description`. Key triggers:
- User asks for a **PT, PRD, change spec, or requirements document** → `client-pt-prd-writer`
- User provides a **meeting transcript (.vtt, .docx)** and asks for a **summary or email** → `client-meeting-recap`
- User asks for a **postmortem, RCA, incident report** → `devops-incident-postmortem`

When activating a skill, read the full `SKILL.md` and all files referenced inside it before generating output.

## Core Rules (All Skills)

- **No hallucination:** Every fact in output must come from user-provided materials. Missing data → mark as `[Do potwierdzenia]`, `OPEN-NNN`, or `Brak danych`.
- **User's template takes priority** over the skill's fallback template.
- **No sensitive data in commits:** No client names, credentials, tokens, or production hostnames.

## Contributing a New Skill

Copy `skills/_template/`, fill in `SKILL.md` frontmatter, and add the skill to the catalog table in `README.md`. The CI pipeline validates frontmatter on every push and PR.
