# dataform

SQL transformations in BigQuery, run every 15 minutes (+5 min after the collector).
Owner: **DE2** (models) + **DA1** (KPI definitions) · Due: silver **D5**, gold **D7**

| Folder | Contents |
|---|---|
| `definitions/sources/` | Declarations for `raw.traffic_events`, `raw.weather_events`, `ref.dim_segment`, `ref.dim_zone` |
| `definitions/silver/` | Dedupe on `event_id`, slot spine (explicit gaps), nearest zone, derived values only |
| `definitions/gold/` | `fact_traffic_15m`, KPIs, baselines, completeness |
| `definitions/assertions/` | Freshness < 20 min and other checks |
| `includes/constants.js` | Shared constants (timezone, class thresholds) |

Silver and gold keep **derived values only** (ratio, delay, TTI), never raw TomTom speeds.

Compile locally: `npx @dataform/cli@3.0.0 compile` (from this folder).
