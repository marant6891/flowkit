# Zasady projektu i dobre praktyki inżynierskie — FlowKit

> Dokument określa standardy pracy, strategię gałęzi Git, zasady bezpieczeństwa oraz kryteria jakościowe obowiązujące wszystkich autorów, kontrybutorów oraz asystentów AI w repozytorium **FlowKit**.

---

## 1. Strategia pracy z Git (Branching & PR Workflow)

### 1.1 Złota zasada: Żadnych bezpośrednich commitów do `main`
- **Gałąź `main` jest chroniona** i reprezentuje stabilny, przetestowany stan produkcyjny biblioteki.
- **Wszystkie zmiany trafiają do `main` wyłącznie poprzez Pull Request (PR)**.
- Zasada dotyczy **wszystkich** — zarówno zewnętrznych kontrybutorów, jak i właściciela repozytorium (dogfooding dobrych praktyk).

### 1.2 Cykl życia zmiany (Feature Branch Workflow)
1. **Aktualizacja gałęzi bazowej:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Utworzenie dedykowanej gałęzi funkcyjnej:**
   Nazwa gałęzi powinna jednoznacznie wskazywać charakter zmiany:
   - Nowy skill: `feat/nazwa-skilla` (np. `feat/k8s-pod-troubleshooter`)
   - Poprawka istniejącego skilla: `fix/nazwa-skilla-opis` (np. `fix/postmortem-table-format`)
   - Dokumentacja: `docs/opis` (np. `docs/update-installation-guide`)
   - Infrastruktura CI / narzędzia: `ci/opis` lub `chore/opis`
   ```bash
   git checkout -b feat/user-story-acc-writer
   ```
3. **Praca na gałęzi i testy lokalne:**
   Przed commitem zawsze uruchom walidator:
   ```bash
   python scripts/validate_skills.py
   ```
4. **Wypchnięcie gałęzi i otwarcie Pull Requesta:**
   ```bash
   git push -u origin feat/user-story-acc-writer
   ```
   Wypełnij checklistę w formularzu Pull Requesta.
5. **Weryfikacja CI i Merge:**
   - Merge jest dozwolony wyłącznie wtedy, gdy automatyczny pipeline CI (`Validate Skills`) zakończył się sukcesem (zielony znacznik).
   - Rekomendowana metoda łączenia: **Squash and merge** (utrzymuje czystą, jednowierszową historię w `main`).
6. **Usunięcie gałęzi funkcyjnej** po udanym merge.

### 1.3 Konwencja komunikatów commitów (Conventional Commits)
Wszystkie commity powinny być sformatowane według schematu `typ: zwięzły opis po polsku lub angielsku`:
- `feat:` — nowy skill lub nowa istotna funkcjonalność,
- `fix:` — poprawka błędu w logice skilla, checklistach lub szablonach,
- `docs:` — zmiany wyłącznie w dokumentacji (README, DEVELOPMENT, opisy),
- `style:` — formatowanie, końce linii (CRLF/LF), usuwanie zbędnych spacji,
- `refactor:` — przebudowa struktury bez zmiany zachowania,
- `ci:` — zmiany w plikach GitHub Actions (`.github/workflows/`),
- `chore:` — zadania pomocnicze (aktualizacja `.gitignore`, skryptów instalatora).

---

## 2. Standardy jakościowe skilli (Kultura FlowKit)

### 2.1 Zasada nr 1: Zero halucynacji (Brak źródła = brak treści)
To najważniejsza reguła odróżniająca FlowKit od innych repozytoriów promptów:
- Skille **nie mogą zgadywać, konfabulować ani uzupełniać braków „typowymi danymi"**.
- Jeśli użytkownik nie dostarczył terminu, osoby odpowiedzialnej, architektury czy metryki:
  - Zastosuj oznaczenie: `[Do potwierdzenia]`, `OPEN-NNN` lub `Nie analizowano — brak dostępu do <źródła>`.
