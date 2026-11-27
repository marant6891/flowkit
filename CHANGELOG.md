# Changelog — FlowKit

Wszystkie znaczące zmiany w repozytorium. Format zgodny z [Keep a Changelog](https://keepachangelog.com/pl/).

---

## [Unreleased]

### Zmieniono
- `flowkit-client-message-editor` 1.2: wersja do wysłania trafia do pliku `mail-RRRR-MM-DD-[temat].md` (komunikator: `wiadomosc-…md`), sprawdzanego przez `check_message.py`.
- `doctor`: przy nieaktualnych agentach w `.githubgents` podpowiedź `install.ps1` zawiera `-AgentTargetPath` z pełną ścieżką, więc działa z dowolnego katalogu.

### Dodano
- **Skill `flowkit-client-solution-docs-writer` 1.0:** dokumentacja gotowego rozwiązania na podstawie jego kodu: pomoc dla użytkownika końcowego (help, podręcznik, szybki start, FAQ), instrukcja administratora albo dokumentacja techniczna. Brief w oknie pytań (typ dokumentu, odbiorca, kod rozwiązania, szablon Word), inwentaryzacja kodu z perspektywy roli odbiorcy (ekrany, pola, walidacje, komunikaty, uprawnienia, flagi), plan do akceptacji, tematy-zadania w języku odbiorcy, zapis `.docx` w szablonie, tryby roboczy, dla klienta i końcowy. Kontrola `check_user_docs.py` (uruchamiana przez executor), prompt VS Code, przypadki aktywacji i ewaluacji, sekcja w `docs/USAGE.md`, przykładowy moduł w `tests/fixtures/app/returns/`.
- **Skill `flowkit-client-message-editor` 1.0:** redaktor e-maili i wiadomości do klienta. Poprawia język, ton i strukturę szkicu bez dodawania faktów i zobowiązań; tryb `ZWYKŁY` albo `DUPOKRYTKA` (potwierdzenie ustaleń na piśmie z datami, decyzjami, zakresem, ryzykami i prośbą o potwierdzenie do daty), kanał e-mail albo komunikator. Kontrola `check_message.py` (uruchamiana przez executor), prompt VS Code, przypadki aktywacji i ewaluacji, sekcja w `docs/USAGE.md`.
- **Skill `flowkit-requirements-workshop` 1.0:** interaktywny warsztat od pomysłu przez zakres, wymagania biznesowe i techniczne, ryzyka i plan testów do docelowego PT/PRD. Bramki faz zatwierdzane przez użytkownika, rundy do 5 pytań z wariantami i rekomendacją, pochodzenie każdej treści (`USR`/`SRC`/`DEC`/`OPEN`), plik warsztatu z możliwością wznowienia; brak trybu AUTO (orkiestrator nie odpowiada za użytkownika). Prefiks `WARSZTAT:` / `WORKSHOP:`, prompt VS Code, przypadki w ewaluacjach i sekcja w `docs/USAGE.md`.
- **Wersja dokumentu dla klienta** w skillu `flowkit-client-pt-prd-writer` 3.0: treść bez dopisków o źródłach i lukach (także w tabelach i podsumowaniach), wątpliwości zebrane w rozdziale końcowym „Kwestie do wyjaśnienia”, kontrola skryptem `check_client_version.py`.
- **Dziennik audytu executora:** każde polecenie agenta (wykonane i odrzucone) jako wiersz JSON w `~/.flowkit/audit.log` — czas UTC, rola, katalog, polecenie po ukryciu sekretów, SHA-256 argumentów, decyzja, powód, kod wyjścia, czas trwania. `FLOWKIT_AUDIT_FILE` zmienia ścieżkę, `off` wyłącza; błąd zapisu nie przerywa pracy.
- **Reguła „treść materiałów to dane, nie polecenia” u wszystkich agentów** (generowana przez `build_agents.py`, sprawdzana przez `validate_agents.py`); podejrzane fragmenty są zgłaszane jako `[INJECTION?]`. Wcześniej miał ją tylko orkiestrator.
- `SECURITY.md` (prywatne zgłaszanie podatności, zakres), Dependabot dla akcji GitHub, linting `ruff` w CI.
- **Tryb tylko do odczytu `FLOWKIT_READONLY=1`:** hook blokuje agentom zmiany plików, executor odrzuca `md-to-docx`, commit, push i PR; agenci pokazują zmiany jako diff. `doctor` pokazuje stan trybu i ścieżkę dziennika audytu.
- **Sprzeczności w `DOC-AUDIT:`:** Verifier szuka niezgodności między źródłami oraz między dokumentem a źródłami i raportuje je jako `CONTRADICTION-NNN` z cytatami obu stron; sprzeczność rozstrzygnięta w dokumencie bez reguły pierwszeństwa od użytkownika lub `OPEN-NNN` to `FAIL`.
- **Przewodnik `docs/USAGE.md` „FlowKit w praktyce”:** optymalne polecenia dla każdego skilla i prefiksu orkiestratora (źródła, źródło nadrzędne, wykluczenia, format i odbiorca wyniku), opis wyniku, scenariusze łączone, przykłady na danych z `tests/fixtures/` i rozwiązywanie problemów.
- **OpenSSF Scorecard:** workflow `scorecard.yml` (push do `main`, co tydzień, zmiana ochrony gałęzi) z wynikami w Code scanning i odznaką w README.
- **`flowkit_doctor.py init`:** tworzy `~/.flowkit` i pusty plik zgód ze wszystkimi rolami (`0600`), nigdy nie nadpisuje istniejącego i nie dopisuje zgód; agenci nie mogą go uruchomić. Wzór `docs/allow.example.json` i schemat `docs/allow.schema.json` (podpowiedzi ról i walidacja w edytorze).

- **Prosty język PL i EN we wszystkich skillach i agentach:** standard `runtime/procedures/plain-language.md` oparty na zaleceniach gov.pl, Obserwatorium Językowego UW, artykule o kalkach składniowych (Magazyn PAN 4/2023), Federal Plain Language Guidelines i GOV.UK Style Guide. Reguły mają identyfikatory, poziomy (`FAIL`, `WARN`, `PRZEGLĄD`) i przykłady.
  - Wspólny checker `runtime/plain_language.py` i polecenie executora `plain-check` (role orchestrator, analyst, verifier, implementer): długość zdań, wata i nominalizacje, korpomowa, kalki składniowe, fałszywi przyjaciele w angielskim, skróty bez rozwinięcia, półpauzy, emoji i formułki AI; słownik projektu z `flowkit-project.md`, znaczniki `<!-- plain-check: off/on -->` dla celowych złych przykładów.
  - Każdy skill ma zasadę prostego języka, sekcję checklisty i kontrolę przed oddaniem; `check_message.py` i `check_user_docs.py` korzystają ze wspólnego modułu. Wersje: message-editor 1.1, solution-docs-writer 1.1, meeting-recap 1.6, pt-prd-writer 3.4, postmortem 1.6, sre-review 1.2, requirements-workshop 1.3, sql-data-assistant 1.4.
  - Agenci orchestrator, analyst, verifier i product-owner stosują standard; `DOC-AUDIT:` uruchamia `plain-check --strict`. Reguła w `copilot-instructions.md` i w promptach VS Code.
  - Walidatory i testy: `validate_skills.py` wymaga odwołania do standardu, `validate_agents.py` pilnuje go w adapterach, testy sprawdzają szablony, dokumentację i pliki skilli w trybie końcowym. Nowe scenariusze ewaluacji `message-editor-plain-pl` i `message-editor-plain-en` z wzorcowymi odpowiedziami ocenianymi offline (bez API) w testach.

### Zmieniono
- `flowkit-sql-data-assistant` 1.3: skrypty zmieniające dane są opakowane jak skrypt wdrożeniowy — nagłówek, kontrola serwera i bazy, numerowane kroki z komunikatami liczby wierszy, plan zmian z kopią poprzednich wartości, obsługa błędów, domyślne `ROLLBACK` z gotowym `COMMIT` w komentarzu, sprzątanie i skrypt odtworzenia; `check_sql.py` pilnuje opakowania.
- **Nowy `doctor`** (`runtime/flowkit_doctor.py`, także jako polecenie executora): sekcje Instalacja, Bezpieczeństwo, Konfiguracja i Narzędzia ze statusem `OK`/`INFO`/`UWAGA`/`BŁĄD` i podpowiedzią dla każdego problemu.
  - Sprawdza: zgodność wersji runtime, wtyczki i agentów (znacznik `FlowKit X.Y.Z` w adapterach), starych agentów `agent-3x3*`, Pythona używanego przez hooki (alias Microsoft Store), plik zgód (składnia z numerem linii, nieznane role z podpowiedzią, pominięte wpisy z powodem, uprawnienia na Linux/macOS), zapis dziennika audytu oraz katalogi z `FLOWKIT_EXTRA_PATHS`.
  - Kod wyjścia 1 przy błędach, `--json`, `--role`.
  - Uruchomienie: polecenie wtyczki `/flowkit:doctor`, prompt VS Code `/flowkit-doctor`, ścieżki wypisywane przez instalatory.
- **Jedno zachowanie okna pytań:** orkiestrator zadaje każde pytanie (punkt kontrolny, `ASK_USER`, pytania skilli i subagentów) przez okno pytań — VS Code `vscode/askQuestions`, Claude Code `AskUserQuestion` (nowe narzędzie orkiestratora); najwyżej 4 pytania w oknie, rekomendacja pierwsza, tekst tylko gdy okno jest niedostępne. Subagenci zwracają pytania jako `QUESTION-NNN`. Wszystkie skille mają sekcję „Pytania do użytkownika” (meeting-recap 1.5, pt-prd-writer 3.3, postmortem 1.5, sre-review 1.1, requirements-workshop 1.2), a prompty VS Code działają w trybie `agent` z narzędziem `vscode/askQuestions`. Walidatory pilnują reguły w agentach i skillach.
- **Diagnostyka okna pytań:** wiersz `Ask: window | text — <powód> | auto` w punktach kontrolnych i w `AGENT_LOG.md`; hook `runtime/log_tool_event.py` (PostToolUse) zapisuje w dzienniku audytu użycie okna pytań, skilli i subagentów FlowKit bez treści pytań; raport `runtime/checkpoint_report.py` z dziennika i zapisów rozmów Claude Code. Opis w `docs/USAGE.md` („Diagnoza okna pytań”).
- `flowkit-sql-data-assistant` 1.2: tryb `ANALYTICS_REPORT` dla zestawień analitycznych i raportowych na żądanie użytkownika — karta raportu, słownik miar, wzorce dla każdej bazy (trend m/m, udział, narastająco, top N, ABC, tabela przestawna, kohorty), zapytanie kontrolne; nowy przypadek ewaluacji `sql-analytics-report`.
- `flowkit-client-pt-prd-writer` 3.2: izolacja materiałów źródłowych (zasada 10) jest wymogiem, a nie zaleceniem.
- Hook blokuje agentom edycję katalogu `.git`, plików wrażliwych (`.env*` poza `.env.example`, klucze) i dziennika audytu, także w katalogach z `FLOWKIT_EXTRA_PATHS`; `md-to-docx` nie zapisuje w `.git`.
- Akcje GitHub w CI przypięte do SHA commita; checkout bez zapisanych poświadczeń (`persist-credentials: false`).
- CI: nowy push do PR anuluje nieaktualny przebieg (`concurrency`); na `main` każdy commit ma własny przebieg.
- CI uruchamia wszystkie pliki `tests/test_*.py` (wcześniej 4 pliki z listy; nie były uruchamiane m.in. testy `doctor`, redaktora maili i dokumentacji rozwiązania).
- Szablony zapasowe skilli, README, `docs/USAGE.md` i pliki skilli bez półpauz i pauz oraz bez zdań dłuższych niż 35 słów.

### Naprawiono
- **Niezależny audyt `DOC-AUDIT:` nie mógł czytać dokumentów:** rola `verifier` dostała `read-document` i `detect-docx-libs` oraz skrypty kontrolne skilli, które tylko czytają pliki (`check_client_version.py`, `check_status_labels.py`, `validate_diagram.py`, `check_sql.py`); nadal nie zapisuje DOCX i nie generuje diagramów. Verifier ma instrukcję czytania DOCX/XLSX/PDF w audycie.
- **Podpowiedzi odrzuceń nie proponują już złych reguł zgód:** dla poleceń wbudowanych FlowKit (`read-document`, `md-to-docx` itd.) zamiast reguły w `allow.json` pada wskazanie roli i `doctor`; dla pozostałych poleceń reguła nie zawiera ścieżki pliku (wcześniej powstawała osobna reguła dla każdego pliku). Orkiestrator nie proponuje zgód dla poleceń wbudowanych.
- **`doctor` wskazuje przyczynę `Ask: text`:** błąd, gdy zainstalowany orkiestrator nie ma narzędzia okna pytań (stary agent); ostrzeżenia o starym runtime instalatora (`~/.claude/flowkit/runtime`) i o podwójnej instalacji (wtyczka i agenci z instalatora); dla starych agentów podaje dokładne polecenie ponownej instalacji. Powód w `Ask: text — …` jest konkretny, a postoje trybu `AUTO:` też idą przez okno pytań.
- `flowkit-requirements-workshop` 1.1: jednoznaczne przekazanie rekomendacji do PT/PRD, audyt bez orkiestratora, warsztat nie trafia do subagenta.
- `run_evals.py`: błąd API Claude Code (np. „Credit balance is too low”) jest raportowany z treścią jako błąd infrastruktury, a nie jako sam „kod wyjścia 1” lub ocena jakości.
- Komunikaty executora na stderr (np. błąd zapisu dziennika) są w UTF-8 także w Windows.
- Polskie znaki w wynikach skryptów Pythona uruchamianych przez executor nie są już zniekształcone w Windows (`PYTHONIOENCODING=utf-8`).

---

## [1.8.0] — 2026-11-20

### Dodano
- **Agent `agent-3x3-validator`:** statyczna walidacja plików infrastruktury i CI w roli `validator` (`terraform fmt/validate`, `tflint`, `hadolint`, `docker compose config -q`, `helm lint/template`, `kubeconform`, `yamllint`, `actionlint`, `shellcheck`, `check-json`), bez wdrażania i dostępu do klastra.
- **Skill `devops-sre-review`:** przegląd niezawodności (SLI/SLO, alerty, RED/USE, sondy, zasoby, HPA/PDB, backup i RPO/RTO, koszt) z ustaleniami opartymi na plikach.
- **Zgody użytkownika na polecenia:** plik `~/.flowkit/allow.json` (`FLOWKIT_ALLOW_FILE`) — polecenia wpisane przez użytkownika agent wykonuje sam; hook blokuje agentom edycję pliku zgód i runtime.
- **Tryby ryzyka `FAST`/`STANDARD`/`STRICT`** w orkiestratorze oraz prefiksy `FAST:` i `STRICT:`.
- **Wspólne statusy** `PASS`/`FAIL`/`NOT_RUN`/`UNKNOWN`/`BLOCKED` i procedura `devops-loop.md` (Diagnostics → DevOps → Validator → zgoda → ponowne sprawdzenie) z blokiem przekazania.
- **Kontrola DOCX:** `md-to-docx` ponownie otwiera wynik i porównuje nagłówki, tabele, obrazy oraz nagłówki i stopki szablonu (kod 4 przy niezgodności); opcja `--pdf` z LibreOffice.
- **Scenariusze E2E** w ewaluacji: badanie danych SQL i przegląd manifestu Kubernetes.
- **Zapis DOCX `md-to-docx`:** polecenie executora zapisuje Word z Markdown na kopii szablonu klienta (`--template` z treścią szablonu i znacznikiem `[[FLOWKIT:TREŚĆ]]` albo `--reference-doc` z samymi stylami). Dokument ma komplet stylów, numerację, nagłówki, stopki i styl tabel szablonu. Bloki mermaid są renderowane lokalnym mermaid-cli, a SVG zamieniane na PNG (Playwright, CairoSVG, rsvg-convert), więc Pandoc nie wymaga `rsvg-convert`.
- **`help` w executorze:** `flowkit_exec.py --role <rola> -- help` wypisuje polecenia dozwolone dla roli; odrzucenie wskazuje, jak zapisać DOCX.
- **Tryb `AUTO:`:** orkiestrator i skill PT/PRD realizują całe zadanie na rekomendacjach i oddają rejestr przyjętych decyzji.
- **Pytanie o źródła danych:** praca nad dokumentem zaczyna się od pytania o znane źródła do przygotowania i weryfikacji.

### Zmieniono
- **Nazwy agentów z prefiksem `flowkit-`:** `agent-3x3` → `flowkit-orchestrator`, `agent-3x3-analyzer` → `flowkit-code-analyzer`, `agent-3x3-pm` → `flowkit-product-owner`, pozostali `agent-3x3-<rola>` → `flowkit-<rola>`. Hook rozpoznaje dawne nazwy do kolejnego wydania.
- **Główny agent widoczny jako jedyny:** w VS Code subagenci mają `user-invocable: false` (ukryci na liście wyboru, dostępni dla orkiestratora przez pole `agents`); opis orkiestratora zaczyna się od „Główny agent FlowKit — zacznij tutaj”. Instalatory mają opcję `-SetDefaultAgent` / `--set-default-agent` (domyślny agent projektu w Claude Code).
- Executor rozwija wzorce plików (np. `diagrams/D-*.yaml`) w obrębie katalogu roboczego — wcześniej kroki diagramów skilla PT/PRD dostawały wzorzec dosłownie i kończyły się błędem.
- **Nazwy skilli z prefiksem `flowkit-`:** `flowkit-client-pt-prd-writer`, `flowkit-client-meeting-recap`, `flowkit-devops-incident-postmortem`, `flowkit-sql-data-assistant`, `flowkit-devops-sre-review` (katalogi, prompty VS Code, routing agentów, instalatory). Po aktualizacji usuń stare katalogi skilli bez prefiksu z `~/.claude/skills/` lub `.github/skills/`.
- Analityk oznacza rodzaj stwierdzeń (fakt, obserwacja, interpretacja, założenie, decyzja, rekomendacja, pytanie) i raportuje luki pokrycia wymagań testami.
- `client-pt-prd-writer` 2.9: kontrola pokrycia w wariancie pełnym, oznaczanie interpretacji.
- `client-meeting-recap` 1.4: właściciel zadania tylko z dowodem (osoba, zespół, niepotwierdzony, brak), konfigurowalne okno korekt, brak sugestii „milczenie = akceptacja”.
- `sql-data-assistant` 1.1: tryby `READ_ONLY`/`DATA_INVESTIGATION`/`DATA_REPAIR`, oczekiwana liczba rekordów, zachowanie poprzednich wartości i skrypt odtworzenia, współbieżność i różnice silników.
- Każde polecenie executora kończy się linią `[kod wyjścia: N]`; brak narzędzia to `NOT_RUN`.
- Macierz platform w README ma uczciwe statusy `PARTIAL`/`UNVERIFIED` i ograniczenia.

### Naprawiono
- `read-document` odrzucał kod źródłowy (np. `.cs`). Teraz czyta każdy plik tekstowy rozpoznany po treści, w kodowaniu UTF-8, UTF-16 lub CP1250; pliki binarne są odrzucane z czytelnym komunikatem.
- Orkiestrator nie mógł uruchomić testów (`python -m unittest`, `pytest`, `dotnet test` itd.) ani kontroli statycznych potrzebnych w ścieżce szybkiej.
- Podpowiedź przy odrzuceniu wskazywała `md-to-docx` dla każdego polecenia `python`. Teraz pokazuje ją tylko dla narzędzi DOCX, a dla innych poleceń wskazuje role, którym wolno je uruchomić.
- Agenci nie mogli zapisać DOCX: `pandoc` i skrypty Python były poza listą dozwolonych poleceń.
- `detect-docx-libs` pokazuje też Pandoc, mermaid-cli, Playwright, CairoSVG i rsvg-convert.

### Bezpieczeństwo
- **Granica katalogu roboczego:** executor odrzuca ścieżki poza katalogiem roboczym, także przez `..`, `~` i dowiązania symboliczne (`read-document`, `rg`, `grep`, `find`, `md-to-docx`, argumenty skryptów skilli). Dodatkowe katalogi użytkownik dopisuje w `FLOWKIT_EXTRA_PATHS`.
- `md-to-docx` nie osadza obrazów spoza katalogu roboczego.
- README opisuje, czego runtime nie zabezpiecza (brak izolacji systemowej).

### Ewaluacja
- `run_evals.py`: limit czasu scenariusza (`--timeout`) i sesji (`--total-timeout`), zakończenie zawieszonego procesu razem z potomnymi, zapis wyników po każdym scenariuszu.
- Statusy `PASS`, `FAIL`, `TIMEOUT`, `ERROR`, `SKIPPED`; błąd infrastruktury nie jest liczony jako błąd jakości. Kod wyjścia 2 oznacza problem infrastruktury.

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

