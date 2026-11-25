# Wzorce zestawień analitycznych i raportowych

Używaj w trybie `ANALYTICS_REPORT`. Nazwy `schemat.zamowienie`, `zamowienie_id`, `klient_id`, `data_zamowienia`,
`status`, `wartosc_netto` i wartości statusów są **przykładowe** — zastąp je nazwami ze schematu lub zgłoszenia
(zasada 2). Każdy wzorzec to tylko odczyt: `SELECT` z agregacją lub limitem.

## 1. Ściągawka różnic między bazami

| Potrzeba | PostgreSQL | SQL Server | Oracle | MySQL 8 / MariaDB 10.2+ |
|---|---|---|---|---|
| Parametry okresu | CTE `parametry` z `DATE '2026-01-01'` | `DECLARE @DataOd date = '2026-01-01';` | CTE `parametry` z `DATE '...' FROM dual` | `SET @data_od = DATE '2026-01-01';` |
| Początek miesiąca | `date_trunc('month', d)::date` | `DATEFROMPARTS(YEAR(d), MONTH(d), 1)` (2022+: `DATETRUNC(month, d)`) | `TRUNC(d, 'MM')` | `CAST(DATE_FORMAT(d, '%Y-%m-01') AS DATE)` |
| Początek tygodnia (pon.) | `date_trunc('week', d)::date` | `DATEADD(day, -((DATEPART(weekday, d) + @@DATEFIRST - 2) % 7), CAST(d AS date))` | `TRUNC(d, 'IW')` | `DATE(d) - INTERVAL WEEKDAY(d) DAY` |
| Dodanie miesiąca | `d + INTERVAL '1 month'` | `DATEADD(month, 1, d)` | `ADD_MONTHS(d, 1)` | `d + INTERVAL 1 MONTH` |
| Kalendarz (pełny szereg okresów) | `generate_series(od, do, interval)` | rekurencyjne CTE + `OPTION (MAXRECURSION n)` | `CONNECT BY LEVEL` | `WITH RECURSIVE` |
| Mediana / percentyl | `percentile_cont(0.5) WITHIN GROUP (ORDER BY x)` | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) OVER (PARTITION BY ...)` (tylko jako funkcja okna) | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x)` | MySQL: brak — `ROW_NUMBER` + `COUNT`; MariaDB 10.3+: `PERCENTILE_CONT ... OVER` |
| Łączenie tekstów w grupie | `string_agg(x, ', ' ORDER BY x)` | `STRING_AGG(x, ', ') WITHIN GROUP (ORDER BY x)` (2017+) | `LISTAGG(x, ', ') WITHIN GROUP (ORDER BY x)` | `GROUP_CONCAT(x ORDER BY x SEPARATOR ', ')` |
| Dzielenie bez błędu przez 0 | `a / NULLIF(b, 0)` | `a / NULLIF(b, 0)` | `a / NULLIF(b, 0)` | `a / NULLIF(b, 0)` |
| Uniknięcie dzielenia całkowitego | `100.0 * a / ...` lub `::numeric` | `100.0 * a / ...` lub `CAST(a AS decimal(19,4))` | zwykle zbędne (`NUMBER`) | zwykle zbędne |
| Limit wierszy | `LIMIT n` | `SELECT TOP (n)` | `FETCH FIRST n ROWS ONLY` (12c+) | `LIMIT n` |
| Funkcje okna i CTE od wersji | 8.4+ | 2012+ (pełne `ROWS`) | 8i / 9i+ | MySQL 8.0+, MariaDB 10.2+ |

`ROUND(wartość, n)` w PostgreSQL wymaga typu `numeric`; dla `double precision` dodaj `::numeric`.
W Oracle aliasu tabeli nie poprzedza się `AS` (`FROM schemat.zamowienie z`).

## 2. Zasady poprawnego raportu

