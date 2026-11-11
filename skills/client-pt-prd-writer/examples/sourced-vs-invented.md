# Przykłady: treść ze źródła vs treść zmyślona

Materiał źródłowy (SRC-001, ticket): „Klient chce, żeby w formularzu zamówienia
można było dodać numer PO. Pole ma być widoczne na fakturze PDF.”

## Wymaganie funkcjonalne

ŹLE (zmyślone szczegóły):
| FR-001 | Pole „Numer PO” (wymagane, max 35 znaków, alfanumeryczne) w formularzu zamówienia, walidowane w czasie rzeczywistym | Wysoki | … |

DOBRZE:
| FR-001 | Dodanie pola „Numer PO” w formularzu zamówienia | DO POTWIERDZENIA | Pole jest dostępne w formularzu i zapisywane z zamówieniem | US-001 | SRC-001 | Proponowane |
| FR-002 | Wyświetlanie numeru PO na fakturze PDF | DO POTWIERDZENIA | Numer PO zapisany w zamówieniu jest widoczny na fakturze PDF | US-001 | SRC-001 | Proponowane |

+ OPEN-001: Czy pole jest obowiązkowe? OPEN-002: Format i długość numeru PO? OPEN-003: Priorytet zmiany?

## Wymagania niefunkcjonalne

ŹLE: „NFR-001 Wydajność: formularz ładuje się w < 2 s dla 95% żądań.” (brak w źródle)

DOBRZE: „Nie dotyczy – materiały nie definiują wymagań niefunkcjonalnych dla tej
zmiany; zmiana nie wpływa na wydajność w sposób wymagający osobnych kryteriów.”
lub, jeśli to istotne: „Brak danych – patrz OPEN-004.”

## Analiza wpływu (brak dostępu do kodu)

ŹLE: „Zmiana obejmuje `OrderController`, tabelę `Orders` (nowa kolumna `PoNumber`) i serwis `InvoicePdfGenerator`.”

DOBRZE: „Nie analizowano – brak dostępu do repozytorium. Na podstawie SRC-001
zmiana dotyczy obszarów: formularz zamówienia, zapis zamówienia, szablon faktury
PDF. Szczegółowe komponenty – OPEN-005.”

## Ryzyka

ŹLE: „RISK-001 Integracja z ERP może odrzucać nowe pole” (ERP nie występuje w żadnym źródle).

DOBRZE: ryzyka tylko zidentyfikowane w materiałach lub analizie, np.
„RISK-001 Faktury wystawione przed wdrożeniem nie będą miały numeru PO –
Źródło: analiza zakresu (SRC-001 nie przewiduje korekty historycznych faktur) – OPEN-006.”

Jeśli autor widzi potencjalny problem spoza źródeł (np. ERP) – zapisuje go jako
`REC-001` w sekcji „Rekomendacje” lub jako pytanie, nie jako fakt.
