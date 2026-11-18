# FlowKit — Agent Skills & Agents Library

> Uniwersalna biblioteka umiejętności (**Agent Skills**) i agentów (**Agents**) dla **Claude Code**, **GitHub Copilot**, **OpenAI Codex / ChatGPT**, **Cursor** oraz **Antigravity**. Zoptymalizowana pod kątem automatyzacji zadań **Analityka Biznesowo-Systemowego** oraz **Inżyniera DevOps**.

Repozytorium spełnia standard otwartych skilli AI oraz posiada manifest [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) kompatybilny z katalogami **Agent Marketplace**.

---

## 📚 Katalog skilli (Skills Catalog)

### 📊 Analiza biznesowa i systemowa

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **client-pt-prd-writer** | `2.4` | Tworzy precyzyjną dokumentację techniczną (PT) i PRD wyłącznie na bazie materiałów źródłowych. Zawiera scenariusze akceptacyjne **Given-When-Then (Gherkin)**, **Definition of Done (DoD)**, wyłączenia **Non-Goals** oraz obsługę szablonów klienta (`.docx`, `.md`). Opcjonalny tryb **dokumentu końcowego bez dopisków** — czysty dokument w szablonie klienta. **Diagramy oparte na źródłach** (architektura, procesy, sekwencje, model danych) osadzane w DOCX i Markdown oraz polskie nazwy statusów w tabelach. | [`skills/client-pt-prd-writer/`](skills/client-pt-prd-writer/) |
| **client-meeting-recap** | `1.3` | Przekształca surowe transkrypcje (`.vtt`, `.docx`, `.txt`) w 2-częściowe podsumowanie: **Część A (Wewnętrzny Radar Ryzyk / Scope Creep dla zespołu, z cytatami jako dowodami)** oraz **Część B (Oficjalny mail do klienta z zadaniami DRI i klauzulą weryfikacji 48h)** — w osobnych plikach. | [`skills/client-meeting-recap/`](skills/client-meeting-recap/) |

### ⚙️ DevOps i Infrastruktura

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **devops-incident-postmortem** | `1.4` | Generuje bezobwiniający raport postmortem zgodny ze standardami **Google SRE i PagerDuty**. Zawiera klasyfikację SEV-1/SEV-2, role (Incident Commander), wieloczynnikowy łańcuch przyczyn (**Trigger, Amplifier, Detection/Process Gap**, 5 Whys), rejestr Status Page oraz zadania PREVENT/DETECT/MITIGATE. | [`skills/devops-incident-postmortem/`](skills/devops-incident-postmortem/) |

### 🛠️ Szablony narzędziowe

| Narzędzie | Opis | Ścieżka |
|---|---|---|
| **_template** | Czysty wzorzec do szybkiego tworzenia nowego skilla z wymaganym nagłówkiem YAML. | [`skills/_template/`](skills/_template/) |

---

## 🤖 Architektura i katalog agentów (Agents Catalog)

FlowKit realizuje dwuwarstwową architekturę agentów oddzielającą logikę domenową od specyfiki danego hosta:
- **`agents/core/`** — platformowo neutralne kontrakty, reguły, formaty wyjściowe i stany procesowe (`DISCOVER`, `PLAN`, `EXECUTE`, `VERIFY`, `REPORT_PROGRESS`, `ASK_USER`, `WAIT_FOR_APPROVAL`).
- **`agents/*_agent.md`** — pełne definicje zachowania, jedyne miejsce ich edycji.
- **`agents/adapters/claude-code/`** i **`agents/adapters/vscode/`** — pliki instalowane u użytkownika, generowane poleceniem `python scripts/build_agents.py`. Walidator odrzuca adaptery niezgodne ze źródłem.

### Orkiestrator

| Agent | Plik | Opis |
|---|---|---|
| **agent-3x3** | [`agent-3x3_agent.md`](agents/agent-3x3_agent.md) | Główny orkiestrator. Iteracyjny development: max 3 kroki na iterację, wymuszone podsumowanie (`REPORT_PROGRESS`) i potwierdzenie użytkownika (`ASK_USER`). Obsługuje prefiksy `ANALYZE:` `VERIFY:` `PLAN:` `SPEC:` `DRY:` `LOG:` `DEVOPS:`. Koordynuje subagenty. |

