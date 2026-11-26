# Prosty język we FlowKit (PL i EN)

Ten standard mówi, jak pisać teksty dla ludzi: dokumenty dla klienta, maile, podsumowania spotkań, PT/PRD,
dokumentację użytkownika i postmortemy. Obowiązuje wszystkie skille, agentów i prompty FlowKit.
Plik leży w `<runtime>/procedures/plain-language.md`, więc jest dostępny po każdej instalacji.

Każda reguła ma identyfikator (np. `PL-Z1`), poziom, przykład i źródło. Reguły z poziomem `WARN` lub `FAIL`
sprawdza polecenie `plain-check` (punkt 8). Reguły z poziomem `PRZEGLĄD` sprawdza autor lub verifier.

## 1. Poziomy i tryby

| Poziom | Znaczenie |
|---|---|
| `FAIL` | błąd; w trybie końcowym tekst nie przechodzi kontroli |
| `WARN` | ostrzeżenie; popraw, chyba że masz dobry powód |
| `PRZEGLĄD` | skrypt tego nie wykryje; sprawdza autor lub verifier w `DOC-AUDIT` |

- **Tryb roboczy** (domyślny): wszystkie naruszenia są ostrzeżeniami.
- **Tryb końcowy** (`--strict`): reguły oznaczone `FAIL` blokują wynik.

Kalki i korpomowę oceniamy przypadek po przypadku (tak radzi Obserwatorium Językowe UW). Dlatego mają poziom
`WARN`, a nie `FAIL`.

## 2. Wyjątki

Reguły nie dotyczą:

- kodu, bloków kodu, `identyfikatorów`, nazw plików, poleceń i adresów URL,
- cytatów ze źródeł w cudzysłowie (np. wypowiedź klienta, treść zgłoszenia),
- nazw własnych, nazw produktów i nazw ekranów w systemie,
- tekstu, którego brzmienie narzuca umowa, prawo lub szablon klienta,
- terminów ze słownika dozwolonych (punkt 6).
- fragmentów objętych komentarzami `<!-- plain-check: off -->` i `<!-- plain-check: on -->`. Używaj ich tylko
  dla celowych złych przykładów, np. kolumny „Zamiast” w tabeli zwrotów.
- nagłówka YAML na początku pliku (np. w `SKILL.md`).

Gdy profil stylu klienta lub jego szablon mówi inaczej niż ten standard, wygrywa klient. Odstępstwo zapisz
w uwagach do dokumentu.

## 3. Polski

### 3.1 Struktura tekstu

| ID | Reguła | Poziom | Źródło |
|---|---|---|---|
| PL-S1 | Zacznij od tego, co najważniejsze dla odbiorcy: decyzja, prośba, wynik. Tło i szczegóły dalej. | PRZEGLĄD | GOV |
| PL-S2 | Dziel tekst nagłówkami i krótkimi akapitami. Wyliczenia daj w listach, porównania w tabelach. | PRZEGLĄD | GOV |
| PL-S3 | Pisz wprost do odbiorcy, formami osobowymi: „Prosimy o potwierdzenie”, a nie „Wymagane jest potwierdzenie”. | PRZEGLĄD | GOV |
| PL-S4 | Rozwiń skrót przy pierwszym użyciu: „wymagania niefunkcjonalne (NFR)”. Wyjątek: skróty ze słownika (punkt 6). | WARN | GOV |
| PL-S5 | Jedna rzecz, jedna nazwa. Nie zmieniaj nazwy dla urozmaicenia („moduł”, „komponent”, „element” o tym samym). | PRZEGLĄD | GOV |

### 3.2 Zdanie

| ID | Reguła | Poziom | Źródło |
|---|---|---|---|
| PL-Z1 | Zdanie ma do 20 słów. Dłuższe podziel. | WARN powyżej 20, `FAIL` powyżej 35 | GOV |
| PL-Z2 | Strona czynna zamiast biernej: „Zmieniliśmy konfigurację”, a nie „Konfiguracja została zmieniona”. | PRZEGLĄD | GOV |
| PL-Z3 | Czasownik zamiast rzeczownika odczasownikowego: „zmienić”, a nie „dokonać zmiany”. | WARN | GOV |
| PL-Z4 | Unikaj imiesłowów i wtrąceń. „Po weryfikacji danych wyślemy raport” zamiast „Zweryfikowawszy dane, wyślemy raport”. | PRZEGLĄD | GOV |
| PL-Z5 | Najpierw to, co znane, na końcu to, co nowe. Okolicznik czasu i miejsca stawiaj przed zdarzeniem. | PRZEGLĄD | PAN |

