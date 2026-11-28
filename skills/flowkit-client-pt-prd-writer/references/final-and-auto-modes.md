# Tryby na żądanie: dokument końcowy i AUTO

Plik czytaj tylko wtedy, gdy użytkownik wybrał jeden z tych trybów (Etap 0, pkt 5 albo prefiks `AUTO:`).
Zasady nadrzędne z `SKILL.md` obowiązują bez zmian.

Spis treści:
- [Tryb „Dokument końcowy bez dopisków”](#tryb-dokument-końcowy-bez-dopisków)
- [Tryb AUTO: cała praca na rekomendacjach](#tryb-auto-cała-praca-na-rekomendacjach)

## Tryb „Dokument końcowy bez dopisków”

Cel: kompletny dokument **dokładnie w udostępnionym szablonie**, gotowy do
przekazania klientowi, bez śladów pracy skilla. Gdy użytkownik nie dał szablonu,
użyj szablonu zapasowego z tymi samymi regułami.

1. **Czego nie ma w dokumencie:** `SRC-NNN`, `plik:linia`, `ASSUMPTION-NNN`,
   `OPEN-NNN`, `Q-NNN`, `REC-NNN`, `DO POTWIERDZENIA`, „Nie analizowano”,
   „Brak danych”, kolumn „Źródło” i legendy oznaczeń, komentarzy,
   placeholderów oraz sekcji dodawanych przez skill (Materiały źródłowe,
   Założenia, Tematy do wyjaśnienia, Rekomendacje) - chyba że przewiduje je
   sam szablon. Identyfikatory wymagań (`FR-001` itd.) stosuj tylko, jeśli
   używa ich szablon.
2. **Struktura = szablon.** Żadnych dodanych, usuniętych ani przestawionych
   sekcji. Sekcja, której zmiana nie dotyczy, dostaje samo „Nie dotyczy.”
   (bez odwołań do źródeł).
3. **Treść nadal wyłącznie ze źródeł.** Pracuj jak w trybie roboczym (Etapy
   1-5), a oznaczenia prowadź w **rejestrze pochodzenia** poza dokumentem:
   sekcja szablonu → źródła, przyjęte założenia, luki. Rejestr oddaj jako
   osobny plik `<nazwa-dokumentu>-rejestr-pochodzenia.md` albo w odpowiedzi.
4. **Luki rozstrzyga użytkownik, nie skill.** Przed wygenerowaniem pokaż listę
   wszystkich `OPEN` i `ASSUMPTION` i dla każdej pozycji poproś o decyzję:
   - (a) uzupełnienie brakującej informacji,
   - (b) zatwierdzenie założenia jako ustalenia,
   - (c) pominięcie elementu w dokumencie,
   - (d) neutralne sformułowanie w języku klienta, bez identyfikatorów
     (np. „Do ustalenia z Zamawiającym przed rozpoczęciem prac”).

   Nigdy nie wypełniaj luki samodzielnie „typową” treścią. Jeśli użytkownik
   każe generować bez odpowiedzi, zastosuj (d), a gdy element bez tej
   informacji nie ma sensu - (c), i wypisz te miejsca pod dokumentem.
5. **Status dokumentu** w metryczce wpisz taki, jaki wskaże użytkownik; nie
   nadawaj samodzielnie statusu „Zaakceptowany”.
6. **Weryfikacja:** oprócz zwykłej checklisty wykonaj sekcję F
   [checklisty końcowej](../checklists/final-review-checklist.md) i uruchom
   `check_client_version.py <dokument> --mode final`.

## Tryb AUTO: cała praca na rekomendacjach

Włącz, gdy użytkownik użyje prefiksu `AUTO:` albo poprosi wprost o realizację całości bez pytań
(„zrób całość”, „akceptuj rekomendacje”, „bez dopytywania”). Skill przechodzi Etapy 0-6 bez
zatrzymywania się, a każde pytanie rozstrzyga swoją rekomendacją:

1. Pytania z Etapów 1, 2 i 4 nie są zadawane - wypisz je w dokumencie i w odpowiedzi.
2. Pytanie z „Propozycją domyślną” wynikającą z materiałów lub bezpieczną i odwracalną → przyjmij ją
   jako `ASSUMPTION-NNN (AUTO)`. Pytanie bez takiej propozycji → `OPEN-NNN`. Nigdy nie zgaduj treści
   merytorycznej: zasady 1, 3, 6 i 7 obowiązują bez zmian.
3. Plan sekcji i plan diagramów z Etapu 4 realizuj w wersji rekomendowanej (diagram tam, gdzie spełnia
   kryterium).
4. Domyślnie oddaj **Wersję dla klienta** (status dokumentu: „Roboczy” lub zgodnie z szablonem): luki i założenia trafiają do sekcji „Kwestie do wyjaśnienia” (K-NN, Z-NN), a rejestr pochodzenia powstaje poza dokumentem. W trybie końcowym bez dopisków luki rozstrzygaj według pkt 4 tego trybu: (d) neutralne sformułowanie, a gdy element bez informacji nie ma sensu - (c) pominięcie. W trybie roboczym (tylko na prośbę) zostaw `OPEN-NNN` i `ASSUMPTION-NNN (AUTO)` w treści.
5. Zapis: jeśli jest szablon, `md-to-docx` z `--template` lub `--reference-doc`; potem Etap 6 w całości.
6. Zatrzymaj się tylko, gdy: brak materiałów źródłowych, szablon wspomniany, ale niedostępny, polecenie
   zostało odrzucone dwa razy, albo działanie wymaga zgody (usunięcie plików, wysyłka, publikacja).
7. Pod dokumentem wypisz **rejestr decyzji AUTO**: każde pytanie, przyjętą rekomendację i jej
   identyfikator, aby użytkownik mógł je potwierdzić lub odrzucić po fakcie.
