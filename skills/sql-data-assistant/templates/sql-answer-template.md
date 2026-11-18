# Wzór odpowiedzi dla testera i serwisanta

## Co robi ten skrypt

[1–2 proste zdania. Czy tylko odczytuje dane, czy może je zmienić.]

**Baza:** [typ] · **Środowisko:** [środowisko] · **Zgłoszenie:** [numer]

## Co uzupełnić przed uruchomieniem

| Zmienna | Co wpisać | Skąd wziąć wartość |
|---|---|---|
| [nazwa] | [opis] | [zgłoszenie lub ekran] |

## Skrypt

```sql
[skrypt]
```

## Jak sprawdzić wynik

- **Poprawnie:** [jaki wynik i ile wierszy].
- **Niepoprawnie:** [co oznacza inny wynik i co zrobić].

## Zatwierdzenie zmiany

[Tylko dla skryptów zmieniających dane.] Skrypt kończy się `ROLLBACK`, więc pierwsze uruchomienie niczego nie zapisuje. Zamień `ROLLBACK` na `COMMIT` dopiero po sprawdzeniu wyniku i uzyskaniu wymaganej zgody.
