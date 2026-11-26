# Checklista bramek warsztatu wymagań

## Każda runda i bramka
- [ ] Najwyżej 5 pytań w rundzie; każde ma `Q-NNN`, „po co pytam”, warianty, „inne” i „nie wiem”.
- [ ] Żadna odpowiedź nie została przyjęta za użytkownika; `REC` bez jego zgody nie jest w rejestrach jako treść.
- [ ] Każdy wpis w rejestrach ma pochodzenie (`USR`, `SRC`, `DEC`, `ASSUMPTION` na wyraźne polecenie) albo jest `OPEN`.
- [ ] Liczby (budżet, terminy, wolumeny, SLA) pochodzą od użytkownika lub z materiału, nie z założeń.
- [ ] Nowe odpowiedzi nie przeczą zatwierdzonym decyzjom; sprzeczności pokazano i rozstrzygnął je użytkownik.
- [ ] Plik warsztatu zaktualizowany (albo zmiany oddane jako blok do wklejenia).
- [ ] Podsumowanie fazy ma najwyżej 15 linii i kończy się pytaniem: zatwierdzasz / poprawiasz / wracamy.

## Faza 0: Koncepcja
- [ ] Wizja: problem, dla kogo, co zmieniamy, jak poznamy sukces.
- [ ] Co najmniej jeden `GOAL` z miarą sukcesu albo `OPEN` na brakującą wartość.
- [ ] Ograniczenia i interesariusze zapisane lub jawnie „brak danych”.

## Faza 1: Zakres
- [ ] Każda możliwość ma decyzję: MVP, później albo poza zakresem.
- [ ] Zakres MVP mieści się w ograniczeniach z Fazy 0 albo konflikt rozstrzygnął użytkownik.

## Faza 2: Wymagania biznesowe
- [ ] Role mają opisane uprawnienia.
- [ ] Każdy proces ma stan docelowy i obsługę wyjątków (albo `OPEN`).
- [ ] Każda `US` z zakresu MVP ma co najmniej `AC` ścieżki poprawnej i jednej ścieżki błędu.
- [ ] Reguły biznesowe pochodzą z odpowiedzi lub materiałów, nie z „praktyki branżowej”.

## Faza 3: Wymagania techniczne
- [ ] Pytania techniczne dopasowane do rozmówcy; braki skierowane jako `OPEN` do osoby odpowiedzialnej.
- [ ] Ustalenia z kodu mają `plik:linia` i zostały potwierdzone.
- [ ] Każda `INT` ma właściciela po drugiej stronie albo `OPEN`.
- [ ] Każde `NFR` ma wartość od użytkownika albo `OPEN`; brak wymyślonych progów.
- [ ] Warianty rozwiązania przedstawione jako `REC` z alternatywą i konsekwencjami.

## Faza 4: Ryzyka, plan i weryfikacja
- [ ] Ryzyka mają właściciela i sposób ograniczenia.
- [ ] Każdy `AC` z MVP ma `TEST`; luki pokrycia pokazane, nie zamaskowane.
- [ ] `OPEN` mają osobę i termin; oznaczono te, które blokują dokument.

## Faza 5: Przed przekazaniem do dokumentu
- [ ] Fazy 0-4 zatwierdzone (w głębokości szybkiej: fazy wymagane dla tej głębokości).
- [ ] Ustalone: szablon, format, tryb wyniku i miejsce zapisu.
- [ ] Tryb „końcowy bez dopisków” tylko bez otwartych `OPEN`.
- [ ] Plik warsztatu przekazany do `flowkit-client-pt-prd-writer` jako źródło nadrzędne.
- [ ] Ustalenia `DOC-AUDIT:` wróciły do właściwej fazy warsztatu, a dokument wygenerowano ponownie.
- [ ] Akceptacja użytkownika i ścieżka wersji docelowej zapisane w pliku warsztatu.

## Prosty język (`<runtime>/procedures/plain-language.md`)
- [ ] Najważniejsze na początku: każde wymaganie to jedno zdanie z podmiotem i czasownikiem.
- [ ] Zdania do 20 słów (EN: 25); czasowniki zamiast rzeczowników („wdrożyć”, nie „dokonać wdrożenia”).
- [ ] Bez korpomowy i kalk („zaparkować”, „zaadresować”, „na ten moment”, „To, co…, to…”, „To drugi raz, gdy…”); w EN bez fałszywych przyjaciół (*actual*, *eventually*).
- [ ] Szyk naturalny: to, co znane, na początku zdania, a nowe na końcu; strona czynna, gdy wiadomo, kto działa.
- [ ] Skróty rozwinięte przy pierwszym użyciu, chyba że są w słowniku projektu.
- [ ] `plain-check` na dokumencie docelowym z `--strict` nie zgłasza błędów; ostrzeżenia poprawione albo uzasadnione.