1. **Miara ma definicję.** Dla każdej miary zapisz wzór, jednostkę i wykluczenia (np. „sprzedaż netto = suma
   `wartosc_netto` zamówień w statusach innych niż anulowane, w PLN”). Definicję spoza źródeł oznacz jako założenie.
2. **Okres jest półotwarty:** `>= początek` i `< pierwszy dzień po okresie`. Funkcja na kolumnie daty tylko w
   `SELECT` i `GROUP BY`, nie w `WHERE` (inaczej indeks nie zadziała).
3. **Strefa czasowa i data biznesowa.** Ustal, czy raport liczy po dacie utworzenia, zapłaty czy księgowania i w
   jakiej strefie. Gdy kolumna to `timestamp with time zone` lub UTC, przelicz na strefę raportu przed obcięciem do dnia.
4. **Bez zwielokrotnienia (fan-out).** Złączenie tabeli nagłówków z pozycjami powiela wartości nagłówka. Agreguj
   każdą tabelę szczegółów w osobnym CTE do poziomu klucza, a dopiero potem łącz. Liczbę obiektów licz przez
   `COUNT(DISTINCT klucz)`, gdy złączenie może powielić wiersze.
5. **Puste okresy są widoczne.** Szereg czasowy buduj z kalendarza i `LEFT JOIN`, a brak danych pokazuj jako `0`
   (`COALESCE`), żeby trend i porównania okres do okresu nie przeskakiwały miesięcy.
6. **`NULL` i dzielenie.** Każde dzielenie przez `NULLIF(mianownik, 0)`. Pamiętaj, że `AVG` i `COUNT(kolumna)`
   pomijają `NULL`, a `x <> 'A'` nie zwraca wierszy z `NULL` w `x`.
7. **Kontrola spójności (rekonsyliacja).** Do raportu dołącz zapytanie kontrolne: suma z raportu = suma bez podziału
   na wymiary dla tego samego okresu i filtrów; liczba wierszy źródłowych objętych raportem; liczba odrzuconych
   wierszy (np. `NULL` w wymiarze). Rozbieżność opisz jako problem do wyjaśnienia.
8. **Ochrona danych.** Raport zwraca agregaty. Identyfikatory osób, e-maile i inne dane osobowe tylko wtedy, gdy są
   niezbędne; rozważ próg minimalnej liczebności grupy (np. pokaż grupę dopiero od 5 osób).
9. **Wydajność.** Duże tabele: najpierw krótki okres testowy, filtr po kolumnach indeksowanych, plan wykonania
   (`EXPLAIN` / plan szacowany), uruchomienie na replice lub poza godzinami szczytu. Nie zalecaj `NOLOCK` ani
   `READ UNCOMMITTED` — dają niespójne sumy.

## 3. Pełny przykład: sprzedaż miesięcznie, zmiana m/m, udział i narastająco

Wynik: jeden wiersz na każdy miesiąc okresu (także bez sprzedaży), liczba zamówień, wartość netto, wartość
poprzedniego miesiąca, zmiana procentowa m/m, udział miesiąca w całym okresie i suma narastająca.

### PostgreSQL

