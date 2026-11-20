---
name: client-pt-prd-writer
version: "2.8"
tags: [analyst, prd, pt, requirements, documentation, client, gherkin, dod, diagrams]
description: >
  Tworzy profesjonalną dokumentację PT/PRD (projekt techniczny, specyfikacja
  zmiany, analiza przedwdrożeniowa) dla klienta końcowego, opisującą rzeczywiste
  zmiany w aplikacji wyłącznie na podstawie dostarczonych materiałów, bez
  dopisywania treści. Pracuje na szablonie dokumentu użytkownika (.docx, .dotx,
  .md), a gdy go brak, na szablonie zapasowym. Użyj, gdy użytkownik prosi o
  dokument PT, PRD, specyfikację lub dokumentację zmiany, change request,
  analizę wpływu lub dokumentację rozwoju aplikacji dla klienta. Na życzenie
  oddaje też wersję końcową bez dopisków (bez oznaczeń źródeł i tematów
  otwartych) dokładnie w udostępnionym szablonie. Ocenia procesy, przepływy,
  integracje i relacje między systemami lub komponentami, a gdy poprawia to
  zrozumienie, dodaje do dokumentu diagramy oparte wyłącznie na źródłach.
---

# Cel

Przygotuj rzetelny dokument PT/PRD opisujący **rzeczywistą** zmianę w aplikacji:
na szablonie, na którym pracuje użytkownik, wyłącznie na podstawie dostarczonych
materiałów. Dokument ma być profesjonalny, ale jego wartością jest prawdziwość,
a nie kompletność wszystkich sekcji.

# Zasady nadrzędne (obowiązują zawsze)

1. **Brak źródła = brak treści.** Każde zdanie merytoryczne (wymaganie, fakt o
   systemie, priorytet, termin, właściciel, miara, ryzyko) musi wynikać z
   materiału źródłowego. Jeśli nie wynika, wpisz `DO POTWIERDZENIA` i dodaj
   pozycję `OPEN-NNN`. Nie uzupełniaj luk „typowymi” treściami.
2. **Każdy wpis ma oznaczenie pochodzenia** (kolumna „Źródło” lub dopisek):
   - `SRC-NNN` – fakt potwierdzony pozycją z rejestru źródeł (Etap 1); dla kodu
     dodatkowo `plik:linia`,
   - `ASSUMPTION-NNN` – założenie zaakceptowane przez użytkownika do czasu potwierdzenia,
   - `OPEN-NNN` – brak informacji, temat do wyjaśnienia,
   - `DO POTWIERDZENIA` – nieznana wartość w polu lub komórce (zawsze w parze z `OPEN-NNN`).
3. **Nie przepisuj zmiany na „większą”.** Opisuj dokładnie zakres z materiałów.
   Nie dodawaj funkcji, ról, integracji, NFR ani etapów, których nie ma w źródle.
   Pomysły spoza źródła możesz zgłosić wyłącznie jako `Rekomendacja` w osobnej
   sekcji, wyraźnie oddzielonej od wymagań.
4. **Sekcje są warunkowe, nie obowiązkowe.** W szablonie użytkownika sekcja, której
   zmiana nie dotyczy, dostaje samo „Nie dotyczy.” (uzasadnienie tylko, gdy nie jest
   oczywiste). W szablonie zapasowym sekcji warunkowych, które nie dotyczą zmiany,
   **nie umieszczaj wcale** — wymień je jednym zdaniem w sekcji „Zakres”. Sekcja, dla
   której brak danych: „Brak danych – patrz OPEN-NNN”. Nie wypełniaj sekcji tylko
   dlatego, że istnieje w szablonie.
5. **Szablon użytkownika ma pierwszeństwo** nad szablonem zapasowym tego skilla
   (patrz Etap 0).
