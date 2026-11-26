---
description: Diagnoza FlowKit — instalacja i wersje, plik zgód ~/.flowkit/allow.json, dziennik audytu, konfiguracja i narzędzia (tylko odczyt).
agent: agent
tools: ['vscode/askQuestions', 'read', 'edit', 'search', 'execute', 'todo']
---

Uruchom diagnozę FlowKit w terminalu: `python .github/flowkit/runtime/flowkit_doctor.py`
(gdy tego pliku nie ma, FlowKit nie jest zainstalowany w projekcie — podaj polecenie instalatora z README).

Pokaż podsumowanie: najpierw wiersze `BŁĄD`, potem `UWAGA`, każdy z podpowiedzią „→”; wiersze `OK` i `INFO` streść
jednym zdaniem. Nie zmieniaj żadnych plików. Gdy brakuje pliku zgód, podaj polecenie `init` z wyniku do uruchomienia
przez użytkownika — nie uruchamiaj go sam i nie dopisuj zgód.

Pytania do użytkownika zadawaj przez okno pytań (`#tool:vscode/askQuestions`) i kończ je wierszem `Ask: window | text — <powód> | auto`.
