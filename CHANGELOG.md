# Changelog — FlowKit

Wszystkie znaczące zmiany w repozytorium. Format zgodny z [Keep a Changelog](https://keepachangelog.com/pl/).

---

## [Unreleased]

---

## [1.3.0] — 2026-11-17

### Dodano
- **Katalog Agentów (`agents/`)**: Wprowadzono pełny system 7 agentów (`agent-3x3` jako główny orkiestrator oraz 6 wyspecjalizowanych subagentów: Analyzer, Verifier, Planner, Implementer, DevOps, PM).
- **Deterministyczny silnik obsługi dokumentów (.docx/.dotx)**: Dodano `references/docx-engine.md` z inteligentną detekcją zainstalowanych bibliotek w środowisku (`python-docx` jako priorytet 1, `mammoth`, `docx2txt`, `pypandoc`, fallback do Markdown).
- **Instalator skilli i agentów**: Rozszerzono `install.ps1` oraz `install.sh` o obsługę instalacji agentów (`-AgentName all` / `agent all`) do `~/.claude/agents/`.
- **Manifesty wtyczek**: Zaktualizowano `.claude-plugin/plugin.json` oraz `marketplace.json` do wersji 1.3.0 z definicjami sekcji `agents`.

### Poprawiono i zabezpieczono
- Naprawiono wykrywanie agenta domyślnego w VS Code (`agent-3x3`).
- Zabezpieczenie autora w repozytorium publicznym: rozszerzono `.gitignore` (m.in. `agent-context/`, `AGENT_LOG.md`, pliki klientów, transkrypcje, klucze) oraz dodano dedykowaną sekcję bezpieczeństwa w `README.md`.
- Wdrożono pełne 16 poprawek jakościowych audytu agentów (m.in. whitelist narzędzi `execute`, jawne raportowanie w trybie RE-CHECK, standalone mode dla DevOps).

---

## [1.2.0] — 2026-11-11

### Rozszerzenia standardu rynkowego (Benchmark Alignment)

#### `client-pt-prd-writer` v2.1
- **Gherkin Given-When-Then**: Wprowadzono scenariusze akceptacyjne dla User Stories przygotowane pod automatyzację QA.
- **Definition of Done (DoD)**: Dodano 5-punktową checklistę ukończenia zmiany w szablonie i instrukcji.
- **Non-Goals (Anty-cele)**: Jawna sekcja ograniczeń zakresu przeciwko zjawisku Scope Creep.
- **Context Boundary (XML Tags)**: Wytyczne izolacji bloków `<source_materials>` i `<user_template>`.

#### `client-meeting-recap` v1.1
- **Dwuczęściowy format (Dual Output)**:
  - **Część A: Wewnętrzny Radar Ryzyk** (nastroje klienta, próby rozszerzenia zakresu, blokady decyzyjne — wyłącznie dla zespołu),
  - **Część B: Oficjalny szkic e-maila** do klienta.
- **Zasada DRI (Directly Responsible Individual)**: Wymóg przypisania konkretnego imiennego właściciela do każdego zadania.
- **Correction Safety Net**: Klauzula bezpieczeństwa dająca klientowi 24–48h na zgłoszenie korekt.
- **Filtr Burzy Mózgów**: Odróżnianie luźnych pomysłów od wiążących uzgodnień.

#### `devops-incident-postmortem` v1.2
- **Zgodność z Google SRE & PagerDuty**:
  - Formalne role incydentowe: Incident Commander (IC), Tech Lead, Comms Lead.
  - Severity Matrix: SEV-1, SEV-2, SEV-3 oraz Near-Miss (postmortem prewencyjny).
  - Wieloczynnikowy łańcuch przyczyn: **Trigger, Amplifier, Detection Gap, Process Gap** + 5 Whys.
  - Rejestr komunikatów zewnętrznych, historia Status Page i analiza naruszenia SLA.

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
- `DEVELOPMENT.md` ze standardami inżynierskimi, strategią gałęzi Git (zasada zmian wyłącznie przez PR do `main`), konwencją Conventional Commits i polityką bezpieczeństwa.

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