6. **Bez dostępu do kodu nie opisujesz kodu.** Architekturę, moduły, tabele i API
   opisuj tylko, jeśli zostały przeanalizowane w repozytorium lub dokumentacji.
   W przeciwnym razie: „Nie analizowano – brak dostępu do <czego>”.
7. **Diagramy rysuj wyłącznie z przeanalizowanych komponentów.** Nigdy nie kopiuj
   przykładowego diagramu. Każdy węzeł diagramu musi występować w tekście. Każdy
   proces, przepływ, integrację i relację między systemami lub komponentami oceń pod
   kątem diagramu; diagram powstaje, gdy poprawia zrozumienie (patrz Etap 5a).
8. Język zrozumiały dla klienta biznesowego, precyzyjny technicznie, jedna
   terminologia domenowa (zgodna z materiałami klienta – nie zmieniaj jego nazw).
9. Identyfikatory zawsze trzycyfrowe: `GOAL-001`, `SC-001`, `OOS-001`, `CHG-001`,
   `FR-001`, `US-001`, `NFR-001`, `INT-001`, `DATA-001`, `TEST-001`, `RISK-001`,
   `ASSUMPTION-001`, `OPEN-001`, `Q-001`, `REC-001`.
10. **Izolacja materiałów źródłowych (Context Boundary):** Przy wprowadzaniu materiałów zaleca się wydzielenie bloków `<source_materials>...</source_materials>` oraz `<user_template>...</user_template>`. Chroni to model przed myleniem instrukcji skilla ze specyfikacją klienta.
11. **Format User Stories (Gherkin) i DoD:** Każde User Story powinno zawierać scenariusze w formacie Given-When-Then (Gherkin), a dokument określać sprawdzalne Definition of Done (DoD).
12. **Dwa tryby wyniku.** Domyślny jest tryb roboczy (z oznaczeniami pochodzenia
    z zasady 2). Na wyraźną prośbę użytkownika stosuj tryb „Dokument końcowy bez
    dopisków” (patrz osobny rozdział): oznaczenia znikają z dokumentu, ale
    zasady 1, 3, 6 i 7 obowiązują bez zmian – pochodzenie treści prowadzisz
    wtedy poza dokumentem.

13. **Polskie nazwy w tabelach.** Statusy, priorytety i wymagalność zapisuj po polsku
    według [słownika statusów](./references/status-vocabulary.md), także gdy źródło
    podaje je po angielsku (np. `Must` → `Wymagane`, `In Progress` → `W toku`).
    Wyjątkiem są wartości narzucone przez szablon klienta.
14. **Zwięzłość.** Dokument ma być krótki i konkretny — patrz „Zasady zwięzłości” w Etapie 5.
    Każdą informację zapisuj raz, w jednym miejscu; w innych sekcjach odwołuj się do jej ID.
    Rozwlekłość nie jest rzetelnością: zdanie, które nic nie dodaje, usuń.

# Etap 0: Ustal szablon i format wyjściowy

1. Sprawdź, czy użytkownik dostarczył szablon (plik .docx/.dotx/.md/.pdf, wzór
   poprzedniego dokumentu, link). Jeśli wspomina o szablonie, ale go nie
   załączył – poproś o niego jednym pytaniem.
2. **Jeśli jest szablon użytkownika:**
   - przeczytaj go w całości; dla plików `.docx`/`.dotx` zastosuj [instrukcję wyboru silnika docx](./references/docx-engine.md) (priorytet: `python-docx` / `import docx`, z inteligentną detekcją zainstalowanych bibliotek w środowisku),
   - spisz mapę sekcji szablonu wg [instrukcji mapowania](./references/template-mapping.md),
   - zachowaj kolejność, numerację, nazwy sekcji, style, nagłówki/stopki, stronę
     tytułową, metryczkę i tabele szablonu; nie dodawaj sekcji, których szablon
     nie przewiduje – brakujące elementy obowiązkowe (np. Tematy do wyjaśnienia)
     dołącz jako ostatni rozdział lub załącznik, w stylu szablonu,
   - wynik oddaj w formacie szablonu: szablon .docx/.dotx → dokument .docx z kompletem stylów i
     formatowania szablonu. Pisz treść w Markdown, a potem uruchom `md-to-docx` z `--template` (szablon
     z treścią, np. strona tytułowa) albo `--reference-doc` (same style), zgodnie z
     [instrukcją DOCX](./references/docx-engine.md). Markdown oddajesz tylko, gdy `md-to-docx` zwróci
     kod 3 (brak silnika), z dokładnym komunikatem i instrukcją instalacji.
