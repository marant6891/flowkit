# Rysunki w pomocy i dokumentacji rozwiązania

Rysunek ma pokazać użytkownikowi coś, czego tekst nie pokaże szybko: gdzie co jest na ekranie, jak przebiega
proces, jak zmieniają się statusy, skąd biorą się dane. Rysujesz tylko to, co wynika z kodu.

## Kiedy rysunek jest wymagany

| Temat w katalogu funkcji | Kryterium | Typ silnika | Przykład |
|---|---|---|---|
| Układ ekranu modułu | Ekran ma co najmniej 3 obszary (np. pasek narzędzi, tabela, mapa, panel szczegółów) | `architecture` z grupami lub `flowchart` „obszar → co zawiera” | Monitoring: tabela, panel szczegółów, mapa |
| Proces użytkownika | Co najmniej 3 kroki i decyzja, wyjątek albo ścieżka alternatywna | `flowchart` | Logowanie z kodem weryfikacyjnym i resetem hasła |
| Współpraca kilku stron | Proces przechodzi między co najmniej 2 rolami lub systemami | `swimlane` | Dyspozytor wysyła wiadomość, kierowca ją odczytuje |
| Cykl statusów | Co najmniej 3 statusy z przejściami zależnymi od działań | `state-machine` | Status zadania kierowcy |
| Przepływ danych widoczny dla odbiorcy | Dane pochodzą z innego miejsca i odświeżają się cyklicznie | `flowchart` | Serwer → tabela i mapa co ok. 60 s |
| Kolejne kroki w czasie | Etapy z kolejnością | `user-journey`, `timeline` | Pierwsze uruchomienie |
| Dokumentacja techniczna | Według [zasad wyboru diagramów](../../flowkit-client-pt-prd-writer/references/diagram-selection.md) | `architecture`, `sequence`, `er` | Komponenty, integracje, model danych |

Lista, tabela opcji i pojedyncza informacja zostają w tekście. Najwyżej jeden rysunek na podrozdział.

## Zasady

- Etykieta węzła to **dosłowny fragment tekstu dokumentu**: kroku, komunikatu albo zdania z tego samego
  rozdziału (np. krok „Kliknij **Zaloguj**.” → węzeł „Kliknij Zaloguj”, komunikat z tabeli problemów → węzeł
  z tym komunikatem). Pytanie decyzyjne też buduj z frazy z tekstu („Puste pole Login lub Hasło?”).
  `validate_diagram.py` sprawdza to dopasowanie. Bez nazw klas, plików i endpointów w pomocy dla użytkownika.
- Najwyżej 12 węzłów; większy przebieg dziel na przegląd i szczegóły.
- Decyzje formułuj jako pytania z perspektywy użytkownika („Czy konto ma kod weryfikacyjny?”).
- Układ ekranu: numeruj obszary w kolejności czytania (od lewej do prawej, z góry na dół); te same numery
  w legendzie pod rysunkiem i w tabeli opcji.
- Niewiadome: nigdy na obraz. W wersji roboczej trafiają do `remarks` (tekst „Uwagi do rysunku” pod grafiką).
  W domyślnym dokumencie dla klienta model **nie ma** `remarks` z `OPEN` ani `ASSUMPTION`: lukę zapisujesz
  w tematach do wyjaśnienia wersji roboczej (trafią do rejestru pochodzenia), a rysunki generujesz,
  osadzasz i sprawdzasz z `--mode final`.

## Model i silnik

Model YAML zapisujesz według [wzoru silnika diagramów](../../flowkit-client-pt-prd-writer/templates/diagram-model.yaml)
i [instrukcji silnika](../../flowkit-client-pt-prd-writer/references/diagram-engine.md). Silnik jest częścią
skilla `flowkit-client-pt-prd-writer`; gdy ten skill nie jest zainstalowany, oddaj modele YAML i zapisz w
odpowiedzi, że rysunki nie zostały osadzone.

```bash
python "<PT_PRD_SKILL_DIR>/scripts/generate_diagram.py" output/diagrams/D-*.yaml --out output/diagrams
python "<PT_PRD_SKILL_DIR>/scripts/export_diagram.py" output/diagrams/D-*.svg
python "<PT_PRD_SKILL_DIR>/scripts/insert_diagrams.py" output/pomoc.docx --diagrams output/diagrams --output output/pomoc.docx
python "<PT_PRD_SKILL_DIR>/scripts/validate_diagram.py" output/diagrams/D-*.yaml --document output/pomoc.docx --svg-dir output/diagrams
```

Modele źródłowe trzymaj w osobnym katalogu (np. `modele-rysunkow/`), a wynik generuj do `output/diagrams`:
generator zapisuje tam kopię modelu pod nazwą `D-NN-<typ>.yaml`, której używa `insert_diagrams.py`.
Po zmianie modelu wygeneruj rysunki do nowego katalogu albo nadpisz pliki; nie usuwaj katalogów wzorcem.

W Markdown miejsce rysunku wskazuje znacznik `[[DIAGRAM:D-NN]]` w osobnym akapicie; `insert_diagrams.py`
wstawia w to miejsce zdanie wprowadzające, grafikę i podpis „Rysunek N.”.
