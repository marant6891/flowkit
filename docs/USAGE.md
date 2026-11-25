# FlowKit w praktyce — gotowe polecenia

Ten przewodnik pokazuje, **jak sformułować polecenie**, żeby FlowKit od razu dał użyteczny wynik: jakie źródła wskazać,
co doprecyzować i czego się spodziewać na końcu. Każdy skill ma polecenie minimalne (działa, ale skill dopyta) i
optymalne (skill od razu wie, co robić).

Spis treści:

1. [Zanim zaczniesz](#1-zanim-zaczniesz)
2. [Budowa dobrego polecenia](#2-budowa-dobrego-polecenia)
3. [PT/PRD dla klienta](#3-ptprd-dla-klienta--flowkit-client-pt-prd-writer)
4. [Podsumowanie spotkania](#4-podsumowanie-spotkania--flowkit-client-meeting-recap)
5. [Postmortem po incydencie](#5-postmortem-po-incydencie--flowkit-devops-incident-postmortem)
6. [Przegląd SRE](#6-przegląd-sre--flowkit-devops-sre-review)
7. [SQL i poprawa danych](#7-sql-i-poprawa-danych--flowkit-sql-data-assistant)
8. [Agenci i prefiksy](#8-agenci-i-prefiksy-orkiestratora)
9. [Scenariusze łączone](#9-scenariusze-łączone)
10. [Gdy wynik nie jest taki, jak trzeba](#10-gdy-wynik-nie-jest-taki-jak-trzeba)

---

## 1. Zanim zaczniesz

**Uruchom orkiestrator w katalogu projektu** — on dobiera skill lub agenta i pilnuje weryfikacji:

```bash
claude --agent flowkit:flowkit-orchestrator
```

Skill można też wywołać bez orkiestratora: Claude Code uruchamia go sam, gdy prośba pasuje do opisu skilla.
W VS Code Copilot wybierz plik promptu z `.github/prompts/` (np. `/flowkit-client-pt-prd-writer`).

**Materiały trzymaj w projekcie.** Agenci czytają tylko katalog, w którym ich uruchomiono. Wygodny układ:

```text
projekt/
├── materialy/        # źródła: brief, notatki, eksporty Jira/Confluence, transkrypcje, logi
├── szablony/         # szablon klienta (.docx/.dotx/.md)
├── wynik/            # tu proś o zapis dokumentów
└── flowkit-project.md  # opcjonalnie: stałe zasady projektu (wzór: docs/flowkit-project.template.md)
```

Materiały spoza projektu skopiuj do `materialy/` albo dopisz ich katalog do zmiennej `FLOWKIT_EXTRA_PATHS`
przed uruchomieniem sesji. Stan środowiska (Python, biblioteki DOCX, zgody, tryby) sprawdzisz poleceniem:

```bash
python ~/.claude/flowkit/runtime/flowkit_exec.py --role orchestrator -- doctor
```

**Chcesz najpierw zobaczyć, co agent zmieni?** Uruchom sesję z `FLOWKIT_READONLY=1`. Agenci nie zmienią wtedy
żadnego pliku i pokażą zmiany jako diff.

---

## 2. Budowa dobrego polecenia

Optymalne polecenie odpowiada na sześć pytań. Każde, którego nie ma, skill zada sam (najwyżej kilka pytań
blokujących) albo zapisze lukę jako `OPEN-NNN`.

| Element | Przykład | Po co |
|---|---|---|
| **Co** | „Przygotuj PT dla zmiany eksportu faktur” | wybór skilla i zakresu |
| **Źródła** | „Źródła: `materialy/brief.docx`, `materialy/jira-PROJ-142.md`, kod w `src/billing/`” | tylko z nich powstaje treść |
| **Źródło nadrzędne** | „Przy sprzecznościach wygrywa `brief.docx`” | rozstrzyganie sprzeczności bez zgadywania |
| **Wykluczenia** | „Nie cytuj `notatki-wewnetrzne.md`” | ochrona danych poufnych |
| **Wynik** | „Word w szablonie `szablony/klient.dotx`, wersja dla klienta, zapis do `wynik/`” | format, odbiorca i miejsce zapisu |
| **Tryb pracy** | `AUTO:` (bez pytań), `DRY:` (najpierw plan), `STRICT:` (produkcja) | ile decyzji podejmujesz sam |

Wzór do skopiowania:

```text
<CO zrobić>.
Źródła: <pliki i katalogi>. Źródło nadrzędne przy sprzecznościach: <plik>. Nie używaj: <pliki>.
Wynik: <format, szablon, odbiorca, ścieżka zapisu>.
<Dodatkowe ograniczenia: termin, język, profil stylu, długość>.
```

Czego **nie** pisać: „uzupełnij brakujące sekcje typowymi treściami”, „wymyśl przykładowe wymagania”. FlowKit
celowo tego nie zrobi — brak źródła daje `DO POTWIERDZENIA` i `OPEN-NNN`, a nie treść.

---

## 3. PT/PRD dla klienta — `flowkit-client-pt-prd-writer`

**Kiedy:** projekt techniczny, PRD, specyfikacja zmiany, change request, analiza wpływu.

**Minimalne polecenie:**

```text
Przygotuj dokument PT na podstawie materiałów z folderu materialy/.
```

**Optymalne polecenie:**

```text
Przygotuj dokument PT dla zmiany „Eksport faktur do KSeF”.
Źródła: materialy/brief-ksef.docx, materialy/jira-PROJ-142.md, materialy/spotkanie-2026-11-15.vtt,
kod w src/billing/ i schemat bazy materialy/schema.sql.
Źródło nadrzędne przy sprzecznościach: brief-ksef.docx. Nie cytuj materialy/notatki-wewnetrzne.md.
Szablon: szablony/PT-klient.dotx. Wynik: wersja dla klienta, zapis do wynik/PT-KSeF.docx.
Wariant pełny, z diagramem przepływu i sekwencji integracji.
```

**Tryby wyniku** — wskaż wprost, inaczej powstaje wersja robocza:

| Napisz | Dostajesz |
|---|---|
| (nic) | **roboczy**: przy każdym zapisie oznaczenie pochodzenia (`SRC-NNN`, `ASSUMPTION-NNN`, `OPEN-NNN`); dla zespołu |
| „wersja dla klienta”, „do wysłania klientowi” | czysta treść, wszystkie wątpliwości w końcowym rozdziale „Kwestie do wyjaśnienia” (`K-NN`) |
| „wersja końcowa bez dopisków” | czysta treść dokładnie w szablonie; otwarte kwestie musisz rozstrzygnąć wcześniej |

**Przebieg i wynik:**

1. Skill pyta jednym blokiem o źródła (jeśli ich nie podałeś), źródło nadrzędne i wykluczenia.
2. Przed pisaniem pokazuje, jak rozumie zmianę, wariant (skrócony 1–3 strony albo pełny), plan sekcji i diagramów
   oraz pytania. **Tu poprawiasz zakres** — to najtańszy moment.
3. Oddaje `.docx` w stylach szablonu (nagłówki, stopki, numeracja, tabele) albo `.md`, gdy szablonu nie ma.
4. Pod wynikiem: lista luk pokrycia (wymagania bez testów), przyjęte założenia i — po orkiestratorze — wynik
   niezależnego audytu `DOC-AUDIT:` (źródła, sprzeczności `CONTRADICTION-NNN`, styl).

**Wariant bez pytań:** `AUTO: Przygotuj PT ...` — skill przyjmuje rekomendacje i oddaje na końcu rejestr decyzji AUTO
do potwierdzenia.

---

## 4. Podsumowanie spotkania — `flowkit-client-meeting-recap`

**Kiedy:** transkrypcja (`.vtt` z Teams/Zoom/Meet, `.docx`, `.txt`) lub notatki → notatka i mail do klienta.

**Minimalne polecenie:**

```text
Podsumuj spotkanie z pliku materialy/spotkanie.vtt i przygotuj mail do klienta.
```

**Optymalne polecenie:**

```text
Podsumuj spotkanie z materialy/2026-11-15-ksef.vtt (spotkanie z 15.11.2026, projekt KSEF).
Po stronie klienta: Anna Nowak, Piotr Wiśniewski. Nasz zespół: Jan Kowalski, Ewa Lis.
Ton maila: semi-formalny („Dzień dobry Anno”). Okno na korekty: 72 godziny.
Wzór maila: szablony/mail-podsumowanie.md. Zapisz wynik w wynik/.
```

Podanie **daty spotkania** pozwala zamienić „do środy” na datę. Podanie **ról uczestników** zapobiega wpisom
`DO POTWIERDZENIA` w polu „Klient / Nasz zespół”.

**Wynik — zawsze dwa osobne pliki:**

| Plik | Dla kogo | Zawartość |
|---|---|---|
| `recap-2026-11-15-KSEF-wewnetrzne.md` | zespół | radar ryzyk: nastroje, scope creep, blokady — każdy wpis z cytatem i znacznikiem czasu |
| `recap-2026-11-15-KSEF-klient.md` | klient | decyzje, zadania z właścicielem tylko z dowodem, terminy, prośba o korekty w oknie |

Hasła, tokeny, PESEL i podobne dane są zastępowane `[UKRYTO]` — pod wynikiem dostajesz ich liczbę.

**Wypróbuj na danych testowych:**

```text
Podsumuj spotkanie z tests/fixtures/transcripts/sample_meeting.vtt i przygotuj mail do klienta.
```

---

## 5. Postmortem po incydencie — `flowkit-devops-incident-postmortem`

**Kiedy:** po awarii — logi, alerty, zapis rozmów z kanału incydentowego → raport blameless.

**Minimalne polecenie:**

```text
Przygotuj postmortem incydentu na podstawie logów z materialy/incydent/.
```

**Optymalne polecenie:**

```text
Przygotuj postmortem incydentu INC-2291 (brak płatności kartą, 14.11.2026).
Źródła: materialy/incydent/api-gateway.log, materialy/incydent/alerty-pagerduty.json,
materialy/incydent/kanal-incydent.txt (eksport Slack), materialy/incydent/status-page.md.
Wpływ znany z raportu biznesowego: materialy/incydent/wplyw.xlsx. SLA: 99,9% miesięcznie.
Szablon: szablony/postmortem.docx. Zapis: wynik/postmortem-INC-2291.docx.
```

**Wynik:** raport w szablonie (lub zapasowym): klasyfikacja SEV, oś czasu T0–T4 z TTD/TTR wyliczonymi ze znaczników
w logach, łańcuch przyczyn (Trigger, Amplifier, luki wykrycia i procesu, 5 Whys), komunikacja i Status Page oraz
działania naprawcze PREVENT/DETECT/MITIGATE z właścicielem i terminem. Język bez obwiniania osób; brakujące czasy
i wpływ są `DO POTWIERDZENIA`, a nie szacunkiem.

**Wypróbuj:** `Przygotuj postmortem na podstawie tests/fixtures/incident-scenarios/sample_incident.log.`

---

## 6. Przegląd SRE — `flowkit-devops-sre-review`

**Kiedy:** ocena gotowości produkcyjnej usługi: SLO, alerty, sondy, zasoby, skalowanie, backup. (Do raportu po awarii
użyj postmortemu, a do pisania nowej konfiguracji — `DEVOPS:`.)

**Minimalne polecenie:**

```text
Zrób przegląd SRE usługi z katalogu k8s/.
```

**Optymalne polecenie:**

```text
Zrób przegląd SRE usługi payments-api przed wejściem na produkcję.
Źródła: k8s/payments/ (manifesty), charts/payments/ (Helm), monitoring/alerts/payments.yaml,
monitoring/dashboards/payments.json, docs/architektura.md.
Wymagania: SLA 99,9%, RPO 15 min, RTO 1 h (z umowy: materialy/umowa-sla.pdf, §4).
Skup się na alertach i backupie. Raport do wynik/sre-payments.md.
```

**Wynik:** zwięzły raport z ustaleniami `PASS`/`FAIL`/`UNKNOWN`/`NOT_RUN` i dowodem `plik:linia`, interpretacje
oddzielone od faktów, rekomendacje monitoringu z sygnałem, progiem, oknem i uzasadnieniem. Backup bez testu odtworzenia
nie dostaje `PASS`. Bez podanych wymagań SLA trafiają one do „Brak danych”.

**Wypróbuj:** `Zrób przegląd SRE manifestu tests/fixtures/k8s/bad-deployment.yaml.`

---

## 7. SQL i poprawa danych — `flowkit-sql-data-assistant`

**Kiedy:** zestawienie, sprawdzenie danych ze zgłoszenia, skrypt poprawy. Skill **nigdy nie łączy się z bazą** —
przygotowuje skrypt i instrukcję dla osoby, która go uruchomi.

**Minimalne polecenie:**

```text
SQL: przygotuj zapytanie, które pokaże zamówienia bez faktury.
```

**Optymalne polecenie:**

```text
SQL: zgłoszenie SD-4471, PostgreSQL 15, środowisko produkcyjne.
Schemat: materialy/schema.sql (tabele orders, invoices).
Problem: zamówienia ze statusem PAID z 10–12.11.2026 nie mają faktury.
Tryb: DATA_REPAIR — najpierw zapytanie diagnostyczne, potem skrypt ustawiający status INVOICE_PENDING.
Oczekiwana liczba rekordów: 37 (z raportu w zgłoszeniu). Skrypt uruchomi tester — potrzebna prosta instrukcja.
```

| Tryb | Dostajesz |
|---|---|
| `READ_ONLY` | `SELECT` z limitem lub agregacją |
| `DATA_INVESTIGATION` | zapytania diagnostyczne: liczba rekordów, przykładowe ID, opis zakresu |
| `DATA_REPAIR` | najpierw diagnoza, potem skrypt w transakcji: kontrola liczby rekordów (przerwanie przy rozbieżności), zachowanie poprzednich wartości, domyślne `ROLLBACK`, skrypt odtworzenia |

Podanie **typu bazy** i **oczekiwanej liczby rekordów** to dwie najważniejsze informacje — bez nich skill zapyta.
Nieznane triggery i klucze obce są wypisywane jako niewiadome.

**Wypróbuj:** `SQL: SQL Server, schemat tests/fixtures/sql/sample_schema.sql. Policz klientów w tabeli sprzedaz.klient według statusu (READ_ONLY).`

---

## 8. Agenci i prefiksy orkiestratora

Prefiks wpisujesz na początku polecenia; można je łączyć (`AUTO: BA: ...`, `SPEC: PLAN: ...`).

| Cel | Polecenie | Wynik |
|---|---|---|
| Wymagania, procesy, backlog, przypadki testowe | `BA: przygotuj backlog z przypadkami testowymi Given-When-Then z materialy/wymagania.docx. Źródło nadrzędne: wymagania.docx.` | tabela wymagań, konflikty, luki, pytania do klienta, rodzaj każdego stwierdzenia (fakt / interpretacja / założenie) |
| User stories przed implementacją | `SPEC: PLAN: dodaj eksport CSV raportu sprzedaży (src/reports/).` | `US-N` + `AC-N`, potem plan iteracji odwołujący się do nich |
| Testy UI i audyt bezpieczeństwa aplikacji | `QA: sprawdź formularz rejestracji (src/web/register/) — scenariusze manualne i audyt OWASP.` | scenariusze testów frontu + ustalenia OWASP z `plik:linia` i sposobem naprawy |
| Przegląd kodu | `VERIFY: sprawdź zmiany w src/billing/ względem US-3 i US-4.` | 9 wymiarów, `PASS` tylko z dowodem (wynik testów), `[NOT VERIFIED]` gdy testów brak |
| Niezależny audyt dokumentu | `VERIFY: DOC-AUDIT: wynik/PT-KSeF.docx, źródła w materialy/.` | pokrycie w źródłach, sprzeczności `CONTRADICTION-NNN`, styl; orkiestrator robi to sam po skillach dokumentowych |
| Konfiguracja DevOps | `DEVOPS: przygotuj Dockerfile i workflow CI dla aplikacji z src/api/ i zwaliduj je.` | pliki + walidacja (`hadolint`, `actionlint`) przez Validatora, wdrożenie tylko za zgodą |
| Diagnoza bez zmian | `DIAG: dlaczego pody payments-api restartują się? Namespace prod.` | odczyt logów i stanu (tylko odczyt), prawdopodobna przyczyna, kroki wymagające zgody |
| Najpierw plan | `DRY: zmień limit pamięci w k8s/payments/deployment.yaml na 1Gi.` | plan do 3 kroków, czeka na potwierdzenie |
| Dostarczenie | `SHIP: przygotuj PR ze zweryfikowanych zmian.` | gałąź, commit, push, PR — po weryfikacji i Twojej zgodzie |
| Całość bez pytań | `AUTO: ...` | praca na rekomendacjach + lista przyjętych decyzji do potwierdzenia |
| Produkcja, migracje, uprawnienia | `STRICT: ...` | zgoda przed każdym ryzykownym krokiem, weryfikacja po każdej zmianie, plan wycofania |

---

## 9. Scenariusze łączone

**Od spotkania do dokumentu dla klienta:**

```text
1. Podsumuj spotkanie z materialy/2026-11-15-ksef.vtt (projekt KSEF), wynik do wynik/.
2. Przygotuj PT dla zmiany „Eksport faktur do KSeF”. Źródła: materialy/brief-ksef.docx
   i wynik/recap-2026-11-15-KSEF-wewnetrzne.md. Źródło nadrzędne: brief. Szablon: szablony/PT-klient.dotx.
   Wersja robocza.
3. (po odpowiedziach klienta na OPEN-NNN) Przygotuj wersję dla klienta do wynik/PT-KSeF-klient.docx.
```

**Od wymagań do kodu z weryfikacją:**

```text
SPEC: PLAN: LOG: zaimplementuj eksport CSV raportu sprzedaży zgodnie z materialy/wymagania-raporty.md.
```

Orkiestrator: PM (`US-N`/`AC-N`) → Planner → Implementer → Verifier, iteracje w `AGENT_LOG.md`; na koniec
`SHIP:`, jeśli chcesz PR.

**Incydent od diagnozy do postmortemu:**

```text
1. DIAG: sprawdź logi payments-api z ostatnich 2 godzin, namespace prod.
2. Przygotuj postmortem INC-2291 na podstawie wyniku diagnozy i materialy/incydent/.
```

---

## 10. Gdy wynik nie jest taki, jak trzeba

| Objaw | Co zrobić |
|---|---|
| Dużo `OPEN-NNN` / `DO POTWIERDZENIA` | to luki w źródłach, nie błąd. Dodaj materiał albo odpowiedz na pytania i poproś: „Uzupełnij OPEN-003 i OPEN-007 na podstawie odpowiedzi: …” |
| Skill dopisał coś, czego nie ma w źródłach | „Wskaż źródło dla FR-004” — zdanie bez źródła zostanie usunięte albo zamienione na OPEN |
| `CONTRADICTION-NNN` w audycie | wskaż źródło nadrzędne: „Przy sprzecznościach wygrywa brief-ksef.docx” |
| „ścieżka poza katalogiem roboczym” | skopiuj plik do projektu albo dodaj katalog do `FLOWKIT_EXTRA_PATHS` i uruchom sesję ponownie |
| „polecenie niedozwolone dla roli” | agent poda linię do dopisania w `~/.flowkit/allow.json`; dopisz ją sam, jeśli się zgadzasz |
| Word bez stylów szablonu / Markdown zamiast DOCX | uruchom `doctor` — brakuje silnika DOCX (`python-docx` lub Pandoc); instrukcja jest w komunikacie |
| Dokument za długi | „Wariant skrócony” albo „Zmieść się w 3 stronach” |
| `[INJECTION?]` pod wynikiem | materiał zawierał polecenia dla asystenta — sprawdź wskazany fragment; agent ich nie wykonał |

Pełna lista ustawień: [README — Konfiguracja](../README.md#konfiguracja). Co i jak jest zabezpieczone:
[README — Bezpieczeństwo](../README.md#bezpieczeństwo-i-ograniczenia).
