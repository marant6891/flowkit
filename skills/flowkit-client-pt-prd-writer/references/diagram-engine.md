# Silnik diagramów: przebieg pracy

Skrypty znajdują się w folderze `scripts/` skilla. W poleceniach zastąp `<SKILL_DIR>` bezwzględną ścieżką katalogu zawierającego `SKILL.md`, a polecenia uruchamiaj z katalogu projektu. Wzór modelu: [`templates/diagram-model.yaml`](../templates/diagram-model.yaml).

## Przebieg

```bash
# 1. Wygeneruj SVG i HTML (powstają tylko po przejściu walidacji)
python "<SKILL_DIR>/scripts/generate_diagram.py" modele/D-*.yaml --out output/diagrams

# 2. Wyeksportuj PNG
python "<SKILL_DIR>/scripts/export_diagram.py" output/diagrams/D-*.svg

# 3. Sprawdź zgodność z dokumentem i wygląd po wyrenderowaniu
python "<SKILL_DIR>/scripts/validate_diagram.py" output/diagrams/D-*.yaml --document output/dokument.docx --svg-dir output/diagrams

# 4. Osadź diagramy w dokumencie
python "<SKILL_DIR>/scripts/insert_diagrams.py" output/dokument.docx --diagrams output/diagrams --output output/dokument.docx
```

W trybie „Dokument końcowy bez dopisków” dodaj `--mode final` w krokach 1, 3 i 4.

## Model

**Obraz zawiera wyłącznie potwierdzone informacje.** Każdy element na obrazie ma źródło `SRC-NNN`. Słowa typu
„do potwierdzenia”, „do ustalenia” lub „TBD” i oznaczenia źródeł są na grafice odrzucane.

| Sytuacja w źródłach | Zapis w modelu |
|---|---|
| Element potwierdzony | `source: SRC-001` |
| Założenie | Nie rysuj; dodaj do `remarks` z `source: ASSUMPTION-001` |
| Nieznana wartość lub element | Nie rysuj; dodaj do `remarks` z `source: OPEN-001` |
| Nieznany kierunek komunikacji | Nie rysuj połączenia; dodaj do `remarks` z `source: OPEN-001` |
| Mechanizm niewymieniony w źródłach (np. OAuth2) | Nie dodawaj go do modelu |

Kierunki (`direction`): `forward`, `both`; `none` tylko w `er` i macierzach.

Uwagi zapisuj jako `remarks: [{text: "...", source: OPEN-001}]`. Pod podpisem powstaje akapit „Uwagi do rysunku N: ...”.
Gdy bez niepewnego elementu diagram byłby mylący, nie twórz go i zapisz temat jako `OPEN-NNN`.

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
Zapowiedź zakończona dwukropkiem pozostaje razem z tabelą lub listą, a diagram trafia za nie.
Znacznik `[[DIAGRAM:D-01]]` w osobnym akapicie wskazuje dokładne miejsce i jest zachowywany przy ponownym
generowaniu. Aby przenieść taki diagram, wstaw nowy znacznik. Opcja
`placement.position: after-heading` umieszcza diagram zaraz po nagłówku.

Skrypt dodaje zdanie wprowadzające w stylu tekstu dokumentu, grafikę, tekst alternatywny i podpis „Rysunek N.”.
Numeracja wynika z kolejności w dokumencie i uwzględnia rysunki już obecne w szablonie klienta. Uruchomienie skryptu ponownie podmienia diagramy, zamiast je powielać, więc po zmianie jednego
modelu wystarczy powtórzyć kroki 1-4 dla tego diagramu.

- **DOCX i DOTX:** szablon `.dotx` pozostaje bez zmian, a wynik zapisywany jest jako `.docx`. Osadzany jest PNG (3×), dopasowany do marginesów sekcji. Style, nagłówki i stopki szablonu pozostają bez zmian.
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
