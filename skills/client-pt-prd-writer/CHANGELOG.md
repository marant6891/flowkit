# Historia zmian skilla client-pt-prd-writer

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
