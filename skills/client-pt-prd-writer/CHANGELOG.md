# Historia zmian skilla client-pt-prd-writer

## 2.3 (18.11.2026)

### Silnik diagramów
- Nowy Etap 5a: ocena potrzeby, plan, model pośredni YAML, generowanie, walidacja i osadzanie diagramów.
- 15 typów diagramów, 3 motywy oraz kolor i czcionka pobierane z szablonu klienta.
- Eksport SVG, PNG i HTML; osadzanie w DOCX i Markdown z numeracją, podpisem i tekstem alternatywnym.
- Każdy element diagramu ma oznaczenie pochodzenia; niewiadome są widoczne na grafice i blokują tryb końcowy.
- Ponowne generowanie pojedynczego diagramu bez przebudowy dokumentu.

### Polskie nazwy w tabelach
- Nowy słownik `references/status-vocabulary.md` (m.in. `Must` → `Wymagane`) i kontrola `scripts/check_status_labels.py`.

## 2.2 (14.11.2026)

### Tryb „Dokument końcowy bez dopisków”
- Nowy, opcjonalny tryb wyniku (na wyraźną prośbę użytkownika): pełny dokument dokładnie w udostępnionym szablonie, bez oznaczeń SRC / ASSUMPTION / OPEN / DO POTWIERDZENIA, kolumn „Źródło” i sekcji dodawanych przez skill.
- Zasada „brak źródła = brak treści” bez zmian: pochodzenie prowadzone w rejestrze pochodzenia poza dokumentem; luki rozstrzyga użytkownik (uzupełnienie / zatwierdzenie / pominięcie / neutralne sformułowanie).
- Ujednolicone oznaczenie pochodzenia: `SRC-NNN` (dla kodu dodatkowo `plik:linia`) zamiast `ŹRÓDŁO: <...>` — zgodnie z szablonem i promptem Copilota.
- Szablon zapasowy: poprawiona numeracja podsekcji 21.1 / 21.2; usunięty nietrafny tag `blameless`.
- Etap 0: wybór trybu wyniku; nowa sekcja F w checkliście końcowej; uzupełnione `references/template-mapping.md` i prompt Copilota.

## 2.1 (11.11.2026)

### Ulepszenia standardu rynkowego (QA & Dev alignment)
- Dodano format scenariuszy akceptacyjnych **Given-When-Then (Gherkin)** w User Stories.
- Wprowadzono sekcję **Definition of Done (DoD)** z kryteriami ukończenia zmiany.
- Rozszerzono sekcję wyłączeń o jawne **Anty-cele (Non-Goals)** przeciw Scope Creep.
- Dodano zasadę izolacji kontekstu z tagami XML (`<source_materials>`, `<user_template>`).
- Zaktualizowano checklistę końcową o weryfikację DoD i Given-When-Then.

## 2.0 (10.11.2026)

### Praca na szablonie użytkownika
- Nowy Etap 0: szablon użytkownika (.docx/.dotx/.md/.pdf lub wzorcowy dokument) ma pierwszeństwo; zachowanie struktury, numeracji, stylów, metryczki.
- Nowy plik `references/template-mapping.md` – jak odczytać szablon, zmapować sekcje i wypełnić go bez placeholderów.
- Szablon w `templates/` oznaczony jako zapasowy.

### Brak zmyślania
- Zasady nadrzędne: „brak źródła = brak treści”, oznaczenia SRC / ASSUMPTION / OPEN / DO POTWIERDZENIA dla każdego wpisu.
- Rejestr źródeł (SRC-NNN) i sekcja „Materiały źródłowe”.
- Kolumna „Źródło” w tabelach FR, US, NFR, INT, DATA, RISK, CHG, zakresu.
- Priorytety, właściciele, terminy, miary – wyłącznie ze źródła.
- Sekcje warunkowe zamiast 20 obowiązkowych; „Nie dotyczy” / „Brak danych”.
- Tryb bez dostępu do kodu („Nie analizowano”).
- Usunięty przykładowy diagram mermaid; diagram tylko z przeanalizowanych komponentów.
- Sekcja „Rekomendacje” oddziela propozycje autora od wymagań.
- Nowy przykład `examples/sourced-vs-invented.md`.
- Test pochodzenia treści w checkliście końcowej.

### Spójność
- Ujednolicone ID (trzycyfrowe) w SKILL.md, szablonie i przykładach.
- Lista obszarów w SKILL.md zgodna z szablonem.
- Tabela FR z kolumnami źródło i status (wcześniej wymagane, a nieobecne w szablonie).
- Dodane: Historia zmian, Materiały źródłowe, Słownik pojęć, Założenia (ASSUMPTION).
- Kolumna „Data decyzji” w Tematach do wyjaśnienia.

### Proces
- Pytania tylko blokujące i dotyczące tej zmiany; propozycje domyślne tylko bezpieczne i oznaczane jako ASSUMPTION.
- Możliwość wersji roboczej na żądanie (luki jako OPEN, bez zgadywania).
- Streszczenie zarządcze pisane na końcu, bez nowych faktów.
