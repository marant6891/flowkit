---
description: Redaguje szkic e-maila lub wiadomości do klienta (tryb zwykły albo „dupokrytka” — potwierdzenie na piśmie), bez dodawania faktów i zobowiązań.
agent: agent
tools: ['vscode/askQuestions', 'read', 'edit', 'search', 'execute', 'todo']
---

Zredaguj wklejony szkic zgodnie z wytycznymi z pliku `skills/flowkit-client-message-editor/SKILL.md`.

Zasady nadrzędne:
1. Ustal tryb (`ZWYKŁY` albo `DUPOKRYTKA`) i kanał (`EMAIL` albo `WIADOMOŚĆ`) i podaj je w pierwszym wierszu.
2. Nie dodawaj faktów, dat, nazwisk ani obietnic. Braki oznacz `[DO UZUPEŁNIENIA: …]`.
3. Ton partnerski i rzeczowy, jedna wyraźna prośba z terminem, bez ryzykownych zobowiązań i bez „milczenie oznacza zgodę”.
4. W trybie `DUPOKRYTKA`: ponumerowane fakty z datami, decyzje i kto je podjął, zakres, ryzyka, zależności od klienta, prośba o potwierdzenie do daty.
5. Zapisz wersję do wysłania (tylko treść dla klienta) w pliku `mail-RRRR-MM-DD-[krótki-temat].md` (komunikator: `wiadomosc-…md`), nie nadpisuj istniejących plików. W odpowiedzi podaj ścieżkę pliku, wersję do wysłania, listę zmian, listę braków i uwagi tylko dla autora. Niczego nie wysyłaj.
6. Prosty język (PL i EN) według `runtime/procedures/plain-language.md` (po instalacji: `.github/flowkit/runtime/procedures/`): najważniejsze na początku, zdania do 20 słów, czasowniki zamiast „dokonać zmiany”, bez korpomowy i kalk; przed oddaniem `plain-check`.

Pytania do użytkownika zadawaj przez okno pytań (`#tool:vscode/askQuestions`) i kończ je wierszem `Ask: window | text — <powód> | auto`.
