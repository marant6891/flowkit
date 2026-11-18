# Polskie nazwy statusów, priorytetów i wymagalności

Obowiązuje w każdej tabeli dokumentu PT/PRD i na diagramach. Angielskie wartości z materiałów
źródłowych tłumacz według tego słownika. Treść merytoryczna się nie zmienia, zmienia się tylko etykieta.

## Wymagalność (MoSCoW)

| Źródło | W dokumencie | Znaczenie |
|---|---|---|
| Must, Must have, Mandatory, Required | **Wymagane** | Bez tego zmiana nie może zostać odebrana |
| Should, Should have, Recommended | **Zalecane** | Ważne, ale istnieje obejście |
| Could, Could have, Nice to have, Optional | **Opcjonalne** | Realizowane, jeśli pozwolą na to czas i budżet |
| Won't, Won't have | **Wyłączone z zakresu** | Świadomie nierealizowane w tej zmianie |
| Out of scope | **Poza zakresem** | Element spoza zakresu zmiany |

Gdy źródło stosuje MoSCoW, nazwij kolumnę **Wymagalność**. Nie zamieniaj tych wartości na
Wysoki/Średni/Niski, bo to inna skala i zmieniłoby to sens źródła.

## Priorytet, wpływ i ważność

| Źródło | W dokumencie |
|---|---|
| Blocker | Blokujący |
| Critical | Krytyczny |
| High | Wysoki |
| Medium | Średni |
| Normal | Normalny |
| Low | Niski |
| Major | Poważny |
| Minor | Drobny |

## Status

| Źródło | Rodzaj męski (status, temat) | Rodzaj nijaki (wymaganie, zadanie) |
|---|---|---|
| New | Nowy | Nowe |
| Draft | Roboczy | Robocze |
| Proposed | Proponowany | Proponowane |
| Open | Otwarty | Otwarte |
| To Do | Do zrobienia | Do zrobienia |
| In Progress, WIP | W toku | W toku |
| In Review, Under Review | W weryfikacji | W weryfikacji |
| Pending | Oczekujący | Oczekujące |
| On Hold | Wstrzymany | Wstrzymane |
| Blocked | Zablokowany | Zablokowane |
| Approved, Accepted | Zaakceptowany | Zaakceptowane |
| Rejected | Odrzucony | Odrzucone |
| Resolved | Rozstrzygnięty | Rozstrzygnięte |
| Done, Completed | Zakończony | Zakończone |
| Closed | Zamknięty | Zamknięte |
| Cancelled | Anulowany | Anulowane |
| Deferred | Odłożony | Odłożone |

Formę dopasuj do rzeczownika w nagłówku tabeli.

## Wynik testu i wartości ogólne

| Źródło | W dokumencie |
|---|---|
| Pass, Passed | Zaliczony |
| Fail, Failed | Niezaliczony |
| Skipped | Pominięty |
| Yes / No | Tak / Nie |
| N/A | Nie dotyczy |
| TBD | DO POTWIERDZENIA (w parze z `OPEN-NNN`) |

## Nagłówki kolumn

| Źródło | W dokumencie |
|---|---|
| Priority | Priorytet |
| Requirement level | Wymagalność |
| Severity | Ważność |
| Impact | Wpływ |
| Probability | Prawdopodobieństwo |
| Owner | Właściciel |

## Czego nie tłumaczyć

- Identyfikatorów (`FR-001`, `OPEN-001`), nazw własnych systemów, produktów i ról z materiałów klienta.
- Nazw z kodu, API i konfiguracji, na przykład wartości pola `status: "IN_PROGRESS"` opisanej jako dane.
- Wartości narzuconych przez szablon klienta. Szablon ma pierwszeństwo: zachowaj je i zgłoś to użytkownikowi pod dokumentem.

## Kontrola

```bash
python "<SKILL_DIR>/scripts/check_status_labels.py" dokument.docx
```

Skrypt sprawdza całe komórki tabel w plikach `.md` i `.docx` i podaje polski odpowiednik.