3. **Jeśli brak szablonu:** wybierz **wariant dokumentu** i oddaj dokument w formacie, o który
   prosi użytkownik:

   | Wariant | Kiedy | Szablon |
   |---|---|---|
   | **Skrócony** (domyślny dla małych zmian) | do 3 wymagań, jeden obszar aplikacji, bez nowych integracji, migracji danych, zmian uprawnień i architektury | [szablon skrócony](./templates/client-pt-prd-compact-template.md): 6 rozdziałów, 1–3 strony |
   | **Pełny** | pozostałe zmiany albo gdy użytkownik prosi o pełny dokument | [szablon pełny](./templates/client-pt-prd-template.md) |

   Wybór podaj jednym zdaniem w Etapie 4 („Wariant skrócony – zmiana obejmuje 2 wymagania w jednym
   ekranie”). Użytkownik może go zmienić. Gdy w trakcie pracy zakres urośnie ponad kryteria, przejdź na
   wariant pełny i powiedz o tym. Wariant skrócony nie zwalnia z zasad 1–3, 6 i 7: brakujące
   informacje nadal są `OPEN-NNN`.
4. Gdy użytkownik dostarczy poprzedni dokument jako wzór – przejmij z niego
   strukturę, styl i poziom szczegółowości, **nie treść merytoryczną**.
5. Ustal tryb wyniku: **roboczy z oznaczeniami** (domyślny) czy **końcowy bez
   dopisków**. Tryb końcowy włącz tylko, gdy użytkownik prosi o to wprost
   (np. „bez dopisków”, „wersja końcowa”, „czysty dokument”, „do wysłania
   klientowi”). W razie wątpliwości zapytaj jednym pytaniem.

# Etap 1: Zebranie materiałów i inwentaryzacja źródeł

Zbierz wszystko, co dostarczono: brief, ticket, e-mail, notatkę ze spotkania,
istniejącą dokumentację, kod, konfigurację, modele danych, specyfikacje API,
wymagania prawne, oczekiwania co do terminu i wdrożenia.

**Zapytaj o znane źródła danych** — jednym blokiem, na początku pracy, zanim zaczniesz analizę:

| ID | Pytanie |
|---|---|
| Q-001 | Jakie znane źródła mogę wykorzystać do przygotowania i weryfikacji dokumentu? (foldery z dokumentacją, repozytoria kodu, eksporty z Jira/Confluence, schematy baz danych, specyfikacje API, poprzednie wersje dokumentu) |
| Q-002 | Które źródło jest nadrzędne, gdy informacje są sprzeczne? |
| Q-003 | Czy są źródła, których nie wolno używać lub cytować (np. dane osobowe, materiały poufne)? |
| Q-004 | Kto może potwierdzić niejasności (rola lub osoba)? |

Pytania z Etapu 2 numeruj dalej. Wskazane źródła odczytaj (`read-document`, wyszukiwanie w repozytorium) i dopisz do rejestru źródeł.
Gdy użytkownik nie zna źródeł albo pracujesz w trybie AUTO, pracuj na dostarczonych materiałach i zapisz
brak źródeł weryfikujących jako `OPEN-NNN`.

Utwórz **rejestr źródeł** (wewnętrzny, do oznaczania wpisów; w dokumencie
umieść go w sekcji „Materiały źródłowe”):

