# Runbook

Fill in each row as the system is built. One row per alert.

| Symptom | First check | Fix | Owner |
|---|---|---|---|
| No new events for 20 min | Collector job execution history and logs (Log Analytics `ContainerAppConsoleLogs_CL`) | | DE1 |
| Events in the queue but not in `raw` | Loader job executions, active message count on the queue | | DE1 + DE2 |
| Messages in a dead-letter queue | Peek one in Service Bus Explorer, read `DeadLetterReason`, compare with `infra/schemas/` | | DE2 |
| TomTom / OpenWeather HTTP 429 or 403 | Daily quota used, key still valid in Key Vault | | DE1 |
| dbt test or source freshness failed | dbt job logs: failed test name and its compiled SQL | | DE2 |
| PostgreSQL CPU or storage high | Portal → Metrics, `pg_stat_statements` slowest queries, raw cleanup cron ran (`cron.job_run_details`) | | DE1 + DE2 |
| Budget alert | Cost Management → Cost analysis grouped by resource | | DE1 + DA2 |
