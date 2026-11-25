# Historia zmian skilla flowkit-sql-data-assistant

## 1.2 (25.11.2026)

- Tryb `ANALYTICS_REPORT` uruchamiany, gdy użytkownik określi potrzebę analityczną lub raportową: karta raportu, słownik miar, kontrola spójności (zasada 13).
- Wzorce analityczne `references/analytics-report-patterns.md`: ściągawka różnic między bazami, pełny raport miesięczny (m/m, udział, narastająco) dla każdej bazy, top N w grupie, ABC/Pareto, tabela przestawna z sumami, kohorty, rekonsyliacja.
- Wzór odpowiedzi `templates/analytics-report-template.md` i sekcja D checklisty.
- Sekcja „Pytania do użytkownika”: pytania przez okno pytań (VS Code `vscode/askQuestions`, Claude Code `AskUserQuestion`), najwyżej 4 w oknie, rekomendacja pierwsza, wiersz diagnostyczny `Ask:`; w subagencie pytania wracają jako `QUESTION-NNN`.
- `check_sql.py` uznaje `AVG`, `MIN`, `MAX`, `COUNT_BIG` i percentyle za agregację.

## 1.1 (20.11.2026)

- Tryby `READ_ONLY`, `DATA_INVESTIGATION` i `DATA_REPAIR`; naprawa zawsze po zapytaniu diagnostycznym.
- Oczekiwana liczba rekordów przerywa skrypt przy rozbieżności; zachowanie poprzednich wartości i skrypt odtworzenia.
- Współbieżność (warunek po poprzedniej wartości lub wersji), blokady dużych tabel, plan wykonania, różnice silników.
- Nieznane triggery, klucze obce i ograniczenia są wypisywane jako niewiadome.

## 1.0 (18.11.2026)

- Bezpieczne zapytania, zestawienia i skrypty zmiany danych dla PostgreSQL, SQL Server, Oracle, MySQL i MariaDB.
- Obowiązkowy typ bazy, zmienne, transakcja, kontrola liczby wierszy i domyślne `ROLLBACK`.
- Lokalna kontrola skryptów `scripts/check_sql.py`.
- Instrukcje dla początkującego testera i serwisanta.
