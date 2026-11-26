# Struktura profesjonalnej pomocy i dokumentacji rozwiązania

Pomoc ma odpowiedzieć użytkownikowi na cztery pytania: **do czego to służy**, **co widzę na ekranie**, **co
mogę tu zrobić** i **co znaczy każda informacja**. Same kroki odpowiadają tylko na trzecie.

## Rozdział modułu w pomocy dla użytkownika

Każdy moduł lub ekran z katalogu funkcji dostaje rozdział w tej kolejności. Podrozdział, który nie dotyczy
modułu, pomijasz (szablon zapasowy) albo oznaczasz „Nie dotyczy.” (szablon użytkownika).

| Nr | Podrozdział | Treść | Źródło w kodzie |
|---|---|---|---|
| 1 | **Do czego służy** | 2-4 zdania: co użytkownik tu osiąga, dla kogo jest moduł, skąd biorą się dane i jak często się odświeżają | trasa, menu, serwis danych, interwały |
| 2 | **Najważniejsze pojęcia** | Pojęcia potrzebne do zrozumienia ekranu (np. „obiekt”, „zadanie”, „plan”); typy obiektów | słowniki, enumeracje, typy |
| 3 | **Układ ekranu** | Rysunek układu (diagram albo zrzut) z ponumerowanymi obszarami i legendą: numer, obszar, co zawiera | szablon widoku, układ kolumn i paneli |
| 4 | **Opcje i przyciski** | Tabela wszystkich elementów z katalogu opcji: element (ikona i nazwa), gdzie, co robi, kiedy jest dostępny | szablon widoku, uprawnienia, handlery |
| 5 | **Praca z modułem (zadania)** | Tematy-zadania krok po kroku według [wzorców tematów](../templates/topic-patterns.md); przy procesie z decyzją rysunek przebiegu | handlery, walidacje, komunikaty |
| 6 | **Informacje w tabeli (słownik kolumn)** | Wszystkie kolumny, także domyślnie ukryte: kolumna, co pokazuje, jednostka lub format; pogrupowane tematycznie | definicje kolumn, formatery |
| 7 | **Statusy, kolory i ikony** | Każdy status, kolor wiersza, ikona stanu: co oznacza i co z tym zrobić; przy co najmniej 3 stanach z przejściami rysunek | enumeracje, style wierszy, ikony |
| 8 | **Zakładki i panele szczegółów** | Każda zakładka: co pokazuje, jakie ma opcje (daty, filtry, przyciski), kiedy jest widoczna | dyrektywy, komponenty zakładek |
| 9 | **Uprawnienia** | Które opcje wymagają dodatkowego uprawnienia, językiem odbiorcy („widoczne, gdy administrator nada uprawnienie do…”) | klucze uprawnień, opis uprawnień w repozytorium |
| 10 | **Problemy i komunikaty** | Komunikat lub objaw, przyczyna, co zrobić | komunikaty błędów, warunki |
| 11 | **Najczęstsze pytania** | Z reguł, ograniczeń i statusów; odsyłają do podrozdziałów | katalog opcji |

## Dokument jako całość (pomoc)

1. Strona tytułowa i metryczka (z szablonu), spis treści.
2. **Wprowadzenie:** dla kogo, czego dotyczy, wymagania (konto, uprawnienia, przeglądarka), konwencje dokumentu
   (pogrubienie = nazwa z ekranu, `>` = ścieżka menu, ikony opisane słownie).
3. **Pierwsze kroki:** logowanie, nawigacja, wylogowanie; rysunek przebiegu logowania, gdy są warianty (kod
   weryfikacyjny, reset hasła, logowanie zewnętrzne).
4. Rozdziały modułów według struktury powyżej.
5. Słownik pojęć, tematy lub kwestie do wyjaśnienia, załączniki robocze (tylko tryb roboczy).

## Dokumentacja rozwiązania (administrator, zespół techniczny)

Dla każdego obszaru: przeznaczenie, rysunek (komponenty, przepływ danych, sekwencja integracji, model danych),
tabela elementów (ustawienia, endpointy, tabele, zadania cykliczne) z kompletnym katalogiem, procedury krok po
kroku (instalacja, konfiguracja, diagnostyka), problemy. Katalog opcji obejmuje tu ustawienia, role
i uprawnienia, zadania cykliczne, integracje i komunikaty w logach.

## Jakość opisu opcji

- Opis mówi, **co się stanie** albo **co to znaczy**, a nie powtarza nazwy („**Odśwież**: pobiera dane od razu,
  bez czekania na automatyczne odświeżenie”, a nie „**Odśwież**: odświeża”).
- Warunek dostępności podajesz zawsze, gdy element zależy od uprawnienia, typu obiektu lub stanu.
- Ikonę bez napisu opisujesz kształtem i podpowiedzią („przycisk z lejkiem, podpowiedź **Filtr**”).
- Jednostki i formaty: z formaterów w kodzie (km, data i godzina, procent). Bez formatera: nie zgaduj.
