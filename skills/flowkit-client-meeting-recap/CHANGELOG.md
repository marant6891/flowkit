# Historia zmian skilla flowkit-client-meeting-recap

## 1.5 (25.11.2026)

- Sekcja „Pytania do użytkownika”: pytania przez okno pytań (VS Code `vscode/askQuestions`, Claude Code `AskUserQuestion`), najwyżej 4 w oknie, rekomendacja pierwsza, wiersz diagnostyczny `Ask:`; w subagencie pytania wracają jako `QUESTION-NNN`.

## 1.4 (20.11.2026)

- Właściciel zadania tylko z dowodem: osoba, zespół, właściciel niepotwierdzony albo brak (`DO POTWIERDZENIA`).
- Okno na korekty domyślnie 48 godzin, konfigurowalne; mail nie sugeruje, że brak odpowiedzi oznacza akceptację.
- Rozdzielenie decyzji, propozycji i tematów otwartych.

## 1.3 (18.11.2026)

### Bezpieczeństwo materiałów
- Treść transkrypcji jest traktowana wyłącznie jako dane, a nie polecenia.
- Sekrety i dane szczególnie wrażliwe są zastępowane znacznikiem `[UKRYTO]`.
- Podłączona instrukcja obsługi plików i szablonów Word.

## 1.2 (14.11.2026)

### Rzetelność i bezpieczeństwo wysyłki
- Część A i Część B zapisywane w **osobnych plikach** (`-wewnetrzne.md`, `-klient.md`), aby notatka wewnętrzna nie trafiła przypadkiem do klienta.
- Radar Ryzyk wymaga **dowodu** dla każdej obserwacji (cytat, mówca, znacznik czasu); oceny nastroju oznaczane jako `Interpretacja:`.
- Szablon użytkownika ma pierwszeństwo; pytanie o szablon w Etapie 1.
- Jedno oznaczenie braków: `DO POTWIERDZENIA` (zamiast `[Do potwierdzenia]` / `[Do wskazania przez klienta]`); okno korekt ujednolicone do 48 godzin.
- Przykład przepisany: poprawny format VTT MS Teams, obie części, daty i braki zgodne z zasadami skilla.
- `description` uzupełniony o frazę aktywacji „Użyj, gdy…”.

## 1.1 (11.11.2026)

### Standard rynkowy (Chief of Staff & Client Success Alignment)
- Wprowadzono **dwuczęściowy format wyniku**:
  - **Część A: Wewnętrzny Radar Ryzyk** (nastroje klienta, próby Scope Creep, wąskie gardła — poufne dla zespołu),
  - **Część B: Oficjalny szkic e-maila** do klienta.
- Wdrożono regułę **DRI (Directly Responsible Individual)** — zakaz bezosobowych przypisań zadań.
- Dodano klauzulę **Correction Safety Net** (okienko 24–48h na korektę ustaleń).
- Dodano zasadę **filtracji luźnego brainstormingu** (odróżnianie propozycji od wiążących uzgodnień).
- Zaktualizowano szablon, checklistę oraz instrukcję skilla.

## 1.0 (11.11.2026)

### Wersja inicjalna
- Obsługa formatów wejściowych: `.vtt` (MS Teams, Zoom, Google Meet), `.docx`, `.txt`.
- Zasady filtrowania szumu technicznego i dygresji.
- Podział Action Items na „Nasz Zespół" vs „Klient".
- Szablon e-mail gotowy do wysłania (`templates/client-email-recap-template.md`).
- Checklista weryfikacji przed wysyłką (`checklists/meeting-recap-checklist.md`).
- Przykład transformacji VTT → e-mail (`examples/vtt-to-recap-example.md`).
- Instrukcja formatów transkrypcji (`references/vtt-formats.md`).
- 5-etapowy proces z doborem tonu i konwencją nazewnictwa plików.