| ID | Źródło | Typ | Data / wersja | Co z niego wynika |
|---|---|---|---|---|
| SRC-001 | Ticket JIRA-123 | Zgłoszenie | 05.11.2026 | Opis zmiany w formularzu zamówienia |

Następnie przejdź przez [checklistę discovery](./checklists/discovery-checklist.md)
i dla każdego punktu zaznacz: „jest w źródle (SRC-NNN)” / „nie dotyczy” / „brak”.

# Etap 2: Pytania (tylko blokujące)

Zadaj pytania tylko o informacje, bez których nie da się rzetelnie opisać
**tej konkretnej** zmiany. Nie pytaj o sekcje, które jej nie dotyczą.

- Maksymalnie 10 pytań w bloku, najważniejsze najpierw.
- Format:

| ID | Obszar | Pytanie | Dlaczego ważne | Propozycja domyślna (opcjonalnie) |
|---|---|---|---|---|
| Q-001 | Zakres | Czy zmiana obejmuje także panel administracyjny? | Zmienia zakres FR i testów | Brak – wymaga decyzji klienta |

- „Propozycję domyślną” podawaj tylko, gdy wynika z materiałów lub jest
  bezpieczna i odwracalna. Każda przyjęta propozycja staje się `ASSUMPTION-NNN`.
- Jeśli użytkownik nie zna odpowiedzi: zapisz `OPEN-NNN`, nie zgaduj.

# Etap 3: Analiza istniejącej aplikacji (jeśli jest dostęp)

Gdy dostępny jest kod lub dokumentacja techniczna, ustal tylko to, czego dotyczy
zmiana:
- moduły, komponenty, endpointy, tabele i konfiguracje dotknięte zmianą,
- obecne zachowanie (as-is) – dokładnie tak, jak wynika z kodu,
- zależności, integracje i dane, na które zmiana wpływa,
- obszary regresji.

Każde stwierdzenie techniczne opatrz źródłem, np.
`SRC-002, src/orders/OrderService.cs:142, endpoint POST /api/orders`.
Jeśli kodu/dokumentacji nie ma, w sekcjach technicznych wpisz
„Nie analizowano – brak dostępu do <repozytorium/dokumentacji>” i dodaj OPEN.

Nie opisuj stacku, architektury ani modułów niezwiązanych ze zmianą.

# Etap 4: Uzgodnienie zakresu dokumentu

Przed napisaniem pełnego dokumentu przedstaw użytkownikowi krótko:
1. jak rozumiesz zmianę (3–5 zdań, ze wskazaniem źródeł),
2. wariant dokumentu (skrócony/pełny, gdy brak szablonu) oraz które sekcje zostaną wypełnione, które oznaczysz „Nie dotyczy”,
   a które „Brak danych”,
3. listę pytań (Etap 2) i proponowanych `ASSUMPTION`,
4. plan diagramów z decyzją dla każdego procesu, przepływu, integracji i relacji między
   systemami lub komponentami (patrz Etap 5a).

Pełny dokument generuj po odpowiedzi użytkownika. Jeśli użytkownik prosi wprost
o wersję roboczą od razu – wygeneruj ją ze statusem „Roboczy”, z wszystkimi
lukami oznaczonymi jako `OPEN` (bez zgadywania) i listą pytań na końcu.

# Etap 5: Pisanie dokumentu

Pisz w strukturze szablonu (Etap 0). W **wariancie skróconym** obowiązuje tylko jego 6 rozdziałów:
poniższa tabela nie dodaje rozdziałów, a wskazuje, czy temat ma się pojawić jako punkt listy.
W wariancie pełnym i szablonie użytkownika obszary treści umieszczaj w odpowiednich sekcjach
– **tylko jeśli dotyczą zmiany**:

