# Historia zmian skilla flowkit-requirements-workshop

## 1.1 (25.11.2026)

- Przekazanie do dokumentu: przyjęte `REC` trafiają jako `DEC`, odrzucone pomijane, nierozstrzygnięte tylko za zgodą użytkownika do sekcji „Rekomendacje” (w PT/PRD `REC-NNN` ma jedno znaczenie).
- Audyt `DOC-AUDIT:` także bez orkiestratora: skill proponuje gotowe polecenie `VERIFY: DOC-AUDIT:`.
- Orkiestrator prowadzi warsztat sam i nie deleguje go do subagenta (subagenci nie mogą pytać użytkownika).

## 1.0 (25.11.2026)

- Interaktywny warsztat wymagań od pomysłu do dokumentu docelowego: koncepcja, zakres, wymagania biznesowe, wymagania techniczne, ryzyka i plan testów, dokument PT/PRD.
- Bramki faz z podsumowaniem i zatwierdzeniem przez użytkownika; brak trybu AUTO.
- Rundy do 5 pytań z wariantami, opcjami „inne” i „nie wiem” oraz rekomendacją `REC`, która staje się decyzją `DEC` dopiero po zgodzie użytkownika.
- Pochodzenie każdej treści (`USR`, `SRC`, `DEC`, `OPEN`), wykrywanie sprzeczności z wcześniejszymi decyzjami na bieżąco.
- Plik warsztatu `warsztat/<skrót>-warsztat.md` ze stanem pracy i możliwością wznowienia; przekazywany do `flowkit-client-pt-prd-writer` jako źródło nadrzędne.
