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
- [ ] Sekcje niedotyczące mają „Nie dotyczy – uzasadnienie”; sekcje bez danych mają „Brak danych – OPEN-NNN”.
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

## E. Jakość dla klienta
- [ ] Dokument zrozumiały dla osoby nietechnicznej; skróty w słowniku.
- [ ] Wskazano, kto musi podjąć jakie decyzje.
- [ ] Długość adekwatna do wielkości zmiany – brak treści „na wypełnienie”.