```sql
-- Baza: PostgreSQL
-- Raport: sprzedaż netto miesięcznie (ANALYTICS_REPORT)
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od,   -- pierwszy dzień okresu (włącznie)
           DATE '2027-01-01' AS data_do    -- pierwszy dzień PO okresie (wyłącznie)
),
kalendarz AS (
    SELECT gs::date AS miesiac
    FROM parametry AS p
    CROSS JOIN generate_series(p.data_od, p.data_do - INTERVAL '1 day', INTERVAL '1 month') AS gs
),
sprzedaz AS (
    SELECT date_trunc('month', z.data_zamowienia)::date AS miesiac,
           COUNT(*) AS liczba_zamowien,
           SUM(z.wartosc_netto)::numeric AS wartosc_netto
    FROM schemat.zamowienie AS z
    CROSS JOIN parametry AS p
    WHERE z.data_zamowienia >= p.data_od
      AND z.data_zamowienia < p.data_do
      AND z.status <> 'ANULOWANE'          -- wykluczenie do potwierdzenia w definicji miary
    GROUP BY date_trunc('month', z.data_zamowienia)::date
),
szereg AS (
    SELECT k.miesiac,
           COALESCE(s.liczba_zamowien, 0) AS liczba_zamowien,
           COALESCE(s.wartosc_netto, 0) AS wartosc_netto
    FROM kalendarz AS k
    LEFT JOIN sprzedaz AS s ON s.miesiac = k.miesiac
),
z_poprzednim AS (
    SELECT sz.miesiac, sz.liczba_zamowien, sz.wartosc_netto,
           LAG(sz.wartosc_netto) OVER (ORDER BY sz.miesiac) AS wartosc_poprzedni_miesiac
    FROM szereg AS sz
)
SELECT zp.miesiac,
       zp.liczba_zamowien,
       zp.wartosc_netto,
       zp.wartosc_poprzedni_miesiac,
       ROUND(100.0 * (zp.wartosc_netto - zp.wartosc_poprzedni_miesiac)
             / NULLIF(zp.wartosc_poprzedni_miesiac, 0), 1) AS zmiana_mm_proc,
       ROUND(100.0 * zp.wartosc_netto / NULLIF(SUM(zp.wartosc_netto) OVER (), 0), 1) AS udzial_proc,
       SUM(zp.wartosc_netto) OVER (ORDER BY zp.miesiac ROWS UNBOUNDED PRECEDING) AS narastajaco
FROM z_poprzednim AS zp
ORDER BY zp.miesiac;
```

### SQL Server

```sql
-- Baza: SQL Server
-- Raport: sprzedaż netto miesięcznie (ANALYTICS_REPORT)
DECLARE @DataOd date = '2026-01-01';   -- pierwszy dzień okresu (włącznie)
DECLARE @DataDo date = '2027-01-01';   -- pierwszy dzień PO okresie (wyłącznie)

WITH kalendarz AS (
    SELECT @DataOd AS miesiac
    UNION ALL
    SELECT DATEADD(month, 1, k.miesiac) FROM kalendarz AS k WHERE DATEADD(month, 1, k.miesiac) < @DataDo
),
sprzedaz AS (
    SELECT DATEFROMPARTS(YEAR(z.data_zamowienia), MONTH(z.data_zamowienia), 1) AS miesiac,
           COUNT(*) AS liczba_zamowien,
           SUM(CAST(z.wartosc_netto AS decimal(19, 2))) AS wartosc_netto
    FROM schemat.zamowienie AS z
    WHERE z.data_zamowienia >= @DataOd
      AND z.data_zamowienia < @DataDo
      AND z.status <> N'ANULOWANE'
    GROUP BY DATEFROMPARTS(YEAR(z.data_zamowienia), MONTH(z.data_zamowienia), 1)
),
szereg AS (
    SELECT k.miesiac,
           COALESCE(s.liczba_zamowien, 0) AS liczba_zamowien,
           COALESCE(s.wartosc_netto, 0) AS wartosc_netto
    FROM kalendarz AS k
    LEFT JOIN sprzedaz AS s ON s.miesiac = k.miesiac
),
z_poprzednim AS (
    SELECT sz.miesiac, sz.liczba_zamowien, sz.wartosc_netto,
           LAG(sz.wartosc_netto) OVER (ORDER BY sz.miesiac) AS wartosc_poprzedni_miesiac
    FROM szereg AS sz
)
SELECT zp.miesiac,
       zp.liczba_zamowien,
       zp.wartosc_netto,
       zp.wartosc_poprzedni_miesiac,
       ROUND(100.0 * (zp.wartosc_netto - zp.wartosc_poprzedni_miesiac)
             / NULLIF(zp.wartosc_poprzedni_miesiac, 0), 1) AS zmiana_mm_proc,
       ROUND(100.0 * zp.wartosc_netto / NULLIF(SUM(zp.wartosc_netto) OVER (), 0), 1) AS udzial_proc,
       SUM(zp.wartosc_netto) OVER (ORDER BY zp.miesiac ROWS UNBOUNDED PRECEDING) AS narastajaco
FROM z_poprzednim AS zp
ORDER BY zp.miesiac
OPTION (MAXRECURSION 400);
```

