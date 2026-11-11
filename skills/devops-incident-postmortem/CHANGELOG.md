# Historia zmian skilla devops-incident-postmortem

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