Jak liczyć słowa w `PL-Z1`: słowa to ciągi znaków między spacjami. Nie liczymy kodu, adresów URL ani znaczników
listy. Każdy punkt listy i każda komórka tabeli to osobne zdanie.

Przykład do `PL-Z5`:

- Źle: „Kilka incydentów miało miejsce od tego czasu.”
- Dobrze: „Od tego czasu miało miejsce kilka incydentów.”

<!-- plain-check: off -->

### 3.3 Słowa: wata i nominalizacje

| ID | Zamiast | Pisz | Poziom | Źródło |
|---|---|---|---|---|
| PL-W1 | dokonać zakupu, dokonać zmiany, dokonanie analizy | kupić, zmienić, przeanalizować | WARN, `FAIL` w trybie końcowym | GOV |
| PL-W2 | uległ pogorszeniu, uległ zmianie | pogorszył się, zmienił się | WARN | GOV |
| PL-W3 | w dniu dzisiejszym | dziś | `FAIL` | GOV |
| PL-W4 | w miesiącu maju | w maju | `FAIL` | GOV |
| PL-W5 | celem (+ dopełniacz): „celem weryfikacji” | aby, żeby: „aby sprawdzić” | WARN | GOV |
| PL-W6 | niniejszy, niniejsza, niniejsze | ten, ta, to | `FAIL` | GOV |
| PL-W7 | dedykowany (w znaczeniu „przeznaczony”) | przeznaczony dla, osobny | WARN | GOV |
| PL-W8 | komponent (w tekście dla użytkownika, nie w opisie technicznym) | składnik, część, element | WARN | GOV |
| PL-W9 | w chwili obecnej, na chwilę obecną | teraz, obecnie | WARN | FK |
| PL-W10 | posiadać (w znaczeniu „mieć”) | mieć | WARN | FK |
| PL-W11 | w oparciu o | na podstawie | WARN | FK |
| PL-W12 | w związku z faktem, iż; z uwagi na fakt, że | bo, ponieważ | WARN | FK |

Trudny termin wyjaśnij albo zastąp znanym słowem. Przykład z gov.pl: zamiast opisowej nazwy urządzenia napisz
„hak holowniczy”.

### 3.4 Korpomowa i kalki leksykalne

| ID | Zamiast | Pisz | Poziom | Źródło |
|---|---|---|---|---|
| PL-K1 | zaparkować temat, zaparkujmy to | odłóżmy to, wrócimy do tego (podaj kiedy) | WARN | OJUW |
| PL-K2 | połączyć kropki | powiązać fakty, wyciągnąć wniosek | WARN | OJUW |
| PL-K3 | stoi w sprzeczności z | przeczy, jest sprzeczne z | WARN | OJUW |
| PL-K4 | zaadresować problem, zaadresować temat | zająć się problemem, odpowiedzieć na | WARN | FK |
| PL-K5 | dowieźć (projekt, funkcję) | dostarczyć, wdrożyć, skończyć | WARN | FK |
| PL-K6 | na ten moment | teraz, na razie | WARN | FK |
| PL-K7 | to robi sens | to ma sens | WARN | FK |
| PL-K8 | być na tej samej stronie | zgadzać się, rozumieć tak samo | WARN | FK |
| PL-K9 | na koniec dnia (w znaczeniu „ostatecznie”) | ostatecznie, w sumie | WARN | FK |
| PL-K10 | ASAP | do [data], jak najszybciej | WARN | FK |
| PL-K11 | definiować (w znaczeniu „określać, decydować”) | określać, decydować o | PRZEGLĄD | PAN |

### 3.5 Kalki składniowe

Artykuł z PAN pokazuje, że kalka z angielskiego siedzi głównie w szyku zdania, a nie w słowach. Dlatego większość
tych reguł ma poziom `PRZEGLĄD`.

