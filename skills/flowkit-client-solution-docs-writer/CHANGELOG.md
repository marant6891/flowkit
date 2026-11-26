# Historia zmian skilla flowkit-client-solution-docs-writer

## 1.0 (26.11.2026)

- Dokumentacja gotowego rozwiązania na podstawie kodu: pomoc dla użytkownika końcowego (help, podręcznik, szybki start, FAQ), instrukcja administratora i dokumentacja techniczna.
- Brief w oknie pytań: typ dokumentu, odbiorca (rola i poziom wiedzy), kod rozwiązania (repozytorium, moduł, wersja) i szablon Word; drugie okno: zakres funkcji, zrzuty ekranu, tryb wyniku, język.
- Inwentaryzacja kodu z perspektywy odbiorcy (katalog funkcji `FEAT-NNN` z `plik:linia`), filtr uprawnień i flag funkcji, plan dokumentu zatwierdzany przed pisaniem.
- Profile odbiorcy, wzorce tematów (zadanie, pojęcie, opis ekranu, rozwiązywanie problemów, FAQ, ustawienie), szablony zapasowe, mapa „gdzie w kodzie szukać”.
- Trzy tryby wyniku (roboczy, dla klienta, końcowy) i zapis `.docx` w szablonie klienta przez `md-to-docx`.
- Kontrola `scripts/check_user_docs.py`: sekrety i adresy wewnętrzne, język kodu w pomocy dla użytkownika, oznaczenia robocze i znaczniki zrzutów, odwołania K-NN, długie myślniki, formułki, zbyt długie kroki.
