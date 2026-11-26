# Bezpieczne szablony zmiany danych

Zastąp `schemat.tabela`, `kolumna_klucza`, `kolumna_wartosci`, `NAZWA_BAZY` i wartości parametrów nazwami ze
źródeł. Zachowaj kolejność kroków i opakowanie skryptu (zasada 14).

## Opakowanie skryptu

Każdy skrypt zmieniający dane ma ten sam układ:

| Część | Co zawiera |
|---|---|
| Nagłówek | ramka komentarza: cel, zgłoszenie, baza i środowisko, autor i data, lista kroków, jak uruchomić i zatwierdzić |
| `-- Baza: <typ>` | wiersz wymagany przez `check_sql.py` |
| Ustawienia | SQL Server: `SET XACT_ABORT ON`, `SET NOCOUNT ON`; usunięcie pozostałej tabeli tymczasowej |
| Obsługa błędów | SQL Server `BEGIN TRY … BEGIN CATCH`, PostgreSQL blok `DO` z `RAISE EXCEPTION`, Oracle sekcja `EXCEPTION`; każdy błąd wycofuje całość |
| KROK 1: parametry | wszystkie wartości do uzupełnienia, oczekiwana baza i liczba wierszy |
| Kontrola środowiska | serwer i baza wypisane na początku; inna baza niż oczekiwana przerywa skrypt |
| KROK 2: plan zmian | tabela tymczasowa z kluczem, poprzednią i nową wartością (kopia do odtworzenia) |
| KROK 3: PRZED | podgląd planu do zachowania przed zmianą |
| KROK 4: kontrola | liczba wierszy w planie równa oczekiwanej, inaczej przerwanie |
| KROK 5: zmiana | `UPDATE` / `INSERT` tylko według planu, z komunikatem o liczbie wierszy i jej kontrolą |
| KROK 6: PO | sprawdzenie wyniku |
| KROK 7: zakończenie | domyślnie `ROLLBACK` z komunikatem (serwer, baza); `COMMIT` tylko jako komentarz |
| Sprzątanie i odtworzenie | usunięcie tabeli tymczasowej; skrypt odtworzenia w komentarzu, oparty na wyniku KROKU 3 |

Komunikaty kroków piszą to samo, co komentarze (`KROK 5: zmieniono wierszy: 3`), żeby tester widział, gdzie jest.

## SQL Server

### Zmiana wartości

```sql
/* =============================================================================
   SKRYPT:        Zmiana kolumna_wartosci dla wskazanego klucza
   ZGŁOSZENIE:    NUMER
   BAZA:          SQL Server · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola · 5 UPDATE · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: SQL Server
SET XACT_ABORT ON;
SET NOCOUNT ON;

DROP TABLE IF EXISTS #PlanZmian;

BEGIN TRY
    BEGIN TRANSACTION;

    DECLARE @Serwer sysname = @@SERVERNAME;
    DECLARE @Baza sysname = DB_NAME();
    PRINT N'Serwer: ' + @Serwer + N', baza: ' + @Baza;

    /* KROK 1: parametry - uzupełnij przed uruchomieniem */
    DECLARE @OczekiwanaBaza sysname = N'NAZWA_BAZY';
    DECLARE @Klucz int = 0;
    DECLARE @StaraWartosc nvarchar(200) = N'STARA';
    DECLARE @NowaWartosc nvarchar(200) = N'NOWA';
    DECLARE @OczekiwaneWiersze int = 1;
    DECLARE @Zmienione int;

    IF @Baza <> @OczekiwanaBaza
        THROW 50000, N'KROK 1: skrypt uruchomiono na innej bazie niż oczekiwana.', 1;

    /* KROK 2: plan zmian z poprzednimi wartościami (kopia do odtworzenia) */
    SELECT t.kolumna_klucza,
           t.kolumna_wartosci AS PoprzedniaWartosc,
           @NowaWartosc AS NowaWartosc
    INTO #PlanZmian
    FROM schemat.tabela AS t WITH (UPDLOCK, HOLDLOCK)
    WHERE t.kolumna_klucza = @Klucz
      AND t.kolumna_wartosci = @StaraWartosc;

    /* KROK 3: PRZED - zachowaj ten wynik przed zatwierdzeniem */
    SELECT p.kolumna_klucza AS [3. PRZED - plan zmian], p.PoprzedniaWartosc, p.NowaWartosc
    FROM #PlanZmian AS p
    ORDER BY p.kolumna_klucza;

    /* KROK 4: kontrola liczby wierszy w planie */
    IF (SELECT COUNT(*) FROM #PlanZmian) <> @OczekiwaneWiersze
        THROW 50001, N'KROK 4: liczba wierszy w planie jest inna niż oczekiwana.', 1;

    /* KROK 5: UPDATE tylko wierszy z planu, nadal z poprzednią wartością */
    UPDATE t
    SET t.kolumna_wartosci = p.NowaWartosc
    FROM schemat.tabela AS t
    JOIN #PlanZmian AS p ON p.kolumna_klucza = t.kolumna_klucza
    WHERE t.kolumna_wartosci = p.PoprzedniaWartosc;

    SET @Zmienione = @@ROWCOUNT;
    PRINT N'KROK 5: zmieniono wierszy: ' + CAST(@Zmienione AS nvarchar(10));
    IF @Zmienione <> @OczekiwaneWiersze
        THROW 50002, N'KROK 5: liczba zmienionych wierszy jest inna niż oczekiwana.', 1;

    /* KROK 6: PO - sprawdzenie wyniku */
    SELECT t.kolumna_klucza AS [6. PO - wynik], t.kolumna_wartosci
    FROM schemat.tabela AS t
    JOIN #PlanZmian AS p ON p.kolumna_klucza = t.kolumna_klucza
    ORDER BY t.kolumna_klucza;

    /* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
    PRINT N'------------- KONIEC -------------';
    ROLLBACK TRANSACTION; PRINT N'WYCOFANO (ROLLBACK): ' + @Serwer + N', baza: ' + @Baza;
    -- COMMIT TRANSACTION; PRINT N'ZATWIERDZONO (COMMIT): ' + @Serwer + N', baza: ' + @Baza;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT N'BŁĄD - wycofano wszystkie zmiany.';
    THROW;
END CATCH;

DROP TABLE IF EXISTS #PlanZmian;

/* ODTWORZENIE (tylko po COMMIT, gdy trzeba cofnąć zmianę):
   wpisz zachowane wiersze z KROKU 3 i uruchom w tym samym opakowaniu, z kontrolą liczby wierszy:
   UPDATE t SET t.kolumna_wartosci = k.PoprzedniaWartosc
   FROM schemat.tabela AS t
   JOIN (VALUES (0, N'STARA', N'NOWA')) AS k (kolumna_klucza, PoprzedniaWartosc, NowaWartosc)
     ON k.kolumna_klucza = t.kolumna_klucza
   WHERE t.kolumna_wartosci = k.NowaWartosc;
*/
```

