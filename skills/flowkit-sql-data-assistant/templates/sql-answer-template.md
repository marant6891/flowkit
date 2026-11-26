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

## Co pokaże skrypt krok po kroku

| Krok | Co zobaczysz | Poprawnie |
|---|---|---|
| początek | serwer i baza | to baza ze zgłoszenia; inna baza przerywa skrypt |
| KROK 3: PRZED | plan zmian z poprzednią i nową wartością | [liczba] wierszy; **zachowaj ten wynik** (kopia do odtworzenia) |
| KROK 5: zmiana | `KROK 5: zmieniono wierszy: N` | N = [oczekiwana liczba] |
| KROK 6: PO | wynik po zmianie | [co powinno być widać] |
| koniec | `WYCOFANO (ROLLBACK)` | pierwsze uruchomienie niczego nie zapisuje |

Komunikat `BŁĄD - wycofano wszystkie zmiany` oznacza, że kontrola zatrzymała skrypt; nic nie zostało zapisane.

## Jak sprawdzić wynik

- **Poprawnie:** [jaki wynik i ile wierszy].
- **Niepoprawnie:** [co oznacza inny wynik i co zrobić].

## Zatwierdzenie zmiany

[Tylko dla skryptów zmieniających dane.] Skrypt kończy się `ROLLBACK`, więc pierwsze uruchomienie niczego nie zapisuje. Zamień `ROLLBACK` na `COMMIT` (wiersz z `COMMIT` jest gotowy w komentarzu obok) dopiero po sprawdzeniu wyniku i uzyskaniu wymaganej zgody. Gdy po zatwierdzeniu trzeba cofnąć zmianę, użyj skryptu odtworzenia z końca pliku i zachowanego wyniku KROKU 3.
