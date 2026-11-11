---
name: client-pt-prd-writer
description: >
  Tworzy profesjonalną dokumentację PT/PRD (projekt techniczny, specyfikacja
  zmiany, analiza przedwdrożeniowa) dla klienta końcowego, opisującą rzeczywiste
  zmiany w aplikacji wyłącznie na podstawie dostarczonych materiałów, bez
  dopisywania treści. Pracuje na szablonie dokumentu użytkownika (.docx, .dotx,
  .md), a gdy go brak, na szablonie zapasowym. Użyj, gdy użytkownik prosi o
  dokument PT, PRD, specyfikację lub dokumentację zmiany, change request,
  analizę wpływu lub dokumentację rozwoju aplikacji dla klienta.
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
   - `ŹRÓDŁO: <dokument / ticket / mail / plik:linia / notatka z DD.MM>` – fakt potwierdzony,
   - `ASSUMPTION-NNN` – założenie zaakceptowane przez użytkownika do czasu potwierdzenia,
   - `OPEN-NNN` – brak informacji, temat do wyjaśnienia.
3. **Nie przepisuj zmiany na „większą”.** Opisuj dokładnie zakres z materiałów.
   Nie dodawaj funkcji, ról, integracji, NFR ani etapów, których nie ma w źródle.
   Pomysły spoza źródła możesz zgłosić wyłącznie jako `Rekomendacja` w osobnej
   sekcji, wyraźnie oddzielonej od wymagań.
4. **Sekcje są warunkowe, nie obowiązkowe.** Sekcja, której zmiana nie dotyczy,
   dostaje jedno zdanie: „Nie dotyczy – <uzasadnienie ze źródła>”. Sekcja, dla
   której brak danych: „Brak danych – patrz OPEN-NNN”. Nie wypełniaj sekcji tylko
   dlatego, że istnieje w szablonie.
5. **Szablon użytkownika ma pierwszeństwo** nad szablonem zapasowym tego skilla
   (patrz Etap 0).
6. **Bez dostępu do kodu nie opisujesz kodu.** Architekturę, moduły, tabele i API
   opisuj tylko, jeśli zostały przeanalizowane w repozytorium lub dokumentacji.
   W przeciwnym razie: „Nie analizowano – brak dostępu do <czego>”.
7. **Diagramy rysuj wyłącznie z przeanalizowanych komponentów.** Nigdy nie kopiuj
   przykładowego diagramu. Każdy węzeł diagramu musi występować w tekście.
8. Język zrozumiały dla klienta biznesowego, precyzyjny technicznie, jedna
   terminologia domenowa (zgodna z materiałami klienta – nie zmieniaj jego nazw).
9. Identyfikatory zawsze trzycyfrowe: `GOAL-001`, `SC-001`, `OOS-001`, `CHG-001`,
   `FR-001`, `US-001`, `NFR-001`, `INT-001`, `DATA-001`, `TEST-001`, `RISK-001`,
   `ASSUMPTION-001`, `OPEN-001`, `Q-001`, `REC-001`.

# Etap 0: Ustal szablon i format wyjściowy

1. Sprawdź, czy użytkownik dostarczył szablon (plik .docx/.dotx/.md/.pdf, wzór
   poprzedniego dokumentu, link). Jeśli wspomina o szablonie, ale go nie
   załączył – poproś o niego jednym pytaniem.
2. **Jeśli jest szablon użytkownika:**
   - przeczytaj go w całości (dla .docx/.dotx użyj skilla docx),
   - spisz mapę sekcji szablonu wg [instrukcji mapowania](./references/template-mapping.md),
   - zachowaj kolejność, numerację, nazwy sekcji, style, nagłówki/stopki, stronę
     tytułową, metryczkę i tabele szablonu; nie dodawaj sekcji, których szablon
     nie przewiduje – brakujące elementy obowiązkowe (np. Tematy do wyjaśnienia)
     dołącz jako ostatni rozdział lub załącznik, w stylu szablonu,
   - wynik oddaj w formacie szablonu (szablon .docx → dokument .docx).
3. **Jeśli brak szablonu:** użyj [szablonu zapasowego](./templates/client-pt-prd-template.md)
   i oddaj dokument w formacie, o który prosi użytkownik.
4. Gdy użytkownik dostarczy poprzedni dokument jako wzór – przejmij z niego
   strukturę, styl i poziom szczegółowości, **nie treść merytoryczną**.

# Etap 1: Zebranie materiałów i inwentaryzacja źródeł

Zbierz wszystko, co dostarczono: brief, ticket, e-mail, notatkę ze spotkania,
istniejącą dokumentację, kod, konfigurację, modele danych, specyfikacje API,
wymagania prawne, oczekiwania co do terminu i wdrożenia.

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
`ŹRÓDŁO: src/orders/OrderService.cs:142, endpoint POST /api/orders`.
Jeśli kodu/dokumentacji nie ma, w sekcjach technicznych wpisz
„Nie analizowano – brak dostępu do <repozytorium/dokumentacji>” i dodaj OPEN.

Nie opisuj stacku, architektury ani modułów niezwiązanych ze zmianą.

