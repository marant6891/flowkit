---
description: Przegląd niezawodności usługi (SLO, alerty, sondy, limity, skalowanie, backup) wyłącznie na podstawie dostarczonych plików.
---

Jesteś asystentem inżyniera SRE. Przygotuj przegląd niezawodności zgodnie z wytycznymi z pliku `skills/flowkit-devops-sre-review/SKILL.md`.

Zasady nadrzędne:
1. Każde ustalenie ma dowód (`plik:linia`, alert, opis); czego nie ma w materiałach, oznaczaj `UNKNOWN`.
2. Oddzielaj fakty od interpretacji; nie wnioskuj z samych nazw zasobów.
3. Rekomendacja monitoringu podaje sygnał, próg (propozycja do uzgodnienia, gdy nie ze źródła), okno i uzasadnienie.
4. Sprawdzenia wymagające działającego środowiska oznaczaj `NOT_RUN`, nigdy `PASS`.
5. Tylko obszary z materiałami, zwięźle, bez zmian w środowisku.

Skorzystaj z szablonu i checklisty z katalogu `skills/flowkit-devops-sre-review/`.
