# Bezpieczne szablony zmiany danych

Zastąp `schemat.tabela`, `kolumna_klucza`, `kolumna_wartosci` i wartości zmiennych nazwami ze źródeł. Zachowaj kolejność kroków.

## PostgreSQL

### Dodanie wiersza

```sql
-- Baza: PostgreSQL
-- Zgłoszenie: NUMER
BEGIN;

CREATE TEMP TABLE parametry ON COMMIT DROP AS
SELECT 0::integer AS klucz, 'WARTOSC'::text AS wartosc, 1::integer AS oczekiwane_wiersze;

-- Podgląd: wynik powinien być pusty
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN parametry AS p ON t.kolumna_klucza = p.klucz;

DO $$
DECLARE
    zmienione integer;
    oczekiwane integer;
BEGIN
    SELECT oczekiwane_wiersze INTO oczekiwane FROM parametry;

    INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
    SELECT p.klucz, p.wartosc
    FROM parametry AS p
    WHERE NOT EXISTS (
        SELECT 1 FROM schemat.tabela AS t WHERE t.kolumna_klucza = p.klucz
    );

    GET DIAGNOSTICS zmienione = ROW_COUNT;
    IF zmienione <> oczekiwane THEN
        RAISE EXCEPTION 'Zmieniono % wierszy, oczekiwano %', zmienione, oczekiwane;
    END IF;
END $$;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN parametry AS p ON t.kolumna_klucza = p.klucz;

ROLLBACK;
-- COMMIT;
```

### Zmiana wartości

```sql
-- Baza: PostgreSQL
-- Zgłoszenie: NUMER
BEGIN;

CREATE TEMP TABLE parametry ON COMMIT DROP AS
SELECT 0::integer AS klucz, 'STARA'::text AS stara_wartosc, 'NOWA'::text AS nowa_wartosc, 1::integer AS oczekiwane_wiersze;

-- Podgląd danych przed zmianą
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN parametry AS p ON t.kolumna_klucza = p.klucz;

DO $$
DECLARE
    zmienione integer;
    oczekiwane integer;
BEGIN
    SELECT oczekiwane_wiersze INTO oczekiwane FROM parametry;

    UPDATE schemat.tabela AS t
    SET kolumna_wartosci = p.nowa_wartosc
    FROM parametry AS p
    WHERE t.kolumna_klucza = p.klucz
      AND t.kolumna_wartosci = p.stara_wartosc;

    GET DIAGNOSTICS zmienione = ROW_COUNT;
    IF zmienione <> oczekiwane THEN
        RAISE EXCEPTION 'Zmieniono % wierszy, oczekiwano %', zmienione, oczekiwane;
    END IF;
END $$;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
JOIN parametry AS p ON t.kolumna_klucza = p.klucz;

ROLLBACK;
-- COMMIT;
```

## SQL Server

### Dodanie wiersza

```sql
-- Baza: SQL Server
-- Zgłoszenie: NUMER
SET XACT_ABORT ON;

DECLARE @Klucz int = 0;
DECLARE @Wartosc nvarchar(200) = N'WARTOSC';
DECLARE @OczekiwaneWiersze int = 1;
DECLARE @ZmienioneWiersze int;

-- Podgląd: wynik powinien być pusty
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @Klucz;

BEGIN TRANSACTION;

INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
SELECT @Klucz, @Wartosc
WHERE NOT EXISTS (
    SELECT 1 FROM schemat.tabela AS t WITH (UPDLOCK, HOLDLOCK) WHERE t.kolumna_klucza = @Klucz
);

SET @ZmienioneWiersze = @@ROWCOUNT;

IF @ZmienioneWiersze <> @OczekiwaneWiersze
BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Liczba zmienionych wierszy jest inna niz oczekiwana.', 1;
END;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @Klucz;

ROLLBACK TRANSACTION;
-- COMMIT TRANSACTION;
```

### Zmiana wartości

```sql
-- Baza: SQL Server
-- Zgłoszenie: NUMER
SET XACT_ABORT ON;

DECLARE @Klucz int = 0;
DECLARE @StaraWartosc nvarchar(200) = N'STARA';
DECLARE @NowaWartosc nvarchar(200) = N'NOWA';
DECLARE @OczekiwaneWiersze int = 1;
DECLARE @ZmienioneWiersze int;

-- Podgląd danych przed zmianą
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @Klucz;

BEGIN TRANSACTION;

UPDATE t
SET t.kolumna_wartosci = @NowaWartosc
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @Klucz
  AND t.kolumna_wartosci = @StaraWartosc;

SET @ZmienioneWiersze = @@ROWCOUNT;

IF @ZmienioneWiersze <> @OczekiwaneWiersze
BEGIN
    ROLLBACK TRANSACTION;
    THROW 50001, 'Liczba zmienionych wierszy jest inna niz oczekiwana.', 1;
END;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @Klucz;

ROLLBACK TRANSACTION;
-- COMMIT TRANSACTION;
```

