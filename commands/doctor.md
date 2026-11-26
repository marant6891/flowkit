---
description: Diagnoza FlowKit — instalacja i wersje, plik zgód ~/.flowkit/allow.json, dziennik audytu, konfiguracja i narzędzia (tylko odczyt).
argument-hint: "[--role orchestrator|analyst|...]"
allowed-tools: Bash(python:*), Glob
---

Uruchom diagnozę FlowKit i przedstaw wynik użytkownikowi.

1. Uruchom poleceniem Bash (przekaż argumenty użytkownika, jeśli są: $ARGUMENTS):
   `python "${CLAUDE_PLUGIN_ROOT}/runtime/flowkit_doctor.py" $ARGUMENTS`
   Jeśli ścieżka nie istnieje, znajdź `runtime/flowkit_doctor.py` narzędziem Glob w `~/.claude/plugins/`,
   potem w `~/.claude/flowkit/runtime/`, i uruchom znaleziony plik.
2. Pokaż podsumowanie: najpierw wiersze `BŁĄD`, potem `UWAGA`, każdy z podpowiedzią „→”. Wiersze `OK` i `INFO`
   streść jednym zdaniem. Nie zmieniaj żadnych plików.
3. Gdy brakuje pliku zgód, podaj polecenie `init` z wyniku do uruchomienia przez użytkownika. Nie uruchamiaj go sam
   i nie dopisuj zgód: plik zgód zmienia wyłącznie użytkownik.