| ID | Kalka | Pisz | Poziom | Źródło |
|---|---|---|---|---|
| PL-P1 | Rzeczownik w roli przymiotnika: „biznes informacje”, „kredyt bank” | „informacje biznesowe”, „bank kredytowy” | PRZEGLĄD | PAN |
| PL-P2 | Przymiotnik klasyfikujący przed rzeczownikiem: „obcy język”, „ustny egzamin” | „język obcy”, „egzamin ustny” | PRZEGLĄD | PAN |
| PL-P3 | Tryb rozkazujący jako warunek: „Zaloguj się i zyskaj dostęp” | „Po zalogowaniu zyskasz dostęp” | PRZEGLĄD | PAN |
| PL-P4 | „To drugi raz, gdy…”, „To nie pierwszy raz, kiedy…” | „Po raz drugi…”, „Nie po raz pierwszy…” | WARN | PAN |
| PL-P5 | „użyć X, by…”: „Użyliśmy skryptu, by przenieść dane” | narzędnik: „Przenieśliśmy dane skryptem” | WARN | PAN |
| PL-P6 | „To, co…, to…”: „To, co blokuje prace, to brak dostępu” | „Prace blokuje brak dostępu” | WARN | PAN |
| PL-P7 | „Był [czas], kiedy…”: „Był poniedziałek, kiedy system przestał działać” | „W poniedziałek system przestał działać” | WARN | PAN |
| PL-P8 | Puste „to” jako podmiot: „To może zająć kilka dni, zanim…” | „[Czynność] może zająć kilka dni” | WARN | PAN |
| PL-P9 | Nowa informacja na początku zdania: „Awaria wystąpiła wczoraj w nocy” jako otwarcie tekstu | „Wczoraj w nocy wystąpiła awaria” | PRZEGLĄD | PAN |

`PL-P3` nie dotyczy zwykłych próśb: „Proszę potwierdzić do piątku” jest w porządku. Kalka to tryb rozkazujący,
który wyraża warunek albo możliwość.

## 4. English

Źródła w materiałach do standardu dotyczą tylko polskiego. Reguły angielskie opierają się na Federal Plain
Language Guidelines (PLG) i GOV.UK Style Guide (GOVUK). Dodatkowo `EN-F` opisuje błędy typowe dla osób, które
myślą po polsku i piszą po angielsku.

### 4.1 Struktura i zdanie

| ID | Reguła | Poziom | Źródło |
|---|---|---|---|
| EN-S1 | Put the main point first: the decision, the request or the result. | PRZEGLĄD | PLG, GOVUK |
| EN-S2 | Use headings, short paragraphs, lists and tables. | PRZEGLĄD | PLG |
| EN-S3 | Address the reader as "you". Use "we" for your team. | PRZEGLĄD | PLG |
| EN-S4 | Spell out an abbreviation the first time you use it. | WARN | PLG, GOVUK |
| EN-Z1 | Keep sentences to 20 words or fewer on average. | WARN above 25, `FAIL` above 35 | PLG, GOVUK |
| EN-Z2 | Use the active voice: "We updated the configuration", not "The configuration was updated". | PRZEGLĄD | PLG |
| EN-Z3 | Use verbs, not nouns made from verbs: "decide", not "make a decision". | WARN | PLG |

### 4.2 Words

| ID | Instead of | Write | Poziom | Źródło |
|---|---|---|---|---|
| EN-W1 | make a decision, carry out an analysis, provide assistance | decide, analyse, help | WARN | PLG |
| EN-W2 | in order to | to | WARN | PLG |
| EN-W3 | at this point in time, at the present time | now | `FAIL` | PLG |
| EN-W4 | due to the fact that, in view of the fact that | because | WARN | PLG |
| EN-W5 | prior to, subsequent to | before, after | WARN | PLG |
| EN-W6 | with regard to, in relation to | about | WARN | PLG |
| EN-W7 | utilise, utilize, commence, facilitate | use, start, help | WARN | PLG, GOVUK |
| EN-W8 | please do not hesitate to contact us | contact us if you have questions | WARN | GOVUK |

### 4.3 Corporate jargon

| ID | Instead of | Write | Poziom | Źródło |
|---|---|---|---|---|
| EN-K1 | leverage | use | WARN | GOVUK |
| EN-K2 | going forward | from now on, in future | WARN | GOVUK |
| EN-K3 | circle back, touch base | reply, talk, meet (say when) | WARN | FK |
| EN-K4 | deep dive | detailed review, analysis | WARN | FK |
| EN-K5 | low-hanging fruit | quick wins, easy changes | WARN | FK |
| EN-K6 | robust, streamline, synergy | say what it does: "handles 10x load", "removes two steps" | WARN | GOVUK |
| EN-K7 | park this topic | come back to this on [date] | WARN | OJUW (odwrotność PL-K1) |

### 4.4 Polish false friends and calques

| ID | Polish thinking | Wrong | Right | Poziom |
|---|---|---|---|---|
| EN-F1 | aktualny | the actual version | the current version | WARN |
| EN-F2 | aktualnie | actually we are testing | we are currently testing | WARN |
| EN-F3 | ewentualnie | eventually we can add | if needed, we can add | WARN |
| EN-F4 | realizować | realize the project | carry out, deliver the project | WARN |
| EN-F5 | kontrola | control of the data | check of the data | PRZEGLĄD |
| EN-F6 | według mnie | according to me | in my view | WARN |
| EN-F7 | bazując na | basing on | based on | WARN |
| EN-F8 | pytanie do Pana | a question to you | a question for you | WARN |
| EN-F9 | w załączniku przesyłam | in the attachment I send | I've attached | WARN |
| EN-F10 | jesteśmy po spotkaniu | we are after the meeting | we had the meeting | WARN |
| EN-F11 | dedykowany | a dedicated solution (meaning "custom") | a custom solution, a solution for X | PRZEGLĄD |
| EN-F12 | konkretnie | concretely | specifically | WARN |