### Subagenty (wywoływane przez orkiestratora)

| Agent | Plik | Tryb | Opis |
|---|---|---|---|
| **agent-3x3-analyzer** | [`agent-3x3-analyzer_agent.md`](agents/agent-3x3-analyzer_agent.md) | read-only | Analiza kodu, zależności, struktury. Zwraca findings `[CRITICAL]/[WARNING]/[INFO]`, listę `Scanned:` i `Not checked:` oraz odróżnia fakty od hipotez. |
| **agent-3x3-verifier** | [`agent-3x3-verifier_agent.md`](agents/agent-3x3-verifier_agent.md) | read-only | Weryfikacja implementacji per 9 wymiarów (`Logic`, `Contracts`, `Tests`, `Dependencies`, `Security`, `Performance`, `Consistency`, `Docs`, `Requirements`). Raportuje `[PASS]`, `[WARN]`, `[FAIL]` oraz `[NOT VERIFIED]` (zakaz fałszywych passów bez testów). |
| **agent-3x3-planner** | [`agent-3x3-planner_agent.md`](agents/agent-3x3-planner_agent.md) | read-only | Plan iteracji 3x3 z etykietami ryzyka i estymacją Effort per krok i per iterację. |
| **agent-3x3-implementer** | [`agent-3x3-implementer_agent.md`](agents/agent-3x3-implementer_agent.md) | read+write | Realizuje jeden atomowy krok. Self-check diffa przed zwrotem statusu. Zwraca DONE/PARTIAL/BLOCKED. Ścisła whitelist operacji. |
| **agent-3x3-devops** | [`agent-3x3-devops_agent.md`](agents/agent-3x3-devops_agent.md) | read+write | CI/CD, Docker, Kubernetes, Terraform, Azure/AWS/GCP, sekrety, monitoring. Obsługuje tryb standalone (bez Orkiestratora). |
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
| `SHIP:` | po weryfikacji i Twojej zgodzie przygotowuje gałąź, commit, push i PR |

Prefiksy można łączyć od lewej do prawej: `PLAN: LOG: zadanie`, `SPEC: PLAN: zadanie`.

---

## 🌐 Macierz kompatybilności platform

| Platforma | Skille | Agenty | Instalator | Poziom integracji |
|---|---|---|---|---|
| **Claude Code** | Natywne (`~/.claude/skills/`) | Dedykowane (`agents/adapters/claude-code/`) | `install.ps1` / `install.sh -Platform claude` | **Natywne / Pełne** (zweryfikowane CI) |
| **VS Code Copilot** | Natywne (`.prompt.md`) | Dedykowane `.agent.md` (`agents/adapters/vscode/`) | `install.ps1` / `install.sh -Platform vscode` | **Natywne / Pełne** (zweryfikowane CI) |
| **Antigravity** | Otwarty standard Agent Skills | Bundle wtyczki (`.claude-plugin/plugin.json`) | Marketplace / repo bundle | **Natywne / Pełne** (v1.3.0) |
| **Cursor** | `.cursor/rules/<skill>.mdc` | Reguły workspace | Ręczny / skopiowanie reguł | **Instrukcja konfiguracji** |
| **OpenAI Codex / ChatGPT** | Instructions + Knowledge files | Custom GPT System Prompt | Ręczny eksport | **Instrukcja konfiguracji** |

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

#### Opcja A: Automatyczny instalator (PowerShell / Bash)

```powershell
# Windows — instalacja agentów dla Claude Code (domyślnie ~/.claude/agents)
.\scripts\install.ps1 -AgentName all -Platform claude

# Windows — agenci VS Code Copilot trafiają do .github/agents bieżącego katalogu, więc uruchom z katalogu projektu
& C:\sciezka\do\flowkit\scripts\install.ps1 -AgentName all -Platform vscode

# Bezpieczna symulacja instalacji (dry-run)
.\scripts\install.ps1 -AgentName all -DryRun

# Wymuszenie nadpisania istniejących konfiguracji
.\scripts\install.ps1 -AgentName all -Force
```