### Dodanie wiersza

```sql
/* =============================================================================
   SKRYPT:        Dodanie wiersza z kluczem, którego jeszcze nie ma
   ZGŁOSZENIE:    NUMER
   BAZA:          SQL Server · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola · 5 INSERT · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: SQL Server
SET XACT_ABORT ON;
SET NOCOUNT ON;

DROP TABLE IF EXISTS #PlanZmian;

BEGIN TRY
    BEGIN TRANSACTION;

    DECLARE @Serwer sysname = @@SERVERNAME;
    DECLARE @Baza sysname = DB_NAME();
    PRINT N'Serwer: ' + @Serwer + N', baza: ' + @Baza;

    /* KROK 1: parametry - uzupełnij przed uruchomieniem */
    DECLARE @OczekiwanaBaza sysname = N'NAZWA_BAZY';
    DECLARE @Klucz int = 0;
    DECLARE @Wartosc nvarchar(200) = N'WARTOSC';
    DECLARE @OczekiwaneWiersze int = 1;
    DECLARE @Dodane int;

    IF @Baza <> @OczekiwanaBaza
        THROW 50000, N'KROK 1: skrypt uruchomiono na innej bazie niż oczekiwana.', 1;

    /* KROK 2: plan - tylko klucze, których jeszcze nie ma */
    SELECT @Klucz AS kolumna_klucza, @Wartosc AS Wartosc
    INTO #PlanZmian
    WHERE NOT EXISTS (
        SELECT 1 FROM schemat.tabela AS t WITH (UPDLOCK, HOLDLOCK) WHERE t.kolumna_klucza = @Klucz
    );

    /* KROK 3: PRZED - wiersze do dodania */
    SELECT p.kolumna_klucza AS [3. PRZED - do dodania], p.Wartosc
    FROM #PlanZmian AS p;

    /* KROK 4: kontrola liczby wierszy w planie */
    IF (SELECT COUNT(*) FROM #PlanZmian) <> @OczekiwaneWiersze
        THROW 50001, N'KROK 4: liczba wierszy w planie jest inna niż oczekiwana (wiersz już istnieje?).', 1;

    /* KROK 5: INSERT tylko brakujących wierszy */
    INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
    SELECT p.kolumna_klucza, p.Wartosc
    FROM #PlanZmian AS p
    WHERE NOT EXISTS (
        SELECT 1 FROM schemat.tabela AS t WITH (UPDLOCK, HOLDLOCK) WHERE t.kolumna_klucza = p.kolumna_klucza
    );

    SET @Dodane = @@ROWCOUNT;
    PRINT N'KROK 5: dodano wierszy: ' + CAST(@Dodane AS nvarchar(10));
    IF @Dodane <> @OczekiwaneWiersze
        THROW 50002, N'KROK 5: liczba dodanych wierszy jest inna niż oczekiwana.', 1;

    /* KROK 6: PO - sprawdzenie wyniku */
    SELECT t.kolumna_klucza AS [6. PO - wynik], t.kolumna_wartosci
    FROM schemat.tabela AS t
    JOIN #PlanZmian AS p ON p.kolumna_klucza = t.kolumna_klucza;

    /* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
    PRINT N'------------- KONIEC -------------';
    ROLLBACK TRANSACTION; PRINT N'WYCOFANO (ROLLBACK): ' + @Serwer + N', baza: ' + @Baza;
    -- COMMIT TRANSACTION; PRINT N'ZATWIERDZONO (COMMIT): ' + @Serwer + N', baza: ' + @Baza;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT N'BŁĄD - wycofano wszystkie zmiany.';
    THROW;
END CATCH;

DROP TABLE IF EXISTS #PlanZmian;

/* ODTWORZENIE (tylko po COMMIT): usuń dodane wiersze po kluczu z KROKU 3, z kontrolą liczby wierszy
   i warunkiem na wartość, żeby nie usunąć wiersza zmienionego w międzyczasie:
   DELETE t FROM schemat.tabela AS t WHERE t.kolumna_klucza = 0 AND t.kolumna_wartosci = N'WARTOSC';
*/
```