- Wszelkie propozycje własne modelu muszą być wyraźnie odseparowane od wymagań i oznaczone jako `Rekomendacja` (np. `REC-001`).

### 2.2 Wymagana struktura każdego skilla
Żaden skill nie może być „jednym plikiem markdown wrzuconym luzem". Każdy katalog w `skills/` musi posiadać kompletną architekturę:

| Plik / Folder | Rola | Obowiązkowy? |
|---|---|:---:|
| `SKILL.md` | Główna definicja, YAML frontmatter, cel, zasady, etapy | **TAK** |
| `CHANGELOG.md` | Historia wersji danego skilla (SemVer) | **TAK** |
| `templates/` | Co najmniej jeden zapasowy szablon dokumentu (`.md`) | **TAK** |
| `checklists/` | Co najmniej jedna checklista weryfikacji jakości przed oddaniem | **TAK** |
| `examples/` | Przykłady transformacji wejście → wyjście (dobrze vs źle) | Zalecany |
| `references/` | Materiały pomocnicze (obsługa formatów, mapowanie szablonów) | Zalecany |

### 2.3 Wymagania wobec `SKILL.md`
- Poprawny nagłówek YAML frontmatter z polami: `name`, `version`, `tags`, `description`.
- Wartość `name` musi być **identyczna z nazwą katalogu** (`kebab-case`).
- Wersja w formacie `"X.Y"` (np. `"1.0"`).
- Co najmniej 3 tagi po angielsku.
- Ostatni etap w `SKILL.md` **musi być etapem weryfikacji** odsyłającym do pliku w `checklists/`.

### 2.4 Szablon klienta ma zawsze pierwszeństwo (User Template Priority)
Każdy skill generujący dokumenty musi w pierwszym kroku zapytać o szablon klienta/użytkownika (`.docx`, `.md`). Wbudowany szablon w `templates/` jest wyłącznie szablonem zapasowym (*fallback*).

---

## 3. Bezpieczeństwo i ochrona danych (Zero Leaks)

### 3.1 Bezwzględny zakaz publikacji danych poufnych
Do repozytorium **nigdy nie mogą trafić**:
- Rzeczywiste nazwy klientów komercyjnych (zastępuj fikcyjnymi, np. *Klient XYZ*, *ACME Corp*),
- Klucze API, tokeny dostępowe, hasła, certyfikaty, pliki `.pem` / `.key`,
- Prywatne adresy IP infrastruktury produkcyjnej, wewnętrzne domeny intranetowe,
- Prawdziwe dane osobowe (RODO) — w przykładach stosuj *Jan Kowalski*, *Anna Nowak*.

### 3.2 Ochrona automatyczna
- Plik `.gitignore` blokuje pliki środowiskowe (`.env*`), poświadczenia, klucze SSH oraz pliki tymczasowe edytorów pakietu Office (`~$*.docx`).
- Na GitHubie włączone są mechanizmy **Secret Scanning** oraz **Push Protection**.

---

## 4. Wersjonowanie i publikacja (Versioning)

- Repozytorium jako całość podlega wersjonowaniu semantycznemu (**SemVer**): `MAJOR.MINOR.PATCH`.
- Każde wydanie nowej wersji wymaga:
  1. Aktualizacji pola `version` w [`plugin.json`](plugin.json).
  2. Uzupełnienia wpisu w głównym [`CHANGELOG.md`](CHANGELOG.md).
  3. Nadania taga Git (np. `v1.1.0`).
- Każdy pojedynczy skill posiada także własną historię zmian w `skills/<nazwa>/CHANGELOG.md`.

---

## 5. Rola Asystentów AI (GitHub Copilot, Claude, Cursor)

Asystenci AI pracujący w tym repozytorium są zobowiązani do:
1. Bezwzględnego przestrzegania reguły **No Direct Push to `main`** — proponowania zmian w formie gałęzi i PR.
2. Uruchamiania skryptu walidacji `scripts/validate_skills.py` po dodaniu lub edycji dowolnego skilla.
3. Zachowania spójności stylistycznej i modularnej struktury katalogów.
