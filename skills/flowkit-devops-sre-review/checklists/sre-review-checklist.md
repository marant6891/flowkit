# Checklista przeglądu SRE

## SLI/SLO i error budget
- [ ] SLI mierzy doświadczenie użytkownika (np. odsetek udanych żądań, latencja p95/p99 na wejściu usługi).
- [ ] SLO ma wartość, okno czasowe i właściciela; brak SLO = `UNKNOWN`/`FAIL`, nie wymyślona wartość.
- [ ] Jest polityka error budget (co się dzieje po jego wyczerpaniu).

## Alerty
- [ ] Alerty na objawy (burn rate SLO, błędy, latencja), nie wyłącznie na przyczyny (CPU, pamięć).
- [ ] Każdy alert wymaga działania człowieka i ma runbook; alerty informacyjne nie budzą dyżurnego.
- [ ] Brak dublowania alertów i progów bez okna (`for:`), które powodują alert fatigue.

## Metryki
- [ ] Usługa udostępnia RED: liczba żądań, błędy, czas odpowiedzi.
- [ ] Zasoby (bazy, kolejki, węzły) mają USE: wykorzystanie, nasycenie, błędy.

## Sondy
- [ ] readiness i liveness są rozdzielone; liveness nie zależy od zewnętrznych usług.
- [ ] `initialDelaySeconds`/`startupProbe` pasują do czasu startu; progi nie powodują restartów przy chwilowym obciążeniu.

## Zasoby, skalowanie i awaria
- [ ] requests i limits dla CPU i pamięci; limit pamięci uzasadniony zużyciem (ryzyko OOMKill).
- [ ] HPA ma sensowną metrykę i min/max; PDB chroni dostępność przy aktualizacji węzłów.
- [ ] Więcej niż jedna replika dla usług krytycznych, rozkład między strefy, graceful shutdown (`terminationGracePeriodSeconds`, preStop).

## Dane
- [ ] Backup ma harmonogram i retencję; jest dowód testu odtworzenia (bez niego najwyżej `UNKNOWN`).
- [ ] RPO/RTO są zdefiniowane i zgodne z konfiguracją backupu.

## Koszt
- [ ] requests nie są wielokrotnie wyższe od zużycia; repliki i limity są uzasadnione obciążeniem.

## Przed oddaniem
- [ ] Każde ustalenie ma dowód (`plik:linia`, alert, opis) albo status `UNKNOWN`.
- [ ] Interpretacje są oddzielone od faktów; nic nie wywnioskowano z samych nazw zasobów.
- [ ] Każda rekomendacja monitoringu ma sygnał, próg (oznaczony jako propozycja, gdy nie ze źródła), okno i uzasadnienie.
- [ ] Sprawdzenia wymagające działającego środowiska są oznaczone `NOT_RUN`, a nie `PASS`.
- [ ] Raport obejmuje tylko obszary z materiałami; sekrety zastąpiono `[UKRYTO]`.

## Prosty język (`<runtime>/procedures/plain-language.md`)
- [ ] Najważniejsze na początku: ustalenia od najpoważniejszego.
- [ ] Zdania do 20 słów (EN: 25); czasowniki zamiast rzeczowników („wdrożyć”, nie „dokonać wdrożenia”).
- [ ] Bez korpomowy i kalk („zaparkować”, „zaadresować”, „na ten moment”, „To, co…, to…”, „To drugi raz, gdy…”); w EN bez fałszywych przyjaciół (*actual*, *eventually*).
- [ ] Szyk naturalny: to, co znane, na początku zdania, a nowe na końcu; strona czynna, gdy wiadomo, kto działa.
- [ ] Skróty rozwinięte przy pierwszym użyciu, chyba że są w słowniku projektu.
- [ ] `plain-check` nie zgłasza błędów; ostrzeżenia poprawione albo uzasadnione.