### Plan zmian: uzupełnienie i dodanie w jednym skrypcie

Gdy część wierszy istnieje (do uzupełnienia), a części brakuje (do dodania), plan ma kolumnę `Operacja`.
Kolejność: plan → PRZED → kontrola liczby wierszy dla każdej operacji → `UPDATE` → `INSERT` → PO.

```sql
/* =============================================================================
   SKRYPT:        Uzupełnienie pustych wartości i dodanie brakujących wierszy według planu
   ZGŁOSZENIE:    NUMER
   BAZA:          SQL Server · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola · 5 UPDATE · 6 INSERT · 7 PO · 8 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: SQL Server
SET XACT_ABORT ON;
SET NOCOUNT ON;

DROP TABLE IF EXISTS #PlanZmian;

BEGIN TRY
    BEGIN TRANSACTION;

    DECLARE @Serwer sysname = @@SERVERNAME;
    DECLARE @Baza sysname = DB_NAME();
    PRINT N'Serwer: ' + @Serwer + N', baza: ' + @Baza;

    /* KROK 1: parametry - uzupełnij przed uruchomieniem */
    DECLARE @OczekiwanaBaza sysname = N'NAZWA_BAZY';
    DECLARE @IdRodzaju int = 0;                 -- rodzaj wartości, którego dotyczy zmiana
    DECLARE @DomyslnaWartosc nvarchar(200) = N'WARTOSC';
    DECLARE @OczekiwaneUzupelnienia int = 0;    -- z zapytania diagnostycznego
    DECLARE @OczekiwaneDodania int = 0;         -- z zapytania diagnostycznego
    DECLARE @Wiersze int;

    IF @Baza <> @OczekiwanaBaza
        THROW 50000, N'KROK 1: skrypt uruchomiono na innej bazie niż oczekiwana.', 1;

    /* KROK 2: plan - obiekty bez wartości: UZUPEŁNIJ (wiersz jest, wartość pusta) albo DODAJ (brak wiersza) */
    SELECT o.kolumna_klucza,
           w.kolumna_wartosci AS PoprzedniaWartosc,
           @DomyslnaWartosc AS NowaWartosc,
           CASE WHEN w.kolumna_klucza IS NULL THEN N'DODAJ' ELSE N'UZUPEŁNIJ' END AS Operacja
    INTO #PlanZmian
    FROM schemat.obiekt AS o
    LEFT JOIN schemat.wartosc AS w WITH (UPDLOCK, HOLDLOCK)
           ON w.kolumna_klucza = o.kolumna_klucza
          AND w.id_rodzaju = @IdRodzaju
    WHERE o.aktywny = 1
      AND NULLIF(LTRIM(RTRIM(w.kolumna_wartosci)), N'') IS NULL;

    /* KROK 3: PRZED - zachowaj ten wynik przed zatwierdzeniem */
    SELECT p.Operacja AS [3. PRZED - plan zmian], p.kolumna_klucza, p.PoprzedniaWartosc, p.NowaWartosc
    FROM #PlanZmian AS p
    ORDER BY p.Operacja, p.kolumna_klucza;

    /* KROK 4: kontrola liczby wierszy dla każdej operacji */
    IF (SELECT COUNT(*) FROM #PlanZmian WHERE Operacja = N'UZUPEŁNIJ') <> @OczekiwaneUzupelnienia
        THROW 50001, N'KROK 4: liczba wierszy do uzupełnienia jest inna niż oczekiwana.', 1;
    IF (SELECT COUNT(*) FROM #PlanZmian WHERE Operacja = N'DODAJ') <> @OczekiwaneDodania
        THROW 50002, N'KROK 4: liczba wierszy do dodania jest inna niż oczekiwana.', 1;

    /* KROK 5: UPDATE pustych wartości */
    UPDATE w
    SET w.kolumna_wartosci = p.NowaWartosc
    FROM schemat.wartosc AS w
    JOIN #PlanZmian AS p ON p.kolumna_klucza = w.kolumna_klucza
    WHERE w.id_rodzaju = @IdRodzaju
      AND p.Operacja = N'UZUPEŁNIJ'
      AND NULLIF(LTRIM(RTRIM(w.kolumna_wartosci)), N'') IS NULL;

    SET @Wiersze = @@ROWCOUNT;
    PRINT N'KROK 5: uzupełniono wierszy: ' + CAST(@Wiersze AS nvarchar(10));
    IF @Wiersze <> @OczekiwaneUzupelnienia
        THROW 50003, N'KROK 5: liczba uzupełnionych wierszy jest inna niż oczekiwana.', 1;

    /* KROK 6: INSERT brakujących wierszy */
    INSERT INTO schemat.wartosc (id_rodzaju, kolumna_klucza, kolumna_wartosci)
    SELECT @IdRodzaju, p.kolumna_klucza, p.NowaWartosc
    FROM #PlanZmian AS p
    WHERE p.Operacja = N'DODAJ'
      AND NOT EXISTS (
          SELECT 1 FROM schemat.wartosc AS w WITH (UPDLOCK, HOLDLOCK)
          WHERE w.kolumna_klucza = p.kolumna_klucza AND w.id_rodzaju = @IdRodzaju
      );

    SET @Wiersze = @@ROWCOUNT;
    PRINT N'KROK 6: dodano wierszy: ' + CAST(@Wiersze AS nvarchar(10));
    IF @Wiersze <> @OczekiwaneDodania
        THROW 50004, N'KROK 6: liczba dodanych wierszy jest inna niż oczekiwana.', 1;

    /* KROK 7: PO - sprawdzenie wyniku */
    SELECT p.Operacja AS [7. PO - wynik], w.kolumna_klucza, w.kolumna_wartosci
    FROM #PlanZmian AS p
    JOIN schemat.wartosc AS w ON w.kolumna_klucza = p.kolumna_klucza AND w.id_rodzaju = @IdRodzaju
    ORDER BY p.Operacja, w.kolumna_klucza;

    /* KROK 8: zakończenie - domyślnie nic nie jest zapisywane */
    PRINT N'------------- KONIEC -------------';
    ROLLBACK TRANSACTION; PRINT N'WYCOFANO (ROLLBACK): ' + @Serwer + N', baza: ' + @Baza;
    -- COMMIT TRANSACTION; PRINT N'ZATWIERDZONO (COMMIT): ' + @Serwer + N', baza: ' + @Baza;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    PRINT N'BŁĄD - wycofano wszystkie zmiany.';
    THROW;
END CATCH;

DROP TABLE IF EXISTS #PlanZmian;

/* ODTWORZENIE (tylko po COMMIT): na podstawie wyniku KROKU 3
   - UZUPEŁNIJ: przywróć PoprzedniaWartosc z warunkiem, że wartość nadal równa się NowaWartosc,
   - DODAJ: usuń dodane wiersze po kluczu i id_rodzaju, z tym samym warunkiem na wartość.
*/
```

