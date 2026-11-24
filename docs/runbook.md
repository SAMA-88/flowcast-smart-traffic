# Runbook

Fill in each row as the system is built. One row per alert.

| Symptom | First check | Fix | Owner |
|---|---|---|---|
| No new events for 20 min | Cloud Run job executions and logs, Scheduler history | | DE1 |
| Messages in the dead-letter topic | Read one message, compare with `infra/schemas/` | | DE2 |
| TomTom / OpenWeather HTTP 429 or 403 | Daily quota used, key still valid | | DE1 |
| Dataform assertion failed | Failed assertion name and its query | | DE2 |
| Budget alert | `INFORMATION_SCHEMA.JOBS`: biggest queries | | DE1 + DA2 |
