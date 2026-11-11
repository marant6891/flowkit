# Przykład: Tematy do wyjaśnienia

| ID | Temat | Opis | Dlaczego wymaga wyjaśnienia | Wpływ | Właściciel decyzji | Priorytet | Status | Data decyzji |
|---|---|---|---|---|---|---|---|---|
| OPEN-001 | Model rozliczeń | Materiały (SRC-001) nie określają, czy system ma obsługiwać rozliczenia miesięczne, roczne czy oba warianty | Wpływa na model danych, UI, raporty i testy | Wysoki | Właściciel produktu (klient) | Wysoki | Otwarty | – |
| OPEN-002 | Migracja danych | Nie potwierdzono, czy historyczne zamówienia mają zostać zmigrowane | Wpływa na zakres migracji, ryzyko regresji i czas wdrożenia | Wysoki | DO POTWIERDZENIA | Wysoki | Otwarty | – |
| OPEN-003 | Sprzeczność w źródłach | Ticket (SRC-001) mówi o limicie 50 pozycji, notatka ze spotkania (SRC-003) o 100 | Wpływa na walidację FR-004 i test TEST-006 | Średni | Klient | Średni | ROZSTRZYGNIĘTY | 12.11.2026 |

## Zasady prowadzenia listy

1. Każda niejasność, brak danych lub sprzeczność w źródłach otrzymuje `OPEN-NNN`.
2. Opis mówi, czego brakuje i w którym źródle tego szukano – nie zawiera zgadywanej odpowiedzi.
3. Właściciel decyzji tylko ze źródła; inaczej `DO POTWIERDZENIA`.
4. Nie usuwaj pozycji przed rozstrzygnięciem.
5. Po decyzji przenieś treść do właściwej sekcji, zmień status na `ROZSTRZYGNIĘTY`, wpisz datę.
6. Jeśli decyzja zmienia zakres – zaktualizuj FR, US, testy, macierz i historię zmian dokumentu.