## PostgreSQL

W `psql` dodaj na początku `\set ON_ERROR_STOP on`, żeby błąd zatrzymał skrypt przed kolejnymi krokami.

### Zmiana wartości

```sql
/* =============================================================================
   SKRYPT:        Zmiana kolumna_wartosci dla wskazanego klucza
   ZGŁOSZENIE:    NUMER
   BAZA:          PostgreSQL · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola i UPDATE · 5 PO · 6 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: PostgreSQL
BEGIN;

/* KROK 1: parametry - uzupełnij przed uruchomieniem */
CREATE TEMP TABLE parametry ON COMMIT DROP AS
SELECT 'NAZWA_BAZY'::text AS oczekiwana_baza,
       0::integer AS klucz,
       'STARA'::text AS stara_wartosc,
       'NOWA'::text AS nowa_wartosc,
       1::integer AS oczekiwane_wiersze;

/* KROK 2: plan zmian z poprzednimi wartościami (kopia do odtworzenia) */
CREATE TEMP TABLE plan_zmian ON COMMIT DROP AS
SELECT t.kolumna_klucza, t.kolumna_wartosci AS poprzednia_wartosc, p.nowa_wartosc
FROM schemat.tabela AS t
JOIN parametry AS p ON t.kolumna_klucza = p.klucz AND t.kolumna_wartosci = p.stara_wartosc;

/* KROK 3: PRZED - zachowaj ten wynik przed zatwierdzeniem */
SELECT pz.kolumna_klucza AS "3. PRZED - plan zmian", pz.poprzednia_wartosc, pz.nowa_wartosc
FROM plan_zmian AS pz
ORDER BY pz.kolumna_klucza;

/* KROK 4: kontrola środowiska i liczby wierszy, UPDATE według planu */
DO $$
DECLARE
    v_baza text;
    v_oczekiwane integer;
    v_plan integer;
    v_zmienione integer;
BEGIN
    SELECT oczekiwana_baza, oczekiwane_wiersze INTO v_baza, v_oczekiwane FROM parametry;
    RAISE NOTICE 'Serwer: %, baza: %', inet_server_addr(), current_database();
    IF current_database() <> v_baza THEN
        RAISE EXCEPTION 'KROK 4: skrypt uruchomiono na bazie % zamiast %', current_database(), v_baza;
    END IF;

    SELECT count(*) INTO v_plan FROM plan_zmian;
    IF v_plan <> v_oczekiwane THEN
        RAISE EXCEPTION 'KROK 4: plan obejmuje % wierszy, oczekiwano %', v_plan, v_oczekiwane;
    END IF;

    UPDATE schemat.tabela AS t
    SET kolumna_wartosci = pz.nowa_wartosc
    FROM plan_zmian AS pz
    WHERE t.kolumna_klucza = pz.kolumna_klucza
      AND t.kolumna_wartosci = pz.poprzednia_wartosc;

    GET DIAGNOSTICS v_zmienione = ROW_COUNT;
    RAISE NOTICE 'KROK 4: zmieniono wierszy: %', v_zmienione;
    IF v_zmienione <> v_oczekiwane THEN
        RAISE EXCEPTION 'KROK 4: zmieniono % wierszy, oczekiwano %', v_zmienione, v_oczekiwane;
    END IF;
END $$;

/* KROK 5: PO - sprawdzenie wyniku */
SELECT t.kolumna_klucza AS "5. PO - wynik", t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN plan_zmian AS pz ON pz.kolumna_klucza = t.kolumna_klucza
ORDER BY t.kolumna_klucza;

/* KROK 6: zakończenie - domyślnie nic nie jest zapisywane (tabele tymczasowe znikają razem z transakcją) */
ROLLBACK;
-- COMMIT;

/* ODTWORZENIE (tylko po COMMIT): na podstawie wyniku KROKU 3, w tym samym opakowaniu:
   UPDATE schemat.tabela AS t SET kolumna_wartosci = k.poprzednia_wartosc
   FROM (VALUES (0, 'STARA', 'NOWA')) AS k (kolumna_klucza, poprzednia_wartosc, nowa_wartosc)
   WHERE t.kolumna_klucza = k.kolumna_klucza AND t.kolumna_wartosci = k.nowa_wartosc;
*/
```

