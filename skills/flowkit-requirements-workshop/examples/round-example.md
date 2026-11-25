# Przykład: runda pytań i bramka fazy

Fikcyjny projekt „Zwroty w sklepie stacjonarnym” (skrót `zwroty`), Faza 2, głębokość pełna.

## Runda

```text
Faza 2 · Wymagania biznesowe · runda 3/≈5

Q-014 · Kto zatwierdza zwrot powyżej limitu?
Po co: od tego zależy ścieżka procesu PROC-002 i uprawnienia ról ACT-002, ACT-003.
  a) kierownik zmiany   b) dział finansów   c) dwie osoby (kierownik + finanse)
  d) inne: …            e) nie wiem (zapiszę OPEN i osobę, która wie)
  REC-007: c) — zwroty powyżej limitu to ryzyko nadużyć (USR-009); kosztem jest dłuższa obsługa.

Q-015 · Jaki jest limit zwrotu bez dodatkowej zgody?
Po co: to reguła BR-003; bez wartości nie da się napisać kryteriów akceptacji US-004.
  a) kwota: … zł   b) zależy od kategorii towaru   c) nie wiem
  (Nie proponuję wartości — limit musi pochodzić od Państwa.)

Q-016 · Czy klient dostaje potwierdzenie zwrotu?
Po co: decyduje o powiadomieniach i danych kontaktowych (RODO).
  a) paragon korekty   b) e-mail   c) SMS   d) a + b   e) nie wiem
```

**Odpowiedź użytkownika:** „14a, 15 nie wiem — zna to Marta z finansów, 16d”.

**Zapis w pliku warsztatu:**

| ID | Pytanie | Odpowiedź |
|---|---|---|
| USR-031 | Q-014 | Zwrot powyżej limitu zatwierdza kierownik zmiany. |
| USR-032 | Q-015 | Nie wiem, wie Marta (dział finansów). |
| USR-033 | Q-016 | Paragon korekty i e-mail. |

- `DEC-012` (USR-031): zatwierdzenie zwrotu powyżej limitu — kierownik zmiany. `REC-007` odrzucona.
- `OPEN-006`: limit zwrotu bez zgody (BR-003). Kto: Marta, dział finansów. Blokuje: kryteria `AC` dla US-004.
- `DEC-013` (USR-033): potwierdzenie paragonem korekty i e-mailem → nowe pytanie o zgodę na e-mail w następnej rundzie.

## Bramka Fazy 2

```text
Podsumowanie · Faza 2 · Wymagania biznesowe

Role: kasjer (ACT-001), kierownik zmiany (ACT-002), finanse (ACT-003).
Procesy: zwrot standardowy (PROC-001), zwrot powyżej limitu (PROC-002).
Reguły: BR-001…BR-004 (BR-003 — limit — czeka na OPEN-006).
User stories: US-001…US-006, kryteria AC-001…AC-014; US-004 bez AC do czasu OPEN-006.
Zmiany od ostatniej bramki: DEC-012, DEC-013; REC-007 odrzucona.
Otwarte: OPEN-006 (Marta, finanse) — blokuje AC dla US-004, nie blokuje Fazy 3.

Zatwierdzasz Fazę 2 (z OPEN-006 do uzupełnienia), poprawiasz coś, czy wracamy do Fazy 1?
```
