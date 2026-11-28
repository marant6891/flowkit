# PT: Reset hasła w portalu klienta (dane fikcyjne)

Wersja 1.0, 20.11.2026. Dokument testowy FlowKit, bez danych rzeczywistych.

## Wymagania funkcjonalne

| ID | Wymaganie |
|---|---|
| FR-001 | Użytkownik podaje adres e-mail na ekranie „Nie pamiętam hasła”, a system wysyła link do ustawienia nowego hasła. |
| FR-002 | Link jest jednorazowy i ważny 30 minut od wysłania. Po tym czasie system pokazuje komunikat „Link wygasł” i przycisk „Wyślij nowy link”. |
| FR-003 | Nowe hasło ma od 12 do 64 znaków i zawiera co najmniej jedną cyfrę. Przy błędzie system pokazuje komunikat „Hasło nie spełnia wymagań”. |
| FR-004 | Dla adresu, którego nie ma w systemie, ekran pokazuje ten sam komunikat co dla istniejącego konta: „Jeśli konto istnieje, wysłaliśmy link”. |

## User story

US-001: Jako klient portalu chcę ustawić nowe hasło, gdy zapomnę obecnego, aby znowu się zalogować.

- AC-001: Po kliknięciu ważnego linku i podaniu poprawnego hasła użytkownik loguje się nowym hasłem.
- AC-002: Ponowne użycie tego samego linku pokazuje komunikat „Link wygasł”.

## Ryzyka

- RISK-001: Ujawnienie, czy konto istnieje (enumeracja kont). Ogranicza je FR-004.