### Dodanie wiersza

```sql
/* =============================================================================
   SKRYPT:        Dodanie wiersza z kluczem, którego jeszcze nie ma
   ZGŁOSZENIE:    NUMER
   BAZA:          PostgreSQL · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola i INSERT · 5 PO · 6 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: PostgreSQL
BEGIN;

/* KROK 1: parametry - uzupełnij przed uruchomieniem */
CREATE TEMP TABLE parametry ON COMMIT DROP AS
SELECT 'NAZWA_BAZY'::text AS oczekiwana_baza,
       0::integer AS klucz,
       'WARTOSC'::text AS wartosc,
       1::integer AS oczekiwane_wiersze;

/* KROK 2: plan - tylko klucze, których jeszcze nie ma */
CREATE TEMP TABLE plan_zmian ON COMMIT DROP AS
SELECT p.klucz AS kolumna_klucza, p.wartosc
FROM parametry AS p
WHERE NOT EXISTS (SELECT 1 FROM schemat.tabela AS t WHERE t.kolumna_klucza = p.klucz);

/* KROK 3: PRZED - wiersze do dodania */
SELECT pz.kolumna_klucza AS "3. PRZED - do dodania", pz.wartosc
FROM plan_zmian AS pz;

/* KROK 4: kontrola środowiska i liczby wierszy, INSERT według planu */
DO $$
DECLARE
    v_baza text;
    v_oczekiwane integer;
    v_plan integer;
    v_dodane integer;
BEGIN
    SELECT oczekiwana_baza, oczekiwane_wiersze INTO v_baza, v_oczekiwane FROM parametry;
    RAISE NOTICE 'Serwer: %, baza: %', inet_server_addr(), current_database();
    IF current_database() <> v_baza THEN
        RAISE EXCEPTION 'KROK 4: skrypt uruchomiono na bazie % zamiast %', current_database(), v_baza;
    END IF;

    SELECT count(*) INTO v_plan FROM plan_zmian;
    IF v_plan <> v_oczekiwane THEN
        RAISE EXCEPTION 'KROK 4: plan obejmuje % wierszy, oczekiwano % (wiersz już istnieje?)', v_plan, v_oczekiwane;
    END IF;

    INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
    SELECT pz.kolumna_klucza, pz.wartosc
    FROM plan_zmian AS pz
    ON CONFLICT DO NOTHING;

    GET DIAGNOSTICS v_dodane = ROW_COUNT;
    RAISE NOTICE 'KROK 4: dodano wierszy: %', v_dodane;
    IF v_dodane <> v_oczekiwane THEN
        RAISE EXCEPTION 'KROK 4: dodano % wierszy, oczekiwano %', v_dodane, v_oczekiwane;
    END IF;
END $$;

/* KROK 5: PO - sprawdzenie wyniku */
SELECT t.kolumna_klucza AS "5. PO - wynik", t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN plan_zmian AS pz ON pz.kolumna_klucza = t.kolumna_klucza;

/* KROK 6: zakończenie - domyślnie nic nie jest zapisywane */
ROLLBACK;
-- COMMIT;

/* ODTWORZENIE (tylko po COMMIT): usuń dodane wiersze po kluczu z KROKU 3, z warunkiem na wartość:
   DELETE FROM schemat.tabela WHERE kolumna_klucza = 0 AND kolumna_wartosci = 'WARTOSC';
*/
```

