"""Collector entry point (Cloud Run job). Run: python -m collector.main

Owner: DE1 + DE2 · Due: D1

What one run does (one 15-minute slot):
  1. Compute the slot: nearest 15-minute boundary in UTC.
  2. Call TomTom Traffic Flow for every segment in config/segments.yml.
  3. Call OpenWeather (Current Weather 2.5, no card needed) for every zone in config/zones.yml.
  4. Publish one JSON event per segment / zone to Pub/Sub.

Rules (see docs/architecture.png):
  - event_id = <segment_or_zone_id>_<slot_ts>, e.g. "S06_2026-11-29T14:15:00Z"
  - Event fields must match infra/schemas/raw_*_events.json
  - API keys come from environment variables (Secret Manager), never from code
  - Never log a URL: the API key is in the query string
  - One failed location = log it and continue (it becomes a gap downstream)
"""


def main() -> int:
    # TODO(DE1/DE2): implement the steps above.
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
