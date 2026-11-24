# Historia zmian skilla flowkit-client-pt-prd-writer

## 3.1 (24.11.2026)

### Styl sekcji technicznych i zakaz bagatelizowania nakładu
- Dodano profil stylu sekcji technicznych: **biznesowy**, **zrównoważony** *(domyślny)* oraz **techniczny**, żeby uniknąć zbyt „maszynowego” opisu przy jednoczesnym zachowaniu precyzji.
- Wprowadzono zakaz sformułowań bagatelizujących pracochłonność i sugerujących tanie reużycie (*„proste”*, *„wystarczy”*, *„gotowa podstawa”*, *„drobna zmiana”*) — zamiast nich neutralny opis stanu i zakresu potrzebnych prac (dostosowanie, konfiguracja, obsługa błędów, testy regresyjne).
- Rozszerzono `examples/sourced-vs-invented.md` oraz `checklists/final-review-checklist.md` (sekcja E1).

## 3.0 (23.11.2026)

### Wersja dla klienta
- Nowy tryb wyniku: czysta treść bez oznaczeń źródeł, identyfikatorów roboczych i „DO POTWIERDZENIA” — także w tabelach, streszczeniu i podsumowaniach.
- Wszystkie wątpliwości w ostatnim rozdziale „Kwestie do wyjaśnienia” (K-NN) oraz „Przyjęte założenia do potwierdzenia” (Z-NN); w treści tylko odwołanie „Do ustalenia (K-NN)”.
- Pochodzenie treści w rejestrze poza dokumentem, z mapowaniem K-NN ↔ OPEN-NNN.
- Skrypt `check_client_version.py` (`--mode client|final`) wykrywa pozostawione dopiski w DOCX i Markdown oraz odwołania bez punktu w sekcji końcowej.

## 2.9 (20.11.2026)

- Kontrola pokrycia w wariancie pełnym: wymagania bez testu i testy bez wymagania są zgłaszane, bez fikcyjnych powiązań.
- Wnioski spoza źródeł są oznaczane jako interpretacja; zakaz wnioskowania o zachowaniu systemu z samych nazw.

## 2.8 (20.11.2026)

### Wariant skrócony dla małych zmian
- Nowy szablon `client-pt-prd-compact-template.md`: 6 rozdziałów, 1–3 strony, listy zamiast tabel.
- Bez szablonu użytkownika skill sam wybiera wariant: skrócony dla zmian do 3 wymagań w jednym obszarze, bez integracji, migracji, uprawnień i architektury; pełny dla pozostałych.
- Tabela tylko przy co najmniej 3 wierszach; 1–2 elementy jako lista. Bez osobnych tabel dla każdego typu identyfikatora.
- W szablonie użytkownika przy małej zmianie: „Nie dotyczy.” i po kilka punktów w pozostałych sekcjach.

## 2.7 (20.11.2026)

### Zwięzłość dokumentu
- Nowa zasada zwięzłości z orientacyjną objętością zależną od wielkości zmiany (2–4, 4–8, do 15 stron).
- Każda informacja raz: kryteria akceptacji nie są powielane w FR, US, testach i macierzy; plan testów odwołuje się do scenariuszy US.
- Szablon zapasowy: niedotyczące sekcje warunkowe są pomijane i wymieniane jednym zdaniem; US jako zwarta tabela Given-When-Then; DoD bez ogólnych formułek; krótsze tabele OPEN i ASSUMPTION; macierz śledzenia od 6 FR.
- Etap 6 zawiera test zwięzłości, a checklista końcowa sekcję E2.

## 2.6 (19.11.2026)

### Zapis DOCX zgodny z szablonem
- Dokument powstaje przez `md-to-docx` na kopii szablonu klienta: komplet stylów, numeracja, nagłówki, stopki i motyw.
- `--template` zachowuje treść szablonu i wstawia dokument w miejsce `[[FLOWKIT:TREŚĆ]]`.
- Diagramy mermaid i SVG trafiają do DOCX jako PNG, bez wymagania `rsvg-convert`.

### Źródła danych i tryb AUTO
- Na początku pracy skill pyta o znane źródła danych do przygotowania i weryfikacji dokumentu.
- Tryb `AUTO:` realizuje całość na rekomendacjach i oddaje rejestr przyjętych decyzji.

## 2.5 (18.11.2026)

### Krytyczny przegląd
- Etap 6 zaczyna się od przeglądu przypadków brzegowych, sprzeczności, sprawdzalności wymagań i ukrytych założeń.

## 2.4 (18.11.2026)

### Obraz tylko z potwierdzonymi informacjami
- Na grafice są wyłącznie elementy potwierdzone źródłem `SRC-NNN`; niepewna treść jest odrzucana.
- Niewiadome i założenia trafiają do akapitu „Uwagi do rysunku” pod grafiką.

### Dobór diagramów
- Obowiązkowa ocena procesów, przepływów, komunikacji, integracji i relacji między systemami lub komponentami.
- Mierzalne kryteria dla każdego typu diagramu, także dla komunikacji dwóch systemów.
- Plan zawiera decyzję „Diagram” albo „Bez diagramu” z powodem.
- Szablon zapasowy, discovery i checklisty wskazują miejsca oraz informacje potrzebne do diagramów.

### Zgodność ze źródłami
- Kontrola obejmuje etykiety połączeń, grupy, role, atrybuty, opisy, daty i adnotacje, a nie tylko nazwy węzłów.
- Tryb końcowy blokuje oznaczenia robocze w tytule, podpisie, opisie i tekście alternatywnym.
- Angielskie statusy na diagramach są odrzucane.

### Szablony klienta
- Obsługa szablonów `.dotx` oraz nagłówków w stylach własnych klienta.
- Zdanie wprowadzające przejmuje styl tekstu dokumentu.
- Zapowiedź tabeli lub listy nie jest oddzielana od zapowiadanej treści.
- Diagram wstawiony znacznikiem zachowuje miejsce przy ponownym generowaniu.
- Numeracja uwzględnia rysunki istniejące w szablonie.
- Instrukcja wypełniania placeholderów zachowuje formatowanie.

### Uruchamianie
- Polecenia używają ścieżki katalogu skilla, dzięki czemu działają po instalacji w dowolnym projekcie.

## 2.3 (18.11.2026)

### Silnik diagramów
- Nowy Etap 5a: ocena potrzeby, plan, model pośredni YAML, generowanie, walidacja i osadzanie diagramów.
- 15 typów diagramów, 3 motywy oraz kolor i czcionka pobierane z szablonu klienta.
- Eksport SVG, PNG i HTML; osadzanie w DOCX i Markdown z numeracją, podpisem i tekstem alternatywnym.
- Każdy element diagramu ma oznaczenie pochodzenia.
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
