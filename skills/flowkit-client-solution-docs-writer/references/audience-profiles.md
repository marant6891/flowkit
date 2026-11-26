# Profile odbiorcy

Profil wybiera odpowiedź na Q-002. Decyduje o słownictwie, poziomie szczegółu i tym, co wolno pokazać.
Kontrola `check_user_docs.py --audience` sprawdza granice profilu.

| Profil | Odbiorca | Cel dokumentu | Pisz | Nie pisz | `--audience` |
|---|---|---|---|---|---|
| **Podstawowy** | Użytkownik biznesowy, bez wiedzy technicznej | Wykonać codzienne zadania w aplikacji | Zadania krok po kroku, nazwy z interfejsu, skutki działań („Zwrot trafia do akceptacji”), komunikaty i co z nimi zrobić | Nazwy klas, plików, endpointów, tabel, kodów HTTP, wyjątków, ustawień serwera; żargon („request”, „payload”, „cache”) | `user` |
| **Zaawansowany** | Użytkownik kluczowy (key user), koordynator procesu | Zadania, wyjątki i reguły biznesowe, wsparcie innych użytkowników | Jak podstawowy oraz reguły (np. limity, statusy i przejścia między nimi), uprawnienia ról, importy i eksporty | Jak podstawowy | `user` |
| **Administrator** | Dział IT klienta, administrator aplikacji | Zainstalować, skonfigurować, utrzymać | Wymagania, instalacja, ustawienia (nazwa, znaczenie, wartość domyślna, skutek zmiany), role i uprawnienia, zadania cykliczne, logi, kopie, typowe problemy | Wartości sekretów, wewnętrzne adresy dostawcy, szczegóły implementacji bez wpływu na administrację | `admin` |
| **Techniczny** | Zespół developerski klienta, architekt | Zrozumieć budowę, integrować, rozwijać | Architektura, moduły i ich odpowiedzialności, API (kontrakty), model danych, konfiguracja, budowanie i wdrożenie, miejsca w kodzie | Sekretów i danych osobowych; ocen łatwości („proste”, „wystarczy”) | `tech` |

## Język i forma

- Forma zwracania się: zgodnie z szablonem i odpowiedzią na Q-008, jednolicie w całym dokumencie.
- Profil podstawowy: zdania do ok. 20 słów, strona czynna, jedno pojęcie domenowe objaśnione przy pierwszym
  użyciu. Liczby i limity zawsze z jednostką.
- Słownik pojęć dodaj, gdy dokument używa co najmniej 3 pojęć domenowych lub skrótów.
- Terminologię bierz z interfejsu aplikacji (pliki tłumaczeń), a nie z nazw w kodzie. Gdy w interfejsie
  i w materiałach klienta ten sam element ma różne nazwy, użyj nazwy z interfejsu i zgłoś rozbieżność jako `OPEN`.