## Oracle

Włącz wyświetlanie komunikatów: `SET SERVEROUTPUT ON`.

### Dodanie wiersza

```sql
-- Baza: Oracle
-- Zgłoszenie: NUMER
DECLARE
    v_klucz       schemat.tabela.kolumna_klucza%TYPE := 0;
    v_wartosc     schemat.tabela.kolumna_wartosci%TYPE := 'WARTOSC';
    v_oczekiwane  PLS_INTEGER := 1;
    v_zmienione   PLS_INTEGER;
    v_liczba      PLS_INTEGER;
BEGIN
    INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
    SELECT v_klucz, v_wartosc FROM dual
    WHERE NOT EXISTS (
        SELECT 1 FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz
    );

    v_zmienione := SQL%ROWCOUNT;
    IF v_zmienione <> v_oczekiwane THEN
        RAISE_APPLICATION_ERROR(-20001, 'Liczba zmienionych wierszy jest inna niz oczekiwana.');
    END IF;

    SELECT COUNT(*) INTO v_liczba FROM schemat.tabela t WHERE t.kolumna_klucza = v_klucz;
    DBMS_OUTPUT.PUT_LINE('Zmienione: ' || v_zmienione || ', wiersze po zmianie: ' || v_liczba);

    ROLLBACK;
    -- COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/
```

### Zmiana wartości

```sql
-- Baza: Oracle
-- Zgłoszenie: NUMER
DECLARE
    v_klucz       schemat.tabela.kolumna_klucza%TYPE := 0;
    v_stara       schemat.tabela.kolumna_wartosci%TYPE := 'STARA';
    v_nowa        schemat.tabela.kolumna_wartosci%TYPE := 'NOWA';
    v_oczekiwane  PLS_INTEGER := 1;
    v_zmienione   PLS_INTEGER;
    v_liczba      PLS_INTEGER;
BEGIN
    UPDATE schemat.tabela
    SET kolumna_wartosci = v_nowa
    WHERE kolumna_klucza = v_klucz
      AND kolumna_wartosci = v_stara;

    v_zmienione := SQL%ROWCOUNT;
    IF v_zmienione <> v_oczekiwane THEN
        RAISE_APPLICATION_ERROR(-20001, 'Liczba zmienionych wierszy jest inna niz oczekiwana.');
    END IF;

    SELECT COUNT(*) INTO v_liczba FROM schemat.tabela t
    WHERE t.kolumna_klucza = v_klucz AND t.kolumna_wartosci = v_nowa;
    DBMS_OUTPUT.PUT_LINE('Zmienione: ' || v_zmienione || ', wiersze po zmianie: ' || v_liczba);

    ROLLBACK;
    -- COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/
```

## MySQL i MariaDB

Transakcje działają dla tabel InnoDB. Porównaj kolumny `zmienione` i `oczekiwane`, zanim zatwierdzisz zmianę.

### Dodanie wiersza

```sql
-- Baza: MySQL
-- Zgłoszenie: NUMER
SET @klucz = 0;
SET @wartosc = 'WARTOSC';
SET @oczekiwane = 1;

-- Podgląd: wynik powinien być pusty
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @klucz;

START TRANSACTION;

INSERT INTO schemat.tabela (kolumna_klucza, kolumna_wartosci)
SELECT @klucz, @wartosc FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM schemat.tabela AS t WHERE t.kolumna_klucza = @klucz
);

SET @zmienione = ROW_COUNT();
SELECT @zmienione AS zmienione, @oczekiwane AS oczekiwane;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @klucz;

ROLLBACK;
-- COMMIT;
```

### Zmiana wartości

```sql
-- Baza: MySQL
-- Zgłoszenie: NUMER
SET @klucz = 0;
SET @stara_wartosc = 'STARA';
SET @nowa_wartosc = 'NOWA';
SET @oczekiwane = 1;

-- Podgląd danych przed zmianą
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @klucz;

START TRANSACTION;

UPDATE schemat.tabela
SET kolumna_wartosci = @nowa_wartosc
WHERE kolumna_klucza = @klucz
  AND kolumna_wartosci = @stara_wartosc;

SET @zmienione = ROW_COUNT();
SELECT @zmienione AS zmienione, @oczekiwane AS oczekiwane;

-- Sprawdzenie wyniku
SELECT t.kolumna_klucza, t.kolumna_wartosci
FROM schemat.tabela AS t
WHERE t.kolumna_klucza = @klucz;

ROLLBACK;
-- COMMIT;
```
