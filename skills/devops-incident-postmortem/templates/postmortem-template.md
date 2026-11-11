# Raport Postmortem: [Nazwa Incydentu / System]

| Metryka | Wartość |
|---|---|
| **Data zdarzenia** | YYYY-MM-DD |
| **Krytyczność (Severity)** | Sev-1 / Sev-2 / Sev-3 |
| **Właściciel raportu** | [Imię / Rola] |
| **Czas trwania przestoju** | [X godz. / min — T4 minus T0] |
| **Czas do wykrycia (TTD)** | [X min — T1 minus T0] |
| **Czas do naprawy (TTR)** | [X min — T4 minus T1] |
| **MTTD (Mean Time to Detect)** | [Uzupełnij przy serii incydentów lub DO POTWIERDZENIA] |
| **MTTR (Mean Time to Recover)** | [Uzupełnij przy serii incydentów lub DO POTWIERDZENIA] |
| **Status raportu** | Szkic / W recenzji / Zaakceptowany |

---

## 1. Streszczenie incydentu (Executive Summary)
*Zwięzłe podsumowanie dla kadry zarządzającej: co się stało, jaki był wpływ biznesowy i jak przywrócono działanie systemu.*

---

## 2. Wpływ na użytkowników i biznes (Impact)
- **Dotknięte usługi / komponenty:** [lista komponentów]
- **Szacowana liczba dotkniętych użytkowników:** [liczba lub %]
- **Wpływ na SLA / SLO:** [np. spadek dostępności z 99.9% do 99.2%]
- **Wpływ finansowy / operacyjny:** [np. utracone transakcje, opóźnienia w przetwarzaniu zamówień]

---

## 3. Oś czasu (Timeline)

*Wszystkie czasy w strefie [UTC / CET].*

| Czas | Opis zdarzenia | Źródło (Log / Alert / Chat) |
|---|---|---|
| **HH:MM** | Wystąpienie anomalii w usłudze X | [np. Grafana dashboard] |
| **HH:MM** | Podniesienie alertu PagerDuty #1234 | [np. Alert bot] |
| **HH:MM** | Inżynier dołącza do kanału incydentu | [np. Slack #incident] |
| **HH:MM** | Zastosowanie obejścia / rollback | [np. CI/CD pipeline #567] |
| **HH:MM** | Potwierdzenie powrotu metryk do normy | [np. Dashboard metryk] |

---

## 4. Analiza przyczyn (Root Cause Analysis - 5 Whys)

- **Wyzwalacz (Trigger):** [bezpośrednie zdarzenie inicjujące]
1. *Dlaczego wystąpił błąd?* -> ...
2. *Dlaczego to spowodowało przestój?* -> ...
3. *Dlaczego mechanizm zabezpieczający nie zadziałał?* -> ...
4. *Dlaczego problem nie został wykryty na etapie staging/testów?* -> ...
5. *Dlaczego architektura nie była odporna na tę awarię?* -> ...

---

## 5. Co zadziałało dobrze vs Co wymaga poprawy

### Co poszło dobrze:
*Na podstawie osi czasu i materiałów — konkretne zachowania i mechanizmy, które ograniczyły skutki incydentu.*
- [Opisz konkretne działania lub mechanizmy, które zadziałały poprawnie — ze źródła]

### Gdzie pojawiły się trudności:
*Luki w procesach, automatyzacji lub monitoringu, które wydłużyły TTD lub TTR.*
- [Opisz konkretne problemy z procesu reakcji — ze źródła lub analizy osi czasu]

---

## 6. Komunikacja podczas incydentu (Communication)

| Czas | Kanał | Odbiorca | Treść komunikatu |
|---|---|---|---|
| **HH:MM** | [Slack / E-mail / Status Page] | [Klienci / Zarząd / Interesariusze] | [Treść lub link do komunikatu] |

---

## 7. Działania naprawcze (Action Items)

| ID | Typ | Opis zadania | Priorytet | Właściciel | Ticket |
|---|---|---|---|---|---|
| **ACT-001** | PREVENT | Wdrożenie walidacji schematu przed zapisem konfiguracji | P1 | DevOps Team | JIRA-101 |
| **ACT-002** | DETECT | Konfiguracja alertu na skok błędów HTTP 5xx powyżej 2% | P1 | Monitoring Team | JIRA-102 |
| **ACT-003** | MITIGATE | Aktualizacja procedury rollbacku w runbooku | P2 | SRE | JIRA-103 |

