# Szablon zapasowy: dokumentacja rozwiązania (instrukcja administratora, dokumentacja techniczna)

Używaj tylko, gdy użytkownik nie dał szablonu Word. Kolumna „Profil” mówi, dla którego dokumentu rozdział jest
przeznaczony: **A** = instrukcja administratora, **T** = dokumentacja techniczna. Rozdziały, które nie dotyczą
rozwiązania lub nie mają źródła, pomijasz albo (tryb roboczy) oznaczasz „Brak danych - patrz OPEN-NNN”.

| Rozdział | Profil | Treść |
|---|---|---|
| 1. Wprowadzenie | A, T | Cel biznesowy i przeznaczenie rozwiązania, granice systemu (co wchodzi, co jest zewnętrzne), role systemów, odbiorca i wersja kodu (gałąź, tag, commit) |
| 2. Przegląd rozwiązania | A, T | Główne moduły i ich odpowiedzialności, zależności zewnętrzne; diagram komponentów, gdy są co najmniej 3 elementy |
| 3. Wymagania | A, T | Środowisko uruchomieniowe, bazy, usługi zewnętrzne, tylko z plików projektu |
| 4. Instalacja i wdrożenie | A, T | Kroki z `README`, skryptów, manifestów; kolejność, polecenia, sprawdzenie poprawności |
| 5. Konfiguracja | A, T | Tabela ustawień: klucz, znaczenie, typ/dozwolone wartości, wartość domyślna, skutek zmiany; bez sekretów |
| 6. Użytkownicy, role i uprawnienia | A | Role, co każda może, jak nadać rolę |
| 7. Zadania cykliczne i integracje | A, T | Przepływy end-to-end (krok po kroku, korelacja, ponowienia, callbacki), harmonogram zadań, mapowanie komunikatów, gdzie widać wynik i błędy |
| 8. Monitorowanie, logi i kopie zapasowe | A | Gdzie są logi, pola korelacji, poziomy, co obserwować; kopie tylko ze źródeł |
| 9. Rozwiązywanie problemów | A | Komunikat lub objaw, przyczyna w kodzie, co zrobić |
| 10. Architektura i moduły | T | Struktura katalogów, warstwy, główne klasy/serwisy i ich rola, przepływ żądania, miejsca w kodzie |
| 11. API | T | Kontrakty: metoda, ścieżka, nagłówki, parametry, przykłady payloadu (JSON/XML), odpowiedzi i kody błędów, uprawnienia; odesłanie do OpenAPI, gdy jest |
| 12. Model danych | T | Encje/tabele z migracji, kluczowe pola, relacje, maszyna stanów; diagram ER od 3 encji i diagram stanów od 3 stanów |
| 13. Budowanie, testy i rozwój | T | Polecenia budowania i testów z plików projektu, konwencje |
| 14. Słownik pojęć | A, T | Gdy są co najmniej 3 pojęcia lub skróty |
| 15. Tematy do wyjaśnienia / Kwestie do wyjaśnienia | A, T | Tryb roboczy i dla klienta |

---

# [Nazwa rozwiązania]: [instrukcja administratora | dokumentacja techniczna]

| Wersja rozwiązania | Wersja dokumentu | Data | Odbiorca |
|---|---|---|---|
| [tag lub commit] | 1.0 | [DD.MM.RRRR] | [rola] |

## 1. Wprowadzenie

## 2. Przegląd rozwiązania

(kolejne rozdziały według tabeli powyżej)
