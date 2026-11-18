# Checklist jakości diagramów

## A. Uzasadnienie
- [ ] Wszystkie procesy, przepływy, integracje i relacje z materiałów przejrzano według `references/diagram-selection.md`.
- [ ] Każdy temat spełniający kryterium ma diagram albo zapisany powód rezygnacji.
- [ ] Typ diagramu odpowiada na pytanie stawiane w sekcji.
- [ ] Listy i zestawienia parametrów pozostały listami lub tabelami.

## B. Zgodność ze źródłami
- [ ] Każdy element i połączenie na obrazie ma źródło `SRC-NNN`.
- [ ] Obraz nie zawiera słów „do potwierdzenia”, „do ustalenia” ani elementów niepewnych.
- [ ] Nie dodano systemów, mechanizmów, ról ani kierunków spoza źródeł.
- [ ] Niewiadome są opisane w „Uwagach do rysunku” pod grafiką i mają pozycję w „Tematach do wyjaśnienia”.
- [ ] Każdy węzeł występuje w tekście dokumentu pod tą samą nazwą, a etykiety połączeń, grup, ról i atrybutów wynikają z dokumentu.

## C. Kontrola automatyczna
- [ ] `validate_diagram.py` z `--document` i `--svg-dir` zakończył się wynikiem OK.
- [ ] Kontrola po wyrenderowaniu została wykonana. Jeśli ją pominięto, użytkownik o tym wie.

## D. Dokument
- [ ] Diagram stoi po pierwszym omówieniu zagadnienia, a nie na końcu dokumentu.
- [ ] Każdy diagram ma numer, podpis, zdanie wprowadzające i tekst alternatywny.
- [ ] Numeracja rysunków jest ciągła.
- [ ] Style, nagłówki i stopki szablonu klienta nie zmieniły się.
- [ ] Dokument DOCX otwarto i obejrzano strony z diagramami: grafika mieści się w marginesach, a tekst jest czytelny.

## E. Tryb „Dokument końcowy bez dopisków”
- [ ] Generowanie i walidacja przeszły z `--mode final`.
- [ ] Uwagi pod rysunkami nie zawierają oznaczeń roboczych.
- [ ] Modele z pochodzeniem elementów przekazano poza dokumentem.
