<!--
Szablon ZAPASOWY. Używaj go tylko, gdy użytkownik nie dostarczył własnego szablonu.
Sekcje oznaczone (warunkowa) umieszczaj tylko, gdy dotyczą zmiany. Niedotyczące usuń
i wymień jednym zdaniem w sekcji 3 („Pominięto sekcje: …”). Brak danych: „Brak danych - patrz OPEN-NNN”.
Zwięzłość: każda informacja raz, tabele bez zdań wprowadzających, objętość wg SKILL.md (Etap 5).
Usuń wszystkie komentarze i placeholdery [..] przed oddaniem dokumentu.
Statusy, priorytety i wymagalność zapisuj po polsku (references/status-vocabulary.md).
Gdy źródło stosuje MoSCoW, zamień kolumnę „Priorytet” na „Wymagalność”
(Wymagane / Zalecane / Opcjonalne / Wyłączone z zakresu).
Procesy, przepływy, integracje i relacje oceń pod kątem diagramu (SKILL.md, Etap 5a).
-->

# Dokument PT/PRD: [Nazwa zmiany]

| Pole | Wartość |
|---|---|
| Wersja dokumentu | [0.1] |
| Data | [DATA] |
| Autor | [AUTOR] |
| Klient | [KLIENT] |
| Projekt / system | [PROJEKT] |
| Status | Roboczy / Do akceptacji / Zaakceptowany |
| Właściciel produktowy | [OSOBA lub DO POTWIERDZENIA] |
| Właściciel techniczny | [OSOBA lub DO POTWIERDZENIA] |

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 0.1 | [DATA] | [AUTOR] | Wersja robocza |

## Materiały źródłowe

| ID | Źródło | Typ | Data / wersja | Zakres informacji |
|---|---|---|---|---|
| SRC-001 | [Nazwa / link] | [Ticket / mail / notatka / kod / dokumentacja] | [Data] | [Co z niego wynika] |

Oznaczenia w dokumencie: `SRC-NNN` - informacja potwierdzona źródłem;
`ASSUMPTION-NNN` - założenie do potwierdzenia; `OPEN-NNN` - temat do wyjaśnienia;
`DO POTWIERDZENIA` - wartość nieznana.

## 1. Streszczenie zarządcze

[Najwyżej 5 zdań, pisane na końcu, tylko z treści dokumentu: problem, co się zmienia,
efekt dla klienta, kluczowe ryzyka i decyzje oczekujące.]

## 2. Kontekst i cel zmiany

[Jeden akapit: obecny stan i powód zmiany - ze źródłem.]

| ID | Cel | Mierzalny efekt | Źródło |
|---|---|---|---|
| GOAL-001 | [Cel] | [Miara ze źródła lub DO POTWIERDZENIA] | SRC-001 |

## 3. Zakres

### 3.1 W zakresie

| ID | Element zakresu | Opis | Źródło |
|---|---|---|---|
| SC-001 | [Element] | [Opis] | SRC-001 |

### 3.2 Poza zakresem i Anty-cele (Non-Goals)

| ID | Element wyłączony | Powód wyłączenia / Ryzyko Scope Creep | Źródło |
|---|---|---|---|
| OOS-001 | [Element] | [Dlaczego tego świadomie NIE robimy w tej zmianie] | SRC-001 |

Pominięto sekcje: [lista sekcji warunkowych, których zmiana nie dotyczy].

## 4. Proces obecny i docelowy (warunkowa)

### 4.1 Stan obecny
[As-is - ze źródła / z analizy kodu.]

### 4.2 Stan docelowy
[To-be - ze źródła. Diagram procesu, gdy spełnia kryteria z Etapu 5a.]

### 4.3 Różnice

| ID | Obszar | Obecnie | Po zmianie | Źródło |
|---|---|---|---|---|
| CHG-001 | [Obszar] | [Stan obecny] | [Stan docelowy] | SRC-001 |

## 5. Role i uprawnienia (warunkowa)

| Rola | Opis | Zmiana uprawnień | Źródło |
|---|---|---|---|
| [Rola] | [Opis] | [Co się zmienia] | SRC-001 |

## 6. Wymagania funkcjonalne

| ID | Wymaganie | Priorytet | Kryterium akceptacji | Źródło | Status |
|---|---|---|---|---|---|
| FR-001 | [Wymaganie] | [Wysoki/Średni/Niski ze źródła lub DO POTWIERDZENIA] | [Sprawdzalne kryterium albo „US-001”] | SRC-001 | Proponowane / Zaakceptowane |

## 7. User stories (warunkowa)

### US-001: [Tytuł] (FR-001, SRC-001)

**Jako** [rola] **chcę** [akcja], **aby** [korzyść].

| Scenariusz | Mając (Given) | Gdy (When) | Wtedy (Then) |
|---|---|---|---|
| S1 Ścieżka główna | [stan początkowy] | [akcja] | [oczekiwany wynik] |
| S2 [Przypadek brzegowy ze źródła] | [stan] | [akcja] | [wynik] |

## 8. Wymagania niefunkcjonalne (warunkowa - tylko ze źródeł)

