# Warsztat wymagań: <Nazwa projektu>

| Pole | Wartość |
|---|---|
| Skrót projektu | <skrót> |
| Rozpoczęty | <RRRR-MM-DD> |
| Ostatnia aktualizacja | <RRRR-MM-DD>, runda <N> |
| Uczestnicy i role | <osoba - rola; kto decyduje o biznesie, kto o technice> |
| Odbiorca dokumentu docelowego | <klient / zespół / …> |
| Głębokość | szybka / pełna |
| Rodzaj | nowa aplikacja / zmiana istniejącej |
| Aktualna faza | <0-5> |

## Status faz

| Faza | Status | Data zatwierdzenia | Decyzja |
|---|---|---|---|
| 0. Koncepcja | w toku / zatwierdzona / do przeglądu | | DEC-… |
| 1. Zakres | | | |
| 2. Wymagania biznesowe | | | |
| 3. Wymagania techniczne | | | |
| 4. Ryzyka, plan i weryfikacja | | | |
| 5. Dokument docelowy | | | |

## Rejestr źródeł

| ID | Źródło | Opis | Nadrzędne |
|---|---|---|---|
| SRC-001 | <plik, sekcja> | | tak / nie |

## Odpowiedzi użytkownika

| ID | Data | Pytanie | Odpowiedź |
|---|---|---|---|
| USR-001 | | Q-001 | |

## Rekomendacje i decyzje

| ID | Treść | Podstawa | Status |
|---|---|---|---|
| REC-001 | | USR-… / SRC-… / dobra praktyka | proponowana / przyjęta (DEC-…) / odrzucona |
| DEC-001 | | USR-… / REC-… | obowiązuje / zastąpiona przez DEC-… |

## Faza 0: Koncepcja

**Wizja:** <problem → dla kogo → co zmieniamy → jak poznamy sukces>

| ID | Cel | Miara sukcesu (obecnie → docelowo) | Źródło |
|---|---|---|---|
| GOAL-001 | | | USR-… |

Ograniczenia (termin, budżet, regulacje, technologia): …  
Interesariusze: …

## Faza 1: Zakres

| ID | Możliwość | Decyzja | Źródło |
|---|---|---|---|
| SC-001 | | MVP / później | DEC-… |
| OOS-001 | | poza zakresem | DEC-… |

## Faza 2: Wymagania biznesowe

### Aktorzy i role

| ID | Rola | Co robi | Uprawnienia | Źródło |
|---|---|---|---|---|

### Procesy

| ID | Proces | Stan obecny | Stan docelowy | Wyjątki | Źródło |
|---|---|---|---|---|---|

### Reguły biznesowe

| ID | Reguła | Źródło |
|---|---|---|

### User stories i kryteria akceptacji

**US-001** Jako <rola> chcę <cel>, aby <korzyść>. Zakres: MVP. Źródło: DEC-…

- **AC-001** Given <stan> When <działanie> Then <wynik>
- **AC-002** Given <stan> When <błąd lub wyjątek> Then <wynik>

### Informacje biznesowe, raporty i wymagania prawne

…

## Faza 3: Wymagania techniczne

### Wymagania funkcjonalne

| ID | Wymaganie | Powiązane US | Źródło |
|---|---|---|---|

### Integracje

| ID | System | Kierunek | Sposób | Częstotliwość | Właściciel | Obsługa błędów | Źródło |
|---|---|---|---|---|---|---|---|

### Dane

| ID | Encja / zbiór | Zmiana | Migracja | Retencja | Źródło |
|---|---|---|---|---|---|

### Wymagania niefunkcjonalne

| ID | Obszar | Wymaganie i wartość | Źródło |
|---|---|---|---|

### Rozwiązanie, środowiska i wdrożenie

…

## Faza 4: Ryzyka, plan i weryfikacja

### Ryzyka

| ID | Ryzyko | Prawdopodobieństwo | Wpływ | Ograniczenie | Właściciel |
|---|---|---|---|---|---|

### Plan testów

| ID | Test | Pokrywa (AC / INT / NFR) | Rodzaj |
|---|---|---|---|

Definition of Done odbioru: …  
Etapy wdrożenia: …

## Otwarte kwestie

| ID | Pytanie | Kto odpowie | Termin | Blokuje | Status |
|---|---|---|---|---|---|
| OPEN-001 | | | | dokument / fazę N / nie | otwarta / zamknięta (USR-…) |

## Dokument docelowy

| Wersja | Data | Tryb | Ścieżka | Audyt DOC-AUDIT | Akceptacja |
|---|---|---|---|---|---|

## Historia zmian

| Data | Zmiana | Powód | Dotknięte elementy |
|---|---|---|---|
| | DEC-004 zastąpiona przez DEC-011 | USR-019 | BR-002, US-003 |
