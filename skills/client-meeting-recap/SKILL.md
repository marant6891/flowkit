---
name: client-meeting-recap
version: "1.1"
tags: [analyst, meeting, recap, email, vtt, transcript, action-items, client, dri, risk-radar]
description: >
  Przekształca surowe transkrypcje spotkań (.vtt, .txt, .docx z MS Teams, Zoom,
  Google Meet) lub notatki w profesjonalne, 2-częściowe podsumowanie: Część A
  (Wewnętrzny Radar Ryzyk dla zespołu) oraz Część B (Oficjalny e-mail do klienta)
  w formacie Markdown (.md). Ekstrahuje kluczowe decyzje, zadania z jednoznacznymi
  właścicielami (DRI) i terminami oraz klauzulę weryfikacji ustaleń (Safety Net).
---

# Cel

Przekształć surowy zapis lub transkrypcję spotkania w kompletny dokument Markdown (`.md`) składający się z:
1. **Części A: Wewnętrznego Radaru Ryzyk** (dla Zespołu — nastroje, ukryte ryzyka, próby Scope Creep),
2. **Części B: Oficjalnego szkicu e-maila do klienta** (zwięzłe podsumowanie, decyzje, zadania DRI, klauzula weryfikacji 48h).

# Zasady nadrzędne (obowiązują zawsze)

1. **Brak zmyślania ustaleń i terminów:** Jeżeli termin wykonania zadania lub osoba odpowiedzialna nie padły w transkrypcji, wpisz `[Do potwierdzenia]` lub `[Do wskazania przez klienta]`. Nigdy nie zgaduj terminów ani nazwisk.
2. **Odróżnianie Burzy Mózgów (Brainstorming) od Zobowiązań:** Klienci często rzucają luźnymi pomysłami („Fajnie byłoby dodać aplikację na zegarki”, „Może zmienimy cały układ bazy?”). Jeśli pomysł nie zakończył się twardą zgodą obu stron, **nie wpisuj go jako zadania ani decyzji** — odnotuj go wyłącznie w Części A jako potencjalny *Scope Creep* lub pomysł do analizy.
3. **Zasada DRI (Directly Responsible Individual):** Każde zadanie po stronie naszego zespołu oraz po stronie klienta musi mieć przypisanego **jednego, konkretnego właściciela z imienia i nazwiska**. Zakazane są ogólne wpisy typu „Klient”, „DevOps” czy „Zespół”. Jeśli właściciel nie padł, wpisz `[Do wskazania przez Klienta]`.
4. **Izolacja Części Wewnętrznej od Maila do Klienta:**
   - Informacje wrażliwe (trudne nastroje, obawy o budżet, wewnętrzne uwagi techniczne) trafiają **wyłącznie do Części A**.
   - Do Części B trafia wyłącznie treść partnerska, konstruktywna i bezpieczna do wysłania klientowi.
5. **Klauzula bezpieczeństwa ustaleń (Correction Safety Net):** Każdy szkic maila do klienta musi kończyć się formułą proszącą o weryfikację ustaleń w ciągu 24–48 godzin.
6. **Filtracja szumu technicznego i dygresji:** Bezwzględnie usuwaj:
   - kwestie techniczne połączenia („czy mnie słychać?”, „udostępniam ekran”),
   - kurtuazyjne wstępy i pogawędki nieformalne.
7. **Plik wyjściowy:** Zapisz wynik jako plik `.md` o nazwie `recap-YYYY-MM-DD-[skrót-projektu].md`.

# Etapy pracy

### Etap 1: Oczyszczenie, analiza i identyfikacja uczestników
Obsługiwane formaty opisano w [instrukcji formatów transkrypcji](./references/vtt-formats.md):
- `.vtt` (MS Teams, Zoom, Google Meet), `.docx`, `.txt`.
- Wyodrębnij imiona mówców, zmapuj role: Klient vs Nasz Zespół.
- Ustal ton relacji: formalny (`Szanowni Państwo`) vs semi-formalny (`Cześć / Dzień dobry`).

### Etap 2: Analiza ryzyk i nastrojów (Wsad do Części A)
Zidentyfikuj:
- Czy klient wyrażał frustrację, niepokój lub zniecierpliwienie?
- Czy padły propozycje wychodzące poza uzgodniony budżet/zakres (Scope Creep)?
- Jakie są blokady organizacyjne po stronie klienta (np. brak zgód, opóźnienia decyzyjne)?

### Etap 3: Ekstrakcja decyzji i zadań DRI (Wsad do Części B)
- Wypisz wyłącznie decyzje potwierdzone przez obie strony.
- Odrzuć pomysły z fazy luźnej dyskusji.
- Zbuduj tabelę zadań (Nasz Zespół vs Klient) z imiennym DRI i terminem.

### Etap 4: Redakcja dwuczęściowego dokumentu w Markdown
Sformatuj wynik zgodnie z [szablonem zapasowym](./templates/client-email-recap-template.md).

### Etap 5: Weryfikacja przed wysyłką
Przejdź przez [checklistę weryfikacji](./checklists/meeting-recap-checklist.md) punkt po punkcie przed przekazaniem podsumowania do wysyłki.
