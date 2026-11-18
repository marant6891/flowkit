# Silnik diagramów: przebieg pracy

Skrypty znajdują się w `scripts/`. Wzór modelu: [`templates/diagram-model.yaml`](../templates/diagram-model.yaml).

## Przebieg

```bash
# 1. Wygeneruj SVG i HTML (powstają tylko po przejściu walidacji)
python scripts/generate_diagram.py modele/D-*.yaml --out output/diagrams

# 2. Wyeksportuj PNG
python scripts/export_diagram.py output/diagrams/D-*.svg

# 3. Sprawdź zgodność z dokumentem i wygląd po wyrenderowaniu
python scripts/validate_diagram.py output/diagrams/D-*.yaml --document output/dokument.docx --svg-dir output/diagrams

# 4. Osadź diagramy w dokumencie
python scripts/insert_diagrams.py output/dokument.docx --diagrams output/diagrams --output output/dokument.docx
```

W trybie „Dokument końcowy bez dopisków” dodaj `--mode final` w krokach 1 i 3.

## Model

Każdy element ma pole `source` z oznaczeniem `SRC-NNN`, `ASSUMPTION-NNN` albo `OPEN-NNN`.

| Sytuacja w źródłach | Zapis w modelu |
|---|---|
| Element potwierdzony | `source: SRC-001` |
| Założenie | `source: ASSUMPTION-001` (rysowane linią przerywaną) |
| Nieznana wartość | `label: DO POTWIERDZENIA`, `source: OPEN-001` |
| Nieznany kierunek komunikacji | `direction: unknown`, `source: OPEN-001` |
| Mechanizm niewymieniony w źródłach (np. OAuth2) | Nie dodawaj go do modelu |

Kierunki (`direction`): `forward`, `both`, `unknown`; `none` tylko w `er` i macierzach.

Pola zależne od typu:

| Typ | Pola |
|---|---|
| `swimlane` | `lanes`, a w węzłach `lane` |
| `architecture`, `deployment` i podobne | opcjonalnie `groups`, a w węzłach `group` |
| `er` | węzły `type: entity` z listą `attributes`, relacje `direction: none` |
| `sequence` | kolejność `connections` jest kolejnością komunikatów; `kind: reply` dla odpowiedzi |
| `timeline`, `user-journey` | kolejność `nodes`, pole `date` |
| macierze | węzły z `axis: row` lub `axis: column`; komórka to połączenie wiersz → kolumna |

Typy węzłów: `application`, `service`, `database`, `external`, `actor`, `queue`, `process`, `decision`,
`state`, `start`, `end`, `entity`, `step`, `item`, `participant`.

## Osadzanie

Domyślnie diagram trafia za pierwszy blok treści w sekcji `placement.section` (lub `source.section`).
Znacznik `[[DIAGRAM:D-01]]` w osobnym akapicie wskazuje dokładne miejsce. Opcja
`placement.position: after-heading` umieszcza diagram zaraz po nagłówku.

Skrypt dodaje zdanie wprowadzające, grafikę, tekst alternatywny i podpis „Rysunek N.”. Numeracja wynika
z kolejności w dokumencie. Uruchomienie skryptu ponownie podmienia diagramy, zamiast je powielać, więc po zmianie jednego
modelu wystarczy powtórzyć kroki 1–4 dla tego diagramu.

- **DOCX:** osadzany jest PNG (3×), dopasowany do marginesów sekcji. Style, nagłówki i stopki szablonu pozostają bez zmian.
- **Markdown:** dokument odwołuje się względną ścieżką do pliku SVG.

## Artefakty

```text
output/
├── dokument.docx
└── diagrams/
    ├── D-01-architecture.yaml
    ├── D-01-architecture.svg
    ├── D-01-architecture.png
    └── D-01-architecture.html
```

## Zależności i tryby awaryjne

| Brak | Zachowanie |
|---|---|
| PyYAML | Silnik nie działa; zainstaluj `pyyaml` |
| Playwright z przeglądarką i CairoSVG | Powstają SVG i HTML, bez PNG; dokument oddaj w Markdown albo poinformuj, że DOCX nie zawiera diagramów |
| Playwright z przeglądarką | Kontrola po wyrenderowaniu jest zgłaszana jako POMINIĘTA |
| `python-docx` | Oddaj dokument w Markdown, zgodnie z [docx-engine.md](./docx-engine.md) |
| Możliwość uruchamiania skryptów | Dołącz modele YAML i poinformuj, że grafiki nie zostały wygenerowane |

Odrzucony diagram popraw w modelu (najczęściej podziel go na przegląd i szczegóły). Po dwóch nieudanych
poprawkach zgłoś problem użytkownikowi i nie osadzaj grafiki.

## Aktualizacja

Przy nowej wersji dokumentu porównaj źródła z modelami o tym samym `D-NN`, zaktualizuj model i wygeneruj
diagram ponownie. Następnie sprawdź, czy tekst sekcji i diagram opisują ten sam stan.