| ID | Kategoria | Wymaganie | Miara / kryterium | Źródło |
|---|---|---|---|---|
| NFR-001 | [Kategoria] | [Wymaganie] | [Miara lub DO POTWIERDZENIA] | SRC-001 |

## 9. Analiza wpływu na aplikację

[Jeśli brak dostępu do kodu/dokumentacji: „Nie analizowano - brak dostępu do …” + OPEN.]

| Obszar / komponent | Obecny stan | Planowana zmiana | Wpływ / regresja | Źródło |
|---|---|---|---|---|
| [Moduł, plik, endpoint] | [Stan] | [Zmiana] | [Wpływ] | [plik:linia / SRC-NNN] |

## 10. Architektura (warunkowa)

[Opis tylko przeanalizowanych komponentów. Diagram architektury lub komponentów, gdy
spełnia kryteria z Etapu 5a; każdy węzeł musi występować w tekście i tabeli wpływu.]

## 11. Integracje (warunkowa)

[Diagram sekwencji, integracji lub przepływu danych, gdy spełnia kryteria z Etapu 5a.]

| ID | System | Kierunek | Dane | Format | Obsługa błędów | Źródło |
|---|---|---|---|---|---|---|
| INT-001 | [System] | [We/Wy] | [Dane] | [Format] | [Ze źródła lub DO POTWIERDZENIA] | SRC-001 |

## 12. Model danych i migracje (warunkowa)

[Diagram ER, gdy spełnia kryteria z Etapu 5a.]

| ID | Encja / tabela | Zmiana | Wpływ na dane | Migracja | Źródło |
|---|---|---|---|---|---|
| DATA-001 | [Encja] | [Zmiana] | [Wpływ] | [Plan lub OPEN] | [plik / SRC-NNN] |

## 13. Bezpieczeństwo i zgodność (warunkowa)

[Uwierzytelnianie, autoryzacja, dane osobowe/RODO, audyt - tylko to, czego zmiana dotyczy.]

## 14. Plan testów

Scenariusze akceptacyjne: US-001/S1-S2 [odwołania do US]. Dodatkowe testy (tylko te, których US nie pokrywają):

| ID | Scenariusz | Oczekiwany wynik | Wymaganie |
|---|---|---|---|
| TEST-001 | [np. regresja, integracja, migracja] | [Wynik] | FR-001 |

## 15. Kryteria ukończenia zmiany (Definition of Done - DoD)

[Tylko kryteria tej zmiany, ze źródeł, wymagań i testów - bez ogólnych formułek.]

| Lp. | Kryterium DoD | Odpowiedzialny |
|---|---|---|
| 1 | [np. Scenariusze US-001-US-003 zaliczone na środowisku testowym] | [Rola ze źródła lub DO POTWIERDZENIA] |

## 16. Wdrożenie i rollback (warunkowa)

| Etap | Działanie | Odpowiedzialny | Warunek wejścia | Warunek wyjścia |
|---|---|---|---|---|
| 1 | [Działanie] | [Osoba lub DO POTWIERDZENIA] | [Warunek] | [Warunek] |

Rollback: [Sposób wycofania - ze źródła lub OPEN.]

## 17. Ryzyka i zależności

| ID | Ryzyko / zależność | Wpływ | Prawdopodobieństwo | Działanie łagodzące | Właściciel | Źródło |
|---|---|---|---|---|---|---|
| RISK-001 | [Ryzyko] | [W/Ś/N] | [W/Ś/N] | [Działanie] | [Osoba lub DO POTWIERDZENIA] | [SRC-NNN / analiza] |

## 18. Rekomendacje (opcjonalna - poza zakresem wymagań)

| ID | Rekomendacja | Uzasadnienie | Wymaga decyzji |
|---|---|---|---|
| REC-001 | [Propozycja autora] | [Dlaczego] | Tak |

## 19. Słownik pojęć (warunkowa)

| Pojęcie / skrót | Znaczenie |
|---|---|
| [Pojęcie] | [Wyjaśnienie] |

## 20. Macierz śledzenia wymagań (warunkowa - od 6 FR, gdy powiązania nie wynikają z tabel)

| Wymaganie | User story | Test | Komponent | Źródło | Status |
|---|---|---|---|---|---|
| FR-001 | US-001 | TEST-001 | [Komponent] | SRC-001 | Otwarte / W toku / Zamknięte |

## 21. Założenia i tematy do wyjaśnienia

### 21.1 Założenia

| ID | Założenie | Do potwierdzenia przez | Status |
|---|---|---|---|
| ASSUMPTION-001 | [Założenie] | [Osoba/rola] | Do potwierdzenia |

### 21.2 Tematy do wyjaśnienia

| ID | Temat | Czego brakuje i na co wpływa | Właściciel decyzji | Priorytet | Status |
|---|---|---|---|---|---|
| OPEN-001 | [Temat] | [Czego brakuje] - wpływa na [FR/US/obszar] | [Osoba lub DO POTWIERDZENIA] | [W/Ś/N] | Otwarty |
