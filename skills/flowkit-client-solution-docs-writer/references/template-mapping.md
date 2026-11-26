# Praca na szablonie Word użytkownika

## 1. Odczyt

- `.docx` / `.dotx`: `read-document szablon.dotx --outline`, potem `--lines OD-DO` według
  [instrukcji DOCX](./docx-engine.md). Spisz nagłówki i ich poziomy, stronę tytułową, metryczkę, tabele,
  pola do wypełnienia (`[TYTUŁ]`, `{{WERSJA}}`, „[wpisz…]”) i teksty instruktażowe.
- Poprzedni dokument jako wzór: przejmij strukturę, poziom szczegółu i formę zwracania się, **nie treść**.
- `.pdf`: tylko wzór struktury; wynik `.docx` w szablonie zapasowym z tą strukturą.

## 2. Mapa sekcji (pokaż w Etapie 2)

| Sekcja szablonu | Treść | Tematy | Status |
|---|---|---|---|
| 1. Wprowadzenie | Dla kogo, czego dotyczy, wymagania wstępne | - | Wypełniona |
| 3. Praca z aplikacją | Tematy-zadania | FEAT-001…FEAT-006 | Wypełniona |
| 5. Administracja | - | - | Nie dotyczy (help dla użytkownika) |
| (brak w szablonie) | Tematy do wyjaśnienia | - | Dodana jako ostatni rozdział (tylko tryb roboczy i dla klienta) |

## 3. Zasady

- Zachowaj nazwy, numerację, kolejność i poziomy nagłówków. Rozdziały na tematy dziel nagłówkiem o jeden
  poziom niższym niż rozdział szablonu.
- Teksty instruktażowe szablonu zastąp treścią albo „Nie dotyczy.”; nie zostawiaj ich w wersji dla klienta.
- Kolumny tabel szablonu mają pierwszeństwo nad tabelami z tego skilla.
- Metryczka (`--set`): tytuł, wersja aplikacji, data, autor tylko ze źródeł lub od użytkownika.
- Spis treści i pola Worda (odsyłacze, numery stron) aktualizuje się w Wordzie (F9); przypomnij o tym
  w odpowiedzi, gdy szablon ma spis treści.
- W trybie końcowym nie dodajesz żadnej sekcji spoza szablonu.