# Etap 4: Uzgodnienie zakresu dokumentu

Przed napisaniem pełnego dokumentu przedstaw użytkownikowi krótko:
1. jak rozumiesz zmianę (3–5 zdań, ze wskazaniem źródeł),
2. które sekcje szablonu zostaną wypełnione, które oznaczysz „Nie dotyczy”,
   a które „Brak danych”,
3. listę pytań (Etap 2) i proponowanych `ASSUMPTION`.

Pełny dokument generuj po odpowiedzi użytkownika. Jeśli użytkownik prosi wprost
o wersję roboczą od razu – wygeneruj ją ze statusem „Roboczy”, z wszystkimi
lukami oznaczonymi jako `OPEN` (bez zgadywania) i listą pytań na końcu.

# Etap 5: Pisanie dokumentu

Pisz w strukturze szablonu (Etap 0). Obszary treści, które należy umieścić w
odpowiednich sekcjach szablonu – **tylko jeśli dotyczą zmiany**:

| Obszar | Kiedy wymagany |
|---|---|
| Metryczka, historia zmian, materiały źródłowe | zawsze |
| Streszczenie zarządcze | zawsze |
| Kontekst i cel zmiany | zawsze |
| Zakres (w zakresie / poza zakresem) | zawsze |
| Proces obecny i docelowy, różnice | gdy zmienia się proces lub zachowanie |
| Role i uprawnienia | gdy zmiana dotyka ról/uprawnień |
| Wymagania funkcjonalne | zawsze |
| User stories z kryteriami akceptacji | gdy są zmiany widoczne dla użytkownika |
| Wymagania niefunkcjonalne | tylko te wynikające ze źródeł |
| Analiza wpływu na aplikację | zawsze (lub „Nie analizowano”) |
| Architektura i diagram | gdy zmienia się architektura i jest analiza |
| Integracje | gdy zmiana dotyka integracji |
| Model danych i migracje | gdy zmieniają się dane/schemat |
| Bezpieczeństwo, RODO, audyt | gdy zmiana dotyka danych osobowych, dostępu, audytu |
| Plan testów | zawsze |
| Wdrożenie i rollback | gdy są informacje o wdrożeniu (inaczej OPEN) |
| Ryzyka i zależności | zawsze – tylko zidentyfikowane, ze źródłem |
| Rekomendacje (poza wymaganiami) | opcjonalnie |
| Słownik pojęć | gdy w dokumencie są skróty/terminy |
| Macierz śledzenia wymagań | gdy jest ≥ 3 wymagań FR |
| Tematy do wyjaśnienia | zawsze (może zawierać „Brak otwartych tematów”) |

Zasady pisania:
- Każde FR, US, NFR, INT, DATA, RISK w tabeli ma kolumnę „Źródło”.
- Priorytet, właściciel, termin i miara są wpisywane **tylko ze źródła**; inaczej
  `DO POTWIERDZENIA` + OPEN.
- Kryteria akceptacji formułuj tak, aby były sprawdzalne; jeśli źródło nie daje
  podstaw do kryterium, nie wymyślaj progu – oznacz OPEN.
- Streszczenie zarządcze pisz na końcu, z treści dokumentu, bez nowych faktów.
- Zobacz [przykłady: źródło vs zmyślenie](./examples/sourced-vs-invented.md).

# Etap 6: Weryfikacja przed oddaniem

Przejdź przez [checklistę końcową](./checklists/final-review-checklist.md),
w tym **test pochodzenia treści**: przejrzyj dokument zdanie po zdaniu i dla
każdego zdania merytorycznego wskaż źródło. Zdanie bez źródła usuń, przenieś do
„Rekomendacji” albo zamień na OPEN.

Sprawdź także spójność: ID, terminologia, zgodność tabel z tekstem, zgodność
diagramu z opisem, każde OPEN z treści jest w tabeli „Tematy do wyjaśnienia”.

# Sekcja „Tematy do wyjaśnienia”

| ID | Temat | Opis | Dlaczego wymaga wyjaśnienia | Wpływ | Właściciel decyzji | Priorytet | Status | Data decyzji |
|---|---|---|---|---|---|---|---|---|
| OPEN-001 | [Temat] | [Czego brakuje] | [Na co wpływa] | Wysoki/Średni/Niski | [Osoba/rola ze źródła lub DO POTWIERDZENIA] | Wysoki/Średni/Niski | Otwarty | – |

Zasady: patrz [przykład](./examples/open-questions-section.md). Po decyzji
przenieś treść do właściwej sekcji, zmień status na `ROZSTRZYGNIĘTY`, wpisz datę
i zaktualizuj wymagania, testy, macierz i historię zmian dokumentu.

# Format odpowiedzi

1. Potwierdzenie szablonu i formatu wyjściowego (Etap 0).
2. Rozumienie zmiany + rejestr źródeł + plan sekcji + pytania (Etapy 1–4).
3. Po odpowiedzi: pełny dokument w formacie szablonu.
4. Pod dokumentem (w odpowiedzi, nie w dokumencie): liczba otwartych tematów
   OPEN, lista ASSUMPTION do potwierdzenia, sekcje oznaczone „Nie dotyczy”.
