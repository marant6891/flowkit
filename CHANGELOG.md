# Changelog — FlowKit

Wszystkie znaczące zmiany w repozytorium. Format zgodny z [Keep a Changelog](https://keepachangelog.com/pl/).

---

## [1.1.0] — 2026-11-11

### Dodano
- **Skill `client-meeting-recap` v1.0**: Transformacja transkrypcji VTT/DOCX w podsumowanie e-mail dla klienta z podziałem Action Items (Nasz Zespół vs Klient).
- **Skill `devops-incident-postmortem` v1.0+1.1**: Blameless postmortem z osią czasu, 5 Whys i Action Items PREVENT/DETECT/MITIGATE.
- `references/vtt-formats.md` w `client-meeting-recap` — instrukcja obsługi formatów MS Teams, Zoom, Google Meet.
- `checklists/postmortem-review-checklist.md` w `devops-incident-postmortem`.
- `examples/log-to-timeline-example.md` w `devops-incident-postmortem`.
- Sekcja komunikacji (interesariusze) w szablonie postmortem.
- Metryki MTTD/MTTR w tabeli nagłówkowej szablonu postmortem.
- Reguła doboru tonu (formalny/semi-formalny) w szablonie e-mail `client-meeting-recap`.
- Konwencja nazewnictwa pliku wyjściowego `recap-YYYY-MM-DD-[skrót].md`.
- `CHANGELOG.md` dla skilli `client-meeting-recap` i `devops-incident-postmortem`.
- Pola `version`, `tags`, `author`, `homepage` w `plugin.json`.
- Rozbudowane `.github/copilot-instructions.md` z sekcjami Role, When to Activate, Core Rules.
- `CHANGELOG.md` projektu (ten plik).
- `CONTRIBUTING.md` z wytycznymi dla autorów nowych skilli.

### Zmieniono
- `_template/SKILL.md`: dodano pola `version`, `tags`, komentarze HTML, kompletna struktura etapów.
- `_template`: dodano podkatalogi `checklists/`, `examples/`, `references/`, `templates/` z plikami `.gitkeep`.
- CI `validate-skills.yml`: rozbudowana walidacja (zgodność `name` z katalogiem, weryfikacja `version`, `tags`, `templates/`, sprawdzanie wewnętrznych linków w SKILL.md).
- Frontmatter wszystkich skilli uzupełniony o `version` i `tags`.

### Naprawiono
- Hardcoded przykłady (`Szybka reakcja dyżurnego`) usunięte z szablonu postmortem.
- Dwuznaczne otwarcie e-maila (`Cześć / Dzień dobry`) zastąpione logiką wyboru tonu.

---

## [1.0.0] — 2026-11-11

### Dodano
- Inicjalne repozytorium FlowKit z pierwszym skillem `client-pt-prd-writer` v2.0.
- Licencja MIT, `.gitignore`, `README.md`, `plugin.json`.
- Skrypty instalacyjne `scripts/install.ps1` i `scripts/install.sh`.
- GitHub Ruleset ochrony gałęzi `main` (`protect-main.json`).
- CI workflow `validate-skills.yml` (walidacja frontmatteru YAML).
- Szablony PR i Issues dla społeczności.
- `.github/copilot-instructions.md` i `.github/prompts/`.