Źródło `EN-F`: FK, na podstawie typowych błędów z korespondencji projektowej.

## 5. Styl naturalny

Te reguły już obowiązują w agentach (`Natural style`). Standard je porządkuje.

| ID | Reguła | Poziom |
|---|---|---|
| NS-1 | Bez półpauzy i pauzy (`–`, `—`). Użyj myślnika `-`, przecinka lub dwukropka. | `FAIL` |
| NS-2 | Bez emoji ozdobnych. | `FAIL` |
| NS-3 | Bez formułek AI i waty: „Warto podkreślić, że”, „Należy zauważyć, że”, „Mam nadzieję, że ta wiadomość zastaje…”, „I hope this email finds you well”. | WARN |
| NS-4 | Bez wykrzykników i WIELKICH LITER dla nacisku. | WARN |

Pełna lista formułek do usunięcia jest w phrasebooku redaktora maili
(`skills/flowkit-client-message-editor/references/phrasebook.md`).

<!-- plain-check: on -->

## 6. Słownik dozwolonych terminów

Terminy branżowe nie są błędem, gdy odbiorca ich używa. Checker ich nie zgłasza.

- **Zawsze dozwolone:** API, backend, frontend, backlog, branch, commit, deploy, endpoint, hotfix, log, pull request,
  release, runbook, sprint, SLA, SLO, SQL, UI, UX.
- **Projekt może dodać własne** w `flowkit-project.md`. Checker czyta je z dwóch miejsc:
  - sekcja `Słownik`: każdy punkt listy to termin, np. `- HPA: autoskalowanie podów`,
  - sekcja `Klient i terminologia`: punkt `Terminy, których należy używać: KSeF, ZUS` i punkty `termin = znaczenie`.
- W dokumencie dla użytkownika końcowego wyjaśnij termin przy pierwszym użyciu albo użyj polskiego odpowiednika:
  „wdrożenie” zamiast „deploy”.

## 7. Źródła

| Skrót | Źródło |
|---|---|
| GOV | Prosty język, gov.pl, Dostępność cyfrowa: https://www.gov.pl/web/dostepnosc-cyfrowa/prosty-jezyk |
| OJUW | „Zaparkować temat i połączyć kropki, czyli korpofrazeo”, Obserwatorium Językowe UW: https://obserwatoriumjezykowe.uw.edu.pl/?p=7998 |
| PAN | M. Górnicz, „Pożyczki językowe”, Academia. Magazyn PAN 4/76/2023, DOI 10.24425/academiaPAN.2023.147616 |
| PLG | Federal Plain Language Guidelines: https://www.plainlanguage.gov/guidelines/ |
| GOVUK | GOV.UK Style Guide i „Words to avoid”: https://www.gov.uk/guidance/style-guide |
| FK | własna reguła FlowKit; nie pochodzi z powyższych źródeł |

Do oceny trudności polskiego tekstu gov.pl poleca narzędzia Logios i Jasnopis.

## 8. Jak sprawdzić tekst

Agent uruchamia kontrolę przez executor:

```bash
python "<runtime>/flowkit_exec.py" --role analyst -- plain-check wynik/dokument.md
python "<runtime>/flowkit_exec.py" --role verifier -- plain-check wynik/dokument.docx --strict
```

Opcje: `--lang auto|pl|en`, `--strict` (tryb końcowy), `--audience user` (tekst dla użytkownika końcowego),
`--glossary plik`. Bez `--glossary` checker czyta `flowkit-project.md` z bieżącego katalogu.

Skrypt nie oceni szyku ani strony biernej. Przed oddaniem tekstu przejdź też tę listę:

1. Czy pierwszy akapit mówi, co odbiorca ma wiedzieć albo zrobić?
2. Czy żadne zdanie nie ma więcej niż 20 słów (EN: 25)?
3. Czy w tekście są frazy z tabel `W` i `K`?
4. Czy przy zdaniach na „To, co…”, „To drugi raz…”, „Był…, kiedy…” da się zmienić szyk?
5. Czy skróty są rozwinięte, a terminy spoza słownika wyjaśnione?
6. Czy nie ma `–`, `—`, emoji i formułek AI?
