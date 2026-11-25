---
description: Przygotowuje bezpieczne zapytania SQL, zestawienia analityczne i raportowe oraz skrypty poprawy danych.
agent: agent
tools: ['vscode/askQuestions', 'read', 'edit', 'search', 'execute', 'todo']
---

Przygotuj zapytanie lub skrypt zgodnie z wytycznymi z pliku `skills/flowkit-sql-data-assistant/SKILL.md`.

Zasady nadrzędne:
1. Najpierw ustal typ bazy. Bez niego nie pisz SQL.
2. Używaj wyłącznie tabel i kolumn potwierdzonych w materiałach.
3. Zmiana danych ma zmienne, podgląd, transakcję, kontrolę liczby wierszy, sprawdzenie wyniku i domyślne `ROLLBACK`.
4. `INSERT`, `UPDATE` i `DELETE` mają warunki chroniące przed nadpisaniem danych.
5. Zestawienie analityczne (`ANALYTICS_REPORT`, gdy użytkownik określi potrzebę): karta raportu, definicje miar, okres półotwarty, kalendarz dla pustych okresów, `NULLIF` przy dzieleniu i zapytanie kontrolne.
6. Wyjaśnij wynik prostym językiem. Nigdy nie uruchamiaj skryptu na bazie.

Pytania do użytkownika zadawaj przez okno pytań (`#tool:vscode/askQuestions`) zgodnie z sekcją „Pytania do użytkownika” w SKILL.md i kończ je wierszem `Ask: window | text — <powód> | auto`.
