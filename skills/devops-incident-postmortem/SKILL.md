---
name: devops-incident-postmortem
version: "1.0"
tags: [devops, sre, postmortem, rca, incident, blameless, monitoring, production]
description: >
  Generuje profesjonalny, bezobwiniający (blameless) raport postmortem po awarii
  lub incydencie produkcyjnym w oparciu o dostarczone logi, zrzuty z monitoringu,
  komunikację ze Slacka/Teams i tickety. Tworzy precyzyjną oś czasu (Timeline),
  analizę przyczyn źródłowych (RCA / 5 Whys) oraz mierzalne działania naprawcze
  (Action Items). Użyj, gdy użytkownik prosi o postmortem, raport z awarii, RCA,
  analizę incydentu lub podsumowanie przestoju systemu.
---

# Cel

Przygotuj rzetelny, bezobwiniający raport postmortem opisujący przebieg incydentu produkcyjnego, jego rzeczywisty wpływ na użytkowników i biznes, przyczyny bezpośrednie i źródłowe oraz konkretne działania zapobiegające powtórzeniu się problemu.

# Zasady nadrzędne (obowiązują zawsze)

1. **Blameless Culture (Kultura bez obwiniania):** Skupiaj się na lukach w procesach, architekturze, monitoringu i automatyzacji, a nie na błędach ludzkich. Używaj sformułowań systemowych (np. „Mechanizm walidacji nie wykrył błędu w formacie konfiguracji”, a nie „Inżynier X wdrożył złą konfigurację”).
2. **Brak logu/źródła = brak wpisu w osi czasu:** Każde zdarzenie na osi czasu musi mieć określony dokładny znacznik czasu (UTC lub lokalny) i źródło (np. `Log z Pod-A`, `Alert Datadog #1234`, `Wpis ze Slack #incident-room`). Jeśli czas jest przybliżony, oznacz go dopiskiem `[SZACUNEK]`.
3. **Mierzalny wpływ (SLO / SLA / Biznes):** Jeśli dostarczono dane o błędach, oblicz: czas trwania (TTD, TTR), liczbę dotkniętych użytkowników, utracone transakcje lub procent naruszenia SLO. Jeśli danych brak, wpisz `Brak danych analitycznych – patrz ACTION-001`.
4. **Identyfikatory działań:** Wszystkie działania naprawcze muszą mieć format `ACT-001`, `ACT-002` oraz przypisany typ:
   - **PREVENT** – zapobieganie wystąpieniu przyczyny,
   - **DETECT** – szybsze wykrywanie (nowe alerty, metryki),
   - **MITIGATE** – skrócenie czasu przywracania (runbooki, automatyczny rollback).
5. **Szablon użytkownika ma pierwszeństwo:** Jeśli dostarczono firmowy szablon postmortem, użyj jego struktury. W przeciwnym razie skorzystaj z [szablonu zapasowego](./templates/postmortem-template.md).

# Etapy pracy

### Krok 1: Inwentaryzacja materiałów incydentu
Zbierz logi, wykresy metryk, zrzuty alertów, zapisy czatów awaryjnych i tickety.
Zidentyfikuj kluczowe metryki czasowe:
- **T0 (Wystąpienie):** Moment, w którym błąd zaczął występować w systemie.
- **T1 (Detekcja):** Moment, w którym system monitoringu podniósł alert lub zgłoszono błąd.
- **T2 (Rozpoczęcie diagnostyki):** Kiedy zespół zaczął reakcję.
- **T3 (Mitigacja):** Kiedy przywrócono stabilność (np. rollback, restart, zmiana routingu).
- **T4 (Pełne rozwiązanie):** Kiedy potwierdzono powrót wszystkich metryk do normy.

### Krok 2: Konstrukcja Osi Czasu (Timeline)
Uporządkuj zdarzenia chronologicznie. Każdy punkt musi zawierać:
- Znacznik czasu (np. `14:32 UTC`)
- Podsumowanie zdarzenia
- Źródło informacji

### Krok 3: Analiza 5 Whys i Przyczyny Źródłowej (RCA)
- **Przyczyna bezpośrednia (Trigger):** Co bezpośrednio wywołało awarię (np. timeout połączenia do bazy).
- **Przyczyny źródłowe (Root Causes):** Dlaczego system na to pozwolił (np. brak mechanizmu circuit breaker, brak healthchecka, brak testów obciążeniowych).

### Krok 4: Opracowanie Działań Naprawczych (Action Items)

Każde działanie musi spełniać następujące warunki — jeśli któregoś brakuje, dodaj `[Do uzupełnienia]`:

- **Konkretne i mierzalne:** Zamiast „Poprawić monitoring" wpisz „Dodać alert Datadog na błędy HTTP 5xx > 2% przez 5 min w usłudze X".
- **Przypisane do właściciela:** Konkretna osoba lub zespół (np. `SRE Team`, `Jan Kowalski`), nigdy `ktoś` ani `team`.
- **Określony termin lub sprint:** Data lub numer sprintu. Brak terminu → `[Do ustalenia na retro]`.
- **Ticket powiązania** (jeśli system istnieje): `JIRA-NNN`, `GH-NNN`, `ADO-NNN`.
- **Typ działania** (jeden z trzech):
  - `PREVENT` — eliminuje przyczynę źródłową (np. walidacja schematu przed deployem),
  - `DETECT` — skraca czas do wykrycia (nowy alert, dashboard, test syntetyczny),
  - `MITIGATE` — skraca czas przywracania (runbook, circuit breaker, automatyczny rollback).

Zasady dodatkowe:
- Każde zidentyfikowane Root Cause musi mieć co najmniej jedno działanie PREVENT.
- Każda luka w detekcji (T1 > 15 min od T0) musi mieć działanie DETECT.
- Jeśli TTR był > 1h, dodaj działanie MITIGATE poprawiające procedurę przywracania.
- Nie dodawaj działań ogólnych w stylu „Poprawić komunikację w zespole" — są nieweryfikowalne.
- Sprawdź kompletność z [checklistą weryfikacji raportu](./checklists/postmortem-review-checklist.md).

### Krok 5: Weryfikacja przed publikacją

Przejdź przez [checklistę weryfikacji raportu](./checklists/postmortem-review-checklist.md) przed udostępnieniem raportu zespołowi lub interesariuszom.

