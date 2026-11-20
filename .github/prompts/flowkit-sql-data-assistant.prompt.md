---
description: Przygotowuje bezpieczne zapytania SQL, zestawienia i skrypty poprawy danych dla testerów i serwisantów.
---

Przygotuj zapytanie lub skrypt zgodnie z wytycznymi z pliku `skills/flowkit-sql-data-assistant/SKILL.md`.

Zasady nadrzędne:
1. Najpierw ustal typ bazy. Bez niego nie pisz SQL.
2. Używaj wyłącznie tabel i kolumn potwierdzonych w materiałach.
3. Zmiana danych ma zmienne, podgląd, transakcję, kontrolę liczby wierszy, sprawdzenie wyniku i domyślne `ROLLBACK`.
4. `INSERT`, `UPDATE` i `DELETE` mają warunki chroniące przed nadpisaniem danych.
5. Wyjaśnij wynik prostym językiem. Nigdy nie uruchamiaj skryptu na bazie.