| Obszar | Kiedy wymagany |
|---|---|
| Metryczka, historia zmian, materiały źródłowe | zawsze |
| Streszczenie zarządcze | zawsze |
| Kontekst i cel zmiany | zawsze |
| Zakres (w zakresie / poza zakresem i Non-Goals) | zawsze |
| Proces obecny i docelowy, różnice | gdy zmienia się proces lub zachowanie; oceń diagram procesu |
| Role i uprawnienia | gdy zmiana dotyka ról/uprawnień |
| Wymagania funkcjonalne | zawsze |
| User stories z kryteriami akceptacji (Given-When-Then) | gdy są zmiany widoczne dla użytkownika |
| Wymagania niefunkcjonalne | tylko te wynikające ze źródeł |
| Analiza wpływu na aplikację | zawsze (lub „Nie analizowano”) |
| Architektura | gdy zmienia się architektura i jest analiza; oceń diagram architektury lub komponentów |
| Integracje | gdy zmiana dotyka integracji; oceń diagram sekwencji, integracji lub przepływu danych |
| Model danych i migracje | gdy zmieniają się dane/schemat; oceń diagram ER |
| Bezpieczeństwo, RODO, audyt | gdy zmiana dotyka danych osobowych, dostępu, audytu |
| Plan testów | zawsze |
| Kryteria ukończenia (Definition of Done - DoD) | zawsze |
| Wdrożenie i rollback | gdy są informacje o wdrożeniu (inaczej OPEN) |
| Ryzyka i zależności | zawsze – tylko zidentyfikowane, ze źródłem |
| Rekomendacje (poza wymaganiami) | opcjonalnie |
| Słownik pojęć | gdy w dokumencie są skróty/terminy |
| Macierz śledzenia wymagań | gdy jest ≥ 6 wymagań FR i powiązania nie wynikają z kolumn tabel FR/US/TEST |
| Tematy do wyjaśnienia | zawsze (może zawierać „Brak otwartych tematów”) |

Zasady pisania:
- Każde FR, US, NFR, INT, DATA, RISK ma źródło: w tabeli kolumna „Źródło”, w liście dopisek w nawiasie.
- Priorytet, właściciel, termin i miara są wpisywane **tylko ze źródła**; inaczej
  `DO POTWIERDZENIA` + OPEN.
- Gdy źródło określa wymagalność w skali MoSCoW, użyj kolumny „Wymagalność” z wartościami
  `Wymagane`, `Zalecane`, `Opcjonalne`, `Wyłączone z zakresu`. Nie przeliczaj ich na
  Wysoki/Średni/Niski.
- Kryteria akceptacji formułuj tak, aby były sprawdzalne; jeśli źródło nie daje
  podstaw do kryterium, nie wymyślaj progu – oznacz OPEN.
- Streszczenie zarządcze pisz na końcu, z treści dokumentu, bez nowych faktów.
- Zobacz [przykłady: źródło vs zmyślenie](./examples/sourced-vs-invented.md).

**Zasady zwięzłości** (obowiązują zawsze, także w szablonie użytkownika):

| Wielkość zmiany | Orientacyjna objętość treści (bez strony tytułowej i metryczki) |
|---|---|
| Mała: do 3 FR, jeden obszar (wariant skrócony) | 1–3 strony |
| Średnia: 4–10 FR lub kilka obszarów | 4–8 stron |
| Duża: ponad 10 FR, integracje, migracja | do 15 stron; więcej tylko, gdy wymaga tego treść źródeł |

- **Raz, w jednym miejscu.** Kryterium akceptacji jest w US (Given-When-Then) albo w tabeli FR, nie w obu.
  Plan testów odwołuje się do scenariuszy US (`US-001/S1`) i dodaje tylko testy, których scenariusze nie
  pokrywają. Ryzyko opisane w Ryzykach nie wraca w Analizie wpływu — tam tylko jego ID.