### Oracle

```sql
-- Baza: Oracle
-- Raport: sprzedaż netto miesięcznie (ANALYTICS_REPORT)
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od,   -- pierwszy dzień okresu (włącznie)
           DATE '2027-01-01' AS data_do    -- pierwszy dzień PO okresie (wyłącznie)
    FROM dual
),
kalendarz AS (
    SELECT ADD_MONTHS(p.data_od, LEVEL - 1) AS miesiac
    FROM parametry p
    CONNECT BY ADD_MONTHS(p.data_od, LEVEL - 1) < p.data_do
),
sprzedaz AS (
    SELECT TRUNC(z.data_zamowienia, 'MM') AS miesiac,
           COUNT(*) AS liczba_zamowien,
           SUM(z.wartosc_netto) AS wartosc_netto
    FROM schemat.zamowienie z
    CROSS JOIN parametry p
    WHERE z.data_zamowienia >= p.data_od
      AND z.data_zamowienia < p.data_do
      AND z.status <> 'ANULOWANE'
    GROUP BY TRUNC(z.data_zamowienia, 'MM')
),
szereg AS (
    SELECT k.miesiac,
           COALESCE(s.liczba_zamowien, 0) AS liczba_zamowien,
           COALESCE(s.wartosc_netto, 0) AS wartosc_netto
    FROM kalendarz k
    LEFT JOIN sprzedaz s ON s.miesiac = k.miesiac
),
z_poprzednim AS (
    SELECT sz.miesiac, sz.liczba_zamowien, sz.wartosc_netto,
           LAG(sz.wartosc_netto) OVER (ORDER BY sz.miesiac) AS wartosc_poprzedni_miesiac
    FROM szereg sz
)
SELECT zp.miesiac,
       zp.liczba_zamowien,
       zp.wartosc_netto,
       zp.wartosc_poprzedni_miesiac,
       ROUND(100 * (zp.wartosc_netto - zp.wartosc_poprzedni_miesiac)
             / NULLIF(zp.wartosc_poprzedni_miesiac, 0), 1) AS zmiana_mm_proc,
       ROUND(100 * zp.wartosc_netto / NULLIF(SUM(zp.wartosc_netto) OVER (), 0), 1) AS udzial_proc,
       SUM(zp.wartosc_netto) OVER (ORDER BY zp.miesiac ROWS UNBOUNDED PRECEDING) AS narastajaco
FROM z_poprzednim zp
ORDER BY zp.miesiac;
```

### MySQL i MariaDB

