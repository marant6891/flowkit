# Checklista weryfikacji raportu postmortem

Przed publikacją raportu (Slack / Confluence / Jira) zweryfikuj poniższe punkty.

## A. Oś czasu i źródła
- [ ] Każde zdarzenie na osi czasu ma znacznik czasu i źródło (log / alert / chat).
- [ ] Czasy przybliżone oznaczone jako `[SZACUNEK]`.
- [ ] Zidentyfikowano i uzupełniono metryki T0–T4, TTD, TTR.
- [ ] Oś czasu odczytana chronologicznie jest logicznie spójna.

## B. Analiza przyczyn (RCA)
- [ ] Wyraźnie oddzielono Trigger (wyzwalacz) od Root Cause (przyczyny źródłowej).
- [ ] Każda root cause ma co najmniej jedno Action Item typu PREVENT.
- [ ] Analiza 5 Whys nie zatrzymała się na błędzie ludzkim (sięga głębiej do procesów/architektury).

## C. Blameless Culture
- [ ] Raport nie wskazuje imiennie winnych.
- [ ] Wszystkie sformułowania skupiają się na systemie, procesie lub automatyzacji.
- [ ] Wpływ na użytkowników i biznes jest podany w liczbach (lub zaznaczono brak danych).

## D. Action Items
- [ ] Każde działanie jest konkretne, mierzalne i przypisane do właściciela.
- [ ] Każde działanie ma termin lub numer sprintu.
- [ ] Luka w detekcji (TTD > 15 min) ma co najmniej jedno DETECT.
- [ ] Długi TTR (> 1h) ma co najmniej jedno MITIGATE.
- [ ] Brak działań ogólnych w stylu „Poprawić komunikację".

## E. Kompletność raportu
- [ ] Streszczenie (Executive Summary) zrozumiałe dla osoby nieznającej incydentu.
- [ ] Wpływ finansowy/operacyjny podany lub oznaczony jako `Brak danych`.
- [ ] Sekcja komunikacji (do klientów/interesariuszy) jest wypełniona lub zaznaczono `Nie dotyczy`.
- [ ] Usunięto hardcoded przykłady z szablonu (placeholdery w nawiasach `[...]`).
