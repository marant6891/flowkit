<!--
Szablon ZAPASOWY. Używaj go tylko, gdy użytkownik nie dostarczył własnego szablonu.
Sekcje oznaczone (warunkowa) wypełniaj tylko, gdy dotyczą zmiany; inaczej wpisz
„Nie dotyczy – <uzasadnienie>” albo „Brak danych – patrz OPEN-NNN”.
Usuń wszystkie komentarze i placeholdery [..] przed oddaniem dokumentu.
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

Oznaczenia w dokumencie: `SRC-NNN` – informacja potwierdzona źródłem;
`ASSUMPTION-NNN` – założenie do potwierdzenia; `OPEN-NNN` – temat do wyjaśnienia;
`DO POTWIERDZENIA` – wartość nieznana.

## 1. Streszczenie zarządcze

[3–8 zdań, pisane na końcu, tylko z treści dokumentu: problem, co się zmienia,
efekt dla klienta, kluczowe ryzyka i decyzje oczekujące.]

## 2. Kontekst i cel zmiany

[Obecny stan i powód zmiany – ze źródłem.]

| ID | Cel | Mierzalny efekt | Źródło |
|---|---|---|---|
| GOAL-001 | [Cel] | [Miara ze źródła lub DO POTWIERDZENIA] | SRC-001 |

## 3. Zakres

### 3.1 W zakresie

| ID | Element zakresu | Opis | Źródło |
|---|---|---|---|
| SC-001 | [Element] | [Opis] | SRC-001 |

### 3.2 Poza zakresem

| ID | Element | Powód wyłączenia | Źródło |
|---|---|---|---|
| OOS-001 | [Element] | [Powód] | SRC-001 |

## 4. Proces obecny i docelowy (warunkowa)

### 4.1 Stan obecny
[As-is – ze źródła / z analizy kodu.]

### 4.2 Stan docelowy
[To-be – ze źródła.]

### 4.3 Różnice

| ID | Obszar | Obecnie | Po zmianie | Źródło |
|---|---|---|---|---|
| CHG-001 | [Obszar] | [Stan obecny] | [Stan docelowy] | SRC-001 |

## 5. Role i uprawnienia (warunkowa)

| Rola | Opis | Zmiana uprawnień | Źródło |
|---|---|---|---|
| [Rola] | [Opis] | [Co się zmienia] | SRC-001 |

## 6. Wymagania funkcjonalne

| ID | Wymaganie | Priorytet | Kryterium akceptacji | US | Źródło | Status |
|---|---|---|---|---|---|---|
| FR-001 | [Wymaganie] | [Wysoki/Średni/Niski ze źródła lub DO POTWIERDZENIA] | [Sprawdzalne kryterium] | US-001 | SRC-001 | Proponowane / Zaakceptowane |

## 7. User stories (warunkowa)

### US-001: [Tytuł]

**Jako** [rola]
**chcę** [akcja]
**aby** [korzyść].

Źródło: SRC-001 · Powiązane wymagania: FR-001

**Kryteria akceptacji:**
- [ ] [Kryterium sprawdzalne]

## 8. Wymagania niefunkcjonalne (warunkowa – tylko ze źródeł)

| ID | Kategoria | Wymaganie | Miara / kryterium | Źródło |
|---|---|---|---|---|
| NFR-001 | [Kategoria] | [Wymaganie] | [Miara lub DO POTWIERDZENIA] | SRC-001 |

## 9. Analiza wpływu na aplikację

[Jeśli brak dostępu do kodu/dokumentacji: „Nie analizowano – brak dostępu do …” + OPEN.]

| Obszar / komponent | Obecny stan | Planowana zmiana | Wpływ / regresja | Źródło |
|---|---|---|---|---|
| [Moduł, plik, endpoint] | [Stan] | [Zmiana] | [Wpływ] | [plik:linia / SRC-NNN] |

## 10. Architektura (warunkowa)

[Opis tylko przeanalizowanych komponentów. Diagram tylko, jeśli zmiana dotyka
architektury; każdy węzeł musi występować w tekście i tabeli wpływu.]

## 11. Integracje (warunkowa)

| ID | System | Kierunek | Dane | Format | Obsługa błędów | Źródło |
|---|---|---|---|---|---|---|
| INT-001 | [System] | [We/Wy] | [Dane] | [Format] | [Ze źródła lub DO POTWIERDZENIA] | SRC-001 |

## 12. Model danych i migracje (warunkowa)

| ID | Encja / tabela | Zmiana | Wpływ na dane | Migracja | Źródło |
|---|---|---|---|---|---|
| DATA-001 | [Encja] | [Zmiana] | [Wpływ] | [Plan lub OPEN] | [plik / SRC-NNN] |

## 13. Bezpieczeństwo i zgodność (warunkowa)

[Uwierzytelnianie, autoryzacja, dane osobowe/RODO, audyt – tylko to, czego zmiana dotyczy.]

## 14. Plan testów

| ID | Scenariusz | Oczekiwany wynik | Wymaganie |
|---|---|---|---|
| TEST-001 | [Scenariusz] | [Wynik] | FR-001 |

## 15. Wdrożenie i rollback (warunkowa)

| Etap | Działanie | Odpowiedzialny | Warunek wejścia | Warunek wyjścia |
|---|---|---|---|---|
| 1 | [Działanie] | [Osoba lub DO POTWIERDZENIA] | [Warunek] | [Warunek] |

Rollback: [Sposób wycofania – ze źródła lub OPEN.]

## 16. Ryzyka i zależności

| ID | Ryzyko / zależność | Wpływ | Prawdopodobieństwo | Działanie łagodzące | Właściciel | Źródło |
|---|---|---|---|---|---|---|
| RISK-001 | [Ryzyko] | [W/Ś/N] | [W/Ś/N] | [Działanie] | [Osoba lub DO POTWIERDZENIA] | [SRC-NNN / analiza] |

## 17. Rekomendacje (opcjonalna – poza zakresem wymagań)

| ID | Rekomendacja | Uzasadnienie | Wymaga decyzji |
|---|---|---|---|
| REC-001 | [Propozycja autora] | [Dlaczego] | Tak |

## 18. Słownik pojęć (warunkowa)

| Pojęcie / skrót | Znaczenie |
|---|---|
| [Pojęcie] | [Wyjaśnienie] |

## 19. Macierz śledzenia wymagań (warunkowa – od 3 FR)

| Wymaganie | User story | Test | Komponent | Źródło | Status |
|---|---|---|---|---|---|
| FR-001 | US-001 | TEST-001 | [Komponent] | SRC-001 | Otwarte / W toku / Zamknięte |

## 20. Założenia i tematy do wyjaśnienia

### 20.1 Założenia

| ID | Założenie | Uzasadnienie | Do potwierdzenia przez | Status |
|---|---|---|---|---|
| ASSUMPTION-001 | [Założenie] | [Dlaczego bezpieczne] | [Osoba/rola] | Do potwierdzenia |

### 20.2 Tematy do wyjaśnienia

| ID | Temat | Opis | Dlaczego wymaga wyjaśnienia | Wpływ | Właściciel decyzji | Priorytet | Status | Data decyzji |
|---|---|---|---|---|---|---|---|---|
| OPEN-001 | [Temat] | [Czego brakuje] | [Na co wpływa] | [W/Ś/N] | [Osoba lub DO POTWIERDZENIA] | [W/Ś/N] | Otwarty | – |
