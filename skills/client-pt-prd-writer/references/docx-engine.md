# Obsługa plików .docx — odczyt, zapis i diagramy

Instrukcja obowiązuje zawsze, gdy skill lub agent musi **odczytać lub wygenerować plik `.docx`/`.dotx`**.
Agenci FlowKit uruchamiają polecenia wyłącznie przez lokalny executor:

```bash
python "<runtime>/flowkit_exec.py" --role <rola> -- <polecenie> [argumenty]
```

`<runtime>` to `${CLAUDE_PLUGIN_ROOT}/runtime` (wtyczka), `~/.claude/flowkit/runtime` (Claude Code) albo
`.github/flowkit/runtime` (VS Code). Listę poleceń dozwolonych dla roli pokazuje `-- help`.
Nie uruchamiaj `pandoc`, `pypandoc`, `python -c` ani własnych skryptów — executor je odrzuci.
Do zapisu DOCX służy wbudowane polecenie `md-to-docx`.

## Krok 1 — Wykrycie środowiska (raz na sesję)

```bash
python "<runtime>/flowkit_exec.py" --role <rola> -- detect-docx-libs
```

Wynik pokazuje: `python-docx`, `pypandoc`, `pandoc`, `mermaid-cli (mmdc)`, `npx`, `playwright`, `cairosvg`,
`rsvg-convert`. Zapisz go i nie powtarzaj wykrywania przy każdym pliku.

## Krok 2 — Odczyt szablonu i materiałów

```bash
python "<runtime>/flowkit_exec.py" --role <rola> -- read-document szablon.dotx --outline
python "<runtime>/flowkit_exec.py" --role <rola> -- read-document szablon.dotx --lines 1-200
```

`read-document` czyta `.docx`, `.dotx`, `.xlsx`, `.pdf` i pliki tekstowe lokalnie, bez dodatkowych bibliotek.
Duże dokumenty czytaj partiami: najpierw `--outline`, potem `--lines OD-DO`.

## Krok 3 — Zapis DOCX

Najpierw zapisz kompletny dokument w Markdown (narzędziem edycji plików), a potem skonwertuj go.
**Gdy użytkownik dał szablon, zawsze przekaż go do konwersji** — dokument końcowy ma mieć komplet stylów
i formatowania szablonu:

```bash
# Szablon z treścią (strona tytułowa, metryczka, stałe akapity zostają); dokument trafia w miejsce akapitu [[FLOWKIT:TREŚĆ]]
python "<runtime>/flowkit_exec.py" --role <rola> -- md-to-docx output/dokument.md output/dokument.docx --template szablon.dotx

# Sam komplet stylów szablonu, bez jego treści
python "<runtime>/flowkit_exec.py" --role <rola> -- md-to-docx output/dokument.md output/dokument.docx --reference-doc szablon.dotx
```

W obu trybach dokument powstaje na **kopii pliku szablonu** (silnik python-docx), więc przejmuje wszystkie style,
numerację nagłówków, motyw, czcionki, marginesy, nagłówki i stopki stron. Markdown jest mapowany na style
szablonu: `#`–`######` → Nagłówek 1–6 (`Heading N`), tekst → styl podstawowy szablonu, listy → `List Bullet`/`List Number`
(lub polskie odpowiedniki), tabele → styl tabeli użyty już w szablonie, podpis obrazu → `Caption`/`Legenda`.
Wynik zgłasza linię `Style szablonu: ...` — sprawdź, czy wskazuje style klienta.

| Opcja | Działanie |
|---|---|
| `--template PLIK` | kopia szablonu z jego treścią; dokument w miejscu `[[FLOWKIT:TREŚĆ]]` (bez znacznika: na końcu) |
| `--reference-doc PLIK` | kopia szablonu bez treści: komplet stylów, nagłówki, stopki, ustawienia stron |
| `--engine auto\|pandoc\|python-docx` | `auto`: z szablonem python-docx, bez szablonu Pandoc; `pandoc` przejmuje z szablonu tylko część stylów |
| `--keep-images` | zachowuje wyrenderowane diagramy w `<wynik>_diagrams/` |
| `--set POLE=WARTOŚĆ` | wypełnia pole szablonu (treść, tabele metryczki, nagłówki, stopki) z zachowaniem formatowania; powtarzalne, np. `--set "[TYTUŁ]=Analiza zmian" --set "[WERSJA]=1.0"` |

