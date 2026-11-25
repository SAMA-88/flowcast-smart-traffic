-- Raw and reference tables in Azure Database for PostgreSQL (Flexible Server).
-- Columns match infra/schemas/*.schema.json plus Service Bus metadata added by the loader.
-- Apply once per database: psql "$PG_URL" -f infra/sql/001_raw_tables.sql
-- Extensions must be allow-listed first (Terraform: server parameter azure.extensions).

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_cron;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS ref;

CREATE TABLE IF NOT EXISTS raw.traffic_events (
  event_id              text        PRIMARY KEY,          -- loader: INSERT ... ON CONFLICT DO NOTHING
  segment_id            text        NOT NULL,
  slot_ts               timestamptz NOT NULL,
  current_speed         double precision,                 -- raw TomTom value: kept 24 h only
  free_flow_speed       double precision,                 -- raw TomTom value: kept 24 h only
  current_travel_time   integer,
  free_flow_travel_time integer,
  confidence            double precision,
  road_closure          boolean,
  frc                   text,
  source                text        NOT NULL,
  schema_version        integer     NOT NULL,
  collected_at          timestamptz NOT NULL,
  -- Service Bus metadata (set by the loader)
  message_id            text,
  enqueued_time         timestamptz NOT NULL DEFAULT now(),
  loaded_at             timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS traffic_events_slot_idx ON raw.traffic_events (slot_ts, segment_id);

CREATE TABLE IF NOT EXISTS raw.weather_events (
  event_id        text        PRIMARY KEY,
  zone_id         text        NOT NULL,
  slot_ts         timestamptz NOT NULL,
  temp_c          double precision,
  humidity        integer,
  wind_ms         double precision,
  rain_1h_mm      double precision,
  visibility_m    integer,
  condition_code  integer,
  source          text        NOT NULL,
  schema_version  integer     NOT NULL,
  collected_at    timestamptz NOT NULL,
  message_id      text,
  enqueued_time   timestamptz NOT NULL DEFAULT now(),
  loaded_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS weather_events_slot_idx ON raw.weather_events (slot_ts, zone_id);

CREATE TABLE IF NOT EXISTS ref.dim_segment (
  segment_id text PRIMARY KEY,
  name       text NOT NULL,
  city       text NOT NULL,
  area       text,
  geog       geography(Point, 4326) NOT NULL
);

CREATE TABLE IF NOT EXISTS ref.dim_zone (
  zone_id text PRIMARY KEY,
  name    text NOT NULL,
  city    text NOT NULL,
  geog    geography(Point, 4326) NOT NULL
);

-- TomTom terms: raw speeds are kept 24 h only. Runs every hour at :07.
SELECT cron.schedule(
  'expire-raw-tomtom',
  '7 * * * *',
  $$DELETE FROM raw.traffic_events WHERE slot_ts < now() - interval '24 hours'$$
);
