# FlowKit

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/marant6891/flowkit/badge)](https://securityscorecards.dev/viewer/?uri=github.com/marant6891/flowkit)

Biblioteka skilli i agentów AI dla **analityków biznesowo-systemowych** i **inżynierów DevOps**. FlowKit prowadzi od materiału wejściowego (brief, transkrypcja, logi, kod, manifesty) do zweryfikowanego rezultatu: dokumentu PT/PRD w szablonie klienta, podsumowania spotkania, raportu postmortem, skryptu SQL albo zwalidowanej konfiguracji.

Zasady, na których opiera się całe rozwiązanie:

- **Brak źródła = brak treści.** Fakty mają wskazane źródło, a luki są oznaczane (`DO POTWIERDZENIA`, `OPEN-NNN`), nie uzupełniane „typowymi” treściami.
- **Statusy zgodne z tym, co faktycznie wykonano.** Sprawdzenie, którego nie uruchomiono, ma status `NOT_RUN`, nigdy `PASS`.
- **Praca lokalna i kontrolowana.** Agenci nie korzystają z sieci ani MCP; polecenia uruchamiają tylko przez lokalny executor z listą dozwoloną dla roli.
- **Decyzje ryzykowne należą do człowieka.** Wdrożenia, usuwanie, commit, push i publikacja zawsze czekają na zgodę.

Wersja: **1.8.0** · Licencja: [MIT](LICENSE) · Historia zmian: [CHANGELOG.md](CHANGELOG.md)

---

## Spis treści

1. [Szybki start](#szybki-start)
2. [Wymagania](#wymagania)
3. [Skille](#skille)
4. [Agenci](#agenci)
5. [Jak to działa](#jak-to-działa)
6. [Konfiguracja](#konfiguracja)
7. [Bezpieczeństwo i ograniczenia](#bezpieczeństwo-i-ograniczenia)
8. [Obsługiwane platformy](#obsługiwane-platformy)
9. [Instalacja](#instalacja)
10. [Aktualizacja z wersji 1.7](#aktualizacja-z-wersji-17)
11. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
12. [Rozwój i współtworzenie](#rozwój-i-współtworzenie)

**Praktyczne użycie:** gotowe polecenia dla każdego skilla i agenta (jakie źródła wskazać, jak opisać oczekiwany wynik, co dostaniesz) - [docs/USAGE.md](docs/USAGE.md).

**Prosty język (PL i EN):** wszystkie skille i agenci piszą według jednego standardu - [runtime/procedures/plain-language.md](runtime/procedures/plain-language.md).

---

## Szybki start

Claude Code, instalacja jako wtyczka (skille, agenci, runtime i hook bezpieczeństwa):

```bash
claude plugin marketplace add marant6891/flowkit
```

```bash
claude plugin install flowkit@flowkit
```

Uruchom głównego agenta - orkiestrator - w katalogu projektu. W instalacji przez wtyczkę jego nazwa ma prefiks wtyczki:

```bash
claude --agent flowkit:flowkit-orchestrator
```

Aby każda sesja w projekcie startowała od orkiestratora, ustaw go jako domyślnego agenta (patrz [Główny agent](#główny-agent)).

Przykładowe zadania:

```text
Przygotuj dokument PT na podstawie materiałów z folderu materialy/ w szablonie szablon-klienta.dotx.
Podsumuj spotkanie z pliku spotkanie.vtt i przygotuj mail do klienta.
DEVOPS: przygotuj Dockerfile dla aplikacji i zwaliduj go.
AUTO: BA: przygotuj backlog z przypadkami testowymi z dokumentu wymagania.docx.
```

Orkiestrator sam rozpoznaje rodzaj zadania i wybiera skill lub subagenta. Optymalne polecenia ze wskazaniem źródeł i oczekiwanego wyniku dla każdego skilla: [**FlowKit w praktyce**](docs/USAGE.md). Instalacja dla VS Code Copilot i instalacja ręczna: [Instalacja](#instalacja).

---

## Wymagania

| Składnik | Wymagany do | Instalacja |
|---|---|---|
| Python 3.10+ | executor, hook, skrypty skilli | wymagany |
| `python-docx` | zapis i kontrola plików Word (`md-to-docx`) | `pip install python-docx` |
| `pyyaml` | silnik diagramów skilla PT/PRD | `pip install pyyaml` |
| Pandoc | alternatywny silnik DOCX bez szablonu | `winget install JohnMacFarlane.Pandoc` |
| mermaid-cli | diagramy mermaid w DOCX | `npm install -g @mermaid-js/mermaid-cli` |
| Playwright lub CairoSVG | konwersja SVG → PNG | `pip install playwright` + `playwright install chromium` |
| LibreOffice | opcjonalny podgląd PDF (`--pdf`) | pakiet systemowy |
| `pypdf` | odczyt PDF | `pip install pypdf` |
| Walidatory DevOps i bezpieczeństwa | agenci Validator i Verifier | `terraform`, `tflint`, `hadolint`, `helm`, `kubeconform`, `conftest`, `kyverno`, `yamllint`, `actionlint`, `zizmor`, `shellcheck`, `semgrep` (reguły lokalne), `osv-scanner`, `gitleaks`, Docker - według potrzeb |

Brak opcjonalnego narzędzia nie przerywa pracy: odpowiednie sprawdzenie dostaje status `NOT_RUN`, a agent podaje polecenie instalacji. Stan środowiska pokazuje `doctor` (patrz [Diagnoza](#diagnoza-doctor)).

---

## Skille

Wszystkie skille mają prefiks `flowkit-`. Skill uruchamia się automatycznie, gdy prośba pasuje do jego opisu, albo przez orkiestrator.

### Analiza biznesowa i systemowa

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **flowkit-client-pt-prd-writer** | `3.6` | Dokument PT/PRD dla klienta wyłącznie na podstawie materiałów, w szablonie klienta (`.docx`, `.dotx`, `.md`) z kompletem jego stylów. Wariant skrócony dla małych zmian (1-3 strony) i pełny. Trzy tryby wyniku: **wersja dla klienta** (domyślna: czysta treść, wątpliwości zebrane w rozdziale końcowym), dokument końcowy bez dopisków i roboczy z oznaczeniami źródeł. User stories Given-When-Then, Definition of Done, kontrola pokrycia wymagań testami, diagramy oparte na źródłach, tryb `AUTO`. | [`skills/flowkit-client-pt-prd-writer/`](skills/flowkit-client-pt-prd-writer/) |
| **flowkit-requirements-workshop** | `1.3` | Interaktywny warsztat wymagań prowadzony krok po kroku: koncepcja, zakres, wymagania biznesowe (role, procesy, reguły, user stories Given-When-Then) i techniczne (integracje, dane, NFR), ryzyka i plan testów, a na końcu docelowy PT/PRD przez `flowkit-client-pt-prd-writer`. Każda faza zatwierdzana przez użytkownika, bez trybu AUTO; stan w pliku warsztatu, który można wznowić. | [`skills/flowkit-requirements-workshop/`](skills/flowkit-requirements-workshop/) |
| **flowkit-client-message-editor** | `1.1` | Redakcja szkicu e-maila lub wiadomości (Teams, Slack) do klienta: ton, struktura, jedna prośba z terminem, bez nowych faktów i zobowiązań. Tryb `ZWYKŁY` albo `DUPOKRYTKA` (potwierdzenie na piśmie: ponumerowane fakty z datami, decyzje, zakres, ryzyka, zależności od klienta, prośba o potwierdzenie do daty). Kontrola `check_message.py`. | [`skills/flowkit-client-message-editor/`](skills/flowkit-client-message-editor/) |
| **flowkit-client-solution-docs-writer** | `1.4` | Dokumentacja gotowego rozwiązania z jego kodu: **pomoc dla użytkownika końcowego** (help, podręcznik, szybki start, FAQ), instrukcja administratora albo dokumentacja techniczna. Najpierw brief w oknie pytań: typ dokumentu, odbiorca (rola, poziom wiedzy), kod rozwiązania (repozytorium, moduł, wersja) i szablon Word. Inwentaryzacja kodu z perspektywy roli (ekrany, pola, walidacje, komunikaty, uprawnienia, flagi), plan do akceptacji, tematy-zadania krok po kroku w języku odbiorcy, zapis `.docx` w stylach szablonu, tryby roboczy, dla klienta i końcowy. Pełna struktura rozdziału modułu (układ ekranu z legendą, wszystkie opcje, słownik kolumn, statusy, zakładki), katalog opcji z kontrolą pokrycia `check_coverage.py` i rysunki z silnika diagramów. Domyślnie dokument dla klienta bez dopisków (`make_client_version.py`, pochodzenie w osobnym rejestrze). Kontrola `check_user_docs.py`. | [`skills/flowkit-client-solution-docs-writer/`](skills/flowkit-client-solution-docs-writer/) |
| **flowkit-client-meeting-recap** | `1.6` | Z transkrypcji (`.vtt`, `.docx`, `.txt`) dwa osobne pliki: wewnętrzny radar ryzyk z cytatami jako dowodami oraz szkic maila do klienta z decyzjami, zadaniami i właścicielami potwierdzonymi w rozmowie oraz prośbą o korekty w ustalonym oknie. | [`skills/flowkit-client-meeting-recap/`](skills/flowkit-client-meeting-recap/) |

### Dane i SQL

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **flowkit-sql-data-assistant** | `1.4` | Zapytania, raporty analityczne i skrypty poprawy danych. Bazy: PostgreSQL, SQL Server, Oracle, MySQL i MariaDB. Tryby: `READ_ONLY`, `ANALYTICS_REPORT`, `DATA_INVESTIGATION` i `DATA_REPAIR`. Raporty: karta raportu z definicjami miar, funkcje okna, porównania okresów, rankingi, kohorty i kontrola spójności. Zmiany danych: transakcja, kontrola liczby rekordów, domyślne `ROLLBACK`, zachowanie poprzednich wartości i skrypt odtworzenia. Nigdy nie łączy się z bazą. | [`skills/flowkit-sql-data-assistant/`](skills/flowkit-sql-data-assistant/) |

### DevOps i SRE

| Skill | Wersja | Opis | Ścieżka |
|---|---|---|---|
| **flowkit-devops-sre-review** | `1.2` | Przegląd niezawodności usługi na podstawie plików: SLI/SLO i error budget, alerty, metryki RED/USE, sondy, requests i limits, HPA i PDB, backup i RPO/RTO, koszt. Ustalenia z dowodem `plik:linia`, rekomendacje z sygnałem, progiem i uzasadnieniem. | [`skills/flowkit-devops-sre-review/`](skills/flowkit-devops-sre-review/) |
| **flowkit-devops-incident-postmortem** | `1.6` | Bezobwiniający raport postmortem: klasyfikacja SEV, oś czasu, łańcuch przyczyn (Trigger, Amplifier, Detection/Process Gap, 5 Whys), komunikacja i działania PREVENT/DETECT/MITIGATE. | [`skills/flowkit-devops-incident-postmortem/`](skills/flowkit-devops-incident-postmortem/) |

Nowy skill zaczyna się od wzorca [`skills/_template/`](skills/_template/) - patrz [Rozwój i współtworzenie](#rozwój-i-współtworzenie).

---

## Agenci

### Główny agent

**`flowkit-orchestrator`** to jedyny agent, z którym się rozmawia. Rozpoznaje zadanie, wybiera skill, pracuje w pętli 3x3 (najwyżej 3 kroki, podsumowanie, decyzja użytkownika) i deleguje pracę do 9 subagentów. Subagentów nie wybiera się ręcznie.

| Platforma | Jak jest widoczny |
|---|---|
| Claude Code | `claude --agent flowkit-orchestrator` (wtyczka: `flowkit:flowkit-orchestrator`). Domyślny agent projektu: `install.ps1 -SetDefaultAgent` / `install.sh --set-default-agent` zapisuje `"agent": "flowkit-orchestrator"` w `.claude/settings.json` bieżącego projektu; w instalacji przez wtyczkę wpisz tam `flowkit:flowkit-orchestrator`. Lista `/agents` pokazuje także subagentów - Claude Code nie pozwala ich ukryć. |
| VS Code Copilot | Na liście wyboru agentów jest tylko `flowkit-orchestrator`. Subagenci mają `user-invocable: false`: są ukryci, a orkiestrator może ich wywołać (lista w polu `agents`). |

### Subagenci

| Agent | Uprawnienia | Zadanie |
|---|---|---|
| **flowkit-analyst** | odczyt, edycja, dokumenty | Wymagania, proces, analiza wpływu, backlog, przypadki testowe, scenariusze testów manualnych frontu, gotowe treści zgłoszeń Jira/Azure DevOps oraz UAT na dokumentach Word, Excel, PDF i tekstowych |
| **flowkit-code-analyzer** | tylko odczyt | Analiza kodu i zależności z rozróżnieniem faktów i hipotez |
| **flowkit-planner** | tylko odczyt | Plan iteracji z etykietami ryzyka i szacunkiem pracy |
| **flowkit-product-owner** | tylko odczyt | User stories, kryteria akceptacji, ADR |
| **flowkit-implementer** | edycja, testy | Jeden atomowy krok zmiany z samokontrolą diffa |
| **flowkit-verifier** | tylko odczyt, testy | Weryfikacja kodu w 9 wymiarach (bez testów `[NOT VERIFIED]`), niezależny audyt dokumentów klienckich (`DOC-AUDIT:`), zmian w skillach/agentach (`SKILL-AUDIT:`) oraz defensywny audyt bezpieczeństwa OWASP i testów frontu (`QA-AUDIT:`) |
| **flowkit-devops** | edycja, bez wykonywania poleceń | CI/CD, Docker, Kubernetes, IaC, chmura; polecenia zmieniające środowisko tylko jako propozycja `REQUIRES APPROVAL` |
| **flowkit-diagnostics** | tylko odczyt | Logi, stan klastra i kontenerów, runbooki |
| **flowkit-validator** | tylko odczyt, walidatory | Statyczna walidacja Terraform, Dockerfile, compose, Helm, Kubernetes YAML, CI, skryptów i JSON; bez wdrażania i dostępu do klastra |

Definicje źródłowe są w [`agents/*_agent.md`](agents/), kontrakty niezależne od platformy w [`agents/core/`](agents/core/), a pliki instalowane u użytkownika w [`agents/adapters/`](agents/adapters/) (generowane przez `python scripts/build_agents.py`).

### Prefiksy orkiestratora

Prefiksy są opcjonalne - bez nich orkiestrator sam dobiera działanie i podaje je w linii `Mode:`. Można je łączyć: `PLAN: LOG: zadanie`, `AUTO: BA: zadanie`.

| Prefiks | Działanie |
|---|---|
| `ANALYZE:` · `VERIFY:` · `PLAN:` · `SPEC:` | zaczyna od Analyzera, Verifiera, Plannera albo PM |
| `BA:` · `QA:` · `DEVOPS:` · `DIAG:` · `SQL:` | analityk, testy manualne frontu i audyt OWASP (`QA:`), DevOps, diagnostyka albo skill SQL |
| `WARSZTAT:` / `WORKSHOP:` | interaktywny warsztat wymagań: od pomysłu przez część biznesową i techniczną do docelowego PT/PRD, z zatwierdzeniem każdej fazy |
| `DRY:` | pokazuje plan i czeka na potwierdzenie |
| `LOG:` | zapisuje iteracje w `AGENT_LOG.md` |
| `SHIP:` | po weryfikacji i zgodzie: gałąź, commit, push, PR |
| `FAST:` / `STRICT:` | wymusza tryb ryzyka (patrz niżej) |
| `AUTO:` | realizuje całe zadanie na rekomendacjach i oddaje listę przyjętych decyzji |

---

## Jak to działa

### Tryby ryzyka

| Tryb | Kiedy | Zachowanie |
|---|---|---|
| `FAST` | prosta zmiana w jednym pliku, pytanie, podsumowanie | bez subagentów i pośrednich checkpointów; jedno podsumowanie |
| `STANDARD` | typowe zadania | iteracje po 3 kroki z checkpointem |
| `STRICT` | produkcja, migracje, dane, uprawnienia, operacje nieodwracalne (wybierany automatycznie) | zgoda przed każdym krokiem średniego i wysokiego ryzyka, weryfikacja po każdej zmianie, rollback ustalony przed zmianą |

Żaden tryb, także `AUTO`, nie pomija zgody na kroki wysokiego ryzyka, usuwanie, dostarczenie i publikację.

### Dokumenty klienta

1. Agent pyta o znane źródła danych do przygotowania i weryfikacji dokumentu (w trybie `AUTO` pracuje na dostarczonych materiałach).
2. Czyta materiały i szablon poleceniem `read-document` (Word, Excel, PDF, tekst, kod źródłowy; duże pliki partiami).
3. Pisze treść w Markdown według zasad skilla: tylko ze źródeł, zwięźle, z oznaczonymi lukami, prostym językiem.
   Przed oddaniem sprawdza tekst poleceniem `plain-check` (patrz [Prosty język](#prosty-język)).
4. Zapisuje DOCX poleceniem `md-to-docx` na kopii szablonu klienta - dokument ma komplet jego stylów, numerację, nagłówki i stopki. `--template` zachowuje stronę tytułową i metryczkę, `--set POLE=WARTOŚĆ` wypełnia pola szablonu, diagramy mermaid i SVG trafiają do dokumentu jako PNG.
5. Konwerter ponownie otwiera wynik i porównuje jego strukturę ze źródłem (`Kontrola DOCX: PASS/FAIL`); opcjonalnie tworzy podgląd PDF.
6. Przed przekazaniem dokumentu końcowego lub wersji dla klienta `flowkit-verifier` wykonuje niezależny audyt `DOC-AUDIT:`. Audyt widzi tylko materiały źródłowe, dokument i checklistę skilla. Sprawdza pokrycie w źródłach, brak bagatelizowania pracochłonności, prosty język oraz spójność stylu i tabel. Sprzeczności między źródłami oraz między dokumentem a źródłami zgłasza jako `CONTRADICTION-NNN` z cytatami obu stron.

Szczegóły: [docx-engine.md](skills/flowkit-client-pt-prd-writer/references/docx-engine.md).

### Prosty język

Tekst dla ludzi (dokumenty, maile, podsumowania, raporty) w języku polskim i angielskim spełnia standard
[runtime/procedures/plain-language.md](runtime/procedures/plain-language.md). Standard opiera się na zaleceniach
gov.pl (prosty język), Obserwatorium Językowego UW (korpomowa) i artykule o kalkach składniowych z Magazynu PAN.
Dla angielskiego korzysta z Federal Plain Language Guidelines i GOV.UK Style Guide.

- Najważniejsze na początku, zdania do 20 słów (EN: 25), czasowniki zamiast „dokonać zmiany”.
- Bez korpomowy („zaparkować”, „zaadresować”, „na ten moment”) i kalk składniowych („To, co…, to…”).
- W angielskim bez fałszywych przyjaciół (*actual*, *eventually*, *realize*).

Polecenie executora `plain-check <plik> [--strict] [--lang pl|en] [--audience user]` sprawdza około 60 reguł.
Czyta `.md`, `.txt`, `.docx` i `.pdf`, a terminy projektu bierze ze słownika w `flowkit-project.md`. Tryb roboczy
zgłasza ostrzeżenia, a `--strict` blokuje wynik przy błędach. Kalki są zawsze ostrzeżeniem. Szyk zdania i stronę
bierną ocenia autor oraz verifier w audycie `DOC-AUDIT:`. Redaktor maili i skill dokumentacji rozwiązania sprawdzają
prosty język własnymi skryptami (`check_message.py`, `check_user_docs.py`).

### Infrastruktura

Diagnostics zbiera dowody → DevOps przygotowuje zmianę w plikach → Validator uruchamia statyczne walidatory → użytkownik zatwierdza wdrożenie i wykonuje je sam lub przez zatwierdzony pipeline → Diagnostics sprawdza efekt. Agenci przekazują sobie jeden blok `HANDOFF` z objawami, dowodami, hipotezami, planem walidacji i wynikiem ([devops-loop.md](runtime/procedures/devops-loop.md)).

### Statusy

Wszyscy agenci i raporty używają tych samych statusów: `PASS` (sprawdzone, zaliczone), `FAIL` (sprawdzone, niezaliczone), `NOT_RUN` (nie wykonano - brak narzędzia, dostępu lub warunku wstępnego), `UNKNOWN` (za mało danych), `BLOCKED` (zatrzymane przez brak uprawnień lub zależność).

---

## Konfiguracja

| Ustawienie | Gdzie | Do czego służy |
|---|---|---|
| `flowkit-project.md` | katalog główny projektu | zasady projektu czytane przez orkiestrator na starcie; wzór: [`docs/flowkit-project.template.md`](docs/flowkit-project.template.md) |
| `FLOWKIT_EXTRA_PATHS` | zmienna środowiskowa | dodatkowe katalogi poza projektem, z których agenci mogą czytać (rozdzielone `;` w Windows, `:` w Linux/macOS) |
| `~/.flowkit/allow.json` | katalog domowy (inna ścieżka: `FLOWKIT_ALLOW_FILE`) | polecenia spoza listy roli, które świadomie pozwalasz agentom wykonywać |

Przykład pliku zgód - wpis to początek polecenia, dla wszystkich ról (`"*"`) albo dla jednej roli:

```json
{
  "commands": {
    "*": ["make lint"],
    "orchestrator": ["dotnet build", "terraform plan"],
    "validator": ["checkov -d"]
  }
}
```

Agent wykonuje te polecenia sam, zamiast odsyłać je do czatu. Wpisy otwierające dowolne polecenia (`bash`, `pwsh`, samo `python` lub `node`, `python -c`, `node -e`) są pomijane. Plik jest opcjonalny. Pusty plik ze wszystkimi rolami tworzy `flowkit_doctor.py init` (nigdy nie nadpisuje istniejącego). Wzór: [`docs/allow.example.json`](docs/allow.example.json), schemat dla edytora z podpowiedziami ról: [`docs/allow.schema.json`](docs/allow.schema.json).

### Diagnoza (`doctor`)

| Instalacja | Polecenie |
|---|---|
| wtyczka Claude Code | `/flowkit:doctor` w sesji Claude Code |
| instalator Claude Code | `python ~/.claude/flowkit/runtime/flowkit_doctor.py` |
| VS Code | prompt `/flowkit-doctor` albo `python .github/flowkit/runtime/flowkit_doctor.py` |

`doctor` sprawdza:
- instalację i zgodność wersji runtime, wtyczki i agentów (także starych agentów `agent-3x3*`);
- Python używany przez hooki (w Windows wykrywa alias Microsoft Store);
- plik zgód: składnię z numerem linii, nieznane nazwy ról z podpowiedzią, pominięte wpisy z powodem i uprawnienia pliku;
- zapis dziennika audytu, katalogi z `FLOWKIT_EXTRA_PATHS` i silnik DOCX.

Każdy problem ma podpowiedź „→”. Kod wyjścia 1 oznacza błędy, a `--json` daje wynik do skryptów, `--role <rola>` pokazuje zgody aktywne dla roli. Lista poleceń roli: `flowkit_exec.py --role <rola> -- help`.

```bash
python ~/.claude/flowkit/runtime/flowkit_doctor.py init     # pusty plik zgód (uruchamia tylko użytkownik)
```

Zmienne środowiskowe i plik zgód ustawia tylko użytkownik: hook odrzuca przypisania zmiennych w poleceniach agentów i blokuje im edycję pliku zgód.

---

## Bezpieczeństwo i ograniczenia

**Co jest egzekwowane**

- **Executor z listą dozwoloną dla roli** ([`runtime/flowkit_exec.py`](runtime/flowkit_exec.py)): polecenia bez powłoki, potoków i przekierowań; każda rola ma minimalny zestaw poleceń (`help` je pokazuje).
- **Hook w Claude Code** ([`runtime/guard_bash.py`](runtime/guard_bash.py)): agent FlowKit nie uruchomi polecenia z pominięciem executora i nie zmieni pliku zgód, dziennika audytu, plików runtime, katalogu `.git` (hooki gita uruchamiają kod) ani plików wrażliwych (`.env*` poza `.env.example`, klucze). Ochrona obowiązuje także w katalogach z `FLOWKIT_EXTRA_PATHS`. Zwykłe sesje nie są objęte hookiem.
- **Dziennik audytu**: każde polecenie agenta, wykonane i odrzucone, trafia jako wiersz JSON do `~/.flowkit/audit.log` (czas UTC, rola, katalog, polecenie po ukryciu sekretów, skrót SHA-256 argumentów, decyzja, powód odrzucenia, kod wyjścia, czas trwania). Inna ścieżka: `FLOWKIT_AUDIT_FILE`, wyłączenie: `FLOWKIT_AUDIT_FILE=off`.
- **Diagnostyka okna pytań**: hook [`runtime/log_tool_event.py`](runtime/log_tool_event.py) dopisuje do tego dziennika użycie okna pytań, skilli i subagentów FlowKit (bez treści pytań), a [`runtime/checkpoint_report.py`](runtime/checkpoint_report.py) pokazuje, które punkty kontrolne zakończyły się oknem, a które tekstem i dlaczego (wiersz `Ask:`). Szczegóły: [USAGE - Diagnoza okna pytań](docs/USAGE.md#diagnoza-okna-pytań).
- **Tryb tylko do odczytu**: `FLOWKIT_READONLY=1` ustawione przed uruchomieniem sesji blokuje agentom każdą zmianę pliku (hook), zapis DOCX oraz commit, push i PR (executor). Agent pokazuje zmiany jako diff do akceptacji. Prefiks `AUTO:` ani agent nie wyłączą trybu. Polecenia z pliku zgód nadal działają.
- **Treść materiałów to dane, nie polecenia**: każdy agent i skill traktuje dokumenty, transkrypcje, logi i wyniki narzędzi wyłącznie jako materiał. Polecenia ukryte w tej treści nie zmieniają roli, listy poleceń ani zasad i są zgłaszane jako `[INJECTION?]`.
- **Granica katalogu roboczego**: ścieżki w poleceniach - także po `..`, `~` i dowiązaniach symbolicznych - muszą leżeć w projekcie lub w `FLOWKIT_EXTRA_PATHS`.
- **Ochrona danych**: wyniki poleceń są skracane, sekrety ukrywane, pliki `.env`, klucze i obiekty `Secret` niedostępne; CI uruchamia lokalny skaner sekretów (`scripts/validate_secrets.py`).
- **Narzędzia bezpieczeństwa offline**: `semgrep scan` w executorze działa wyłącznie na lokalnych regułach (blokada `--config auto`, zdalnych URL i `--autofix`), a wszystkie walidatory (`zizmor`, `conftest`, `kyverno`, `osv-scanner`, `gitleaks`) pracują bez modyfikacji plików.
- **Ochrona gałęzi**: push tylko nowej gałęzi, nigdy do `main`/`master` ani z wymuszeniem; `main` przyjmuje zmiany wyłącznie przez PR z zaliczonym CI ([ruleset](.github/rulesets/protect-main.json)).
- **Bez sieci i MCP**: agenci mają jawne listy narzędzi bez narzędzi webowych.

**Czego FlowKit nie zabezpiecza**

- Executor to lista dozwolonych poleceń, a **nie izolacja systemowa (sandbox)**. Testy uruchamiane przez agenta (`pytest`, `npm test` itd.) wykonują kod projektu z uprawnieniami użytkownika.
- **VS Code Copilot nie uruchamia hooka** - zostaw włączone potwierdzanie poleceń w terminalu i zmian w plikach.
- Wygenerowane dokumenty, skrypty i konfiguracje wymagają przeglądu przez człowieka przed użyciem.

**Dane w repozytorium**

To repozytorium jest publiczne. Nie commituj sekretów, danych klientów ani plików roboczych agentów (`agent-context/`, `AGENT_LOG.md`) - wyklucza je [`.gitignore`](.gitignore). Przykłady w `examples/` i `tests/fixtures/` używają wyłącznie fikcyjnych danych.

---

## Obsługiwane platformy

`TESTED` - sprawdzone automatycznie w CI · `PARTIAL` - CI sprawdza pliki, ale nie instalację ani działanie na platformie · `UNVERIFIED` - opis konfiguracji, bez testów.

| Platforma | Skille | Agenci i runtime | Status | Ograniczenia |
|---|---|---|---|---|
| **Claude Code** | `~/.claude/skills/` lub wtyczka | adaptery `agents/adapters/claude-code/`, hook | `PARTIAL` | CI waliduje adaptery, manifest, hook i runtime; instalacja w Claude Code nie jest testowana w CI |
| **VS Code Copilot** | `.github/skills/`, prompty `.github/prompts/` | adaptery `agents/adapters/vscode/` | `PARTIAL` | brak hooka - potwierdzanie poleceń w terminalu |
| **Antigravity** | standard Agent Skills | bundle wtyczki | `UNVERIFIED` | brak testów |
| **Cursor** | `.cursor/rules/<skill>.mdc` | - | `UNVERIFIED` | tylko treść skilli, bez agentów i runtime |
| **ChatGPT / Codex** | Instructions + Knowledge | - | `UNVERIFIED` | tylko treść skilli, bez agentów i runtime |

---

## Instalacja

### Claude Code: wtyczka (zalecane)

Patrz [Szybki start](#szybki-start). Wtyczka instaluje skille, agentów, runtime i hook.

### Claude Code: instalator

```powershell
# Windows: agenci i runtime (~/.claude/agents, ~/.claude/flowkit/runtime)
.\scripts\install.ps1 -AgentName all -Platform claude

# Skille instaluje się pojedynczo (~/.claude/skills)
.\scripts\install.ps1 -SkillName flowkit-client-pt-prd-writer
```

```bash
# Linux / macOS
./scripts/install.sh agent all --platform claude
./scripts/install.sh skill flowkit-client-pt-prd-writer
```

Opcje: `-DryRun` / `--dry-run` (symulacja), `-Force` / `--force` (nadpisanie bez pytania), `-Uninstall` / `--uninstall`, `-TargetPath` / `--target` (instalacja skilla w projekcie, np. `./.claude/skills`), `-SetDefaultAgent` / `--set-default-agent` (orkiestrator domyślnym agentem bieżącego projektu; uruchom w katalogu projektu).

### VS Code Copilot

Uruchom instalator **z katalogu projektu** - agenci trafiają do `.github/agents`, runtime do `.github/flowkit/runtime`, skille do `.github/skills`:

```powershell
& C:\sciezka\do\flowkit\scripts\install.ps1 -AgentName all -Platform vscode
& C:\sciezka\do\flowkit\scripts\install.ps1 -SkillName flowkit-client-pt-prd-writer -Platform vscode
```

Prompty skilli dla Copilot Chat są w [`.github/prompts/`](.github/prompts/) (np. `/flowkit-client-pt-prd-writer`).

### Instalacja ręczna

- Skille: skopiuj `skills/<nazwa>/` do `~/.claude/skills/` (Claude Code) lub `.github/skills/` (VS Code).
- Agenci: skopiuj pliki z `agents/adapters/claude-code/` do `~/.claude/agents/` albo z `agents/adapters/vscode/` do `.github/agents/`, a katalog `runtime/` do `~/.claude/flowkit/runtime` lub `.github/flowkit/runtime`.
- Cursor i ChatGPT: wklej treść `SKILL.md` do reguł (`.cursor/rules/<nazwa>.mdc`) albo do Instructions, a szablony i checklisty dołącz jako pliki.

---

## Aktualizacja z wersji 1.7

1. Zainstaluj ponownie agentów i runtime (`-AgentName all`) oraz potrzebne skille - runtime zawiera nowe zabezpieczenia i polecenia.
2. **Usuń stare katalogi skilli bez prefiksu** `flowkit-` (np. `~/.claude/skills/client-pt-prd-writer`, `.github/skills/client-meeting-recap`), inaczej skille będą widoczne podwójnie.
3. **Usuń starych agentów `agent-3x3*`** (`~/.claude/agents/agent-3x3*.md`, `.github/agents/agent-3x3*.agent.md`). Nowe nazwy:

   | Wersja 1.7 | Wersja 1.8 |
   |---|---|
   | `agent-3x3` | `flowkit-orchestrator` |
   | `agent-3x3-analyst` | `flowkit-analyst` |
   | `agent-3x3-analyzer` | `flowkit-code-analyzer` |
   | `agent-3x3-planner` | `flowkit-planner` |
   | `agent-3x3-pm` | `flowkit-product-owner` |
   | `agent-3x3-implementer` | `flowkit-implementer` |
   | `agent-3x3-verifier` | `flowkit-verifier` |
   | `agent-3x3-devops` | `flowkit-devops` |
   | `agent-3x3-diagnostics` | `flowkit-diagnostics` |
   | `agent-3x3-validator` | `flowkit-validator` |

   Polecenie startowe to teraz `claude --agent flowkit-orchestrator`. Do czasu usunięcia starzy agenci są nadal chronieni przez hook nowego runtime (zgodność wsteczna tylko w wersji 1.8).
4. Agenci czytają teraz tylko pliki z katalogu projektu. Materiały z innych miejsc skopiuj do projektu albo ustaw `FLOWKIT_EXTRA_PATHS`.
5. Polecenia, które agenci mają wykonywać sami (np. budowanie projektu), dopisz do pliku zgód.

Pełna lista zmian: [CHANGELOG.md](CHANGELOG.md).

---

## Rozwiązywanie problemów

| Komunikat | Przyczyna | Co zrobić |
|---|---|---|
| `ODRZUCONO: polecenie niedozwolone dla roli …` | polecenia nie ma na liście roli | jeśli ma je wykonywać agent, dopisz podany prefiks do pliku zgód; komunikat wskazuje też role, którym wolno je uruchomić |
| `ODRZUCONO: ścieżka poza katalogiem roboczym` | plik leży poza projektem | skopiuj plik do projektu albo dopisz katalog do `FLOWKIT_EXTRA_PATHS` |
| `BRAK NARZĘDZIA: … (status: NOT_RUN)` | narzędzie nie jest zainstalowane | zainstaluj je (patrz [Wymagania](#wymagania)) i powtórz krok |
| `BRAK SILNIKA DOCX` (kod 3) | brak `python-docx` i Pandoc | `pip install python-docx` |
| `KONTROLA: FAIL` (kod 4) | DOCX zapisany, ale jego struktura nie zgadza się ze źródłem | sprawdź ostrzeżenia (brakujące obrazy, nagłówki spoza stylów szablonu) przed oddaniem dokumentu |
| diagram mermaid jako blok kodu | brak lokalnego mermaid-cli | `npm install -g @mermaid-js/mermaid-cli` |
| `FlowKit zablokował zmianę pliku` | agent próbował zmienić plik zgód lub runtime | te pliki zmienia tylko użytkownik |
| zgoda z `allow.json` nie działa | błąd składni, literówka w nazwie roli albo wpis pominięty (np. `bash`) | uruchom `doctor`: pokaże linię błędu, podpowie nazwę roli i powód pominięcia |
| `doctor`: „Python dla hooków” - BŁĄD | `python` nie istnieje w PATH albo to alias Microsoft Store | zainstaluj Pythona z python.org z opcją „Add python.exe to PATH” i wyłącz alias w ustawieniach Windows |
| `doctor`: „Agenci” - UWAGA (inna wersja) | agenci i runtime pochodzą z różnych wersji | zainstaluj ponownie agentów i runtime (`-AgentName all` / `agent all`) |
| pytania zwykłym tekstem, `Ask: text — tool not in this agent's tool list` | zainstalowany orkiestrator jest starszy i nie ma narzędzia okna pytań | uruchom `doctor` - wiersz „Okno pytań” poda polecenie ponownej instalacji |
| `read-document` odrzucone w audycie `DOC-AUDIT:` | stary runtime bez `read-document` dla roli `verifier` | zainstaluj ponownie agentów i runtime; nie dopisuj poleceń wbudowanych do pliku zgód |
| w VS Code na liście agentów są `agent-3x3*` | starzy agenci z wersji 1.7 | usuń `.github/agents/agent-3x3*.agent.md` (patrz [Aktualizacja](#aktualizacja-z-wersji-17)) |

---

## Rozwój i współtworzenie

```bash
pip install pyyaml python-docx
python scripts/validate_all.py      # skille, agenci, manifesty i testy jednostkowe (to samo uruchamia CI)
python scripts/build_agents.py      # po każdej zmianie agents/*_agent.md
python scripts/run_evals.py triggers --dry-run   # scenariusze aktywacji skilli
```

Ewaluacja z lokalnym Claude Code (`run_evals.py` bez `--dry-run`) ma limity czasu `--timeout` (scenariusz, 600 s) i `--total-timeout` (sesja, 3600 s), zapisuje wyniki po każdym scenariuszu i rozróżnia błędy jakości (`FAIL`) od błędów infrastruktury (`TIMEOUT`, `ERROR`, `SKIPPED`).
Ta ewaluacja jest opcjonalna i wymaga działającego Claude Code. Skille, `plain-check` i skrypty kontrolne działają
lokalnie, bez sieci i bez API.

**Ocena bez API:** zapisz odpowiedź skilla w pliku i oceń ją lokalnie:

```bash
python scripts/grade_eval.py message-editor-plain-pl odpowiedz.md   # wzorce scenariusza z tests/evals/cases.yaml
python runtime/plain_language.py odpowiedz.md --strict               # reguły prostego języka
```

Wzorcowe odpowiedzi scenariuszy prostego języka leżą w `tests/fixtures/plain_language/golden/`. Testy sprawdzają
offline, że wzorzec przechodzi wszystkie kontrole, a szkic nie.

**Nowy skill**

1. Skopiuj [`skills/_template/`](skills/_template/) do `skills/flowkit-<nazwa>/` (prefiks `flowkit-` jest wymagany).
2. Zmień `SKILL.template.md` na `SKILL.md` i uzupełnij nagłówek YAML: `name` (równy nazwie katalogu), `version`, `tags` (co najmniej 3), `description`.
3. Dodaj `CHANGELOG.md`, `templates/` i `checklists/` (co najmniej jeden plik `.md` w każdym), opcjonalnie `examples/` i `references/`.
4. Dopisz skill do tabeli w sekcji [Skille](#skille), do instalatorów i do `tests/evals/triggers.yaml`.
5. Uruchom `python scripts/validate_all.py` i zgłoś zmianę przez Pull Request.

**Zasady repozytorium**

- Zmiany tylko przez Pull Request z gałęzi `feat/*`, `fix/*` lub `docs/*`; bezpośredni push do `main` jest zablokowany.
- Przykłady i dane testowe są fikcyjne; żadnych sekretów ani danych klientów w commitach.
- Konwencje pracy, commitów i gałęzi: [DEVELOPMENT.md](DEVELOPMENT.md), [CONTRIBUTING.md](CONTRIBUTING.md).

---

Skille i agenci generują treści, które wymagają weryfikacji przez człowieka. Repozytorium jest udostępniane „as is”, na licencji [MIT](LICENSE).
