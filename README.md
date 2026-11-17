# FlowKit — Agent Skills & Agents Library

> Uniwersalna biblioteka umiejętności (**Agent Skills**) i agentów (**Agents**) dla **Claude Code**, **GitHub Copilot**, **OpenAI Codex / ChatGPT**, **Cursor** oraz **Antigravity**. Zoptymalizowana pod kątem automatyzacji zadań **Analityka Biznesowo-Systemowego** oraz **Inżyniera DevOps**.

Repozytorium spełnia standard otwartych skilli AI oraz posiada manifest [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) kompatybilny z katalogami **Agent Marketplace**.

---

## 📚 Katalog skilli (Skills Catalog)

### 📊 Analiza biznesowa i systemowa

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **client-pt-prd-writer** | `2.2` | Tworzy precyzyjną dokumentację techniczną (PT) i PRD wyłącznie na bazie materiałów źródłowych. Zawiera scenariusze akceptacyjne **Given-When-Then (Gherkin)**, **Definition of Done (DoD)**, wyłączenia **Non-Goals** oraz obsługę szablonów klienta (`.docx`, `.md`). Opcjonalny tryb **dokumentu końcowego bez dopisków** — czysty dokument w szablonie klienta. | [`skills/client-pt-prd-writer/`](skills/client-pt-prd-writer/) |
| **client-meeting-recap** | `1.2` | Przekształca surowe transkrypcje (`.vtt`, `.docx`, `.txt`) w 2-częściowe podsumowanie: **Część A (Wewnętrzny Radar Ryzyk / Scope Creep dla zespołu, z cytatami jako dowodami)** oraz **Część B (Oficjalny mail do klienta z zadaniami DRI i klauzulą weryfikacji 48h)** — w osobnych plikach. | [`skills/client-meeting-recap/`](skills/client-meeting-recap/) |

### ⚙️ DevOps i Infrastruktura

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **devops-incident-postmortem** | `1.3` | Generuje bezobwiniający raport postmortem zgodny ze standardami **Google SRE i PagerDuty**. Zawiera klasyfikację SEV-1/SEV-2, role (Incident Commander), wieloczynnikowy łańcuch przyczyn (**Trigger, Amplifier, Detection/Process Gap**, 5 Whys), rejestr Status Page oraz zadania PREVENT/DETECT/MITIGATE. | [`skills/devops-incident-postmortem/`](skills/devops-incident-postmortem/) |

### 🛠️ Szablony narzędziowe

| Narzędzie | Opis | Ścieżka |
|---|---|---|
| **_template** | Czysty wzorzec do szybkiego tworzenia nowego skilla z wymaganym nagłówkiem YAML. | [`skills/_template/`](skills/_template/) |

---

## 🤖 Katalog agentów (Agents Catalog)

Agenty to samodzielne jednostki AI orkiestrowane przez Claude Code. Wszystkie pliki agentów znajdują się w katalogu [`agents/`](agents/).

### Orkiestrator

| Agent | Plik | Opis |
|---|---|---|
| **agent-3x3** | [`agent-3x3_agent.md`](agents/agent-3x3_agent.md) | Główny orkiestrator. Iteracyjny development: max 3 kroki na iterację, wymuszone podsumowanie i potwierdzenie użytkownika. Obsługuje prefiksy `ANALYZE:` `VERIFY:` `PLAN:` `SPEC:` `DRY:` `LOG:` `DEVOPS:`. Koordynuje wszystkie subagenty poniżej. |

### Subagenty (wywoływane przez orkiestratora)

