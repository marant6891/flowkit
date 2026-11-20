# Historia zmian skilla flowkit-sql-data-assistant

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
