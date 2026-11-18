-- Baza: SQL Server
-- Fikcyjny schemat do testów.
CREATE TABLE sprzedaz.klient (
    klient_id int NOT NULL PRIMARY KEY,
    email nvarchar(200) NOT NULL,
    status nvarchar(20) NOT NULL
);
