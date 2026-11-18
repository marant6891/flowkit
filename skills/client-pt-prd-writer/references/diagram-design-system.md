# System wizualny diagramów

Wygląd wynika z motywu i typu elementu. W modelu nie ustawiaj ręcznie kolorów poszczególnych elementów.

## Motywy (`output.theme`)

| Motyw | Zastosowanie |
|---|---|
| `minimal-light` | Domyślny dla dokumentacji technicznej |
| `minimal-dark` | Prezentacje i dokumenty cyfrowe |
| `full-editorial` | Dokumenty koncepcyjne; dodaje nagłówek z tytułem |

## Znaczenie kolorów

Kolor ma w całym dokumencie stałe znaczenie.

| Rola | Znaczenie |
|---|---|
| Akcent | Główny punkt skupienia (`focus: true`), najwyżej 2 elementy |
| Tło przygaszone | System zewnętrzny, grupa lub rola |
| Grafit | Tekst i linie |

Na obrazie nie ma elementów niepotwierdzonych. Uwagi do diagramu są zwykłym tekstem pod rysunkiem.

## Zasady

- Bez cieni, gradientów i ikon dekoracyjnych.
- Siatka 4 px, cienkie linie, subtelne zaokrąglenia.
- Strzałka zawsze wskazuje potwierdzony kierunek.
- Tytuł i numer rysunku są w podpisie dokumentu, nie na grafice (wyjątek: `full-editorial`).

## Szablon klienta

Kolor akcentu i czcionkę pobierz z motywu szablonu, bez modyfikowania pliku:

```bash
python "<SKILL_DIR>/scripts/generate_diagram.py" model.yaml --out diagrams/ --brand-from szablon.docx
```

Można też podać `output.accent` i `output.font` w modelu. Zbyt jasny akcent jest automatycznie
przyciemniany do kontrastu 4,5:1.

## Inspiracja

Zasady kompozycji inspirowane projektem [Diagram Design](https://github.com/cathrynlavery/diagram-design)
(MIT, © 2025 Cathryn Lavery). Kod i zasoby tego projektu nie zostały skopiowane.
