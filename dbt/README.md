# dbt

SQL transformations in Azure Database for PostgreSQL, run every 15 minutes (+5 min after the
collector) by a Container Apps Job. Owner: **DE2** (models) + **DA1** (KPI definitions) · Due: silver **D5**, gold **D7**

| Path | Contents |
|---|---|
| `models/sources.yml` | `raw.traffic_events`, `raw.weather_events`, `ref.dim_segment`, `ref.dim_zone`, plus source freshness (< 20 min) |
| `models/silver/` | Dedupe on `event_id`, slot spine (explicit gaps), nearest zone (PostGIS `ST_Distance`), derived values only |
| `models/gold/` | `fact_traffic_15m`, KPIs, baselines, completeness |
| `tests/` | Singular tests (completeness ≥ 95%, speed range). Generic tests (`not_null`, `unique`) go in each model's `.yml` |
| `dbt_project.yml` `vars` | Shared constants: timezone, collection start, class thresholds |

Silver and gold keep **derived values only** (ratio, delay, TTI), never raw TomTom speeds.

## Run locally

```bash
pip install -r dbt/requirements.txt
cd dbt
# PG_HOST, PG_USER, PG_PASSWORD from .env; DBT_SCHEMA=dev_<yourname> so you never touch prod
dbt parse                      # no database needed: checks Jinja, refs and YAML
dbt build --profiles-dir .     # run models + tests against your dev schemas
dbt source freshness --profiles-dir .
```

In Azure the job runs `dbt source freshness && dbt build --target prod`.

## Postgres notes

- Timestamps are `timestamptz` and stored in UTC. Convert with `AT TIME ZONE '{{ var("local_tz") }}'` only in gold views or BI.
- Incremental models: `unique_key='event_id'` and filter on `slot_ts > (select max(slot_ts) from {{ this }}) - interval '1 hour'`.
- B1ms is 1 vCore and 2 GB RAM: index `(segment_id, slot_ts)` in silver and gold, and avoid full scans of raw.
