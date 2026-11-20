# Przykład: Tematy do wyjaśnienia

| ID | Temat | Czego brakuje i na co wpływa | Właściciel decyzji | Priorytet | Status |
|---|---|---|---|---|---|
| OPEN-001 | Model rozliczeń | SRC-001 nie określa: miesięczne, roczne czy oba – wpływa na model danych, UI i raporty | Właściciel produktu (klient) | Wysoki | Otwarty |
| OPEN-002 | Migracja danych | Brak decyzji o migracji historycznych zamówień – wpływa na zakres i termin wdrożenia | DO POTWIERDZENIA | Wysoki | Otwarty |
| OPEN-003 | Sprzeczność w źródłach | Limit pozycji: 50 (SRC-001) czy 100 (SRC-003) – wpływa na FR-004 | Klient | Średni | ROZSTRZYGNIĘTY (12.11.2026) |

## Zasady prowadzenia listy

1. Każda niejasność, brak danych lub sprzeczność w źródłach otrzymuje `OPEN-NNN`.
2. Opis mówi, czego brakuje i w którym źródle tego szukano – nie zawiera zgadywanej odpowiedzi.
3. Właściciel decyzji tylko ze źródła; inaczej `DO POTWIERDZENIA`.
4. Nie usuwaj pozycji przed rozstrzygnięciem.
5. Po decyzji przenieś treść do właściwej sekcji i zmień status na `ROZSTRZYGNIĘTY (DD.MM.RRRR)`.
6. Jeśli decyzja zmienia zakres – zaktualizuj FR, US, testy, macierz i historię zmian dokumentu.
