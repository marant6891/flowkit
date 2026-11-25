# Checklista bezpieczeństwa SQL

## A. Kontekst
- [ ] Typ bazy jest potwierdzony, a składnia pasuje do tej bazy.
- [ ] Tabele i kolumny pochodzą ze schematu, dokumentacji lub zgłoszenia.
- [ ] Znane są środowisko i numer zgłoszenia.

## B. Odczyt
- [ ] Zapytanie wybiera konkretne kolumny i ma limit wierszy albo agregację.
- [ ] Wynik nie ujawnia niepotrzebnych danych osobowych.

## B1. Tryb
- [ ] Tryb (`READ_ONLY`, `ANALYTICS_REPORT`, `DATA_INVESTIGATION`, `DATA_REPAIR`) jest podany; naprawę poprzedza zapytanie diagnostyczne.

## C. Zmiana danych
- [ ] Wartości są w zmiennych na początku skryptu.
- [ ] Skrypt ma podgląd przed zmianą i sprawdzenie po zmianie.
- [ ] Zmiana działa w transakcji i kontroluje liczbę zmienionych wierszy.
- [ ] `INSERT` nie utworzy duplikatu, a `UPDATE` i `DELETE` mają bezpieczny warunek.
- [ ] Skrypt kończy się `ROLLBACK`, a `COMMIT` pozostaje komentarzem.
- [ ] Oczekiwana liczba rekordów jest podana, a inna liczba przerywa skrypt.
- [ ] Poprzednie wartości są zachowane i jest skrypt odtworzenia; `UPDATE` sprawdza poprzednią wartość lub wersję.
- [ ] Opisano blokady i czas transakcji dla dużych tabel; nieznane triggery, klucze obce i ograniczenia wypisano jako niewiadome.

## D. Zestawienie analityczne (`ANALYTICS_REPORT`)
- [ ] Karta raportu jest kompletna: pytanie biznesowe, okres, granulacja, data biznesowa i strefa czasowa, wymiary, filtry, odbiorca.
- [ ] Każda miara ma definicję i jednostkę; definicje spoza źródeł są oznaczone jako `ZAŁOŻENIE`.
- [ ] Okres jest półotwarty i podany w parametrach; w `WHERE` nie ma funkcji na kolumnie daty.
- [ ] Złączenia nie zwielokrotniają wartości (agregacja szczegółów przed złączeniem, `COUNT(DISTINCT)` tam, gdzie trzeba).
- [ ] Szereg czasowy ma kalendarz i pokazuje puste okresy; `LAG` i średnie kroczące nie przeskakują okresów.
- [ ] Każde dzielenie ma `NULLIF(..., 0)`; nie ma dzielenia całkowitego; `ROUND` dostaje właściwy typ.
- [ ] Funkcje okna, CTE i funkcje dat są dostępne w podanej wersji bazy.
- [ ] Jest zapytanie kontrolne (rekonsyliacja) i opis wierszy pominiętych przez filtry lub `NULL`.
- [ ] Wynik zawiera agregaty; dane osobowe tylko wtedy, gdy są niezbędne.

## E. Odbiorca
- [ ] Instrukcja wyjaśnia prostym językiem, co uzupełnić i jaki wynik jest poprawny.
- [ ] Opisano, co zrobić przy innym wyniku i kto zatwierdza zmianę.
- [ ] `check_sql.py` nie zgłasza błędów.