**Rekomendacja dla dokumentów klienta:** w kopii roboczej szablonu zostaw stronę tytułową i metryczkę, w miejscu
treści wstaw akapit `[[FLOWKIT:TREŚĆ]]`, a Markdown zacznij od pierwszego rozdziału szablonu. Nie zmieniaj
nazw stylów ani nie dodawaj formatowania ręcznie w Markdown — wygląd pochodzi wyłącznie z szablonu.

Konwerter:
- renderuje bloki ` ```mermaid ` do PNG lokalnym `mmdc` (albo `npx --no -p @mermaid-js/mermaid-cli`, bez pobierania),
- zamienia obrazy SVG na PNG: plik `.png` obok `.svg` → Playwright → CairoSVG → `rsvg-convert`,
  dzięki czemu Pandoc nie zgłasza błędu `rsvg-convert is not in path`,
- nie pobiera obrazów z adresów http(s) — zostaje tekst alternatywny,
- nie nadpisuje pliku źródłowego ani szablonu; szablon `.dotx` pozostaje bez zmian.

Każde `OSTRZEŻENIE:` z wyniku przekaż użytkownikowi w podsumowaniu (np. diagram mermaid pozostawiony jako kod).
Kod wyjścia `3` oznacza brak silnika DOCX — przejdź do trybu Markdown.

### Uzupełnianie szablonu z polami do wypełnienia

Markdown odtwarza strukturę szablonu: te same rozdziały w tej samej kolejności i z tymi samymi nazwami.
Wartości metryczki (tytuł, wersja, data, autor) wpisz opcją `--set` — pola w szablonie (np. `[WPISZ TUTAJ]`,
`{{TYTUŁ}}`) zostaną zastąpione z zachowaniem czcionki, pogrubienia i stylu komórki. Pola, których nie znasz,
zostaw do decyzji użytkownika (`OPEN-NNN`), nie wpisuj wartości „typowych”.

## Krok 4 — Weryfikacja wyniku

```bash
python "<runtime>/flowkit_exec.py" --role <rola> -- read-document output/dokument.docx --outline
```

Sprawdź, czy nagłówki i tabele są kompletne, a diagramy osadzone (brak ostrzeżeń o pominiętych obrazach).

## Tryb bezpieczny — Markdown

Gdy `md-to-docx` zwraca kod `3` albo polecenia są niedostępne:

1. Oddaj dokument jako **Markdown** (`.md`) z pełną strukturą (nagłówki, tabele, listy).
2. Poinformuj jednym zdaniem, czego brakuje i jak to doinstalować (patrz niżej).
3. Nie twierdź, że środowisko „nie pozwala zapisać DOCX”, dopóki nie sprawdzisz `detect-docx-libs`
   i nie spróbujesz `md-to-docx`. Podaj dokładny komunikat executora.

## Zasady sesji

- **Wykrywaj raz na początku sesji**; wynik `detect-docx-libs` jest jedynym źródłem prawdy.
- **Informuj o wyborze** jedną linią, np. *„Zapis DOCX: md-to-docx, silnik Pandoc, style z szablonu klienta.”*
- **Nie mieszaj silników** w jednej sesji bez powodu; zmianę silnika zgłoś użytkownikowi.
- Nie instaluj pakietów samodzielnie. Brakujące narzędzia wskaż użytkownikowi.

## Szybka instalacja (dla użytkownika)

```bash
# Zapis i odczyt .docx (wystarczy do md-to-docx)
pip install python-docx

# Lepsza wierność stylów szablonu: Pandoc
# Windows: winget install JohnMacFarlane.Pandoc   macOS: brew install pandoc   Linux: sudo apt install pandoc

# Diagramy mermaid (jednorazowo, potem działa lokalnie)
npm install -g @mermaid-js/mermaid-cli

# Konwersja SVG → PNG
pip install playwright && playwright install chromium
```
