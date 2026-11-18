# Checklist jakości diagramów

## A. Uzasadnienie
- [ ] Każdy diagram przeszedł test przydatności z `references/diagram-selection.md`.
- [ ] Typ diagramu odpowiada na pytanie stawiane w sekcji.
- [ ] Listy i zestawienia parametrów pozostały listami lub tabelami.

## B. Zgodność ze źródłami
- [ ] Każdy element i połączenie ma `SRC-NNN`, `ASSUMPTION-NNN` albo `OPEN-NNN`.
- [ ] Nie dodano systemów, mechanizmów, ról ani kierunków spoza źródeł.
- [ ] Niewiadome są oznaczone `DO POTWIERDZENIA` i mają pozycję w „Tematach do wyjaśnienia”.
- [ ] Każdy węzeł występuje w tekście dokumentu pod tą samą nazwą.

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
- [ ] Na grafikach nie ma oznaczeń roboczych ani linii przerywanych.
- [ ] Modele z pochodzeniem elementów przekazano poza dokumentem.
