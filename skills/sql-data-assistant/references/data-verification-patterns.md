# Wzorce zestawień i weryfikacji danych

Każde zapytanie dopasuj do ustalonego typu bazy. Limit wierszy: PostgreSQL, MySQL i MariaDB `LIMIT 100`, SQL Server `SELECT TOP (100)`, Oracle `FETCH FIRST 100 ROWS ONLY`.

| Co sprawdzasz | Wzorzec | Poprawny wynik |
|---|---|---|
| Czy rekord istnieje | `WHERE klucz = zmienna` | Oczekiwana liczba wierszy |
| Liczba rekordów | `COUNT(*)` z warunkiem | Wartość ze zgłoszenia lub specyfikacji |
| Duplikaty | `GROUP BY klucz HAVING COUNT(*) > 1` | Brak wierszy |
| Brakujące wartości | `WHERE kolumna IS NULL` | Brak wierszy, jeśli pole jest wymagane |
| Rekordy bez powiązania | `LEFT JOIN ... WHERE druga.klucz IS NULL` | Brak wierszy |
| Niedozwolony status | `WHERE status NOT IN (...)` | Brak wierszy |
| Dane z okresu | `WHERE data >= od AND data < do` | Zakres zgodny ze zgłoszeniem |
| Porównanie źródła i celu | `COUNT(*)` i suma kontrolna po obu stronach | Te same wartości |

## Zasady

- Wybieraj tylko potrzebne kolumny.
- Okres zapisuj jako `>= początek` i `< następny dzień`, aby nie pominąć godzin.
- Przy `NOT IN` uwzględnij wartości `NULL` albo użyj `NOT EXISTS`.
- Sprawdź strefę czasową, gdy kolumna przechowuje datę z godziną.
- Przy dużych tabelach filtruj po kolumnach ze źródła wskazanych jako indeksowane i zacznij od małego zakresu.
- W opisie wyniku podaj, jaki wynik oznacza poprawne dane, a jaki problem do zgłoszenia.
