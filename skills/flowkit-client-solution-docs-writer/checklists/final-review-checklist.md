# Checklista końcowa (Etap 6)

## A. Brief

- [ ] Typ dokumentu, odbiorca, zakres kodu i szablon zgodne z odpowiedziami z Etapu 0.
- [ ] Profil odbiorcy zastosowany konsekwentnie (słownictwo, poziom szczegółu, forma zwracania się).

## B. Prawdziwość

- [ ] Każdy temat ma źródło w rejestrze (`SRC-NNN`, `plik:linia`); zdanie bez źródła usunięte albo `OPEN`.
- [ ] **Test wykonalności:** kroki każdego zadania sprawdzone w kodzie: kolejność, nazwy, warunki, wynik.
- [ ] Rola odbiorcy ma uprawnienia do każdego opisanego ekranu i akcji.
- [ ] Brak funkcji za flagą, nieukończonych lub niedostępnych opisanych jako dostępne.
- [ ] Limity, formaty i terminy pochodzą z walidacji lub konfiguracji, nie z „typowych wartości”.
- [ ] Komunikaty przepisane dosłownie z aplikacji.
- [ ] Teksty interfejsu pochodzą z tłumaczeń, eksportu lub zrzutów; nazwy robocze z kluczy tylko w trybie roboczym.

## C. Język odbiorcy

- [ ] Help dla użytkownika: brak nazw klas, plików, endpointów, tabel, wyjątków, kodów HTTP i żargonu.
- [ ] Nazwy elementów interfejsu pogrubione i identyczne z aplikacją; ścieżki menu z `>`.
- [ ] Jedna czynność na krok, kroki numerowane, wynik po krokach.
- [ ] Pojęcia domenowe wyjaśnione raz; terminologia jednolita i zgodna z interfejsem.
- [ ] Brak długich myślników, emoji i formułek („Niniejszy dokument…”, „Należy zauważyć…”).

## D. Bezpieczeństwo

- [ ] Brak haseł, kluczy, tokenów, connection stringów, adresów wewnętrznych i danych osobowych.
- [ ] Przykłady na danych fikcyjnych.

## E. Szablon i forma

- [ ] Struktura, numeracja i nazwy sekcji zgodne z szablonem; sekcje niedotyczące: „Nie dotyczy.” albo pominięte (szablon zapasowy).
- [ ] Metryczka wypełniona tylko danymi ze źródeł lub od użytkownika.
- [ ] `md-to-docx` z `--template` lub `--reference-doc`; `Kontrola DOCX: PASS`; ostrzeżenia przekazane.
- [ ] Zrzuty: dostarczone wstawione z podpisem; w wersji dla klienta i końcowej brak znaczników `[ZRZUT: …]`.

## F. Wersja dla klienta i końcowa

- [ ] Brak `SRC-NNN`, `plik:linia`, `OPEN`, `ASSUMPTION`, `DO POTWIERDZENIA`, placeholderów, komentarzy, surowych bloków ```` ```mermaid ```` oraz niezastąpionych znaczników `[[DIAGRAM:...]]`.
- [ ] Wersja dla klienta: każde K-NN z treści ma punkt w „Kwestiach do wyjaśnienia”.
- [ ] Końcowa: każda luka rozstrzygnięta przez użytkownika; brak sekcji spoza szablonu.
- [ ] Brak powierzchownych sekcji-wstępów: w dokumentacji technicznej/admin zawarto konkretne kontrakty API, pełne tabele konfiguracji (z wartością domyślną i skutkiem zmiany), przepływy end-to-end oraz model danych wynikający z kodu.
- [ ] Rejestr pochodzenia zapisany poza dokumentem.
- [ ] `check_user_docs.py` z właściwymi `--audience` i `--mode`: `PASS`.

## Prosty język (`<runtime>/procedures/plain-language.md`)
- [ ] Najważniejsze na początku: każdy temat zaczyna się od tego, co użytkownik osiągnie.
- [ ] Zdania do 20 słów (EN: 25); czasowniki zamiast rzeczowników („wdrożyć”, nie „dokonać wdrożenia”).
- [ ] Bez korpomowy i kalk („zaparkować”, „zaadresować”, „na ten moment”, „To, co…, to…”, „To drugi raz, gdy…”); w EN bez fałszywych przyjaciół (*actual*, *eventually*).
- [ ] Szyk naturalny: to, co znane, na początku zdania, a nowe na końcu; strona czynna, gdy wiadomo, kto działa.
- [ ] Skróty rozwinięte przy pierwszym użyciu, chyba że są w słowniku projektu.
- [ ] `plain-check` (wbudowany w `check_user_docs.py`) nie zgłasza błędów; ostrzeżenia poprawione albo uzasadnione.

## G. Kompletność (katalog opcji)

- [ ] Katalog opcji obejmuje wszystkie przyciski, ikony, pola, filtry, kolumny (także ukryte), zakładki, polecenia menu, statusy i kolory w zakresie.
- [ ] Każda pozycja jest opisana albo pominięta z powodem; `check_coverage.py`: `PASS`.
- [ ] Opis opcji mówi, co się stanie lub co znaczy informacja, i podaje warunek dostępności.
- [ ] Każdy rozdział modułu ma podrozdziały ze struktury pomocy (do czego służy, układ ekranu, opcje, zadania, słownik kolumn, statusy, zakładki, uprawnienia).

## H. Rysunki

- [ ] Plan rysunków z Etapu 2 zrealizowany: układ ekranu każdego modułu, procesy z decyzją, cykle statusów, przepływ danych.
- [ ] Węzły nazwane jak w dokumencie i interfejsie; brak nazw z kodu w pomocy dla użytkownika.
- [ ] Każdy rysunek ma zdanie wprowadzające, podpis „Rysunek N.” i legendę, gdy numeruje obszary.
- [ ] Niewiadome w uwagach pod rysunkiem (tryb roboczy) albo w kwestiach do wyjaśnienia (wersja dla klienta).

## Gotowość dla odbiorcy (przegląd oczami nowego użytkownika)

- [ ] Po przeczytaniu rozdziału wiem, do czego służy moduł i skąd są dane.
- [ ] Wiem, co oznacza każdy obszar ekranu, przycisk i kolumna, którą widzę.
- [ ] Umiem wykonać każde typowe zadanie bez zgadywania.
- [ ] Wiem, co znaczą statusy i kolory i co mam zrobić, gdy coś jest nie tak.
- [ ] Wiem, dlaczego nie widzę opcji, której nie mam (uprawnienia).
