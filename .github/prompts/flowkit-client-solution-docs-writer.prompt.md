---
description: Tworzy pomoc dla użytkownika końcowego, instrukcję administratora albo dokumentację techniczną gotowego rozwiązania na podstawie jego kodu, dla wskazanego odbiorcy i w szablonie Word.
agent: agent
tools: ['vscode/askQuestions', 'read', 'edit', 'search', 'execute', 'todo']
---

Przygotuj dokumentację rozwiązania zgodnie z wytycznymi z pliku `skills/flowkit-client-solution-docs-writer/SKILL.md`.

Zasady nadrzędne:
1. Najpierw brief w oknie pytań: typ dokumentu, odbiorca (rola, poziom wiedzy), kod rozwiązania (ścieżka, moduł, wersja), szablon Word. Nie pytaj o to, co już jest w prośbie.
2. Kod jest źródłem prawdy: każdy krok, pole, komunikat i uprawnienie z kodu (`SRC-NNN`, `plik:linia`); brak w kodzie to `OPEN-NNN`, nie domysł.
3. Opisuj tylko to, co odbiorca widzi i może zrobić; w pomocy dla użytkownika bez nazw klas, plików, endpointów i kodów HTTP.
4. Plan dokumentu (spis treści, pominięte funkcje, brakujące zrzuty) zatwierdza użytkownik przed pisaniem.
5. Wynik `.docx` przez `md-to-docx` z szablonem użytkownika; na koniec `check_user_docs.py` z `--audience` i `--mode`.
6. Prosty język (PL i EN) według `runtime/procedures/plain-language.md` (po instalacji: `.github/flowkit/runtime/procedures/`): najważniejsze na początku, zdania do 20 słów, czasowniki zamiast „dokonać zmiany”, bez korpomowy i kalk; przed oddaniem `plain-check`.

Pytania do użytkownika zadawaj przez okno pytań (`#tool:vscode/askQuestions`) i kończ je wierszem `Ask: window | text — <powód> | auto`.
