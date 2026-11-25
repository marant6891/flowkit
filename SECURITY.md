# Bezpieczeństwo FlowKit

## Zgłaszanie podatności

Podatności zgłaszaj prywatnie przez **GitHub → Security → Report a vulnerability** w repozytorium
[marant6891/flowkit](https://github.com/marant6891/flowkit/security/advisories/new). Nie opisuj podatności w publicznym issue
ani w Pull Request przed wydaniem poprawki.

W zgłoszeniu podaj:

- wersję FlowKit (`.claude-plugin/plugin.json`) i platformę (Claude Code, VS Code; system operacyjny),
- komponent: executor (`runtime/flowkit_exec.py`), hook (`runtime/guard_bash.py`), skill lub agent,
- kroki odtworzenia, np. polecenie lub treść dokumentu, która obchodzi ograniczenia,
- skutek: co agent mógł wykonać, odczytać lub zmienić poza swoją rolą.

Potwierdzenie otrzymania: do 7 dni. Poprawka trafia do kolejnego wydania i do `CHANGELOG.md`, z podziękowaniem
dla zgłaszającego, jeśli tego chce.

## Zakres

Szczególnie interesują nas:

- obejście listy poleceń roli, granicy katalogu roboczego lub blokady plików wrażliwych w executorze,
- obejście hooka: uruchomienie polecenia bez executora, edycja pliku zgód, dziennika audytu, runtime albo `.git`,
- wyciek sekretów mimo ukrywania w wynikach poleceń lub w dzienniku audytu,
- prompt injection: treść dokumentu, transkrypcji lub logu, która zmienia rolę agenta albo powoduje działanie bez zgody użytkownika.

Poza zakresem (opisane w README, sekcja „Czego FlowKit nie zabezpiecza”):

- kod projektu wykonywany przez testy uruchamiane przez agenta (executor nie jest sandboxem),
- VS Code Copilot, który nie uruchamia hooka,
- polecenia, na które użytkownik świadomie zezwolił w `~/.flowkit/allow.json`.

## Wspierane wersje

Poprawki bezpieczeństwa trafiają do najnowszego wydania. Po aktualizacji zainstaluj ponownie runtime i agentów
(instrukcja w README).
