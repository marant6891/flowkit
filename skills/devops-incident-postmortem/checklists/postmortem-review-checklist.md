# Checklista weryfikacji raportu postmortem

Przed publikacją raportu (Slack / Confluence / Jira / Status Page) zweryfikuj poniższe punkty:

## A. Kwalifikacja i role SRE
- [ ] Określono poziom incydentu (SEV-1 / SEV-2 / SEV-3 / Near-Miss).
- [ ] Wskazano Incident Commandera (IC), Tech Leada oraz Comms Leada.
- [ ] Podano metryki czasowe: T0–T4, TTD (czas do wykrycia) i TTR (czas do naprawy).

## B. Oś czasu i źródła
- [ ] Każde zdarzenie na osi czasu ma dokładny znacznik czasu i źródło (log / alert / chat).
- [ ] Czasy przybliżone oznaczono jako `[SZACUNEK]`.
- [ ] Oś czasu odczytana chronologicznie jest logicznie spójna i kompletna.

## C. Analiza wieloczynnikowa (RCA)
- [ ] Zidentyfikowano bezpośredni Wyzwalacz (Trigger).
- [ ] Zidentyfikowano czynniki wzmacniające (Amplifiers / Cascading failure).
- [ ] Zidentyfikowano luki w detekcji (Detection Gap) oraz procesie/testach (Process Gap).
- [ ] Analiza 5 Whys sięga do architektury i procesów, a nie zatrzymuje się na błędzie człowieka.

## D. Blameless Culture
- [ ] Raport nie wskazuje imiennie winnych awarii.
- [ ] Wszystkie sformułowania skupiają się na odporności systemów, monitoringu i runbookach.
- [ ] Wpływ na użytkowników, transakcje i SLA podano liczbowo (lub oznaczono brak danych).

## E. Komunikacja i Status Page
- [ ] Odnotowano wpisy na publicznym Status Page (godziny i treść).
- [ ] Zidentyfikowano wpływ na umowne SLA i ewentualne ryzyka kar umownych.

## F. Działania naprawcze (Action Items)
- [ ] Każde działanie jest konkretne, mierzalne i przypisane do właściciela (DRI).
- [ ] Każde działanie ma określony termin lub numer sprintu.
- [ ] Każda przyczyna źródłowa ma co najmniej jedno działanie `PREVENT`.
- [ ] Luka w detekcji (TTD > 15 min) ma co najmniej jedno działanie `DETECT`.
- [ ] Długi czas przywracania (TTR > 1h) ma co najmniej jedno działanie `MITIGATE`.
