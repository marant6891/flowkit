---
name: devops-incident-postmortem
version: "1.2"
tags: [devops, sre, postmortem, rca, incident, blameless, monitoring, production, google-sre, pagerduty, statuspage]
description: >
  Generuje profesjonalny, bezobwiniający (blameless) raport postmortem zgodny ze
  standardami Google SRE i PagerDuty po awarii produkcyjnej. Tworzy precyzyjną oś
  czasu (Timeline T0–T4), wieloczynnikową analizę przyczyn (Trigger, Amplifier,
  Detection/Process Gap, 5 Whys), rejestr komunikacji Status Page oraz mierzalne
  działania naprawcze (Action Items PREVENT/DETECT/MITIGATE).
---

# Cel

Przygotuj rzetelny, bezobwiniający raport postmortem opisujący przebieg incydentu produkcyjnego, jego rzeczywisty wpływ na użytkowników, SLA i biznes, łańcuch przyczyn systemowych (Trigger, Amplifier, Gaps) oraz konkretne działania naprawcze zapobiegające powtórzeniu problemu.

# Zasady nadrzędne (obowiązują zawsze)

1. **Blameless Culture (Kultura bez obwiniania):** Skupiaj się na lukach w procesach, architekturze, monitoringu i automatyzacji, a nie na błędach ludzkich. Używaj sformułowań systemowych (np. „Mechanizm walidacji nie wykrył błędu w formacie konfiguracji”, a nie „Inżynier X wdrożył złą konfigurację”).
2. **Kwalifikacja incydentu (Severity Matrix):**
   - **SEV-1 (Krytyczny):** Całkowita niedostępność kluczowej usługi, utrata danych lub bezpośrednie naruszenie SLA klientów. Wymaga pełnego postmortem w ciągu 48h.
   - **SEV-2 (Poważny):** Częściowa degradacja wydajności, brak redundancji, wpływ na część użytkowników.
   - **SEV-3 (Umiarkowany):** Drobny błąd bez bezpośredniego wpływu na transakcje krytyczne.
   - **Near-Miss (Sytuacja potencjalnie wypadkowa):** Awaria wisząca na włosku — zdarzenie, które mogło stać się SEV-1, gdyby nie zbieg okoliczności. Wymaga postmortem prewencyjnego!
3. **Role SRE w incydencie:** Raport musi identyfikować:
   - **Incident Commander (IC):** osoba dowodząca reakcją i koordynująca działania,
   - **Lead Investigator (Tech Lead):** inżynier diagnozujący przyczynę techniczną,
   - **Communications Lead:** osoba odpowiedzialna za aktualizację Status Page i komunikację z klientami.
4. **Wieloczynnikowa analiza przyczyn (Root Cause Chain):** Poważne awarie nigdy nie wynikają z jednej przyczyny. Zidentyfikuj:
   - **Trigger (Wyzwalacz):** bezpośrednie zdarzenie inicjujące (np. deploy, skok ruchu),
   - **Amplifier (Wzmacniacz):** co spowodowało eskalację (np. brak circuit breakera, wyczerpanie puli),
   - **Detection Gap:** dlaczego monitoring nie zareagował od razu (np. zły próg alertu),
   - **Process Gap:** dlaczego zmiana przeszła przez testy/staging.
5. **Rejestr Status Page i Wpływ na SLA:** Każdy postmortem musi odnotować, co i kiedy komunikowano klientom zewnętrznym oraz czy nastąpiło formalne naruszenie SLA.
6. **Brak logu/źródła = brak wpisu w osi czasu:** Każde zdarzenie na osi czasu musi mieć określony dokładny znacznik czasu i źródło (`Log z Pod-A`, `Alert Datadog #1234`, `Wpis ze Slack #incident`).
7. **Identyfikatory działań naprawczych (`ACT-001`):** Klasyfikacja: `PREVENT`, `DETECT`, `MITIGATE`. Każda zidentyfikowana przyczyna źródłowa musi mieć co najmniej jedno zadanie PREVENT.

# Etapy pracy

### Krok 1: Inwentaryzacja materiałów i kwalifikacja (SEV)
- Zbierz logi, alerty z PagerDuty/Datadog, zapisy ze Slacka/Teams i zrzuty ekranu.
- Określ poziom Severity (SEV-1 / SEV-2 / SEV-3 / Near-Miss).
- Zidentyfikuj kluczowe metryki czasowe: T0 (Trigger), T1 (Detection), T2 (Response), T3 (Mitigation), T4 (Resolved), TTD, TTR.

### Krok 2: Konstrukcja Osi Czasu (Timeline)
Uporządkuj zdarzenia chronologicznie ze wskazaniem fazy (T0–T4) oraz źródła informacji. Zobacz [przykład](./examples/log-to-timeline-example.md).

### Krok 3: Analiza wieloczynnikowa i 5 Whys
- Wypełnij łańcuch przyczyn: Trigger, Amplifier, Detection Gap, Process Gap.
- Przeprowadź analizę 5 Whys, drążąc aż do luk w procesie, testach lub architekturze.

### Krok 4: Wypełnienie sekcji komunikacji i Status Page
Odnotuj chronologię komunikatów publicznych oraz wpływ na umowne SLA.

### Krok 5: Opracowanie Działań Naprawczych (Action Items)
Zbuduj tabelę działań spełniających kryteria:
- Konkretne i mierzalne,
- Przypisane do właściciela (DRI),
- Mające określony termin / sprint,
- Posiadające ticket w Jira/GitHub Issues.

### Krok 6: Weryfikacja przed publikacją
Przejdź przez [checklistę weryfikacji raportu](./checklists/postmortem-review-checklist.md) przed udostępnieniem dokumentu.
