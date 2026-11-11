# FlowKit - AI Skills for Analysts & DevOps

Kolekcja sprawdzonych umiejętności (**Agent Skills**) dla narzędzi AI takich jak **Claude Code**, **GitHub Copilot**, **Antigravity** czy **Cursor**. Repozytorium koncentruje się na automatyzacji pracy **Analityka Biznesowo-Systemowego** oraz **Inżyniera DevOps**.

---

## 📦 Dostępne skille

| Skill | Opis | Ścieżka |
|---|---|---|
| **client-pt-prd-writer** | Przygotowuje precyzyjną dokumentację PT/PRD (specyfikacje zmian, analizy przedwdrożeniowe) wyłącznie w oparciu o materiały źródłowe bez halucynacji i zmyślania. Obsługuje szablony klienta (.docx, .md). | [`skills/client-pt-prd-writer`](skills/client-pt-prd-writer/) |

---

## 🚀 Jak zainstalować i używać

### 1. Claude Code

#### Opcja A: Globalnie dla Twojego konta
Skopiuj wybrany folder skilla do katalogu konfiguracyjnego Claude Code:
```bash
# Linux / macOS
mkdir -p ~/.claude/skills
cp -r skills/client-pt-prd-writer ~/.claude/skills/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"
Copy-Item -Recurse -Force skills\client-pt-prd-writer "$HOME\.claude\skills\"
```

#### Opcja B: Lokalnie w projekcie
Umieść skill bezpośrednio w projekcie w folderze `.claude/skills/`:
```bash
mkdir -p .claude/skills
cp -r /path/to/flowkit/skills/client-pt-prd-writer .claude/skills/
```

---

### 2. GitHub Copilot

GitHub Copilot może korzystać z plików instrukcji i promptów:

1. **Copilot Workspace / Agent Mode**: Dodaj referencję do `skills/client-pt-prd-writer/SKILL.md` w pliku `.github/copilot-instructions.md` lub załącz plik w sesji czatu.
2. **Prompty wielokrotnego użytku**: Wykorzystaj treść `SKILL.md` oraz szablony z `templates/` jako reguły systemowe w Copilot Custom Instructions w VS Code / JetBrains.

---

## 🔒 Bezpieczeństwo i uprawnienia repozytorium

- **Dostęp do odczytu (Public)**: Repozytorium jest publicznie dostępne do przeglądania, klonowania (`git clone`) i pobierania.
- **Dostęp do zapisu (Restricted)**: Bezpośrednie wypychanie zmian (`git push`) do głównej gałęzi jest zablokowane dla osób z zewnątrz.
- **Wkład społeczności**: Wszelkie propozycje zmian przyjmowane są wyłącznie drogą Pull Request (PR) z wymaganą akceptacją właściciela.

---

## 📄 Licencja

Projekt udostępniany na licencji [MIT](LICENSE).

