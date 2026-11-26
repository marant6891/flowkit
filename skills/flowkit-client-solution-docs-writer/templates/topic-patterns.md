# Wzorce tematów

Każdy temat dokumentu ma jeden typ. Typ wybierasz w planie (Etap 2). Nagłówek tematu-zadania zaczyna się od
czasownika („Dodawanie zwrotu” albo „Jak dodać zwrot”, jednolicie w całym dokumencie).

## Zadanie (najczęstszy typ w pomocy)

```markdown
### Dodawanie zwrotu

Zgłoś zwrot towaru z zamówienia, które otrzymałeś w ciągu ostatnich 30 dni.

**Zanim zaczniesz:** zamówienie ma status **Dostarczone**.

1. Wybierz **Zamówienia** > **Moje zamówienia**.
2. Przy zamówieniu kliknij **Zgłoś zwrot**.
3. Zaznacz produkty do zwrotu i wybierz **Powód zwrotu**.
4. Kliknij **Wyślij zgłoszenie**.

**Wynik:** zgłoszenie otrzymuje status **Oczekuje na akceptację**, a na ekranie pojawia się komunikat
„Zgłoszenie zwrotu zostało wysłane”.

[ZRZUT: Zamówienia > Zgłoś zwrot – formularz z wybranym produktem]
```

Zasady: jedna czynność na krok; warunek przed czynnością („Jeśli zwracasz kilka produktów, zaznacz…”);
kroki opcjonalne zaczynaj od „(Opcjonalnie)”; podkroki tylko dla wyboru wariantu. Liczby (30 dni) tylko z kodu.

## Pojęcie

Krótkie wyjaśnienie, czym coś jest i dlaczego jest ważne dla odbiorcy (2–5 zdań), bez kroków. Np. „Status
zwrotu”, z tabelą: Status, Co oznacza, Co możesz zrobić.

## Opis ekranu lub formularza

Gdy ekran ma wiele pól: jedno zdanie o przeznaczeniu i tabela pól.

| Pole | Wymagane | Opis i ograniczenia |
|---|---|---|
| **Powód zwrotu** | Tak | Wybór z listy: Uszkodzony, Niezgodny z opisem, Inny |
| **Komentarz** | Nie | Do 500 znaków |
| **Zdjęcia** | Nie | Do 3 plików JPG lub PNG, każdy do 5 MB |

## Rozwiązywanie problemów

| Komunikat lub objaw | Przyczyna | Co zrobić |
|---|---|---|
| „Minął termin zwrotu” | Od dostarczenia minęło ponad 30 dni | Skontaktuj się z obsługą klienta |

Komunikat dosłownie z aplikacji; przyczyna tylko z warunku w kodzie.

## FAQ

Pytanie w języku odbiorcy, odpowiedź 1–3 zdania z odesłaniem do tematu-zadania. Pytania wynikają z katalogu
funkcji (reguły, ograniczenia, statusy), nie z wyobrażeń o tym, o co ludzie pytają.

## Ustawienie (instrukcja administratora)

| Ustawienie | Znaczenie | Wartość domyślna | Skutek zmiany |
|---|---|---|---|
| `Returns:MaxDays` | Liczba dni na zgłoszenie zwrotu od dostarczenia | 30 | Zmiana dotyczy nowych zgłoszeń |

Nazwa ustawienia w czcionce kodu, bez wartości sekretów.
