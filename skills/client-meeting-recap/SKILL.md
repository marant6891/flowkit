---
name: client-meeting-recap
version: "1.0"
tags: [analyst, meeting, recap, email, vtt, transcript, action-items, client]
description: >
  Przekształca surowe transkrypcje spotkań (.vtt, .txt, .docx z MS Teams, Zoom,
  Google Meet) lub notatki w profesjonalne, gotowe do wysłania podsumowanie
  e-mail dla klienta w formacie Markdown (.md). Ekstrahuje kluczowe decyzje,
  podział zadań (Action Items po stronie Zespołu i Klienta) z terminami oraz
  tematy otwarte bez dopisywania nieustalonych faktów.
---

# Cel

Przekształć surowy zapis lub transkrypcję spotkania w zwięzłe, biznesowe i profesjonalne podsumowanie e-mail w formacie Markdown (`.md`), gotowe do bezpośredniego skopiowania i wysłania do klienta.

Podsumowanie musi być natychmiast czytelne dla uczestników biznesowych, eliminować szum rozmowy i precyzyjnie rozliczać odpowiedzialności.

# Zasady nadrzędne (obowiązują zawsze)

1. **Brak zmyślania ustaleń i terminów:** Jeżeli termin wykonania zadania lub osoba odpowiedzialna nie padły w transkrypcji, wpisz `[Do potwierdzenia]` lub `[Do ustalenia w zespole]`. Nigdy nie zgaduj terminów (np. „do piątku"), jeśli nie padły wprost z ust uczestników.
2. **Filtracja szumu technicznego i dygresji:** Bezwzględnie usuwaj:
   - kwestie techniczne połączenia („czy mnie słychać?", „udostępniam ekran"),
   - kurtuazyjne wstępy i pogawędki nieformalne,
   - odrzucone w trakcie dyskusji pomysły (chyba że stanowią istotny kontekst decyzji odrzucającej).
3. **Rozdział odpowiedzialności (My vs Klient):** Lista zadań (Action Items) musi być jednoznacznie podzielona na:
   - **Po stronie Wykonawcy / Naszego Zespołu**,
   - **Po stronie Klienta**.
4. **Format gotowej wiadomości e-mail:** Wynik musi być kompletnym szkicem e-maila zawierającym:
   - Proponowany temat wiadomości (Subject),
   - Odpowiednio dobrane otwarcie (patrz Etap 1 — ton relacji),
   - Kluczowe decyzje i ustalenia merytoryczne,
   - Zadania i terminy w czytelnej tabeli lub liście z przypisanym właścicielem,
   - Tematy otwarte / pytania blokujące,
   - Informację o kolejnym kontakcie lub terminie następnego spotkania.
5. **Plik wyjściowy:** Zapisz wynik jako plik `.md` o nazwie `recap-YYYY-MM-DD-[skrót-projektu].md` (np. `recap-2026-11-11-projekt-alfa.md`). Jeśli nazwa projektu jest nieznana, użyj `recap-YYYY-MM-DD.md`.
6. **Szablon użytkownika ma pierwszeństwo:** Jeśli użytkownik posiada własny wzorzec notatki po spotkaniu, zastosuj jego układ. W przeciwnym razie użyj [szablonu zapasowego](./templates/client-email-recap-template.md).

# Etapy pracy

### Etap 1: Oczyszczenie, analiza i identyfikacja uczestników

Obsługiwane formaty — szczegóły w [instrukcji formatów transkrypcji](./references/vtt-formats.md):
- `.vtt` (MS Teams, Zoom, Google Meet): zignoruj znaczniki czasu, numery sekwencji, powtórzenia ASR.
- `.docx` / `.txt`: wyekstrahuj treść, zidentyfikuj uczestników z listy lub nagłówka spotkania.

Zmapuj uczestników na role:
- *Klient*: np. Jan Kowalski (Product Owner / Sponsor),
- *Nasz Zespół*: np. Anna Nowak (Analityk), Piotr Wiśniewski (DevOps).

Ustal ton relacji z klientem na podstawie kontekstu transkrypcji:
- **Formalny** (`Szanowni Państwo`, `Dzień dobry`) — nowa relacja, duży korporacyjny klient, spotkanie zarządowe.
- **Semi-formalny** (`Cześć [Imię]`, `Dzień dobry`) — robocza relacja, znane osoby, regularne spotkania.

### Etap 2: Ekstrakcja ustaleń i decyzji
Wypisz wyłącznie to, co zostało uzgodnione:
- Co zostało zaakceptowane lub zatwierdzone?
- Jakie zmiany w zakresie lub architekturze zostały przyjęte?
- Jakie warianty zostały wykluczone i dlaczego?

### Etap 3: Ekstrakcja zadań do wykonania (Action Items)
Dla każdego zadania określ:
- **Kto** odpowiada (konkretna osoba z imienia i nazwiska lub zespół, jeśli nie sprecyzowano),
- **Co** dokładnie ma być dostarczone,
- **Do kiedy** (data lub `[Do potwierdzenia]`).

### Etap 4: Redakcja wiadomości e-mail w Markdown
Sformatuj wynik zgodnie z [szablonem zapasowym](./templates/client-email-recap-template.md), stosując ton ustalony w Etapie 1.

Nadaj plikowi wyjściowemu nazwę zgodnie z zasadą: `recap-YYYY-MM-DD-[skrót-projektu].md`.

### Etap 5: Weryfikacja przed wysyłką
Przejdź przez [checklistę weryfikacji](./checklists/meeting-recap-checklist.md) punkt po punkcie przed przekazaniem e-maila do wysyłki.
