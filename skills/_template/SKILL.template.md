---
name: skill-name-here
version: "1.0"
tags: [tag1, tag2, tag3]
description: >
  Zwięzły opis tego, co robi skill (1–3 zdania), kiedy model AI powinien go
  aktywować oraz jakich rezultatów oczekiwać. Użyj, gdy użytkownik prosi o
  [konkretny typ zadania lub dokument].
---

<!-- 
  Instrukcja uzupełniania szablonu:
  - Zmień "skill-name-here" na nazwę katalogu skilla (kebab-case, małe litery).
  - Wypełnij "tags" słowami kluczowymi po angielsku ułatwiającymi wyszukiwanie.
  - Zasady nadrzędne: minimum 3, maksimum 9; każda musi być obiektywnie sprawdzalna.
  - Etapy: wymagaj konkretnych działań, nie ogólnych intencji.
  - Usuń ten komentarz przed commitem.
-->

# Cel

Opisz zwięźle główny cel i przeznaczenie tego skilla w 2-4 zdaniach. Co skill robi? Na jakich materiałach operuje? Co jest wynikiem?

# Zasady nadrzędne (obowiązują zawsze)

1. **[Zasada rzetelności danych]:** Opisz regułę odnoszącą się do źródeł i ich braku.
2. **[Zasada zakresu]:** Opisz czego skill nie robi lub co pomija.
3. **[Zasada formatu wyjściowego]:** Opisz oczekiwany format i strukturę wyniku.
4. **[Naturalny styl bez znaczników AI]:** W treści wyjściowej nie używaj długich myślników (`—`, `–` - zamiast nich stosuj zwykły łącznik `-`, przecinek lub dwukropek), ozdobnych emoji ani typowych formułek AI (*„Należy zauważyć, że…”*, *„Warto podkreślić…”*).
5. **Prosty język.** Tekst dla ludzi pisz według standardu FlowKit `<runtime>/procedures/plain-language.md` (PL i EN): najważniejsze na początku, zdania do 20 słów (EN: 25), czasowniki zamiast „dokonać zmiany”, bez korpomowy i kalk składniowych. Kod, cytaty ze źródeł i brzmienie narzucone przez szablon klienta są wyjątkami.

# Pytania do użytkownika

Każde pytanie do użytkownika zadawaj przez okno pytań, gdy jest dostępne (VS Code: `#tool:vscode/askQuestions`,
Claude Code: `AskUserQuestion`):

- jedno pytanie to jedna pozycja z 2-4 wariantami; rekomendowany wariant pierwszy, oznaczony „(rekomendowane)”;
  użytkownik zawsze może odpowiedzieć własnymi słowami,
- najwyżej 4 pytania w jednym oknie; więcej pytań: najpierw blokujące, resztę w kolejnym oknie,
- tabelę pytań (ID, uzasadnienie, propozycja domyślna) pokaż najpierw jako tekst, a każdy jej wiersz zadaj w oknie,
- warianty wypisane tylko tekstem nie są pytaniem; nie kończ odpowiedzi pytaniem, którego nie było w oknie,
- tekstem pytaj tylko wtedy, gdy okno jest niedostępne, zawiodło albo sesja nie jest interaktywna,
- pod pytaniami dopisz wiersz diagnostyczny `Ask: window`, `Ask: text — <powód>` albo `Ask: auto` (pytanie
  rozstrzygnięte rekomendacją w trybie AUTO); wiersz musi być zgodny z prawdą,
- gdy skill działa w subagencie wywołanym przez orkiestratora, nie czekaj na użytkownika: zwróć pytania jako
  `QUESTION-NNN: <pytanie> — options: 1. <rekomendowane> 2. … — why: <jedno zdanie>`.


# Etapy pracy

### Etap 1: [Nazwa etapu: zbieranie danych / analiza]
Opis działań w tym etapie.

### Etap 2: [Nazwa etapu: przetwarzanie]
Opis działań w tym etapie.

### Etap 3: [Nazwa etapu: generowanie wyniku]
Opis działań w tym etapie. Odwołaj się do szablonu: [szablon](./templates/).

### Etap 4: Weryfikacja przed oddaniem
Przejdź przez [checklistę końcową](./checklists/) punkt po punkcie.
Tekst wynikowy sprawdź poleceniem `python "<runtime>/flowkit_exec.py" --role <rola> -- plain-check <plik> [--strict]`.
Błędy popraw, a ostrzeżenia popraw albo uzasadnij pod wynikiem.
