# Mapa: gdzie w kodzie szukać treści dokumentacji

Czytaj tylko zakres wskazany w Q-003 i Q-005. Każde ustalenie zapisz w katalogu funkcji ze źródłem `plik:linia`.

| Potrzebuję do dokumentu | Gdzie szukać (przykłady wzorców) | Uwagi |
|---|---|---|
| Lista ekranów i ścieżki menu | routing: `routes`, `Route path=`, `@app.route`, `[Route(`, `urls.py`, `@GetMapping`; menu i nawigacja: `menu`, `nav`, `sidebar` | Ekran bez trasy lub pozycji menu nie jest dostępny dla użytkownika |
| Nazwy przycisków, pól, komunikaty | pliki tłumaczeń: `i18n/`, `locales/*.json`, `*.resx`, `messages*.properties`, `*.po`; teksty w komponentach | Cytuj w języku dokumentu; klucz tłumaczenia to tylko źródło, nie treść |
| Pola formularza i walidacje | schematy formularzy, `required`, `maxLength`, `pattern`, `min`/`max`, adnotacje `[Required]`, `@NotNull`, `@Size`, walidatory (`zod`, `yup`, `FluentValidation`, `pydantic`) | Sprawdź walidację po stronie serwera; jeśli różni się od klienta, opisz ostrzejszą i zgłoś rozbieżność jako `OPEN` |
| Uprawnienia i role | `[Authorize(Roles=`, `@PreAuthorize`, `hasRole`, `permission`, `can(`, `guard`, `policy`, ukrywanie elementów (`v-if`, `*ngIf`, warunki w JSX) | Help dla roli opisuje tylko to, co ta rola widzi i może wykonać |
| Statusy i przejścia | `enum Status`, maszyny stanów, `switch` po statusie, przyciski aktywne zależnie od statusu | Dobra kandydatka na tabelę „Status → co oznacza → co możesz zrobić” |
| Skutki akcji | obsługa przycisku → wywołanie usługi → zapis, powiadomienia (`send_mail`, `notify`), zmiana statusu | Opisz skutek widoczny dla odbiorcy, nie mechanizm |
| Komunikaty błędów | wyjątki mapowane na komunikaty, `toast`, `alert`, `ValidationError`, kody błędów w tłumaczeniach | Rozwiązywanie problemów: komunikat → przyczyna z kodu → co zrobić |
| Flagi funkcji | `feature`, `flag`, `toggle`, `isEnabled`, konfiguracja modułów | Funkcja zależna od flagi: opisz tylko, gdy flaga jest włączona w konfiguracji, którą dostaje klient, albo oznacz `OPEN` |
| Ustawienia (admin) | `appsettings*.json`, `.env.example`, `application*.yml`, `config/`, zmienne `os.environ`, `IConfiguration` | Nazwa, znaczenie, wartość domyślna, skutek; nigdy wartości sekretów z prawdziwych plików |
| Zadania cykliczne, integracje | `cron`, `schedule`, `HostedService`, `@Scheduled`, kolejki, klienci HTTP | Admin: kiedy działa, co robi, gdzie widać wynik lub błąd |
| Instalacja i wymagania | `README`, `Dockerfile`, `docker-compose`, manifesty, `package.json` (engines), `*.csproj` (TargetFramework), skrypty migracji | Wymagania tylko z plików, bez „typowych” wartości |
| API i model danych (tech) | kontrolery, specyfikacje OpenAPI, modele ORM, migracje | Kontrakt: metoda, ścieżka, parametry, odpowiedzi, uprawnienia |

## Czego nie wnioskować z kodu

- Zachowania z samej nazwy (`ExportService` nie dowodzi, że eksport jest dostępny w interfejsie).
- Wartości z danych testowych, seedów i fixture'ów jako wartości produkcyjnych.
- Dostępności funkcji z istnienia kodu, gdy nie ma trasy, pozycji menu lub uprawnienia.
- Kolejności kroków z kolejności pól w kodzie, gdy układ ustala CSS lub konfiguracja; w razie wątpliwości `OPEN`
  albo prośba o zrzut ekranu.
