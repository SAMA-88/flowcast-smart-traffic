# scripts

One-off helpers, run from a laptop.

| Script | Purpose | Owner | When |
|---|---|---|---|
| `probe_segments.py` | Call TomTom for each point in `config/segments.yml` and export the returned roads as GeoJSON, to check them on geojson.io | DA1 | D1 morning |
| `load_reference.py` | Load `config/*.yml` into `ref.dim_segment` and `ref.dim_zone` (PostGIS `geography(Point, 4326)`) | DE2 | D1-D2, and after any config change |
| `backfill_events.py` | Send JSON lines collected locally (`SINK=file`) to the Service Bus queues once | DE1 | When the subscription is ready |

Output files go to `scripts/out/` (ignored by git).