## Oracle

Włącz wyświetlanie komunikatów: `SET SERVEROUTPUT ON`. Plan zmian to kursor; jego wynik (KROK 3) zachowaj
przed zatwierdzeniem, bo jest kopią do odtworzenia.

### Zmiana wartości

```sql
/* =============================================================================
   SKRYPT:        Zmiana kolumna_wartosci dla wskazanego klucza
   ZGŁOSZENIE:    NUMER
   BAZA:          Oracle · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2-3 plan i PRZED · 4 kontrola · 5 UPDATE · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz (SET SERVEROUTPUT ON). Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: Oracle
DECLARE
    /* KROK 1: parametry - uzupełnij przed uruchomieniem */
    v_oczekiwana_baza VARCHAR2(128) := 'NAZWA_BAZY';
    v_klucz           schemat.tabela.kolumna_klucza%TYPE := 0;
    v_stara           schemat.tabela.kolumna_wartosci%TYPE := 'STARA';
    v_nowa            schemat.tabela.kolumna_wartosci%TYPE := 'NOWA';
    v_oczekiwane      PLS_INTEGER := 1;
    v_plan            PLS_INTEGER := 0;
    v_zmienione       PLS_INTEGER;
    v_baza            VARCHAR2(128) := SYS_CONTEXT('USERENV', 'DB_NAME');
BEGIN
    DBMS_OUTPUT.PUT_LINE('Serwer: ' || SYS_CONTEXT('USERENV', 'SERVER_HOST') || ', baza: ' || v_baza);
    IF v_baza <> v_oczekiwana_baza THEN
        RAISE_APPLICATION_ERROR(-20000, 'KROK 1: skrypt uruchomiono na innej bazie niż oczekiwana.');
    END IF;

    /* KROK 2-3: plan zmian i PRZED - zachowaj wypisane wiersze */
    FOR w IN (SELECT t.kolumna_klucza, t.kolumna_wartosci
              FROM schemat.tabela t
              WHERE t.kolumna_klucza = v_klucz AND t.kolumna_wartosci = v_stara
              FOR UPDATE) LOOP
        v_plan := v_plan + 1;
        DBMS_OUTPUT.PUT_LINE('KROK 3 PRZED: ' || w.kolumna_klucza || ' | ' || w.kolumna_wartosci || ' -> ' || v_nowa);
    END LOOP;

    /* KROK 4: kontrola liczby wierszy w planie */
    IF v_plan <> v_oczekiwane THEN
        RAISE_APPLICATION_ERROR(-20001, 'KROK 4: liczba wierszy w planie jest inna niż oczekiwana.');
    END IF;

    /* KROK 5: UPDATE z poprzednią wartością */
    UPDATE schemat.tabela
    SET kolumna_wartosci = v_nowa
    WHERE kolumna_klucza = v_klucz
      AND kolumna_wartosci = v_stara;

    v_zmienione := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('KROK 5: zmieniono wierszy: ' || v_zmienione);
    IF v_zmienione <> v_oczekiwane THEN
        RAISE_APPLICATION_ERROR(-20002, 'KROK 5: liczba zmienionych wierszy jest inna niż oczekiwana.');
    END IF;

    /* KROK 6: PO - sprawdzenie wyniku */
    FOR w IN (SELECT t.kolumna_klucza, t.kolumna_wartosci FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz) LOOP
        DBMS_OUTPUT.PUT_LINE('KROK 6 PO: ' || w.kolumna_klucza || ' | ' || w.kolumna_wartosci);
    END LOOP;

    /* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
    DBMS_OUTPUT.PUT_LINE('------------- KONIEC -------------');
    ROLLBACK; DBMS_OUTPUT.PUT_LINE('WYCOFANO (ROLLBACK): ' || v_baza);
    -- COMMIT; DBMS_OUTPUT.PUT_LINE('ZATWIERDZONO (COMMIT): ' || v_baza);
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('BŁĄD - wycofano wszystkie zmiany.');
        RAISE;
END;
/

/* ODTWORZENIE (tylko po COMMIT): dla każdego wiersza z KROKU 3
   UPDATE schemat.tabela SET kolumna_wartosci = '<poprzednia>'
   WHERE kolumna_klucza = <klucz> AND kolumna_wartosci = '<nowa>';  -- z kontrolą SQL%ROWCOUNT
*/
```

### Dodanie wiersza

