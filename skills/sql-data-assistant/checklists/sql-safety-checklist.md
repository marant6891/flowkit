# Checklista bezpieczeństwa SQL

## A. Kontekst
- [ ] Typ bazy jest potwierdzony, a składnia pasuje do tej bazy.
- [ ] Tabele i kolumny pochodzą ze schematu, dokumentacji lub zgłoszenia.
- [ ] Znane są środowisko i numer zgłoszenia.

## B. Odczyt
- [ ] Zapytanie wybiera konkretne kolumny i ma limit wierszy albo agregację.
- [ ] Wynik nie ujawnia niepotrzebnych danych osobowych.

## C. Zmiana danych
- [ ] Wartości są w zmiennych na początku skryptu.
- [ ] Skrypt ma podgląd przed zmianą i sprawdzenie po zmianie.
- [ ] Zmiana działa w transakcji i kontroluje liczbę zmienionych wierszy.
- [ ] `INSERT` nie utworzy duplikatu, a `UPDATE` i `DELETE` mają bezpieczny warunek.
- [ ] Skrypt kończy się `ROLLBACK`, a `COMMIT` pozostaje komentarzem.

## D. Odbiorca
- [ ] Instrukcja wyjaśnia prostym językiem, co uzupełnić i jaki wynik jest poprawny.
- [ ] Opisano, co zrobić przy innym wyniku i kto zatwierdza zmianę.
- [ ] `check_sql.py` nie zgłasza błędów.