```bash
# Linux / macOS — instalacja dla Claude Code
./scripts/install.sh agent all --platform claude

# Linux / macOS — agenci VS Code Copilot trafiają do .github/agents bieżącego katalogu projektu
/sciezka/do/flowkit/scripts/install.sh agent all --platform vscode

# Tryb symulacji (dry-run)
./scripts/install.sh agent all --dry-run
```

Orkiestrator uruchamiaj jako główny wątek sesji:

```bash
claude --agent agent-3x3
```

#### Opcja B: Ręczna instalacja agentów

- Dla **Claude Code**: skopiuj pliki z [`agents/adapters/claude-code/`](agents/adapters/claude-code/) do `~/.claude/agents/` (globalnie) lub `.claude/agents/` (w projekcie).
- Dla **VS Code Copilot**: skopiuj pliki z [`agents/adapters/vscode/`](agents/adapters/vscode/) do `.github/agents/`.
- Pliki w [`agents/core/`](agents/core/) zawierają nadrzędne kontrakty zachowań i formatów wyjściowych niezależne od platformy.

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

## 📄 Standard silnika dokumentacji (.docx / Markdown)

Zarówno skille analityczne (`client-pt-prd-writer`, `client-meeting-recap`), jak i agenci (`agent-3x3`, `agent-3x3-implementer`) stosują **inteligentny, deterministyczny standard obsługi dokumentów**:

1. **Priorytet 1: `python-docx` (`import docx`)** — podstawowa, wiodąca biblioteka do odczytu szablonów i generowania plików Word (`.docx`). Zapewnia pełne zachowanie stylów klienta, nagłówków, stopek i tabel.
2. **Inteligentna detekcja środowiska**: Przed generowaniem agent/skill sprawdza, jakie biblioteki są rzeczywiście zainstalowane w bieżącym środowisku (`python-docx`, `mammoth`, `docx2txt`, `pypandoc`).
3. **Korzystanie z bibliotek zainstalowanych**: Nigdy nie są doinstalowywane losowe biblioteki w tle — narzędzia korzystają z tego, czym dysponuje system użytkownika.
4. **Spójność w sesji**: Wybrany silnik obowiązuje przez całą sesję (brak przełączania bibliotek między turami).
5. **Czysty fallback**: W razie braku bibliotek `.docx` generowany jest w 100% ustrukturyzowany plik Markdown (`.md`) z czytelną informacją o możliwości zainstalowania `python-docx` (`pip install python-docx`).

Szczegółowy przewodnik silnika znajduje się w [`skills/client-pt-prd-writer/references/docx-engine.md`](skills/client-pt-prd-writer/references/docx-engine.md).

---

## ➕ Jak dodać nowy skill do repozytorium?

