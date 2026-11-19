# Changelog — FlowKit

Wszystkie znaczące zmiany w repozytorium. Format zgodny z [Keep a Changelog](https://keepachangelog.com/pl/).

---

## [Unreleased]

### Dodano
- **Zapis DOCX `md-to-docx`:** polecenie executora zapisuje Word z Markdown na kopii szablonu klienta (`--template` z treścią szablonu i znacznikiem `[[FLOWKIT:TREŚĆ]]` albo `--reference-doc` z samymi stylami). Dokument ma komplet stylów, numerację, nagłówki, stopki i styl tabel szablonu. Bloki mermaid są renderowane lokalnym mermaid-cli, a SVG zamieniane na PNG (Playwright, CairoSVG, rsvg-convert), więc Pandoc nie wymaga `rsvg-convert`.
- **`help` w executorze:** `flowkit_exec.py --role <rola> -- help` wypisuje polecenia dozwolone dla roli; odrzucenie wskazuje, jak zapisać DOCX.
- **Tryb `AUTO:`:** orkiestrator i skill PT/PRD realizują całe zadanie na rekomendacjach i oddają rejestr przyjętych decyzji.
- **Pytanie o źródła danych:** praca nad dokumentem zaczyna się od pytania o znane źródła do przygotowania i weryfikacji.

### Naprawiono
- Agenci nie mogli zapisać DOCX: `pandoc` i skrypty Python były poza listą dozwolonych poleceń.
- `detect-docx-libs` pokazuje też Pandoc, mermaid-cli, Playwright, CairoSVG i rsvg-convert.

---

## [1.7.0] — 2026-11-18

### Dodano
- **Automatyczny dobór działania:** `agent-3x3` bez prefiksu rozpoznaje rodzaj zadania i uruchamia właściwy skill lub subagenta.
- **Skill `sql-data-assistant`:** bezpieczne zapytania, zestawienia i skrypty poprawy danych dla PostgreSQL, SQL Server, Oracle, MySQL i MariaDB.
- **Lokalna kontrola `check_sql.py`:** typ bazy, zmienne, transakcja, ochrona przed nadpisaniem, kontrola liczby wierszy i domyślne `ROLLBACK`.

---

## [1.6.0] — 2026-11-18

### Dodano
- **Lokalna warstwa bezpieczeństwa:** `runtime/flowkit_exec.py` i hook `runtime/guard_bash.py` ograniczają polecenia agentów do listy dozwolonej dla roli, ukrywają sekrety i skracają wyniki.
- **Agent `agent-3x3-diagnostics`:** diagnostyka tylko do odczytu oraz szablon runbooka.
- **Agent `agent-3x3-analyst`:** analiza wymagań, procesu i wpływu zmiany, backlog, przypadki testowe i UAT na lokalnych dokumentach.
- **Testy aktywacji skilli** i `scripts/run_evals.py` z pomiarem tokenów oraz porównaniem bez wtyczki.
- Plik zasad projektu `flowkit-project.md`, tryb szybki dla prostych zmian i dwuetapowy przegląd Verifiera.

### Zmieniono
- Agenci pracują wyłącznie lokalnie: usunięto narzędzia webowe, a rozwiązanie nie używa MCP.
- Subagenci Claude Code mają przypisany model i limit kroków.
- Rzadkie procedury orkiestratora są ładowane tylko wtedy, gdy są potrzebne.

---

## [1.5.0] — 2026-11-18

### Naprawiono
- **Wtyczka Claude Code:** `plugin.json` przechodzi `claude plugin validate`, a szablon skilla nie jest ładowany jako skill.
- **Instalatory:** `install.ps1` działa w Windows PowerShell 5.1, a instalacja dla VS Code trafia do bieżącego projektu.
- **Agenci:** instalowane adaptery zawierają pełne definicje i są generowane przez `scripts/build_agents.py`; agent DevOps nie ma narzędzia do uruchamiania poleceń.
- **Skille:** silniejsza kontrola diagramów, obsługa szablonów klienta, ochrona danych w recap i postmortem.

### Dodano
- Prefiks `SHIP:` (gałąź, commit, push i PR po weryfikacji i zgodzie użytkownika) oraz kierowanie dokumentów do skilli.
- Scenariusze oceny `tests/evals/` i `scripts/grade_eval.py` do sprawdzania odpowiedzi modeli.

---

## [1.4.0] — 2026-11-18

### Dodano
- **Silnik diagramów w `client-pt-prd-writer` (2.3)**: 15 typów diagramów opartych wyłącznie na źródłach, eksport SVG/PNG/HTML, walidacja jakości oraz osadzanie w DOCX i Markdown.
- **Polskie nazwy statusów, priorytetów i wymagalności** w tabelach dokumentów PT/PRD wraz z automatyczną kontrolą.
- `tests/test_diagrams.py`: testy silnika diagramów i słownika statusów.

---

## [1.3.0] — 2026-11-17

### Dodano
- **Dwuwarstwowa architektura agentów (`agents/core/` + `agents/adapters/`)**:
  - `agents/core/`: 7 platformowo-neutralnych kontraktów architektonicznych definiujących stany, formaty wejścia/wyjścia i reguły (Orchestrator, Analyzer, Verifier, Planner, Implementer, DevOps, PM).
  - `agents/adapters/claude-code/`: natywne konfiguracje dla Claude Code z oficjalnymi narzędziami (`Read`, `Grep`, `Glob`, `Edit`, `Bash`, `Agent`).
  - `agents/adapters/vscode/`: natywne konfiguracje `.agent.md` dla VS Code Copilot Custom Agents.
  - Pełna kompatybilność wsteczna w katalogu głównym `agents/`.
- **Deterministyczny silnik obsługi dokumentów (.docx/.dotx)**: Dodano `references/docx-engine.md` z inteligentną detekcją zainstalowanych bibliotek w środowisku (`python-docx` jako priorytet 1, `mammoth`, `docx2txt`, `pypandoc`, fallback do Markdown).
- **Kompleksowa suita walidacyjna i testowa (`scripts/validate_all.py`)**:
  - `scripts/validate_agents.py`: automatyczna weryfikacja poprawności YAML, pól `name`/`description` i narzędzi.
  - `scripts/validate_manifest.py`: weryfikacja integralności manifestów wtyczek i istnienia wszystkich deklarowanych ścieżek.
  - `tests/test_flowkit.py` + fixtures (`buggy-code/`, `transcripts/`, `incident-scenarios/`): automatyczne testy jednostkowe kontraktów i integralności platformowej.
- **Bezpieczny instalator (`install.ps1`, `install.sh`)**:
  - Dodano flagi `--dry-run` / `-DryRun` do bezpiecznej symulacji operacji.
  - Dodano flagi `--force` / `-Force` z ochroną przed przypadkowym nadpisaniem plików.
  - Dodano wybór platformy docelowej: `--platform claude` oraz `--platform vscode`.
  - Wprowadzono whitelistę nazw uniemożliwiającą path traversal.
  - Dodano opcję kontrolowanej deinstalacji (`--uninstall`).
- **Macierz kompatybilności platform w README**: Precyzyjne zdefiniowanie poziomu integracji dla Claude Code, VS Code Copilot, Antigravity, Cursor oraz OpenAI ChatGPT/Codex.

### Poprawiono i zabezpieczono
- **Naprawiono błąd YAML w nagłówku orkiestratora (`agent-3x3_agent.md`)**: Wprowadzono bezpieczny blok wieloliniowy YAML scalar (`description: >-`), eliminujący błąd parsowania `mapping values are not allowed in this context`.
- **Neutralizacja zdarzeń procesowych orkiestratora**: Zastąpiono sztywne powiązanie z `vscode_askQuestions` neutralnymi zdarzeniami lifecycle: `REPORT_PROGRESS`, `ASK_USER`, `WAIT_FOR_APPROVAL`, `CONTINUE`, `STOP`.
- **Wymuszenie reguł bezpieczeństwa i eliminacja fałszywych PASS-ów**:
  - W Verifierze wprowadzono status `[NOT VERIFIED]` z zakazem raportowania sukcesu testów bez rzeczywistego uruchomienia suite testowego.
  - W Analyzerze dodano techniczne ograniczenia i raportowanie `Not checked:`.
  - W Implementerze dodano ścisłą whitelistę weryfikacji i ochronę przed scope creep.
- **Zabezpieczenie autora w repozytorium publicznym**: Rozszerzono `.gitignore` (m.in. `agent-context/`, `AGENT_LOG.md`, dane klientów, transkrypcje, klucze) oraz dodano dedykowaną sekcję bezpieczeństwa w `README.md`.

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