```sql
-- Baza: MySQL
-- Raport: sprzedaż netto miesięcznie (ANALYTICS_REPORT); MySQL 8.0+ lub MariaDB 10.2+
SET @data_od = DATE '2026-01-01';   -- pierwszy dzień okresu (włącznie)
SET @data_do = DATE '2027-01-01';   -- pierwszy dzień PO okresie (wyłącznie)

WITH RECURSIVE kalendarz AS (
    SELECT CAST(@data_od AS DATE) AS miesiac
    UNION ALL
    SELECT k.miesiac + INTERVAL 1 MONTH FROM kalendarz AS k WHERE k.miesiac + INTERVAL 1 MONTH < @data_do
),
sprzedaz AS (
    SELECT CAST(DATE_FORMAT(z.data_zamowienia, '%Y-%m-01') AS DATE) AS miesiac,
           COUNT(*) AS liczba_zamowien,
           SUM(z.wartosc_netto) AS wartosc_netto
    FROM schemat.zamowienie AS z
    WHERE z.data_zamowienia >= @data_od
      AND z.data_zamowienia < @data_do
      AND z.status <> 'ANULOWANE'
    GROUP BY CAST(DATE_FORMAT(z.data_zamowienia, '%Y-%m-01') AS DATE)
),
szereg AS (
    SELECT k.miesiac,
           COALESCE(s.liczba_zamowien, 0) AS liczba_zamowien,
           COALESCE(s.wartosc_netto, 0) AS wartosc_netto
    FROM kalendarz AS k
    LEFT JOIN sprzedaz AS s ON s.miesiac = k.miesiac
),
z_poprzednim AS (
    SELECT sz.miesiac, sz.liczba_zamowien, sz.wartosc_netto,
           LAG(sz.wartosc_netto) OVER (ORDER BY sz.miesiac) AS wartosc_poprzedni_miesiac
    FROM szereg AS sz
)
SELECT zp.miesiac,
       zp.liczba_zamowien,
       zp.wartosc_netto,
       zp.wartosc_poprzedni_miesiac,
       ROUND(100 * (zp.wartosc_netto - zp.wartosc_poprzedni_miesiac)
             / NULLIF(zp.wartosc_poprzedni_miesiac, 0), 1) AS zmiana_mm_proc,
       ROUND(100 * zp.wartosc_netto / NULLIF(SUM(zp.wartosc_netto) OVER (), 0), 1) AS udzial_proc,
       SUM(zp.wartosc_netto) OVER (ORDER BY zp.miesiac ROWS UNBOUNDED PRECEDING) AS narastajaco
FROM z_poprzednim AS zp
ORDER BY zp.miesiac;
```

## 4. Katalog wzorców analitycznych

Przykłady w składni PostgreSQL; przenieś je na inną bazę według ściągawki z sekcji 1.

| Potrzeba | Technika | Na co uważać |
|---|---|---|
| Udział w całości | `x / NULLIF(SUM(x) OVER (), 0)` | Udział w grupie: `OVER (PARTITION BY grupa)` |
| Narastająco (YTD, MTD) | `SUM(x) OVER (PARTITION BY rok ORDER BY okres ROWS UNBOUNDED PRECEDING)` | Jawnie `ROWS`, bo domyślne `RANGE` łączy remisy |
| Średnia krocząca | `AVG(x) OVER (ORDER BY okres ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` | Wymaga pełnego kalendarza; pierwsze okresy mają mniej punktów |
| Okres do okresu, rok do roku | `LAG(x, 1)` / `LAG(x, 12) OVER (ORDER BY miesiac)` | Bez kalendarza `LAG` przeskoczy brakujące miesiące |
| Top N w każdej grupie | `ROW_NUMBER() OVER (PARTITION BY grupa ORDER BY x DESC)` i filtr `<= N` | Remisy: `RANK` lub `DENSE_RANK` |
| Pareto / ABC | udział narastający po sortowaniu malejącym; A do 80%, B do 95%, C reszta | Progi do potwierdzenia z użytkownikiem |
| Sumy częściowe i ogólne | `GROUP BY ROLLUP (a, b)` lub `GROUPING SETS` + `GROUPING()` | MySQL: `WITH ROLLUP`; wiersze sum oznacz etykietą |
| Tabela przestawna | agregacja warunkowa `SUM(CASE WHEN wymiar = 'X' THEN x ELSE 0 END)` | Przenośna; `PIVOT` tylko SQL Server i Oracle |
| Mediana, percentyle | `percentile_cont(0.5) WITHIN GROUP (ORDER BY x)` | Średnia przy skośnym rozkładzie wprowadza w błąd |
| Rozkład (histogram) | przedziały `CASE` lub `width_bucket` | Przedziały rozłączne i pokrywające cały zakres |
| Kohorty i retencja | kohorta = miesiąc pierwszej aktywności; aktywność w kolejnych miesiącach | Liczebność kohorty w mianowniku |
| Lejek konwersji | `COUNT(DISTINCT CASE WHEN etap = ... THEN id END)` dla każdego etapu | Kolejność etapów i okno czasowe do ustalenia |
| Ostatni stan rekordu | `ROW_NUMBER() OVER (PARTITION BY klucz ORDER BY data DESC) = 1` | Remis dat: dodaj drugi klucz sortowania |
| Rekonsyliacja | suma raportu vs suma bez wymiarów | Część raportu, nie opcja |