- **Tabela tylko, gdy porządkuje dane:** co najmniej 3 wiersze, które porównuje się w tych samych
  kolumnach. 1–2 elementy zapisz jako punkt listy albo zdanie. Nie twórz osobnej tabeli dla każdego
  typu identyfikatora (GOAL, SC, OOS, CHG, NFR, RISK…) – przy małej zmianie wystarczy lista z ID.
  Tabele narzucone przez szablon użytkownika zostają.
- Bez zdań wprowadzających przed tabelą („Poniższa tabela przedstawia…”).
  Komórka tabeli: jedno zdanie, najlepiej do 15 słów.
- **Szablon użytkownika przy małej zmianie:** sekcje niedotyczące dostają samo „Nie dotyczy.”, a w
  pozostałych pisz po kilka punktów – nie rozbudowuj treści do rozmiaru sekcji.
- **Bez wypełniaczy:** „Niniejszy dokument…”, „W ramach zmiany…”, „Należy zauważyć, że…”, „Celem
  sekcji jest…”, powtarzanie tytułu sekcji w pierwszym zdaniu, podsumowania na końcu sekcji.
- **Streszczenie zarządcze:** najwyżej 5 zdań. **Kontekst:** najwyżej 1 akapit.
- **User stories:** jedna linia na krok Given/When/Then; scenariusz tylko dla odrębnego zachowania
  (ścieżka główna + rzeczywiste przypadki brzegowe ze źródła), zwykle 1–3 na US. Nie dopisuj
  scenariusza „dla formalności”.
- **DoD:** tylko kryteria tej zmiany (wynikające ze źródeł, wymagań i testów), bez ogólnych formułek.
- **Oznaczenia pochodzenia** w kolumnie „Źródło” albo jednym dopiskiem na końcu akapitu — nie po
  każdym zdaniu z osobna, gdy cały akapit ma to samo źródło.
- Przy szablonie użytkownika obowiązuje jego struktura, ale treść w każdej sekcji jest tak samo zwięzła.

# Etap 5a: Diagramy (obowiązkowa ocena, diagram gdy poprawia zrozumienie)

1. **Przejrzyj wszystkie tematy i zapisz decyzje.** Znajdź w materiałach procesy, przepływy danych,
   komunikację, integracje oraz relacje między systemami lub komponentami. Według
   [zasad wyboru diagramów](./references/diagram-selection.md) przypisz każdemu tematowi decyzję „Diagram”
   z typem albo „Bez diagramu” z powodem. Gdy temat spełnia kryterium, domyślną decyzją jest diagram.
   Lista, tabela i pojedyncza informacja pozostają w tekście.
2. **Przygotuj model** każdego diagramu na podstawie [wzoru](./templates/diagram-model.yaml). Każdy
   element na obrazie musi być potwierdzony źródłem `SRC-NNN`. Niewiadomych i założeń nie rysuj: opisz je
   w polu `remarks`, które trafia do tekstu „Uwagi do rysunku” pod grafiką. Nie zgaduj elementów,
   kierunków ani mechanizmów.
3. **Wygeneruj, sprawdź i osadź** diagramy zgodnie z [instrukcją silnika](./references/diagram-engine.md).
   Skrypty uruchamiaj ścieżką bezwzględną z katalogu skilla: `${CLAUDE_SKILL_DIR}/scripts/`. Poza Claude Code
   jest to folder `scripts/` obok tego pliku `SKILL.md`.
   Styl opisuje [system wizualny](./references/diagram-design-system.md); szablon klienta ma pierwszeństwo.
4. **Tryb końcowy:** najpierw rozstrzygnij wszystkie niewiadome z użytkownikiem, potem uruchom skrypty
   z `--mode final`. Uwagi pod rysunkiem mogą zawierać tylko neutralne sformułowania zaakceptowane przez użytkownika.

# Etap 6: Weryfikacja przed oddaniem