```sql
/* =============================================================================
   SKRYPT:        Dodanie wiersza z kluczem, którego jeszcze nie ma
   ZGŁOSZENIE:    NUMER
   BAZA:          Oracle · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2-3 plan i PRZED · 4 kontrola · 5 INSERT · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz (SET SERVEROUTPUT ON). Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: po sprawdzeniu wyniku zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: Oracle
DECLARE
    /* KROK 1: parametry - uzupełnij przed uruchomieniem */
    v_oczekiwana_baza VARCHAR2(128) := 'NAZWA_BAZY';
    v_klucz           schemat.tabela.kolumna_klucza%TYPE := 0;
    v_wartosc         schemat.tabela.kolumna_wartosci%TYPE := 'WARTOSC';
    v_oczekiwane      PLS_INTEGER := 1;
    v_istnieje        PLS_INTEGER;
    v_dodane          PLS_INTEGER;
    v_baza            VARCHAR2(128) := SYS_CONTEXT('USERENV', 'DB_NAME');
BEGIN
    DBMS_OUTPUT.PUT_LINE('Serwer: ' || SYS_CONTEXT('USERENV', 'SERVER_HOST') || ', baza: ' || v_baza);
    IF v_baza <> v_oczekiwana_baza THEN
        RAISE_APPLICATION_ERROR(-20000, 'KROK 1: skrypt uruchomiono na innej bazie niż oczekiwana.');
    END IF;

    /* KROK 2-3: plan i PRZED - czy klucz już istnieje */
    SELECT COUNT(*) INTO v_istnieje FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz;
    DBMS_OUTPUT.PUT_LINE('KROK 3 PRZED: klucz ' || v_klucz || ', istniejących wierszy: ' || v_istnieje);

    /* KROK 4: kontrola - do dodania musi być dokładnie oczekiwana liczba wierszy */
    IF v_istnieje <> 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'KROK 4: wiersz z tym kluczem już istnieje.');
    END IF;

    /* KROK 5: INSERT tylko brakującego wiersza */
    INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
    SELECT v_klucz, v_wartosc FROM dual
    WHERE NOT EXISTS (SELECT 1 FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz);

    v_dodane := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('KROK 5: dodano wierszy: ' || v_dodane);
    IF v_dodane <> v_oczekiwane THEN
        RAISE_APPLICATION_ERROR(-20002, 'KROK 5: liczba dodanych wierszy jest inna niż oczekiwana.');
    END IF;

    /* KROK 6: PO - sprawdzenie wyniku */
    FOR w IN (SELECT t.kolumna_klucza, t.kolumna_wartosci FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz) LOOP
        DBMS_OUTPUT.PUT_LINE('KROK 6 PO: ' || w.kolumna_klucza || ' | ' || w.kolumna_wartosci);
    END LOOP;

    /* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
    DBMS_OUTPUT.PUT_LINE('------------- KONIEC -------------');
    ROLLBACK; DBMS_OUTPUT.PUT_LINE('WYCOFANO (ROLLBACK): ' || v_baza);
    -- COMMIT; DBMS_OUTPUT.PUT_LINE('ZATWIERDZONO (COMMIT): ' || v_baza);
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('BŁĄD - wycofano wszystkie zmiany.');
        RAISE;
END;
/

/* ODTWORZENIE (tylko po COMMIT):
   DELETE FROM schemat.tabela WHERE kolumna_klucza = 0 AND kolumna_wartosci = 'WARTOSC';  -- z kontrolą SQL%ROWCOUNT
*/
```

## MySQL i MariaDB

Transakcje działają dla tabel InnoDB. Zwykły skrypt MySQL nie ma bloku obsługi błędów, dlatego kontrole
zwracają kolumnę `kontrola` z wartością `OK` albo `PRZERWIJ`. Przy `PRZERWIJ` nie zatwierdzaj zmian: skrypt i tak
kończy się `ROLLBACK`. W kliencie `mysql` uruchamiaj plik bez `--force`, żeby błąd zatrzymał skrypt.

### Zmiana wartości

```sql
/* =============================================================================
   SKRYPT:        Zmiana kolumna_wartosci dla wskazanego klucza
   ZGŁOSZENIE:    NUMER
   BAZA:          MySQL · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola · 5 UPDATE · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: gdy wszystkie kontrole mają OK, zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: MySQL
DROP TEMPORARY TABLE IF EXISTS plan_zmian;

/* KROK 1: parametry - uzupełnij przed uruchomieniem */
SET @oczekiwana_baza = 'NAZWA_BAZY';
SET @klucz = 0;
SET @stara_wartosc = 'STARA';
SET @nowa_wartosc = 'NOWA';
SET @oczekiwane = 1;

SELECT @@hostname AS serwer, DATABASE() AS baza,
       IF(DATABASE() = @oczekiwana_baza, 'OK', 'PRZERWIJ: inna baza') AS kontrola;

START TRANSACTION;

/* KROK 2: plan zmian z poprzednimi wartościami (kopia do odtworzenia) */
CREATE TEMPORARY TABLE plan_zmian AS
SELECT t.kolumna_klucza, t.kolumna_wartosci AS poprzednia_wartosc, @nowa_wartosc AS nowa_wartosc
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @klucz
  AND t.kolumna_wartosci = @stara_wartosc;

/* KROK 3: PRZED - zachowaj ten wynik przed zatwierdzeniem */
SELECT pz.kolumna_klucza AS `3. PRZED - plan zmian`, pz.poprzednia_wartosc, pz.nowa_wartosc
FROM plan_zmian AS pz;

/* KROK 4: kontrola liczby wierszy w planie */
SELECT COUNT(*) AS w_planie, @oczekiwane AS oczekiwane,
       IF(COUNT(*) = @oczekiwane, 'OK', 'PRZERWIJ: inna liczba wierszy') AS kontrola
FROM plan_zmian;

/* KROK 5: UPDATE tylko wierszy z planu, nadal z poprzednią wartością */
UPDATE schemat.tabela AS t
JOIN plan_zmian AS pz ON pz.kolumna_klucza = t.kolumna_klucza
SET t.kolumna_wartosci = pz.nowa_wartosc
WHERE t.kolumna_wartosci = pz.poprzednia_wartosc;

SET @zmienione = ROW_COUNT();
SELECT 'KROK 5' AS krok, @zmienione AS zmienione, @oczekiwane AS oczekiwane,
       IF(@zmienione = @oczekiwane, 'OK', 'PRZERWIJ: inna liczba zmian') AS kontrola;

/* KROK 6: PO - sprawdzenie wyniku */
SELECT t.kolumna_klucza AS `6. PO - wynik`, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN plan_zmian AS pz ON pz.kolumna_klucza = t.kolumna_klucza;

/* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
ROLLBACK;
-- COMMIT;
SELECT 'WYCOFANO (ROLLBACK)' AS wynik, @@hostname AS serwer, DATABASE() AS baza;

DROP TEMPORARY TABLE IF EXISTS plan_zmian;

/* ODTWORZENIE (tylko po COMMIT): na podstawie wyniku KROKU 3
   UPDATE schemat.tabela SET kolumna_wartosci = 'STARA' WHERE kolumna_klucza = 0 AND kolumna_wartosci = 'NOWA';
*/
```

