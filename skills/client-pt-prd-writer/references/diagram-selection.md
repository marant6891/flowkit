# Kiedy i jaki diagram

Diagram powstaje tylko wtedy, gdy poprawia zrozumienie. Jakość dokumentu ma pierwszeństwo przed liczbą diagramów.

## Test przydatności

Zaplanuj diagram tylko, gdy odpowiedź na **wszystkie** pytania brzmi „tak”:

1. Czy zagadnienie ma charakter strukturalny, procesowy lub relacyjny?
2. Czy ma co najmniej 3 powiązane elementy albo punkt decyzyjny?
3. Czy sam tekst lub tabela utrudniają zobaczenie zależności?
4. Czy źródła potwierdzają elementy i relacje, które mają znaleźć się na grafice?

| Treść | Forma |
|---|---|
| Prosta lista wymagań | Lista lub tabela, bez diagramu |
| Zestawienie parametrów | Tabela, bez diagramu |
| Pojedyncza informacja lub integracja A → B bez dodatkowej logiki | Zdanie, bez diagramu |
| Proces z decyzjami, wyjątkami lub wieloma rolami | Diagram |
| Kilka komponentów z kierunkami komunikacji | Diagram |

Dokument bez uzasadnionych diagramów jest poprawnym wynikiem.

## Dobór typu

| Pytanie, na które odpowiada diagram | Typ (`type`) | Typowy dokument |
|---|---|---|
| Z czego składa się system i jak łączą się części? | `architecture` | PT, PRD (kontekst) |
| Jakie moduły mają jakie odpowiedzialności? | `component` | PT |
| Jak przebiega proces i gdzie są decyzje? | `flowchart` | PRD, proces |
| Kto za co odpowiada w procesie? | `swimlane` | PRD, proces |
| W jakiej kolejności systemy wymieniają komunikaty? | `sequence` | PT |
| Jakie stany ma obiekt i co je zmienia? | `state-machine` | PRD, PT |
| Jakie są encje i relacje danych? | `er` | PT |
| Którędy płyną dane? | `data-flow` | PT |
| Jakie systemy są zintegrowane i w którą stronę? | `integration` | PT |
| Gdzie uruchomione są komponenty? | `deployment` | PT, DevOps |
| Co od czego zależy? | `dependency` | PT, DevOps |
| Jakie są etapy i terminy? | `timeline` | PRD, wdrożenie |
| Jaką drogę przechodzi użytkownik? | `user-journey` | PRD |
| Jak wymagania łączą się z testami lub komponentami? | `requirement-traceability` | PRD, PT |
| Jakie role mają dostęp do jakich zasobów? | `security-matrix` | PT, bezpieczeństwo |

Macierz śledzenia i macierz uprawnień stosuj jako grafikę tylko wtedy, gdy układ daje więcej niż zwykła tabela dokumentu.

## Plan diagramów

Plan pokaż użytkownikowi w Etapie 4, razem z tematami pominiętymi:

| ID | Sekcja | Typ | Priorytet | Uzasadnienie | Źródła |
|---|---|---|---|---|---|
| D-01 | 10. Architektura | Architektura | Wysoki | 5 komponentów i 2 integracje | SRC-001, SRC-002 |

Pominięte: „Wymagania niefunkcjonalne”, ponieważ tabela wystarcza.

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
