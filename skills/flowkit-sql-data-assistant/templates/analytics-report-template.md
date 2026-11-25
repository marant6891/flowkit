# Wzór odpowiedzi dla zestawienia analitycznego (`ANALYTICS_REPORT`)

## Co pokazuje to zestawienie

[1–2 proste zdania: na jakie pytanie biznesowe odpowiada. Skrypt tylko odczytuje dane.]

**Baza:** [typ i wersja] · **Środowisko:** [środowisko] · **Zgłoszenie / zamawiający:** [numer lub osoba]

## Karta raportu

| Element | Wartość | Źródło |
|---|---|---|
| Pytanie biznesowe | [np. jak zmienia się sprzedaż netto miesiąc do miesiąca] | [zgłoszenie / użytkownik] |
| Okres | [od – do, półotwarty: `>= od` i `< do`] | |
| Granulacja | [dzień / tydzień / miesiąc / kwartał] | |
| Data biznesowa i strefa czasowa | [kolumna daty, strefa] | |
| Wymiary (podział) | [np. miesiąc, region, kategoria] | |
| Filtry i wykluczenia | [np. bez anulowanych, bez kont testowych] | |
| Odbiorca i format | [tabela, CSV, arkusz, wykres] | |

## Słownik miar

| Miara | Definicja (wzór) | Jednostka | Uwagi |
|---|---|---|---|
| [nazwa kolumny wyniku] | [np. `SUM(wartosc_netto)` zamówień poza anulowanymi] | [PLN / szt. / %] | [ZAŁOŻENIE, jeśli definicja nie pochodzi ze źródła] |

## Co uzupełnić przed uruchomieniem

| Parametr | Co wpisać | Przykład |
|---|---|---|
| [data_od] | pierwszy dzień okresu | `2026-01-01` |
| [data_do] | pierwszy dzień PO okresie | `2027-01-01` |

## Skrypt

```sql
[zapytanie raportowe]
```

## Jak czytać wynik

- [Co oznacza jeden wiersz.]
- [Co oznaczają kolumny wyliczane, np. `zmiana_mm_proc` = zmiana procentowa wobec poprzedniego miesiąca;
  pusta wartość = brak danych do porównania lub poprzedni okres równy 0.]

## Kontrola spójności

```sql
[zapytanie kontrolne: suma i liczba wierszy bez podziału na wymiary, wiersze pominięte przez filtry]
```

- **Poprawnie:** [np. suma `wartosc_netto` z raportu = `wartosc_netto_w_raporcie` z zapytania kontrolnego].
- **Niepoprawnie:** [co oznacza rozbieżność i komu ją zgłosić].

## Założenia i niewiadome

- [ZAŁOŻENIE / NIEWIADOMA: np. czy zwroty pomniejszają sprzedaż; strefa czasowa kolumny daty.]

## Wydajność

[Szacunek wielkości tabel, jeśli znany; zalecenie: najpierw krótki okres, plan wykonania, replika lub poza
godzinami szczytu.]
