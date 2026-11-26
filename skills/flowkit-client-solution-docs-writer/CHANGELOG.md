# Historia zmian skilla flowkit-client-solution-docs-writer

## 1.4 (26.11.2026)

- **Jakość dokumentacji technicznej i integracyjnej (`admin`/`tech`):** rozszerzono `references/help-structure.md` oraz `SKILL.md` o wymagane elementy i głębię dla dokumentacji technicznej/integracyjnej (kontrakty API, mapowanie komunikatów, przepływy end-to-end, model danych, pełne tabele konfiguracji z typem, wartością domyślną i skutkiem zmiany) oraz zakaz ogólnikowych sekcji-zaślepek.
- **Rysunki w wersji dla klienta:** zakaz pozostawiania surowych bloków `mermaid` i niezastąpionych znaczników `[[DIAGRAM:...]]` w dokumentach `client`/`final`; `scripts/check_user_docs.py` zgłasza je jako błąd i ostrzega przed zbyt krótkimi sekcjami.

## 1.3 (26.11.2026)

- **Domyślnie dokument dla klienta bez dopisków.** W treści nie ma oznaczeń źródeł, `plik:linia`, `OPEN`, `ASSUMPTION`, „DO POTWIERDZENIA”, znaczników zrzutów ani rozdziałów roboczych. Wersja robocza i rejestr pochodzenia to pliki wewnętrzne; tryb z kwestiami do wyjaśnienia i roboczy tylko na prośbę.
- Nowy skrypt `scripts/make_client_version.py`: z wersji roboczej tworzy czysty dokument i rejestr pochodzenia; luki w treści zatrzymują zapis (tryb `final`) albo stają się kwestiami K-NN (tryb `client`). Rysunki dla dokumentu bez dopisków z `--mode final`.

## 1.2 (26.11.2026)

- **Pełny obraz modułu:** stała struktura rozdziału pomocy (`references/help-structure.md`): do czego służy, pojęcia, układ ekranu z legendą, wszystkie opcje i przyciski, zadania, słownik kolumn, statusy i kolory, zakładki, uprawnienia, problemy, FAQ. Zaktualizowany szablon zapasowy i wzorce tematów.
- **Katalog opcji `OPT-NNN`** (zasada 11): każdy element modułu opisany albo pominięty z powodem; nowa kontrola `scripts/check_coverage.py` (pokrycie katalogu i obecność rysunków).
- **Rysunki** (zasada 12, Etap 3a, `references/help-diagrams.md`): obowiązkowa ocena układu ekranu, procesów, cykli statusów i przepływu danych; rysunki z silnika diagramów FlowKit i znaczniki `[[DIAGRAM:D-NN]]`.
- **Teksty interfejsu spoza repozytorium:** pytanie blokujące o eksport tłumaczeń lub zrzuty; nazwy robocze z kluczy tylko w trybie roboczym.
- Przegląd „oczami odbiorcy” i nowe sekcje checklist (kompletność, rysunki, gotowość dla odbiorcy); `check_user_docs.py` pomija sekcje robocze w trybie roboczym.

## 1.1 (26.11.2026)

- Prosty język PL i EN według standardu FlowKit (`runtime/procedures/plain-language.md`): dokumentacja i pomoc; `check_user_docs.py` sprawdza reguły wspólnym modułem `plain_language` (opcja `--lang`, reguły FAIL są błędami w trybach `client` i `final`). Nowa zasada
  nadrzędna, sekcja checklisty i kontrola poleceniem `plain-check` przed oddaniem.

## 1.0 (26.11.2026)

- Dokumentacja gotowego rozwiązania na podstawie kodu: pomoc dla użytkownika końcowego (help, podręcznik, szybki start, FAQ), instrukcja administratora i dokumentacja techniczna.
- Brief w oknie pytań: typ dokumentu, odbiorca (rola i poziom wiedzy), kod rozwiązania (repozytorium, moduł, wersja) i szablon Word; drugie okno: zakres funkcji, zrzuty ekranu, tryb wyniku, język.
- Inwentaryzacja kodu z perspektywy odbiorcy (katalog funkcji `FEAT-NNN` z `plik:linia`), filtr uprawnień i flag funkcji, plan dokumentu zatwierdzany przed pisaniem.
- Profile odbiorcy, wzorce tematów (zadanie, pojęcie, opis ekranu, rozwiązywanie problemów, FAQ, ustawienie), szablony zapasowe, mapa „gdzie w kodzie szukać”.
- Trzy tryby wyniku (roboczy, dla klienta, końcowy) i zapis `.docx` w szablonie klienta przez `md-to-docx`.
- Kontrola `scripts/check_user_docs.py`: sekrety i adresy wewnętrzne, język kodu w pomocy dla użytkownika, oznaczenia robocze i znaczniki zrzutów, odwołania K-NN, długie myślniki, formułki, zbyt długie kroki.
