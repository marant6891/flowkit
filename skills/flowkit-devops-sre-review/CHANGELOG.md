# Historia zmian skilla flowkit-devops-sre-review

## 1.2 (26.11.2026)

- Prosty język PL i EN według standardu FlowKit (`runtime/procedures/plain-language.md`): ustalenia i rekomendacje. Nowa zasada
  nadrzędna, sekcja checklisty i kontrola poleceniem `plain-check` przed oddaniem.

## 1.1 (25.11.2026)

- Sekcja „Pytania do użytkownika”: pytania przez okno pytań (VS Code `vscode/askQuestions`, Claude Code `AskUserQuestion`), najwyżej 4 w oknie, rekomendacja pierwsza, wiersz diagnostyczny `Ask:`; w subagencie pytania wracają jako `QUESTION-NNN`.

## 1.0 (20.11.2026)

- Przegląd niezawodności usługi: SLI/SLO i error budget, alerty, RED/USE, sondy, requests i limits, HPA i PDB, backup i RPO/RTO, koszt.
- Ustalenia tylko z dowodem (`plik:linia`), statusy `PASS`/`FAIL`/`UNKNOWN`/`NOT_RUN`, interpretacje oddzielone od faktów.
- Rekomendacje monitoringu z sygnałem, progiem, oknem i uzasadnieniem; backup bez testu odtworzenia nie jest `PASS`.
