# Checklist końcowa dokumentu PT/PRD

## A. Test pochodzenia treści (najważniejszy)
- [ ] Każde zdanie merytoryczne ma źródło (SRC-NNN, plik:linia) albo oznaczenie ASSUMPTION / OPEN / DO POTWIERDZENIA.
- [ ] Żaden priorytet, termin, właściciel, miara ani próg nie został nadany bez źródła.
- [ ] Nie dodano funkcji, ról, integracji, NFR, ryzyk ani etapów spoza materiałów.
- [ ] Propozycje autora są wyłącznie w sekcji „Rekomendacje”.
- [ ] Opis kodu/architektury pochodzi z faktycznej analizy; przy braku dostępu jest „Nie analizowano”.
- [ ] Diagram (jeśli jest) zawiera tylko komponenty opisane w tekście; nie jest przykładem z szablonu.
- [ ] Streszczenie zarządcze nie wprowadza nowych faktów.
- [ ] Nazwy i terminy są takie jak w materiałach klienta.

## B. Szablon
- [ ] Użyto szablonu użytkownika (jeśli był) – kolejność, numeracja, nazwy sekcji, style zachowane.
- [ ] Brak pozostawionych placeholderów i tekstów instruktażowych szablonu.
- [ ] Szablon użytkownika: sekcje niedotyczące mają „Nie dotyczy.”; szablon zapasowy: sekcji niedotyczących nie ma, są wymienione jednym zdaniem w Zakresie. Sekcje bez danych mają „Brak danych – OPEN-NNN”.
- [ ] Metryczka i historia zmian są wypełnione (nieznane pola: DO POTWIERDZENIA).
- [ ] Format pliku zgodny z szablonem / prośbą; dokument otwarty i sprawdzony wizualnie.

## C. Kompletność (w granicach zakresu zmiany)
- [ ] Cel i zakres (w / poza zakresem i Non-Goals) są jednoznaczne.
- [ ] Każde FR ma ID, kryterium akceptacji, źródło i status.
- [ ] Każda US ma kryteria akceptacji w formacie Given-When-Then (Gherkin).
- [ ] Zdefiniowano listę kryteriów Definition of Done (DoD) dla zmiany.
- [ ] Każde FR ma co najmniej jeden test.
- [ ] Integracje i zmiany danych (jeśli są) mają opis, obsługę błędów / migrację lub OPEN.
- [ ] Ryzyka mają działanie łagodzące i właściciela (lub DO POTWIERDZENIA).

## D. Spójność
- [ ] ID w formacie trzycyfrowym, bez duplikatów i luk w odwołaniach.
- [ ] Tabele, tekst, macierz śledzenia i diagram są ze sobą zgodne.
- [ ] Brak sprzecznych wymagań; sprzeczności w źródłach są w OPEN.
- [ ] Każde OPEN i ASSUMPTION z treści występuje w sekcji końcowej.
- [ ] Statusy, priorytety i wymagalność w tabelach mają polskie nazwy (`check_status_labels.py` bez uwag).
- [ ] Każdy proces, przepływ, integracja i relacja między systemami ma w planie decyzję „Diagram” albo „Bez diagramu” z powodem.
- [ ] Diagramy (jeśli są) przeszły `diagram-quality-checklist.md`.

## E. Krytyczny przegląd
- [ ] Sprawdzono przypadki brzegowe, błędy i ścieżki alternatywne każdego kluczowego wymagania.
- [ ] Każde wymaganie można zweryfikować testem lub obserwacją.
- [ ] Nie ma sprzeczności między wymaganiami, procesem, diagramami i planem testów.
- [ ] Założenia ukryte w treści zapisano jako `ASSUMPTION-NNN` albo `OPEN-NNN`.

## E1. Jakość dla klienta
- [ ] Dokument zrozumiały dla osoby nietechnicznej; skróty w słowniku.
- [ ] Wskazano, kto musi podjąć jakie decyzje.
- [ ] Długość adekwatna do wielkości zmiany – brak treści „na wypełnienie”.

## E2. Zwięzłość
- [ ] Objętość mieści się w tabeli z Etapu 5 SKILL.md albo przekroczenie jest uzasadnione.
- [ ] Każda informacja występuje raz; w innych sekcjach jest tylko jej ID (kryteria akceptacji nie są powielone w FR, US, testach i macierzy).
- [ ] Brak zdań wprowadzających przed tabelami, wypełniaczy („Niniejszy dokument…”, „W ramach zmiany…”) i podsumowań sekcji.
- [ ] Streszczenie zarządcze ma najwyżej 5 zdań; kontekst – jeden akapit.
- [ ] Mała zmiana bez szablonu użytkownika: użyto wariantu skróconego (6 rozdziałów, 1–3 strony).
- [ ] Żadna tabela nie ma mniej niż 3 wierszy, chyba że narzuca ją szablon użytkownika.
- [ ] Każdy scenariusz Given-When-Then opisuje odrębne zachowanie; DoD nie zawiera ogólnych formułek.

## F. Tryb „Dokument końcowy bez dopisków” (tylko gdy użytkownik o niego poprosił)
- [ ] Użytkownik wprost poprosił o wersję bez dopisków; tryb nie został włączony domyślnie.
- [ ] Dokument ma dokładnie strukturę udostępnionego szablonu – żadnych sekcji dodanych przez skill (Materiały źródłowe, Założenia, Tematy do wyjaśnienia, Rekomendacje), o ile szablon ich nie przewiduje.
- [ ] Wyszukiwanie w dokumencie nie znajduje: `SRC-`, `ŹRÓDŁO:`, `ASSUMPTION-`, `OPEN-`, `Q-`, `REC-`, `DO POTWIERDZENIA`, „Nie analizowano”, „Brak danych”, kolumn „Źródło” spoza szablonu, placeholderów `[...]` ani komentarzy.
- [ ] Każda luka (OPEN) i każde założenie (ASSUMPTION) zostały przed generowaniem rozstrzygnięte decyzją użytkownika: uzupełnione / zatwierdzone / pominięte / zapisane neutralnym sformułowaniem.
- [ ] Żadna luka nie została wypełniona treścią spoza źródeł – test pochodzenia (sekcja A) wykonano na rejestrze pochodzenia.
- [ ] Rejestr pochodzenia przekazano użytkownikowi poza dokumentem (osobny plik lub odpowiedź) wraz z listą miejsc o neutralnym sformułowaniu.
- [ ] Status dokumentu w metryczce jest taki, jaki wskazał użytkownik.
