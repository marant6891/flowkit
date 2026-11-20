<!--
Szablon ZAPASOWY. Używaj go tylko, gdy użytkownik nie dostarczył własnego szablonu.
Wszystko w nawiasach [...] to placeholder – zastąp treścią ze źródeł albo wpisz
`DO POTWIERDZENIA`. Żaden placeholder nie jest przykładem do skopiowania.
Usuń komentarze i placeholdery przed oddaniem raportu.
-->

# Raport Postmortem: [Nazwa Incydentu / System]

| Metryka / Pole | Wartość |
|---|---|
| **Identyfikator incydentu** | [ID incydentu ze źródła, np. z systemu on-call] |
| **Data zdarzenia** | [YYYY-MM-DD] |
| **Krytyczność (Severity)** | [SEV-1 / SEV-2 / SEV-3 / Near-Miss] |
| **Incident Commander (IC)** | [Imię i Nazwisko / Rola] |
| **Lead Investigator (Tech Lead)** | [Imię i Nazwisko / Rola] |
| **Communications Lead** | [Imię i Nazwisko / Rola] |
| **Właściciel raportu** | [Imię i Nazwisko] |
| **Czas trwania przestoju** | [T4 minus T0] |
| **Czas do wykrycia (TTD)** | [T1 minus T0] |
| **Czas do naprawy (TTR)** | [T4 minus T1] |
| **MTTD / MTTR (Średnie)** | [Wartość ze źródła lub „Nie dotyczy – incydent jednostkowy”] |
| **Naruszenie SLA / Kary umowne** | [Brak naruszenia / Naruszenie SLA (X%) / Ryzyko kary umownej] |
| **Status raportu** | [Szkic / W recenzji / Zaakceptowany] |

---

## 1. Streszczenie incydentu (Executive Summary)

[2–4 zdania dla kadry zarządzającej, pisane na końcu i wyłącznie z treści raportu:
co zawiodło, jaki był mierzalny wpływ, jak przywrócono działanie, co zapobiegnie powtórce.]

---

## 2. Wpływ na użytkowników i biznes (Impact)

- **Dotknięte usługi / komponenty:** [lista komponentów]
- **Liczba dotkniętych użytkowników:** [liczba lub % aktywnych sesji]
- **Wpływ na SLA / SLO:** [dostępność przed i po]
- **Wpływ finansowy / operacyjny:** [wartość ze źródła]
- **Liczba zgłoszeń do Supportu / Helpdesku:** [liczba ticketów]

---

## 3. Oś czasu (Timeline)

[Strefa czasowa wszystkich wpisów, np. UTC.] Czasy przybliżone oznacz `[SZACUNEK]`.

| Czas | Zdarzenie | Faza (T0–T4) | Źródło (Log / Alert / Chat) |
|---|---|---|---|
| [HH:MM:SS] | [Zdarzenie inicjujące] | **T0 (Trigger)** | [Źródło] |
| [HH:MM:SS] | [Pierwszy sygnał wykrycia] | **T1 (Detection)** | [Źródło] |
| [HH:MM:SS] | [Rozpoczęcie reakcji] | **T2 (Response)** | [Źródło] |
| [HH:MM:SS] | [Zastosowane obejście / wycofanie zmiany] | **T3 (Mitigation)** | [Źródło] |
| [HH:MM:SS] | [Potwierdzenie powrotu do normy] | **T4 (Resolved)** | [Źródło] |

---

## 4. Łańcuch przyczyn awarii (Root Causes & Contributing Factors)

- **1. Wyzwalacz bezpośredni (Trigger):** [Zdarzenie inicjujące – ze źródłem]
- **2. Czynnik wzmacniający (Amplifier):** [Co spowodowało eskalację – ze źródłem]
- **3. Luka w detekcji (Detection Gap):** [Dlaczego monitoring nie zareagował od razu]
- **4. Luka procesowa / testowa (Process Gap):** [Dlaczego problem nie został wykryty przed produkcją]

### Analiza 5 Whys

1. *Dlaczego [obserwowany objaw]?* → [Odpowiedź ze źródłem]
2. *Dlaczego [odpowiedź 1]?* → [Odpowiedź ze źródłem]
3. *Dlaczego [odpowiedź 2]?* → [Odpowiedź ze źródłem]
4. *Dlaczego [odpowiedź 3]?* → [Odpowiedź ze źródłem]
5. *Dlaczego [odpowiedź 4]?* → [Luka w procesie, testach lub architekturze]

[Jeśli materiały nie pozwalają odpowiedzieć na kolejne „dlaczego”, zakończ łańcuch
wpisem `DO POTWIERDZENIA` zamiast domyślać się przyczyny.]

---

## 5. Co zadziałało dobrze vs Gdzie pojawiły się trudności

### Co zadziałało dobrze
- [Mechanizm lub procedura, która ograniczyła skutki awarii – ze źródłem]

### Gdzie pojawiły się trudności
- [Luka w narzędziach, runbookach lub uprawnieniach – ze źródłem]

---

## 6. Komunikacja zewnętrzna i Status Page (External Comms)

[Jeśli nie było komunikacji zewnętrznej, wpisz to wprost wraz ze źródłem tej informacji.]

| Czas | Kanał komunikacji | Treść komunikatu | Status publiczny |
|---|---|---|---|
| [HH:MM] | [Status Page / e-mail / inny] | [Dosłowna treść komunikatu ze źródła] | [Status ze źródła] |

---

## 7. Działania naprawcze (Action Items)

| ID | Typ | Opis działania naprawczego | Priorytet | Właściciel (DRI) | Ticket | Termin / Sprint |
|---|---|---|---|---|---|---|
| **ACT-001** | `PREVENT` | [Działanie eliminujące przyczynę źródłową] | [Priorytet] | [Osoba lub DO POTWIERDZENIA] | [ID ticketu lub DO POTWIERDZENIA] | [Termin lub DO POTWIERDZENIA] |
| **ACT-002** | `DETECT` | [Alert lub metryka skracająca TTD] | [Priorytet] | [Osoba lub DO POTWIERDZENIA] | [ID ticketu lub DO POTWIERDZENIA] | [Termin lub DO POTWIERDZENIA] |
| **ACT-003** | `MITIGATE` | [Runbook lub automatyzacja skracająca TTR] | [Priorytet] | [Osoba lub DO POTWIERDZENIA] | [ID ticketu lub DO POTWIERDZENIA] | [Termin lub DO POTWIERDZENIA] |
