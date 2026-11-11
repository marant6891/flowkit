# Przykład: Od surowych logów do osi czasu raportu postmortem

## Materiał źródłowy

### Fragment logów z Kubernetes (Pod `api-gateway`)

```text
2026-11-10T14:28:01Z WARN  [api-gateway] upstream connect error: connection reset by peer (db-primary:5432)
2026-11-10T14:28:03Z ERROR [api-gateway] database pool exhausted (max=50), rejecting request /api/orders
2026-11-10T14:28:03Z ERROR [api-gateway] HTTP 503 returned to client
...
2026-11-10T14:35:14Z INFO  [db-primary] pg_hba.conf reloaded after config change
2026-11-10T14:35:16Z INFO  [api-gateway] upstream connection restored: db-primary:5432
```

### Alert z Datadog (email do PagerDuty)

```text
Alert: api-gateway.error_rate > 10% [TRIGGERED at 14:29:05 UTC]
Metric: http.requests.error (503) = 94.3%
Service: api-gateway | Env: production
```

### Notatka z kanału Slack #incidents

```text
14:31 @on-call: Starting investigation. DB connection errors in api-gateway logs.
14:34 @dba: Found unauthorized pg_hba.conf change deployed at 14:27. Rolling back.
14:36 @on-call: Connections restored. Monitoring for 5 min.
14:41 @on-call: Metrics back to normal. Incident resolved.
```

---

## Wynik — prawidłowe wpisy w osi czasu

| Czas | Opis zdarzenia | Źródło |
|---|---|---|
| **14:27 UTC** | Wdrożono nieautoryzowaną zmianę `pg_hba.conf` na `db-primary` | Notatka ze Slack #incidents, wpis DBA 14:34 |
| **14:28:01 UTC** | Pierwsze błędy połączenia `api-gateway → db-primary:5432` | Log Pod api-gateway |
| **14:28:03 UTC** | Wyczerpanie puli połączeń (max=50); serwis zaczął zwracać HTTP 503 | Log Pod api-gateway |
| **14:29:05 UTC** | Alert Datadog: `error_rate > 10%` wyzwolił PagerDuty | Alert Datadog #alert-prod-01 |
| **14:31 UTC** | Inżynier dyżurny rozpoczął diagnostykę | Slack #incidents |
| **14:34 UTC** | DBA zidentyfikował nieautoryzowaną zmianę konfiguracji; inicjacja rollbacku | Slack #incidents |
| **14:35:14 UTC** | Rollback `pg_hba.conf` zakończony; PostgreSQL przeładował konfigurację | Log db-primary |
| **14:35:16 UTC** | `api-gateway` przywrócił połączenia z bazą danych | Log Pod api-gateway |
| **14:41 UTC** | Metryki produkcyjne wróciły do normy; incydent zamknięty | Slack #incidents |

**TTD (T0 → T1):** 14:27 → 14:29:05 = **~2 min 05 s** (automatyczny alert)  
**TTR (T1 → T4):** 14:29:05 → 14:41 = **~12 min** (rollback konfiguracji)

---

## Przykład nieprawidłowego wpisu (do unikania)

```
ŹLE:
| ~14:30 | Coś się zepsuło w bazie | Wiedzieliśmy |
```

```
DOBRZE:
| 14:28:03 UTC | Wyczerpanie puli połączeń db-primary; serwis zwraca HTTP 503 | Log Pod api-gateway |
```

