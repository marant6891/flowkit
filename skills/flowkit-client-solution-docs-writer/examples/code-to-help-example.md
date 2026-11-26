# Przykład: od kodu do tematu pomocy

Źródło: przykładowy moduł zwrotów (`tests/fixtures/app/returns/routes.py`, `pl.json`). Odbiorca: klient sklepu,
profil podstawowy, forma „Ty”.

## 1. Z kodu do katalogu funkcji

| Fakt w kodzie | Zapis w katalogu funkcji |
|---|---|
| `@require_role("customer")` na `create_return` | FEAT-001 „Zgłoszenie zwrotu”, rola: Klient |
| `order.status != "delivered"` → `returns.error.not_delivered` | Warunek: zamówienie dostarczone; komunikat „Zwrot można zgłosić tylko dla dostarczonego zamówienia” |
| `MAX_DAYS = 30` | Termin: 30 dni od dostarczenia; komunikat „Minął termin zwrotu” |
| `REASONS`, `returns.reason.*` | Pole **Powód zwrotu** (wymagane): Uszkodzony, Niezgodny z opisem, Inny |
| `len(comment) > 500` | Pole **Komentarz** (opcjonalne), do 500 znaków |
| `MAX_PHOTOS = 3`, `MAX_PHOTO_MB = 5` | Pole **Zdjęcia** (opcjonalne), do 3 plików, każdy do 5 MB |
| `status="pending_approval"`, `returns.created` | Wynik: status **Oczekuje na akceptację**, komunikat „Zgłoszenie zwrotu zostało wysłane” |
| `approve_return` z `require_role("returns_manager")`, `TODO` | Poza helpem klienta (inna rola); częściowa akceptacja nieukończona → `OPEN-001` |

Formaty zdjęć (JPG, PNG) nie wynikają z kodu: nie wpisuj ich, dodaj `OPEN-002`.

## 2. Źle: opis kodu zamiast pomocy

> Endpoint `POST /orders/{id}/returns/new` tworzy obiekt zwrotu. Jeśli `order.status` nie jest `delivered`,
> zwracany jest błąd 400. Plik może mieć maksymalnie 5 MB. Dozwolone formaty to JPG i PNG.

Błędy: endpoint, nazwy pól z kodu i kod HTTP w pomocy dla użytkownika; „JPG i PNG” zmyślone; brak kroków.

## 3. Dobrze: temat-zadanie (tryb roboczy)

```markdown
### Zgłaszanie zwrotu

Zgłoś zwrot produktów z dostarczonego zamówienia. Masz na to 30 dni od dostarczenia.

1. Wybierz **Zamówienia** > **Moje zamówienia**.
2. Przy zamówieniu kliknij **Zgłoś zwrot**.
3. Wybierz **Powód zwrotu**.
4. (Opcjonalnie) Wpisz **Komentarz** (do 500 znaków) i dodaj **Zdjęcia** (do 3 plików, każdy do 5 MB).
5. Kliknij **Wyślij zgłoszenie**.

**Wynik:** zobaczysz komunikat „Zgłoszenie zwrotu zostało wysłane”, a zgłoszenie otrzyma status
**Oczekuje na akceptację**.

| Komunikat | Przyczyna | Co zrobić |
|---|---|---|
| „Zwrot można zgłosić tylko dla dostarczonego zamówienia” | Zamówienie nie zostało jeszcze dostarczone | Poczekaj na dostarczenie zamówienia |
| „Minął termin zwrotu” | Od dostarczenia minęło ponad 30 dni | DO POTWIERDZENIA (OPEN-003: kontakt do obsługi) |

[ZRZUT: Moje zamówienia > Zgłoś zwrot, formularz z wybranym powodem]

(SRC-001, routes.py:17-37; SRC-002, pl.json)
```

Kolejność kroków 1–2 wynika z menu i przycisku w tłumaczeniach; jeśli układ formularza nie wynika z kodu,
poproś o zrzut ekranu albo oznacz kolejność pól jako `OPEN`.