Najpierw wykonaj **krytyczny przegląd** dokumentu z perspektywy osoby, która ma go podważyć: przypadki
brzegowe, sprzeczności, wymagania niesprawdzalne, niejawne założenia i treści wykraczające poza źródła.
Znalezione braki popraw albo zapisz jako `OPEN-NNN`.

Uruchom `${CLAUDE_SKILL_DIR}/scripts/check_status_labels.py` na gotowym dokumencie, a jeśli są diagramy, przejdź też przez
[checklistę jakości diagramów](./checklists/diagram-quality-checklist.md).

Wykonaj **test zwięzłości**: usuń powtórzenia między sekcjami (zostaw ID), wypełniacze, zdania
wprowadzające przed tabelami i sekcje warunkowe, które nie dotyczą zmiany. Porównaj objętość z
tabelą z Etapu 5; przekroczenie uzasadnij jednym zdaniem w odpowiedzi.

Przejdź przez [checklistę końcową](./checklists/final-review-checklist.md),
w tym **test pochodzenia treści**: przejrzyj dokument zdanie po zdaniu i dla
każdego zdania merytorycznego wskaż źródło. Zdanie bez źródła usuń, przenieś do
„Rekomendacji” albo zamień na OPEN.

Sprawdź także spójność: ID, terminologia, zgodność tabel z tekstem, zgodność
diagramu z opisem, każde OPEN z treści jest w tabeli „Tematy do wyjaśnienia”.

# Sekcja „Tematy do wyjaśnienia”

| ID | Temat | Czego brakuje i na co wpływa | Właściciel decyzji | Priorytet | Status |
|---|---|---|---|---|---|
| OPEN-001 | [Temat] | [Czego brakuje] – wpływa na [FR/US/obszar] | [Osoba/rola ze źródła lub DO POTWIERDZENIA] | Wysoki/Średni/Niski | Otwarty |

Zasady: patrz [przykład](./examples/open-questions-section.md). Po decyzji
przenieś treść do właściwej sekcji, zmień status na `ROZSTRZYGNIĘTY (DD.MM.RRRR)`
i zaktualizuj wymagania, testy, macierz i historię zmian dokumentu.

# Tryb „Dokument końcowy bez dopisków”

Cel: kompletny dokument **dokładnie w udostępnionym szablonie**, gotowy do
przekazania klientowi, bez śladów pracy skilla. Gdy użytkownik nie dał szablonu,
użyj szablonu zapasowego z tymi samymi regułami.

1. **Czego nie ma w dokumencie:** `SRC-NNN`, `plik:linia`, `ASSUMPTION-NNN`,
   `OPEN-NNN`, `Q-NNN`, `REC-NNN`, `DO POTWIERDZENIA`, „Nie analizowano”,
   „Brak danych”, kolumn „Źródło” i legendy oznaczeń, komentarzy,
   placeholderów oraz sekcji dodawanych przez skill (Materiały źródłowe,
   Założenia, Tematy do wyjaśnienia, Rekomendacje) – chyba że przewiduje je
   sam szablon. Identyfikatory wymagań (`FR-001` itd.) stosuj tylko, jeśli
   używa ich szablon.
2. **Struktura = szablon.** Żadnych dodanych, usuniętych ani przestawionych
   sekcji. Sekcja, której zmiana nie dotyczy, dostaje samo „Nie dotyczy.”
   (bez odwołań do źródeł).
3. **Treść nadal wyłącznie ze źródeł.** Pracuj jak w trybie roboczym (Etapy
   1–5), a oznaczenia prowadź w **rejestrze pochodzenia** poza dokumentem:
   sekcja szablonu → źródła, przyjęte założenia, luki. Rejestr oddaj jako
   osobny plik `<nazwa-dokumentu>-rejestr-pochodzenia.md` albo w odpowiedzi.
