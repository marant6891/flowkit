# Checklist discovery

Dla każdego punktu zaznacz jeden status:
`ŹRÓDŁO (SRC-NNN)` / `NIE DOTYCZY` / `BRAK → pytanie Q-NNN lub OPEN-NNN`.
Pytaj tylko o punkty `BRAK`, które dotyczą tej zmiany.

## Szablon i forma
- [ ] Czy użytkownik dostarczył szablon dokumentu (lub wzorcowy dokument)?
- [ ] W jakim formacie ma powstać dokument (.docx, .md, inny)?
- [ ] Jaki jest odbiorca (biznes / IT klienta / oba)?
- [ ] Wersja i status dokumentu, autor, klient, projekt.

## Źródła
- [ ] Jakie materiały są dostępne (ticket, mail, notatka, oferta, dokumentacja, kod)?
- [ ] Czy materiały są aktualne i niesprzeczne? (sprzeczności → OPEN)

## Biznes
- [ ] Jaki problem rozwiązuje zmiana?
- [ ] Czy cel ma mierzalny efekt (podany w źródle)?
- [ ] Kto jest właścicielem decyzji po stronie klienta?
- [ ] Kto korzysta ze zmienianej funkcji?
- [ ] Jaki jest proces obecny i docelowy (jeśli zmiana go dotyczy)?
- [ ] Co jest w zakresie, a co jawnie poza zakresem?

## Funkcjonalność
- [ ] Jakie funkcje są dodawane / zmieniane / usuwane?
- [ ] Jakie są kryteria akceptacji (podane lub możliwe do wyprowadzenia ze źródła)?
- [ ] Przypadki brzegowe, walidacje, komunikaty – czy są określone?
- [ ] Czy zmieniają się role lub uprawnienia?

## Technologia (tylko przy dostępie do kodu/dokumentacji)
- [ ] Które moduły / pliki / endpointy są dotknięte?
- [ ] Jakie dane są tworzone, zmieniane, usuwane? Czy potrzebna migracja?
- [ ] Które integracje są dotknięte?
- [ ] Czy zmiana wpływa na API i zgodność wsteczną?

## Bezpieczeństwo i zgodność (jeśli dotyczy)
- [ ] Czy przetwarzane są dane osobowe? Wymagania RODO / regulacyjne?
- [ ] Wymagania uwierzytelniania, autoryzacji, audytu?

## Wdrożenie
- [ ] Środowiska, termin, sposób wdrożenia, rollback – czy są znane?
- [ ] Kto akceptuje zmianę i na jakiej podstawie (definicja „gotowe”)?
