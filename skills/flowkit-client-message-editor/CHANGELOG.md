# Historia zmian skilla flowkit-client-message-editor

## 1.2 (27.11.2026)

- Wersja do wysłania trafia do pliku Markdown: `mail-RRRR-MM-DD-[krótki-temat].md` (komunikator:
  `wiadomosc-…md`), tylko treść dla klienta, bez nadpisywania istniejących plików (zasada 12). `check_message.py`
  sprawdza ten plik; odpowiedź podaje ścieżkę pliku.

## 1.1 (26.11.2026)

- Prosty język PL i EN według standardu FlowKit (`runtime/procedures/plain-language.md`): zasada 11, nowe sekcje
  w zwrotach (wata, korpomowa, kalki, fałszywi przyjaciele w angielskim) i punkty checklisty.
- `check_message.py` sprawdza reguły prostego języka wspólnym modułem `plain_language` (opcja `--lang`).
  Reguły FAIL są błędami tylko z `--final`.

## 1.0 (26.11.2026)

- Redakcja szkicu e-maila lub wiadomości (Teams, Slack) do klienta: język, ton, struktura, jedna wyraźna prośba z terminem, bez nowych faktów i zobowiązań.
- Tryby `ZWYKŁY` i `DUPOKRYTKA` (potwierdzenie na piśmie: ponumerowane fakty z datami, decyzje z osobą decydującą, zakres, ryzyka, zależności od klienta, prośba o potwierdzenie do daty) oraz kanały `EMAIL` i `WIADOMOŚĆ`.
- Szablony, zwroty (emocje, ryzykowne zobowiązania, formułki), przykłady przed i po, checklista.
- Lokalna kontrola `scripts/check_message.py`: niewypełnione miejsca, uwagi wewnętrzne, sekrety, długie myślniki, emocje, ryzykowne zobowiązania, „milczenie oznacza zgodę”, elementy trybu `DUPOKRYTKA`.
