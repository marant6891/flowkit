# Historia zmian skilla flowkit-sql-data-assistant

## 1.3 (26.11.2026)

- Opakowanie skryptów zmieniających dane (zasada 14): nagłówek w ramce z `ZGŁOSZENIE:`, wypisanie serwera i bazy z kontrolą oczekiwanej bazy, numerowane kroki `KROK n` z komunikatami liczby wierszy, plan zmian w tabeli tymczasowej (kopia poprzednich wartości), obsługa błędów wycofująca całość, `ROLLBACK` z komunikatem i gotowym `COMMIT` w komentarzu, sprzątanie i skrypt odtworzenia.
- Nowe szablony dla SQL Server, PostgreSQL, Oracle i MySQL/MariaDB oraz wzór „Plan zmian” (uzupełnienie i dodanie w jednym skrypcie z osobną kontrolą każdej operacji).
- `check_sql.py`: wymaga nagłówka z `ZGŁOSZENIE:` i co najmniej trzech kroków `KROK n` w skryptach zmieniających dane, w SQL Server bloku `BEGIN TRY … BEGIN CATCH` z `ROLLBACK`; dopuszcza usuwanie tabel tymczasowych (`#plan`, `TEMPORARY`); wykrywa `UPDATE … JOIN … SET` (MySQL).
- Wzór odpowiedzi: tabela „Co pokaże skrypt krok po kroku” dla testera.

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