4. **Luki rozstrzyga użytkownik, nie skill.** Przed wygenerowaniem pokaż listę
   wszystkich `OPEN` i `ASSUMPTION` i dla każdej pozycji poproś o decyzję:
   - (a) uzupełnienie brakującej informacji,
   - (b) zatwierdzenie założenia jako ustalenia,
   - (c) pominięcie elementu w dokumencie,
   - (d) neutralne sformułowanie w języku klienta, bez identyfikatorów
     (np. „Do ustalenia z Zamawiającym przed rozpoczęciem prac”).

   Nigdy nie wypełniaj luki samodzielnie „typową” treścią. Jeśli użytkownik
   każe generować bez odpowiedzi, zastosuj (d), a gdy element bez tej
   informacji nie ma sensu – (c), i wypisz te miejsca pod dokumentem.
5. **Status dokumentu** w metryczce wpisz taki, jaki wskaże użytkownik; nie
   nadawaj samodzielnie statusu „Zaakceptowany”.
6. **Weryfikacja:** oprócz zwykłej checklisty wykonaj sekcję F
   [checklisty końcowej](./checklists/final-review-checklist.md), w tym
   wyszukiwanie pozostawionych znaczników.

# Tryb AUTO — cała praca na rekomendacjach

Włącz, gdy użytkownik użyje prefiksu `AUTO:` albo poprosi wprost o realizację całości bez pytań
(„zrób całość”, „akceptuj rekomendacje”, „bez dopytywania”). Skill przechodzi Etapy 0–6 bez
zatrzymywania się, a każde pytanie rozstrzyga swoją rekomendacją:

1. Pytania z Etapów 1, 2 i 4 nie są zadawane — wypisz je w dokumencie i w odpowiedzi.
2. Pytanie z „Propozycją domyślną” wynikającą z materiałów lub bezpieczną i odwracalną → przyjmij ją
   jako `ASSUMPTION-NNN (AUTO)`. Pytanie bez takiej propozycji → `OPEN-NNN`. Nigdy nie zgaduj treści
   merytorycznej: zasady 1, 3, 6 i 7 obowiązują bez zmian.
3. Plan sekcji i plan diagramów z Etapu 4 realizuj w wersji rekomendowanej (diagram tam, gdzie spełnia
   kryterium).
4. Status dokumentu: „Roboczy”. W trybie końcowym bez dopisków luki rozstrzygaj według pkt 4 tego trybu:
   (d) neutralne sformułowanie, a gdy element bez informacji nie ma sensu — (c) pominięcie.
5. Zapis: jeśli jest szablon, `md-to-docx` z `--template` lub `--reference-doc`; potem Etap 6 w całości.
6. Zatrzymaj się tylko, gdy: brak materiałów źródłowych, szablon wspomniany, ale niedostępny, polecenie
   zostało odrzucone dwa razy, albo działanie wymaga zgody (usunięcie plików, wysyłka, publikacja).
7. Pod dokumentem wypisz **rejestr decyzji AUTO**: każde pytanie, przyjętą rekomendację i jej
   identyfikator, aby użytkownik mógł je potwierdzić lub odrzucić po fakcie.

# Format odpowiedzi

W trybie końcowym bez dopisków punkt 4 zastąp: rejestr pochodzenia, lista
decyzji przyjętych dla luk oraz miejsca z neutralnym sformułowaniem lub
pominięte.

1. Potwierdzenie szablonu i formatu wyjściowego (Etap 0).
2. Rozumienie zmiany + rejestr źródeł + plan sekcji + pytania (Etapy 1–4).
3. Po odpowiedzi: pełny dokument w formacie szablonu.
4. Pod dokumentem (w odpowiedzi, nie w dokumencie, najwyżej 10 linii): liczba otwartych tematów
   OPEN, lista ASSUMPTION do potwierdzenia, sekcje oznaczone „Nie dotyczy”,
   lista diagramów z katalogiem ich plików, tematy bez diagramu z powodem oraz pominięte kontrole.
