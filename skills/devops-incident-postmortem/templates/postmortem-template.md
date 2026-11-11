# Raport Postmortem: [Nazwa Incydentu / System]

| Metryka / Pole | Wartość |
|---|---|
| **Identyfikator incydentu** | INC-YYYY-NNN / [PagerDuty ID] |
| **Data zdarzenia** | YYYY-MM-DD |
| **Krytyczność (Severity)** | **SEV-1** (Krytyczna awaria) / **SEV-2** (Częściowa degradacja) / **SEV-3** / **Near-Miss** |
| **Incident Commander (IC)** | [Imię i Nazwisko / Rola] |
| **Lead Investigator (Tech Lead)** | [Imię i Nazwisko / Rola] |
| **Communications Lead** | [Imię i Nazwisko / Rola] |
| **Właściciel raportu** | [Imię i Nazwisko] |
| **Czas trwania przestoju** | [X godz. / min — T4 minus T0] |
| **Czas do wykrycia (TTD)** | [X min — T1 minus T0] |
| **Czas do naprawy (TTR)** | [X min — T4 minus T1] |
| **MTTD / MTTR (Średnie)** | [Wartość lub DO POTWIERDZENIA przy incydencie jednostkowym] |
| **Naruszenie SLA / Kary umowne** | [Brak naruszenia / Naruszenie SLA (X%) / Ryzyko kary umownej] |
| **Status raportu** | Szkic / W recenzji / Zaakceptowany |

---

## 1. Streszczenie incydentu (Executive Summary)
*Zwięzłe podsumowanie (2–4 zdania) dla kadry zarządzającej: co zawiodło, jaki był mierzalny wpływ biznesowy, jak przywrócono działanie i co robimy, by to się nie powtórzyło.*

---

## 2. Wpływ na użytkowników i biznes (Impact)
- **Dotknięte usługi / komponenty:** [lista komponentów]
- **Liczba dotkniętych użytkowników:** [dokładna liczba lub % aktywnych sesji]
- **Wpływ na SLA / SLO:** [np. spadek dostępności z 99.95% do 98.40%]
- **Wpływ finansowy / operacyjny:** [np. utracone transakcje e-commerce, opóźnienia w przetwarzaniu zamówień]
- **Liczba zgłoszeń do Supportu / Helpdesku:** [liczba ticketów zgłoszonych przez klientów]

---

## 3. Oś czasu (Timeline)

*Wszystkie czasy w strefie UTC (lub CET, jeśli ujednolicone).*

| Czas | Zdarzenie | Faza (T0–T4) | Źródło (Log / Alert / Chat) |
|---|---|---|---|
| **HH:MM** | Wystąpienie anomalii / wdrożenie zmiany | **T0 (Trigger)** | [np. Git commit / Log z Pod-A] |
| **HH:MM** | Pierwszy alert monitoringu | **T1 (Detection)** | [np. Alert Datadog / PagerDuty] |
| **HH:MM** | Otwarcie mostka incydentu / powołanie IC | **T2 (Response)** | [np. Slack #incident-room] |
| **HH:MM** | Zastosowanie obejścia / rollback wersji | **T3 (Mitigation)** | [np. CI/CD pipeline / kubectl] |
| **HH:MM** | Potwierdzenie powrotu metryk do normy | **T4 (Resolved)** | [np. Grafana dashboard] |

---

## 4. Łańcuch przyczyn awarii (Root Causes & Contributing Factors)

*Standard Google SRE zakłada, że poważna awaria jest splotem wielu czynników systemowych, a nie pojedynczego błędu.*

- **1. Wyzwalacz bezpośredni (Trigger):**  
  [np. Wdrożenie wersji 2.4.1 zawierającej niezindeksowane zapytanie SQL]
- **2. Czynnik wzmacniający (Amplifier / Escalating Factor):**  
  [np. Brak limitu połączeń (Connection Pool exhaustion) oraz brak timeoutów w bramce API doprowadziły do lawinowej awarii kolejnych serwisów (Cascading failure)]
- **3. Luka w detekcji (Detection Gap):**  
  [np. Alert był skonfigurowany na średnie obciążenie CPU zamiast na stopę błędów HTTP 5xx, co opóźniło powiadomienie o 18 minut]
- **4. Luka procesowa / testowa (Process / Pre-production Gap):**  
  [np. Środowisko stagingowe posiadało zbyt mały zbiór danych, przez co problem wydajnościowy nie ujawnił się przed produkcją]

### Analiza 5 Whys (Drzewo pytań):
1. *Dlaczego serwis przestał odpowiadać?* -> Baza danych przestała przyjmować połączenia.
2. *Dlaczego baza przestała przyjmować połączenia?* -> Pula połączeń została wyczerpana przez blokujące zapytania.
3. *Dlaczego zapytanie blokowało bazę?* -> Brakowało indeksu na kolumnie `customer_uuid`.
4. *Dlaczego brakowało indeksu?* -> Migracja bazy danych pominęła indeks w skrypcie deployu.
5. *Dlaczego migracja pominęła indeks?* -> Brak automatycznego lintera schematów w pipeline CI/CD przed scaleniem do main.

---

## 5. Co zadziałało dobrze vs Gdzie pojawiły się trudności

### Co zadziałało dobrze (System & Team Resilience):
*Konkretne mechanizmy i procedury, które ograniczyły skutki awarii:*
- [np. Procedura automatycznego rollbacku w CI/CD zadziałała w 3 minuty od decyzji IC]
- [np. Komunikacja na kanale incydentu przebiegała sprawnie i bez chaosu]

### Gdzie pojawiły się trudności (Vulnerabilities & Bottlenecks):
*Luki w narzędziach, runbookach lub uprawnieniach:*
- [np. Inżynier dyżurny nie posiadał uprawnień do natychmiastowego restartu usługi w klastrze B]
- [np. Runbook odzyskiwania bazy danych zawierał nieaktualne polecenia]

---

## 6. Komunikacja zewnętrzna i Status Page (External Comms)

| Czas | Kanał komunikacji | Treść komunikatu | Status publiczny |
|---|---|---|---|
| **HH:MM** | Status Page (`status.domain.com`) | „Investigating: Zidentyfikowano degradację wydajności API" | Yellow (Degraded) |
| **HH:MM** | Status Page | „Identified: Zidentyfikowano przyczynę, trwa procedura wycofywania zmiany" | Red (Major Outage) |
| **HH:MM** | Status Page | „Resolved: Wszystkie usługi działają poprawnie, metryki w normie" | Green (Operational) |
| **HH:MM** | Komunikat bezpośredni do klientów Enterprise | E-mail z oficjalnym powiadomieniem o incydencie | Wysłano |

---

## 7. Działania naprawcze (Action Items)

| ID | Typ | Opis działania naprawczego | Priorytet | Właściciel (DRI) | Ticket | Termin / Sprint |
|---|---|---|---|---|---|---|
| **ACT-001** | `PREVENT` | [Działanie eliminujące Root Cause] | P1 | [Osoba/Zespół] | JIRA-101 | Sprint 42 |
| **ACT-002** | `DETECT` | [Nowy alert lub metryka skracająca TTD] | P1 | [Osoba/Zespół] | JIRA-102 | Sprint 42 |
| **ACT-003** | `MITIGATE` | [Runbook / automatyzacja skracająca TTR] | P2 | [Osoba/Zespół] | JIRA-103 | Sprint 43 |