| Agent | Plik | Tryb | Opis |
|---|---|---|---|
| **agent-3x3-analyzer** | [`agent-3x3-analyzer_agent.md`](agents/agent-3x3-analyzer_agent.md) | read-only | Analiza kodu, zależności, struktury. Zwraca findings z poziomem pewności. |
| **agent-3x3-verifier** | [`agent-3x3-verifier_agent.md`](agents/agent-3x3-verifier_agent.md) | read-only | Weryfikacja implementacji (PASS/WARN/FAIL per wymiar). Wspiera pętlę korekcji. |
| **agent-3x3-planner** | [`agent-3x3-planner_agent.md`](agents/agent-3x3-planner_agent.md) | read-only | Plan iteracji 3x3 z etykietami ryzyka i estymacją. |
| **agent-3x3-implementer** | [`agent-3x3-implementer_agent.md`](agents/agent-3x3-implementer_agent.md) | read+write | Realizuje jeden atomowy krok. Zwraca DONE/PARTIAL/BLOCKED + diff summary. |
| **agent-3x3-devops** | [`agent-3x3-devops_agent.md`](agents/agent-3x3-devops_agent.md) | read+write | CI/CD, Docker, Kubernetes, Terraform, Azure/AWS/GCP, sekrety, monitoring. |
| **agent-3x3-pm** | [`agent-3x3-pm_agent.md`](agents/agent-3x3-pm_agent.md) | read-only | User stories (US-N), acceptance criteria (AC-N), ADR, decyzje produktowe. |

### Prefiksy orkiestratora

| Prefiks | Akcja |
|---|---|
| `ANALYZE:` | wywołuje Analyzer jako pierwszy krok |
| `VERIFY:` | wywołuje Verifier jako pierwszy krok |
| `PLAN:` | wywołuje Planner jako pierwszy krok |
| `SPEC:` | wywołuje PM agenta (user stories + acceptance criteria) |
| `DRY:` | planuje ≤3 kroków i czeka na potwierdzenie |
| `LOG:` | dołącza każdą iterację do `AGENT_LOG.md` |
| `DEVOPS:` | wywołuje agenta DevOps |

Prefiksy można łączyć od lewej do prawej: `PLAN: LOG: zadanie`, `SPEC: PLAN: zadanie`.

---

## 🚀 Instalacja

### Claude Code — skille

#### Opcja A: Automatyczny instalator (rekomendowane)

```powershell
# Windows (PowerShell) — instalacja skilla globalnie
.\scripts\install.ps1 -SkillName client-pt-prd-writer

# Opcjonalnie: instalacja w lokalnym projekcie
.\scripts\install.ps1 -SkillName client-pt-prd-writer -TargetPath ./.claude/skills
```

```bash
# Linux / macOS
./scripts/install.sh skill client-pt-prd-writer
```

#### Opcja B: Ręczna instalacja skilli

- **Globalnie**: skopiuj folder wybranego skilla do `~/.claude/skills/<skill-name>`.
- **W projekcie**: skopiuj folder do `.claude/skills/<skill-name>`.
- **W Claude.ai (Web Projects)**: załącz plik `SKILL.md` oraz szablony z `templates/` w sekcji **Project Knowledge**.

---

### Claude Code — agenty

Agenty instaluje się do `~/.claude/agents/` (globalni) lub `.claude/agents/` (lokalni w projekcie).

#### Opcja A: Automatyczny instalator

```powershell
# Windows — zainstaluj wszystkich agentów globalnie
.\scripts\install.ps1 -AgentName all

# Tylko orkiestrator
.\scripts\install.ps1 -AgentName agent-3x3

# Skill + agent jednocześnie
.\scripts\install.ps1 -SkillName devops-incident-postmortem -AgentName agent-3x3-devops

# Lokalnie w projekcie
.\scripts\install.ps1 -AgentName all -AgentTargetPath ./.claude/agents
```

```bash
# Linux / macOS — wszystkich agentów globalnie
./scripts/install.sh agent all

# Tylko orkiestrator
./scripts/install.sh agent agent-3x3

# Lokalnie w projekcie
./scripts/install.sh agent all ~/.claude/agents
```

#### Opcja B: Ręczna instalacja agentów

