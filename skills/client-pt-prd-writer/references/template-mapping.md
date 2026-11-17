# Praca na szablonie użytkownika

## 1. Odczyt szablonu

- `.docx` / `.dotx` – odczytaj zgodnie z [instrukcją wyboru silnika docx](./docx-engine.md) (priorytet 1: `python-docx` / `import docx`): nagłówki (style Heading),
  tabele, metryczkę, stronę tytułową, nagłówki/stopki, pola (np. numer wersji),
  teksty pomocnicze („[wpisz…]”, komentarze, instrukcje w kursywie).
- `.md` / `.txt` – nagłówki `#`, tabele, placeholdery `[...]`.
- `.pdf` – tylko jako wzór struktury; wynik oddaj w formacie uzgodnionym z
  użytkownikiem (domyślnie .docx odtwarzający układ).

## 2. Mapa sekcji

Przed pisaniem utwórz mapę (wewnętrznie, pokaż użytkownikowi w Etapie 4):

| Sekcja szablonu (numer i nazwa) | Obszar treści skilla | Status | Źródła |
|---|---|---|---|
| 1. Wstęp | Kontekst i cel zmiany | Wypełniona | SRC-001 |
| 4. Wymagania | FR + US | Wypełniona | SRC-001, SRC-002 |
| 7. Wydajność | NFR | Brak danych – OPEN-003 | – |
| 9. Szkolenia | – | Nie dotyczy | SRC-001 (zakres) |
| (brak w szablonie) | Tematy do wyjaśnienia | Dodana jako ostatni rozdział | – |

## 3. Zasady wypełniania

- Zachowaj nazwy, numerację i kolejność sekcji szablonu. Nie zmieniaj stylów,
  czcionek, marginesów, nagłówków/stopek, logo.
- Usuń teksty instruktażowe szablonu (np. „[Opisz tu…]”) – zastąp je treścią
  lub „Nie dotyczy – …” / „Brak danych – patrz OPEN-NNN”. Nie zostawiaj
  placeholderów w wersji dla klienta.
- Jeśli szablon ma tabele z innymi kolumnami niż ten skill – używaj kolumn
  szablonu; kolumnę „Źródło” dodaj tylko wtedy, gdy szablon nie przewiduje
  innego miejsca na pochodzenie (alternatywa: przypis lub dopisek pod tabelą).
- Jeśli szablon nie ma sekcji na element obowiązkowy (Tematy do wyjaśnienia,
  Historia zmian, Materiały źródłowe) – dodaj go jako ostatni rozdział lub
  załącznik w stylu szablonu.
- Metryczkę wypełniaj tylko danymi ze źródła (autor, klient, wersja, data).
  Nieznane pola: `DO POTWIERDZENIA`.
- Nie dodawaj sekcji „na zapas” spoza szablonu.

## 4. Tryb końcowy bez dopisków

Gdy użytkownik prosi o dokument końcowy bez dopisków (patrz SKILL.md):

- Mapę sekcji prowadź jak zwykle, ale traktuj ją jako **rejestr pochodzenia**
  oddawany poza dokumentem – do dokumentu nie trafia żadna jej część.
- Nie dodawaj kolumny „Źródło”, przypisów o pochodzeniu ani rozdziałów spoza
  szablonu (wiersz „(brak w szablonie)” z mapy powyżej w tym trybie nie
  powstaje).
- Używaj wyłącznie kolumn, numeracji i identyfikatorów przewidzianych w szablonie.
- Pola metryczki bez danych uzgodnij z użytkownikiem przed generowaniem;
  nie wpisuj `DO POTWIERDZENIA`.

## 5. Kontrola

Po wygenerowaniu otwórz dokument (dla .docx: konwersja do PDF/obrazu) i sprawdź:
style nagłówków, numerację, tabele, brak placeholderów, spis treści (jeśli
szablon go ma – zaktualizowany).