### Top N klientów w każdym miesiącu z udziałem

```sql
-- Baza: PostgreSQL
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od, DATE '2026-07-01' AS data_do, 5 AS top_n
),
klient_miesiac AS (
    SELECT date_trunc('month', z.data_zamowienia)::date AS miesiac,
           z.klient_id,
           SUM(z.wartosc_netto)::numeric AS wartosc_netto
    FROM schemat.zamowienie AS z
    CROSS JOIN parametry AS p
    WHERE z.data_zamowienia >= p.data_od
      AND z.data_zamowienia < p.data_do
    GROUP BY date_trunc('month', z.data_zamowienia)::date, z.klient_id
),
ranking AS (
    SELECT km.miesiac, km.klient_id, km.wartosc_netto,
           ROW_NUMBER() OVER (PARTITION BY km.miesiac ORDER BY km.wartosc_netto DESC, km.klient_id) AS pozycja,
           ROUND(100.0 * km.wartosc_netto / NULLIF(SUM(km.wartosc_netto) OVER (PARTITION BY km.miesiac), 0), 1) AS udzial_proc
    FROM klient_miesiac AS km
)
SELECT r.miesiac, r.pozycja, r.klient_id, r.wartosc_netto, r.udzial_proc
FROM ranking AS r
CROSS JOIN parametry AS p
WHERE r.pozycja <= p.top_n
ORDER BY r.miesiac, r.pozycja;
```

### Analiza ABC (Pareto) klientów

```sql
-- Baza: PostgreSQL
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od, DATE '2027-01-01' AS data_do
),
klient AS (
    SELECT z.klient_id, SUM(z.wartosc_netto)::numeric AS wartosc_netto
    FROM schemat.zamowienie AS z
    CROSS JOIN parametry AS p
    WHERE z.data_zamowienia >= p.data_od
      AND z.data_zamowienia < p.data_do
    GROUP BY z.klient_id
),
narastajaco AS (
    SELECT k.klient_id, k.wartosc_netto,
           SUM(k.wartosc_netto) OVER (ORDER BY k.wartosc_netto DESC, k.klient_id ROWS UNBOUNDED PRECEDING)
             / NULLIF(SUM(k.wartosc_netto) OVER (), 0) AS udzial_narastajacy
    FROM klient AS k
)
SELECT CASE WHEN n.udzial_narastajacy <= 0.80 THEN 'A'
            WHEN n.udzial_narastajacy <= 0.95 THEN 'B'
            ELSE 'C' END AS klasa,
       COUNT(*) AS liczba_klientow,
       SUM(n.wartosc_netto) AS wartosc_netto
FROM narastajaco AS n
GROUP BY 1
ORDER BY 1;
```

### Tabela przestawna z sumami częściowymi

```sql
-- Baza: PostgreSQL
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od, DATE '2026-04-01' AS data_do
)
SELECT CASE WHEN GROUPING(z.status) = 1 THEN 'RAZEM' ELSE z.status END AS status,
       SUM(CASE WHEN z.data_zamowienia < DATE '2026-02-01' THEN z.wartosc_netto ELSE 0 END) AS styczen,
       SUM(CASE WHEN z.data_zamowienia >= DATE '2026-02-01' AND z.data_zamowienia < DATE '2026-03-01'
                THEN z.wartosc_netto ELSE 0 END) AS luty,
       SUM(CASE WHEN z.data_zamowienia >= DATE '2026-03-01' THEN z.wartosc_netto ELSE 0 END) AS marzec,
       SUM(z.wartosc_netto) AS kwartal
FROM schemat.zamowienie AS z
CROSS JOIN parametry AS p
WHERE z.data_zamowienia >= p.data_od
  AND z.data_zamowienia < p.data_do
GROUP BY ROLLUP (z.status)
ORDER BY GROUPING(z.status), z.status;
```

