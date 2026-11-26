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

- [ ] Brak `SRC-NNN`, `plik:linia`, `OPEN`, `ASSUMPTION`, `DO POTWIERDZENIA`, placeholderów i komentarzy.
- [ ] Wersja dla klienta: każde K-NN z treści ma punkt w „Kwestiach do wyjaśnienia”.
- [ ] Końcowa: każda luka rozstrzygnięta przez użytkownika; brak sekcji spoza szablonu.
- [ ] Rejestr pochodzenia zapisany poza dokumentem.
- [ ] `check_user_docs.py` z właściwymi `--audience` i `--mode`: `PASS`.
