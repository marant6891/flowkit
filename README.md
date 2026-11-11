# FlowKit - AI Skills for Analysts & DevOps

Kolekcja sprawdzonych umiejętności (**Agent Skills**) dla narzędzi AI takich jak **Claude Code**, **GitHub Copilot**, **OpenAI Codex / ChatGPT**, **Cursor** oraz **Antigravity**. Repozytorium koncentruje się na automatyzacji pracy **Analityka Biznesowo-Systemowego** oraz **Inżyniera DevOps**.

Struktura repozytorium jest zgodna ze standardami **Agent Skills** oraz **Agent Marketplace** (`plugin.json`), co umożliwia instalację zarówno w środowiskach lokalnych, jak i jako wtyczkę platformową.

---

## 📦 Dostępne skille

| Skill | Opis | Ścieżka |
|---|---|---|
| **client-pt-prd-writer** | Tworzy precyzyjną dokumentację PT/PRD (specyfikacje zmian, analizy przedwdrożeniowe) wyłącznie w oparciu o materiały źródłowe bez halucynacji i zmyślania. Obsługuje szablony klienta (.docx, .md). | [`skills/client-pt-prd-writer`](skills/client-pt-prd-writer/) |
| **_template** | Wzorzec do szybkiego tworzenia nowych skilli analitycznych i DevOps z nagłówkami YAML. | [`skills/_template`](skills/_template/) |

---

## 🚀 Jak zainstalować i używać

### 1. Claude Code & Claude.ai

#### Opcja A: Szybki skrypt instalacyjny (PowerShell / Bash)
Skrypt automatycznie kopiuje wybrany skill do globalnego katalogu Claude Code (`~/.claude/skills`):
```bash
# Windows (PowerShell)
.\scripts\install.ps1 -SkillName client-pt-prd-writer

# Linux / macOS (Bash)
./scripts/install.sh client-pt-prd-writer
```

Możesz także zainstalować skill lokalnie w bieżącym projekcie:
```powershell
.\scripts\install.ps1 -SkillName client-pt-prd-writer -TargetPath ./.claude/skills
```

#### Opcja B: Ręczna instalacja
- **Globalnie**: Skopiuj folder `skills/client-pt-prd-writer` do katalogu `~/.claude/skills/`.
- **W projekcie**: Skopiuj folder do `.claude/skills/` w głównym katalogu Twojego repozytorium.
- **W Claude.ai (Web Projects)**: Dodaj plik `SKILL.md` oraz szablony z folderu `templates/` do sekcji **Project Knowledge**. W instrukcjach projektu wklej treść nagłówka skilla.

---

### 2. GitHub Copilot

GitHub Copilot obsługuje skille na trzy sposoby:

#### Sposób A: Copilot Prompt Files (VS Code Copilot Chat)
W repozytorium znajduje się gotowy plik promptu w katalogu `.github/prompts/client-pt-prd-writer.prompt.md`.
- W Copilot Chat w VS Code wpisz `/client-pt-prd-writer` lub załącz plik skilla przez `#file:skills/client-pt-prd-writer/SKILL.md`.

#### Sposób B: Reguły repozytorium (.github/copilot-instructions.md)
Plik `.github/copilot-instructions.md` w głównym katalogu repozytorium automatycznie instruuje Copilota, w jaki sposób interpretować skille i formaty dokumentów. Możesz skopiować ten plik lub dodać jego zawartość do swojego projektu.

#### Sposób C: Custom Instructions użytkownika (Globalnie)
W Visual Studio Code otwórz `Settings` → wyszukaj `github.copilot.chat.codeGeneration.instructions` i wklej zawartość lub odnośnik do zasad z `SKILL.md`.

---

### 3. OpenAI Codex / ChatGPT / Cursor

- **Cursor**: 
  - Utwórz plik `.cursor/rules/client-pt-prd-writer.mdc` w swoim projekcie i wklej treść z pliku `SKILL.md`.
  - Alternatywnie skopiuj reguły do pliku `.cursorrules`.
- **OpenAI Codex / ChatGPT / Custom GPTs**:
  - W konfiguracji asystenta (Custom GPT) wklej treść sekcji *Zasady nadrzędne* oraz *Etapy* z `SKILL.md` w polu **Instructions**.
  - W sekcji **Knowledge** załącz pliki checklist i szablonów (`.md`).

---

### 4. Marketplace & Antigravity Plugins

Repozytorium posiada natywny manifest [`plugin.json`](plugin.json). Pozwala to na:
- Instalację jako bundle/plugin w systemie Antigravity oraz zgodnych katalogach **Agent Marketplace**.
- Jednoczesne załadowanie wszystkich zdefiniowanych skilli w sesji agenta AI.
- Wyszukiwanie repozytorium w katalogach wtyczek pod kątem tagów i sugerowanych promptów (`suggestedPrompts`).

---

## 🏗️ Struktura repozytorium

```text
flowkit/
├── .github/
│   ├── copilot-instructions.md    # Instrukcje dla GitHub Copilot
│   ├── prompts/                   # Dedykowane prompty Copilota (.prompt.md)
│   ├── workflows/                 # CI: automatyczna walidacja skilli
│   └── rulesets/                  # Konfiguracja ochrony gałęzi main
├── plugin.json                    # Manifest wtyczki Marketplace
├── scripts/
│   ├── install.ps1                # Instalator PowerShell dla Windows
│   └── install.sh                 # Instalator Bash dla Linux/macOS
├── skills/
│   ├── _template/                 # Wzorzec do tworzenia nowych skilli
│   └── client-pt-prd-writer/      # Dokumentacja PT/PRD bez halucynacji
│       ├── SKILL.md               # Główna definicja i logika skilla
│       ├── checklists/            # Listy kontrolne discovery i weryfikacji
│       ├── examples/              # Przykłady poprawnego vs zmyślonego zapisu
│       ├── references/            # Mapowanie szablonów użytkownika
│       └── templates/             # Zapasowy szablon dokumentu PT/PRD
├── LICENSE                        # Licencja MIT
└── README.md
```

---

## 🔒 Bezpieczeństwo i uprawnienia repozytorium

- **Dostęp do odczytu (Public)**: Każdy może przeglądać, klonować (`git clone`) i pobierać repozytorium.
- **Ochrona gałęzi (`main`)**: Bezpośredni push osób z zewnątrz jest zablokowany przez GitHub Ruleset (`protect-main.json`). Wszelkie zmiany wymagają Pull Requesta.
- **Bezpieczeństwo danych**: Plik `.gitignore` oraz pipeline CI dbają o to, by w repozytorium nigdy nie znalazły się klucze API, hasła, tokeny ani prywatne dane klientów.

---

## 📄 Licencja

Projekt udostępniany na licencji [MIT](LICENSE).