### Kohorty: retencja klientów według miesiąca pierwszego zamówienia

```sql
-- Baza: PostgreSQL
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od, DATE '2027-01-01' AS data_do
),
aktywnosc AS (
    SELECT DISTINCT z.klient_id, date_trunc('month', z.data_zamowienia)::date AS miesiac
    FROM schemat.zamowienie AS z
    CROSS JOIN parametry AS p
    WHERE z.data_zamowienia >= p.data_od
      AND z.data_zamowienia < p.data_do
),
kohorta AS (
    SELECT a.klient_id, MIN(a.miesiac) AS miesiac_kohorty
    FROM aktywnosc AS a
    GROUP BY a.klient_id
),
retencja AS (
    SELECT k.miesiac_kohorty,
           (EXTRACT(YEAR FROM age(a.miesiac, k.miesiac_kohorty)) * 12
            + EXTRACT(MONTH FROM age(a.miesiac, k.miesiac_kohorty)))::int AS miesiac_od_startu,
           COUNT(DISTINCT a.klient_id) AS aktywni_klienci
    FROM aktywnosc AS a
    JOIN kohorta AS k ON k.klient_id = a.klient_id
    GROUP BY 1, 2
)
SELECT r.miesiac_kohorty,
       r.miesiac_od_startu,
       r.aktywni_klienci,
       ROUND(100.0 * r.aktywni_klienci
             / NULLIF(FIRST_VALUE(r.aktywni_klienci) OVER (PARTITION BY r.miesiac_kohorty ORDER BY r.miesiac_od_startu), 0), 1) AS retencja_proc
FROM retencja AS r
ORDER BY r.miesiac_kohorty, r.miesiac_od_startu;
```

Uwaga: klienci aktywni przed `data_od` trafią do kohorty z pierwszego miesiąca okresu. Gdy kohorta ma oznaczać
pierwsze zamówienie w historii, licz `kohorta` bez filtra okresu.

### Zapytanie kontrolne (rekonsyliacja)

```sql
-- Baza: PostgreSQL
-- Suma i liczba wierszy muszą być równe sumom z raportu dla tego samego okresu i filtrów.
WITH parametry AS (
    SELECT DATE '2026-01-01' AS data_od, DATE '2027-01-01' AS data_do
)
SELECT COUNT(*) FILTER (WHERE z.status <> 'ANULOWANE') AS liczba_zamowien_w_raporcie,
       SUM(z.wartosc_netto) FILTER (WHERE z.status <> 'ANULOWANE') AS wartosc_netto_w_raporcie,
       COUNT(*) FILTER (WHERE z.status = 'ANULOWANE') AS wykluczone_anulowane,
       COUNT(*) FILTER (WHERE z.status IS NULL) AS pominiete_bez_statusu,
       COUNT(*) FILTER (WHERE z.wartosc_netto IS NULL) AS bez_wartosci,
       MIN(z.data_zamowienia) AS pierwsza_data,
       MAX(z.data_zamowienia) AS ostatnia_data
FROM schemat.zamowienie AS z
CROSS JOIN parametry AS p
WHERE z.data_zamowienia >= p.data_od
  AND z.data_zamowienia < p.data_do;
```

`pominiete_bez_statusu` większe od zera oznacza, że warunek `status <> 'ANULOWANE'` po cichu pominął wiersze —
opisz to w odpowiedzi i ustal z użytkownikiem, czy mają być w raporcie.
