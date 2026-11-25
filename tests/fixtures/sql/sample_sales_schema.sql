-- Baza: PostgreSQL 16
-- Fikcyjny schemat do testów zestawień analitycznych.
-- Kolumna data_zamowienia jest zapisywana w UTC.
CREATE TABLE sprzedaz.klient (
    klient_id integer PRIMARY KEY,
    region varchar(30) NOT NULL,
    data_rejestracji date NOT NULL
);

CREATE TABLE sprzedaz.zamowienie (
    zamowienie_id bigint PRIMARY KEY,
    klient_id integer NOT NULL REFERENCES sprzedaz.klient (klient_id),
    data_zamowienia timestamptz NOT NULL,
    status varchar(20) NOT NULL  -- NOWE, OPLACONE, WYSLANE, ANULOWANE
);

CREATE TABLE sprzedaz.pozycja_zamowienia (
    zamowienie_id bigint NOT NULL REFERENCES sprzedaz.zamowienie (zamowienie_id),
    nr_pozycji smallint NOT NULL,
    kategoria varchar(40) NOT NULL,
    ilosc integer NOT NULL,
    cena_netto numeric(12, 2) NOT NULL,
    PRIMARY KEY (zamowienie_id, nr_pozycji)
);