Skopiuj pliki `*_agent.md` z katalogu [`agents/`](agents/) do:
- `~/.claude/agents/` — instalacja globalna (agent dostępny we wszystkich projektach)
- `.claude/agents/` w katalogu projektu — instalacja lokalna

Po instalacji globalnej Claude Code automatycznie wykryje agentów. **Domyślnym agentem startowym** w VS Code jest `agent-3x3` (orkiestrator).

---

### GitHub Copilot

Skille mogą być wykorzystywane przez Copilota w VS Code, Visual Studio oraz JetBrains:

1. **Prompt Files (`.prompt.md`)**: W katalogu `.github/prompts/` znajdują się gotowe wywołania Copilot Chat dla każdego skilla (np. `/client-pt-prd-writer`).
2. **Plik referencyjny w sesji czatu**: W Copilot Chat wpisz `#file:skills/<skill-name>/SKILL.md` i zadaj pytanie.
3. **Reguły całego projektu**: Wklej zasady danego skilla do pliku [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
4. **Globalne instrukcje użytkownika**: Dodaj treść do ustawień VS Code: `github.copilot.chat.codeGeneration.instructions`.

---

### OpenAI Codex / ChatGPT / Cursor

- **Cursor**: Utwórz plik `.cursor/rules/<skill-name>.mdc` w swoim projekcie i wklej zawartość `skills/<skill-name>/SKILL.md`.
- **Custom GPTs / OpenAI Assistant**: Wklej treść sekcji *Zasady nadrzędne* do pola **Instructions**, a szablony i checklisty załącz jako pliki w sekcji **Knowledge**.

---

### Agent Marketplace & Antigravity

Dzięki manifestom [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) i [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) repozytorium jest gotowym pakietem (bundle) udostępniającym wszystkie skille i agentów. W Claude Code:

```bash
claude plugin marketplace add marant6891/flowkit
```

```bash
claude plugin install flowkit@flowkit
```

---

## ➕ Jak dodać nowy skill do repozytorium?

1. Skopiuj folder [`skills/_template/`](skills/_template/) do nowego katalogu `skills/<nowa-nazwa>/`.
2. Wypełnij plik `SKILL.md` (upewnij się, że nagłówek YAML zawiera pola `name`, `version`, `tags` i `description`).
3. Dodaj wymagane `CHANGELOG.md`, `templates/` i `checklists/` (co najmniej jeden plik `.md` w każdym) oraz opcjonalne `examples/` i `references/`.
4. Dopisz nowy skill do tabeli w sekcji [Katalog skilli](#-katalog-skilli-skills-catalog) w niniejszym pliku.
5. Zgłoś zmianę przez Pull Request (lokalnie uruchom `python scripts/validate_skills.py`; ten sam walidator działa w CI).

---

## 🔒 Bezpieczeństwo, zasady i licencja

- **Dostęp**: Repozytorium jest publiczne do przeglądania i pobierania.
- **Zasady inżynierskie**: Wszystkie standardy pracy, konwencje commitów oraz strategię gałęzi opisuje dokument [**`DEVELOPMENT.md`**](DEVELOPMENT.md).
- **Ochrona gałęzi `main`**: Bezpośredni push do `main` jest zablokowany regułą GitHub Ruleset ([`protect-main.json`](.github/rulesets/protect-main.json) — wymaga zaimportowania w *Settings → Rules → Rulesets*), która wymaga też zielonego wyniku CI (`validate`). Wszystkie zmiany (zarówno społeczności, jak i właściciela) trafiają do `main` wyłącznie przez Pull Request na gałęziach `feat/*`, `fix/*`.
- **Ochrona danych**: Plik [`.gitignore`](.gitignore) wyklucza dane wrażliwe, sekrety, pliki `.env` oraz tymczasowe pliki edytorów.
- **Licencja**: Kod udostępniany jest na bezpiecznej, otwartej licencji [MIT](LICENSE).