### Dodanie wiersza

```sql
/* =============================================================================
   SKRYPT:        Dodanie wiersza z kluczem, którego jeszcze nie ma
   ZGŁOSZENIE:    NUMER
   BAZA:          MySQL · ŚRODOWISKO: TEST
   AUTOR / DATA:  osoba / RRRR-MM-DD
   KROKI:         1 parametry · 2 plan · 3 PRZED · 4 kontrola · 5 INSERT · 6 PO · 7 zakończenie
   URUCHOMIENIE:  całość naraz. Skrypt kończy się ROLLBACK i niczego nie zapisuje.
   ZATWIERDZENIE: gdy wszystkie kontrole mają OK, zamień ROLLBACK na COMMIT (zgoda osoby odpowiedzialnej za dane).
   ============================================================================= */
-- Baza: MySQL
DROP TEMPORARY TABLE IF EXISTS plan_zmian;

/* KROK 1: parametry - uzupełnij przed uruchomieniem */
SET @oczekiwana_baza = 'NAZWA_BAZY';
SET @klucz = 0;
SET @wartosc = 'WARTOSC';
SET @oczekiwane = 1;

SELECT @@hostname AS serwer, DATABASE() AS baza,
       IF(DATABASE() = @oczekiwana_baza, 'OK', 'PRZERWIJ: inna baza') AS kontrola;

START TRANSACTION;

/* KROK 2: plan - tylko klucze, których jeszcze nie ma */
CREATE TEMPORARY TABLE plan_zmian AS
SELECT @klucz AS kolumna_klucza, @wartosc AS wartosc
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM schemat.tabela AS t WHERE t.kolumna_klucza = @klucz);

/* KROK 3: PRZED - wiersze do dodania */
SELECT pz.kolumna_klucza AS `3. PRZED - do dodania`, pz.wartosc FROM plan_zmian AS pz;

/* KROK 4: kontrola liczby wierszy w planie */
SELECT COUNT(*) AS w_planie, @oczekiwane AS oczekiwane,
       IF(COUNT(*) = @oczekiwane, 'OK', 'PRZERWIJ: wiersz już istnieje?') AS kontrola
FROM plan_zmian;

/* KROK 5: INSERT tylko brakujących wierszy */
INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
SELECT pz.kolumna_klucza, pz.wartosc
FROM plan_zmian AS pz
WHERE NOT EXISTS (SELECT 1 FROM schemat.tabela AS t WHERE t.kolumna_klucza = pz.kolumna_klucza);

SET @dodane = ROW_COUNT();
SELECT 'KROK 5' AS krok, @dodane AS dodane, @oczekiwane AS oczekiwane,
       IF(@dodane = @oczekiwane, 'OK', 'PRZERWIJ: inna liczba wierszy') AS kontrola;

/* KROK 6: PO - sprawdzenie wyniku */
SELECT t.kolumna_klucza AS `6. PO - wynik`, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN plan_zmian AS pz ON pz.kolumna_klucza = t.kolumna_klucza;

/* KROK 7: zakończenie - domyślnie nic nie jest zapisywane */
ROLLBACK;
-- COMMIT;
SELECT 'WYCOFANO (ROLLBACK)' AS wynik, @@hostname AS serwer, DATABASE() AS baza;

DROP TEMPORARY TABLE IF EXISTS plan_zmian;

/* ODTWORZENIE (tylko po COMMIT):
   DELETE FROM schemat.tabela WHERE kolumna_klucza = 0 AND kolumna_wartosci = 'WARTOSC';
*/
```
