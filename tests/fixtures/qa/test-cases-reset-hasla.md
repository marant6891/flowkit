# Przypadki testowe: reset hasła (dane fikcyjne, z celowymi lukami do przeglądu TEST-AUDIT)

Wymagania: `tests/fixtures/qa/pt-reset-hasla.md`.

| ID | Wymaganie | Warunki wstępne | Dane | Kroki | Oczekiwany wynik |
|---|---|---|---|---|---|
| TEST-001 | FR-001 | Konto anna.test@example.com istnieje | anna.test@example.com | 1. Otwórz „Nie pamiętam hasła”. 2. Wpisz adres. 3. Kliknij „Wyślij”. | E-mail z linkiem trafia do skrzynki, ekran pokazuje „Jeśli konto istnieje, wysłaliśmy link” |
| TEST-002 | FR-002 | Link wysłany | link z TEST-001 | 1. Kliknij link. 2. Ustaw nowe hasło. | Reset działa poprawnie |
| TEST-003 | US-001/AC-001 | Ważny link | Haslo2026bezpieczne | 1. Kliknij link. 2. Wpisz hasło. 3. Zaloguj się nowym hasłem. | Logowanie nowym hasłem kończy się sukcesem |
| TEST-004 | FR-009 | Użytkownik zalogowany | brak | 1. Otwórz profil. 2. Zmień numer telefonu. | Numer zapisany |
