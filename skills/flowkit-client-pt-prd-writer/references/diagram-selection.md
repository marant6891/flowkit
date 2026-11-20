# Kiedy i jaki diagram

Skill zawsze ocenia, czy procesy, przepływy i relacje opisane w dokumencie warto pokazać graficznie.
Diagram powstaje, gdy poprawia zrozumienie. Jakość dokumentu ma pierwszeństwo przed liczbą diagramów.

## Obowiązkowy przegląd tematów

Przed pisaniem dokumentu znajdź w materiałach poniższe tematy. Dla każdego znalezionego tematu zapisz decyzję w planie diagramów.

| Temat w materiałach | Diagram jest zasadny, gdy | Typ (`type`) |
|---|---|---|
| Proces biznesowy lub systemowy | Ma co najmniej 3 kroki, decyzję, wyjątek lub ścieżkę alternatywną | `flowchart` |
| Proces z podziałem odpowiedzialności | Zadania przechodzą między co najmniej 2 rolami, zespołami lub systemami | `swimlane` |
| Komunikacja między systemami | Występują co najmniej 3 komunikaty, odpowiedź zwrotna, obsługa błędu lub ważna kolejność, także przy 2 systemach | `sequence` |
| Przepływ danych | Dane przechodzą przez co najmniej 2 etapy lub systemy albo są przekształcane | `data-flow` |
| Integracje | Występują co najmniej 2 integracje albo kierunki komunikacji są istotne dla zmiany | `integration` |
| Relacje między systemami lub komponentami | Co najmniej 3 elementy mają wzajemne zależności | `architecture`, `component`, `dependency` |
| Zmiana stanów obiektu | Obiekt ma co najmniej 3 stany lub przejścia zależne od warunków | `state-machine` |
| Model danych | Co najmniej 3 encje albo 2 relacje | `er` |
| Infrastruktura i wdrożenie | Komponenty działają w co najmniej 2 środowiskach, strefach lub węzłach | `deployment` |
| Etapy i terminy | Co najmniej 3 etapy mają ustaloną kolejność | `timeline` |
| Ścieżka użytkownika | Użytkownik przechodzi przez co najmniej 3 kroki | `user-journey` |
| Powiązania wymagań | Macierz daje więcej niż zwykła tabela dokumentu | `requirement-traceability` |
| Role i dostęp do zasobów | Macierz daje więcej niż zwykła tabela dokumentu | `security-matrix` |

Gdy temat spełnia kryterium, domyślną decyzją jest **diagram**. Jeden temat może wymagać dwóch diagramów tylko wtedy, gdy odpowiadają na różne pytania, np. architektura i sekwencja wywołań.

## Kiedy nie dodawać diagramu

Rezygnację z diagramu uzasadnij w planie jednym z powodów:

| Powód | Przykład | Co zrobić |
|---|---|---|
| Treść nie ma struktury ani relacji | Lista wymagań, zestawienie parametrów, pojedyncza informacja | Zostaw listę lub tabelę |
| Temat nie spełnia kryterium | Jeden komunikat A → B bez dodatkowej logiki | Opisz w zdaniu |
| Źródła nie potwierdzają głównych elementów ani relacji | Wiadomo, że integracja istnieje, ale nie wiadomo między czym | Dodaj `OPEN-NNN`, bez diagramu |
| Diagram powieliłby inny diagram | Ten sam przepływ pokazano już w tej samej sekcji | Odwołaj się do istniejącego rysunku |

Gdy główna struktura jest potwierdzona, a brakuje szczegółu, narysuj tylko potwierdzone elementy, a brak opisz w uwagach pod rysunkiem z `OPEN-NNN`. Niewiadome nigdy nie trafiają na obraz.

Dokument, w którym żaden temat nie spełnia kryteriów, poprawnie pozostaje bez diagramów.

## Plan diagramów

Plan pokaż użytkownikowi w Etapie 4. Obejmuje tematy z diagramem i tematy bez diagramu:

| ID | Temat | Sekcja | Decyzja | Typ | Priorytet | Uzasadnienie | Źródła |
|---|---|---|---|---|---|---|---|
| D-01 | Komunikacja portalu z systemem ERP | 11. Integracje | Diagram | Sekwencja | Wysoki | 4 komunikaty i obsługa błędu | SRC-001, SRC-002 |
| – | Parametry eksportu | 8. Wymagania niefunkcjonalne | Bez diagramu | – | – | Zestawienie parametrów, tabela wystarcza | SRC-003 |

Identyfikator `D-NN` jest stały przez cały cykl życia dokumentu, także po zmianie kolejności rysunków.

## Limity czytelności

Jeden diagram to jedna myśl. Po przekroczeniu limitu podziel treść na przegląd i szczegóły.

| Rodzaj | Zalecany limit |
|---|---|
| Diagram warstwowy | 12 elementów, 16 połączeń |
| Sekwencja | 6 uczestników |
| Swimlane | 5 ról |
| Macierz | 8 kolumn, 14 wierszy |
| Wyróżnienie akcentem | 1–2 elementy |