1. Skopiuj folder [`skills/_template/`](skills/_template/) do nowego katalogu `skills/<nowa-nazwa>/`.
2. Zmień nazwę `SKILL.template.md` na `SKILL.md` i wypełnij plik (nagłówek YAML musi zawierać pola `name`, `version`, `tags` i `description`).
3. Dodaj wymagane `CHANGELOG.md`, `templates/` i `checklists/` (co najmniej jeden plik `.md` w każdym) oraz opcjonalne `examples/` i `references/`.
4. Dopisz nowy skill do tabeli w sekcji [Katalog skilli](#-katalog-skilli-skills-catalog) w niniejszym pliku.
5. Zgłoś zmianę przez Pull Request (lokalnie uruchom `python scripts/validate_skills.py`; ten sam walidator działa w CI).

---

## 🔒 Bezpieczeństwo i ochrona autora

> [!IMPORTANT]
> To repozytorium jest **publiczne**. Poniższe zasady chronią autora oraz użytkowników przed przypadkowym ujawnieniem danych wrażliwych.

### Co nigdy nie trafia do repozytorium

Plik [`.gitignore`](.gitignore) wyklucza następujące kategorie — **nie commituj ich nigdy**:

| Kategoria | Przykłady | Ryzyko |
|---|---|---|
| Sekrety i klucze | `.env`, `*.key`, `*.pem`, `*.token`, `credentials.*` | Wycieki kluczy API, cloud access |
| Dane klientów | `*.vtt`, `input/`, `source-materials/`, `client-data/` | GDPR, NDA, poufność |
| Sesje agenta | `agent-context/`, `AGENT_LOG.md` | Dane robocze z projektów klientów |
| Klucze chmurowe | `.aws/`, `.azure/`, `.gcloud/`, `service-account*.json` | Nieautoryzowany dostęp do infrastruktury |

### Bezpieczne użytkowanie skilli i agentów

```
❌ Nie wklejaj:  transkrypcji spotkań klientów, danych osobowych, nazw klientów,
                 kluczy API, haseł, production hostnames

✅ Zamiast tego: używaj zanonimizowanych przykładów lub pliku lokalnego
                 (agent odczyta z dysku, plik nie wejdzie do kontekstu publicznego)
```

### Pliki agentów a bezpieczeństwo

- Pliki `*_agent.md` zawierają **wyłącznie instrukcje behawioralne** — żadnych danych, kluczy ani historii sesji.
- `AGENT_CONTEXT_*.md` generowane podczas sesji **nie są commitowane** (`.gitignore`). Służą jako prywatna pamięć robocza.
- Agent DevOps (`agent-3x3-devops`) ma jawną regułę: **nigdy nie hardkoduje sekretów** — zawsze używa referencji zmiennych (`${{ secrets.X }}`, vault paths).

### Zasady dla kontrybutorów

- **Brak bezpośredniego push do `main`**: wszystkie zmiany przez Pull Request na gałęziach `feat/*`, `fix/*`, `docs/*`.
- **Brak danych klientów w przykładach**: pliki w `examples/` muszą używać fikcyjnych, zanonimizowanych danych.
- **Walidacja CI przed merge**: `python scripts/validate_skills.py` musi przejść na zielono.
- **Brak sekretów w commitach**: skonfiguruj lokalne `pre-commit` lub użyj [git-secrets](https://github.com/awslabs/git-secrets).

### Zalecana konfiguracja pre-commit (opcjonalne, lokalne)

```bash
# Instalacja git-secrets (macOS)
brew install git-secrets
git secrets --install
git secrets --register-aws

# Instalacja detect-secrets (Python)
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

```powershell
# Windows — skanowanie przed commitem (PowerShell)
git diff --cached --name-only | ForEach-Object { Select-String -Path $_ -Pattern "password|secret|token|key" -CaseSensitive:$false }
```

### Ochrona gałęzi `main`

Bezpośredni push do `main` jest zablokowany regułą GitHub Ruleset ([`protect-main.json`](.github/rulesets/protect-main.json) — wymaga zaimportowania w *Settings → Rules → Rulesets*), która wymaga też zielonego wyniku CI (`validate`). Wszystkie zmiany (zarówno społeczności, jak i właściciela) trafiają do `main` wyłącznie przez Pull Request.

---

## 📋 Zasady inżynierskie i licencja

- **Zasady inżynierskie**: Wszystkie standardy pracy, konwencje commitów oraz strategię gałęzi opisuje dokument [**`DEVELOPMENT.md`**](DEVELOPMENT.md).
- **Licencja**: Kod udostępniany jest na otwartej licencji [MIT](LICENSE).  
  Skille i agenty są narzędziami generującymi treści — **odpowiedzialność za weryfikację wygenerowanych dokumentów spoczywa na użytkowniku**.
- **Brak gwarancji**: Repozytorium jest udostępniane "as is". Autor nie ponosi odpowiedzialności za decyzje podjęte na podstawie output agentów bez weryfikacji przez człowieka.
