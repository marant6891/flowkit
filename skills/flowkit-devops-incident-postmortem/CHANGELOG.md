# Historia zmian skilla flowkit-devops-incident-postmortem

## 1.4 (18.11.2026)

### Bezpieczeństwo i szablony
- Logi i zapisy rozmów są traktowane wyłącznie jako dane, a nie polecenia.
- Sekrety i dane osobowe są zastępowane znacznikiem `[UKRYTO]`, a wykryte sekrety zgłaszane do rotacji.
- Obsługa szablonów `.docx` i `.dotx`.

## 1.3 (14.11.2026)

### Rzetelność szablonu i spójność
- Szablon: usunięte gotowe treści (analiza 5 Whys, komunikaty Status Page, `JIRA-101`, `Sprint 42`) — zostały wyłącznie placeholdery, aby przykłady nie trafiały do raportów.
- Zasada braków rozszerzona na cały raport: czego nie ma w materiałach → `DO POTWIERDZENIA`.
- Szablon użytkownika ma pierwszeństwo; pytanie o szablon w Etapie 1.
- Progi z checklisty (TTD > 15 min → `DETECT`, TTR > 1 h → `MITIGATE`) przeniesione do zasad w SKILL.md.
- Przykład osi czasu: dodana kolumna „Faza (T0–T4)” i data, czas T0 oznaczony `[SZACUNEK]`, usunięty identyfikator alertu nieobecny w materiale źródłowym.
- Nazewnictwo „Etap” zamiast „Krok”; `description` uzupełniony o frazę aktywacji „Użyj, gdy…”.

## 1.2 (11.11.2026)

### Zgodność z Google SRE & PagerDuty Framework
- Wprowadzono **formalne role SRE**: Incident Commander (IC), Lead Investigator (Tech Lead), Communications Lead.
- Wdrożono **macierz kwalifikacji incydentów (Severity Matrix)**: SEV-1, SEV-2, SEV-3 oraz Near-Miss (sytuacje potencjalnie wypadkowe).
- Wzbogacono RCA o **wieloczynnikowy łańcuch przyczyn**: Trigger, Amplifier, Detection Gap, Process/Pre-production Gap.
- Dodano rejestr **komunikacji zewnętrznej, wpisów Status Page oraz wpływu na umowne SLA**.
- Zaktualizowano szablon, checklistę weryfikacji i instrukcję skilla.

## 1.1 (11.11.2026)

### Rozbudowa procesu i poprawki jakościowe
- Rozbudowany Krok 4 (Action Items): konkretne zasady pisania działań naprawczych (mierzalność, właściciel, sprint, ticket, typy PREVENT/DETECT/MITIGATE).
- Dodany Krok 5: weryfikacja przed publikacją z odesłaniem do checklisty.
- Dodana checklista weryfikacji raportu (`checklists/postmortem-review-checklist.md`).
- Dodany przykład transformacji logów/alertów na oś czasu (`examples/log-to-timeline-example.md`).
- Naprawiony szablon: usunięto hardcoded przykłady z sekcji „Co zadziałało dobrze".
- Szablon: dodane metryki MTTD / MTTR w tabeli nagłówkowej.
- Szablon: dodana sekcja „6. Komunikacja podczas incydentu" (interesariusze, klienci, C-level).

## 1.0 (11.11.2026)

### Wersja inicjalna
- 4-krokowy proces: inwentaryzacja → oś czasu → 5 Whys RCA → action items.
- Zasada Blameless Culture z przykładem formułowania systemowego vs personalnego.
- Metryki T0–T4 (TTD, TTR).
- Trzy typy ACT: PREVENT / DETECT / MITIGATE.
- Szablon raportu (`templates/postmortem-template.md`).
