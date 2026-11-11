# FlowKit — Agent Skills Library

> Uniwersalna biblioteka umiejętności (**Agent Skills**) dla **Claude Code**, **GitHub Copilot**, **OpenAI Codex / ChatGPT**, **Cursor** oraz **Antigravity**. Zoptymalizowana pod kątem automatyzacji zadań **Analityka Biznesowo-Systemowego** oraz **Inżyniera DevOps**.

Repozytorium spełnia standard otwartych skilli AI oraz posiada manifest [`plugin.json`](plugin.json) kompatybilny z katalogami **Agent Marketplace**.

---

## 📚 Katalog skilli (Skills Catalog)

### 📊 Analiza biznesowa i systemowa

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **client-pt-prd-writer** | `2.1` | Tworzy precyzyjną dokumentację techniczną (PT) i PRD wyłącznie na bazie materiałów źródłowych. Zawiera scenariusze akceptacyjne **Given-When-Then (Gherkin)**, **Definition of Done (DoD)**, wyłączenia **Non-Goals** oraz obsługę szablonów klienta (`.docx`, `.md`). | [`skills/client-pt-prd-writer/`](skills/client-pt-prd-writer/) |
| **client-meeting-recap** | `1.1` | Przekształca surowe transkrypcje (`.vtt`, `.docx`, `.txt`) w 2-częściowe podsumowanie: **Część A (Wewnętrzny Radar Ryzyk / Scope Creep dla zespołu)** oraz **Część B (Oficjalny mail do klienta z zadaniami DRI i klauzulą weryfikacji 48h)**. | [`skills/client-meeting-recap/`](skills/client-meeting-recap/) |

### ⚙️ DevOps i Infrastruktura

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **devops-incident-postmortem** | `1.2` | Generuje bezobwiniający raport postmortem zgodny ze standardami **Google SRE i PagerDuty**. Zawiera klasyfikację SEV-1/SEV-2, role (Incident Commander), wieloczynnikowy łańcuch przyczyn (**Trigger, Amplifier, Detection/Process Gap**, 5 Whys), rejestr Status Page oraz zadania PREVENT/DETECT/MITIGATE. | [`skills/devops-incident-postmortem/`](skills/devops-incident-postmortem/) |

### 🛠️ Szablony narzędziowe

| Narzędzie | Opis | Ścieżka |
|---|---|---|
| **_template** | Czysty wzorzec do szybkiego tworzenia nowego skilla z wymaganym nagłówkiem YAML. | [`skills/_template/`](skills/_template/) |

---

## 🚀 Uniwersalna instalacja skilli

Wszystkie skille z repozytorium instaluje się w identyczny, ustandaryzowany sposób. Zamień `<skill-name>` na nazwę wybranego skilla (np. `client-pt-prd-writer`).

### 1. Claude Code

#### Opcja A: Automatyczny instalator (rekomendowane)
Repozytorium zawiera gotowe skrypty instalacyjne dla Windows i Linux/macOS:

```powershell
# Windows (PowerShell) - instalacja w ~/.claude/skills/<skill-name>
.\scripts\install.ps1 -SkillName <skill-name>

# Opcjonalnie: instalacja w lokalnym projekcie
.\scripts\install.ps1 -SkillName <skill-name> -TargetPath ./.claude/skills
```

```bash
# Linux / macOS (Bash)
./scripts/install.sh <skill-name>
```

#### Opcja B: Ręczna instalacja
- **Globalnie dla Twojego konta**: skopiuj folder wybranego skilla do `~/.claude/skills/<skill-name>`.
- **W bieżącym projekcie**: skopiuj folder do `.claude/skills/<skill-name>`.
- **W Claude.ai (Web Projects)**: załącz plik `SKILL.md` oraz szablony z katalogu `templates/` w sekcji **Project Knowledge**.

---

### 2. GitHub Copilot

Skille mogą być wykorzystywane przez Copilota w VS Code, Visual Studio oraz JetBrains:

1. **Prompt Files (`.prompt.md`)**: W katalogu `.github/prompts/` znajdują się gotowe wywołania Copilot Chat (np. `/client-pt-prd-writer`).
2. **Plik referencyjny w sesji czatu**: W Copilot Chat wpisz `#file:skills/<skill-name>/SKILL.md` i zadaj pytanie.
3. **Reguły całego projektu**: Wklej zasady danego skilla do pliku [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
4. **Globalne instrukcje użytkownika**: Dodaj treść do ustawień VS Code: `github.copilot.chat.codeGeneration.instructions`.

---

### 3. OpenAI Codex / ChatGPT / Cursor

- **Cursor**: Utwórz plik `.cursor/rules/<skill-name>.mdc` w swoim projekcie i wklej zawartość `skills/<skill-name>/SKILL.md`.
- **Custom GPTs / OpenAI Assistant**: Wklej treść sekcji *Zasady nadrzędne* do pola **Instructions**, a szablony i checklisty załącz jako pliki w sekcji **Knowledge**.

---

### 4. Agent Marketplace & Antigravity

Dzięki obecności manifestu [`plugin.json`](plugin.json) w głównym katalogu, repozytorium jest traktowane jako gotowy pakiet (bundle). Może być dodane jako wtyczka i automatycznie udostępniać wszystkie zainstalowane skille asystentowi.

---

## ➕ Jak dodać nowy skill do repozytorium?

1. Skopiuj folder [`skills/_template/`](skills/_template/) do nowego katalogu `skills/<nowa-nazwa>/`.
2. Wypełnij plik `SKILL.md` (upewnij się, że nagłówek YAML zawiera pola `name` i `description`).
3. Dodaj opcjonalne podkatalogi: `templates/`, `checklists/`, `examples/` lub `references/`.
4. Dopisz nowy skill do tabeli w sekcji [Katalog skilli](#-katalog-skilli-skills-catalog) w niniejszym pliku.
5. Zgłoś zmianę przez Pull Request (automatyczny pipeline CI zweryfikuje składnię nagłówków).

---

## 🔒 Bezpieczeństwo, zasady i licencja

- **Dostęp**: Repozytorium jest publiczne do przeglądania i pobierania.
- **Zasady inżynierskie**: Wszystkie standardy pracy, konwencje commitów oraz strategię gałęzi opisuje dokument [**`DEVELOPMENT.md`**](DEVELOPMENT.md).
- **Ochrona gałęzi `main`**: Bezpośredni push do `main` jest zablokowany regułą GitHub Ruleset (`protect-main.json`). Wszystkie zmiany (zarówno społeczności, jak i właściciela) trafiają do `main` wyłącznie przez Pull Request na gałęziach `feat/*`, `fix/*`.
- **Ochrona danych**: Plik [`.gitignore`](.gitignore) wyklucza dane wrażliwe, sekrety, pliki `.env` oraz tymczasowe pliki edytorów.
- **Licencja**: Kod udostępniany jest na bezpiecznej, otwartej licencji [MIT](LICENSE).
