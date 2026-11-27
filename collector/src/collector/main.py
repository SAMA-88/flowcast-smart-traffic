"""Collector entry point (Azure Container Apps Job). Run: python -m collector.main

Owner: DE1 + DE2 · Due: D1

What one run does (one 15-minute slot):
  1. Compute the slot: nearest 15-minute boundary in UTC.
  2. Call TomTom Traffic Flow for every segment in config/segments.yml.
  3. Call OpenWeather (Current Weather 2.5, no card needed) for every zone in config/zones.yml.
  4. Validate each event against infra/schemas/*.schema.json.
  5. Send one JSON message per segment / zone to the Service Bus queues
     traffic-events and weather-events (set message_id = event_id).

Rules (see docs/architecture.png):
  - event_id = <segment_or_zone_id>_<slot_ts>, e.g. "S06_2026-11-29T14:15:00Z"
  - Event fields must match infra/schemas/*.schema.json
  - API keys come from environment variables (Key Vault secret references), never from code
  - Service Bus auth: DefaultAzureCredential (managed identity in Azure, `az login` locally),
    namespace from SERVICEBUS_NAMESPACE. No connection strings.
  - SINK=file writes JSON lines to scripts/out/events/ instead (local run, backfill)
  - Never log a URL: the API key is in the query string
  - One failed location = log it and continue (it becomes a gap downstream)
"""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import requests
import yaml

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s %(message)s")
log = logging.getLogger("collector")

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", REPO_ROOT / "config"))
SCHEMA_DIR = Path(os.environ.get("SCHEMA_DIR", REPO_ROOT / "infra" / "schemas"))
OUT_DIR = Path(os.environ.get("OUT_DIR", REPO_ROOT / "scripts" / "out" / "events"))

TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT_S = 10
SCHEMA_VERSION = 1

TRAFFIC_QUEUE = "traffic-events"
WEATHER_QUEUE = "weather-events"
SERVICEBUS_SUFFIX = ".servicebus.windows.net"



def compute_slot(now: datetime | None = None) -> datetime:
    """Round a timestamp down to its 15-minute boundary (UTC)."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    return now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)

def format_slot(slot: datetime) -> str:
    """Format a datetime as ISO-8601 UTC with a trailing Z."""
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ")

def make_event_id(location_id: str, slot: datetime) -> str:
    """Build a deterministic event_id, e.g. 'S06_2026-11-25T14:15:00Z'."""
    return f"{location_id}_{format_slot(slot)}"

def load_locations(filename: str, key: str) -> list[dict]:
    """Load a list of locations (segments or zones) from a YAML file."""
    data = yaml.safe_load((CONFIG_DIR / filename).read_text(encoding="utf-8"))
    return data[key]

def load_schema(name: str) -> dict:
    """Load a JSON Schema file from infra/schemas."""
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))

def fetch_traffic(segment: dict, slot: datetime, api_key: str) -> dict:
    """Call TomTom Traffic Flow for one segment and build a traffic event."""
    resp = requests.get(
        TOMTOM_URL,
        params={"point": f"{segment['lat']},{segment['lon']}", "unit": "KMPH", "key": api_key},
        timeout=TIMEOUT_S,
    )
    resp.raise_for_status()
    flow = resp.json()["flowSegmentData"]
    return {
        "event_id": make_event_id(segment["id"], slot),
        "segment_id": segment["id"],
        "slot_ts": format_slot(slot),
        "current_speed": flow.get("currentSpeed"),
        "free_flow_speed": flow.get("freeFlowSpeed"),
        "current_travel_time": flow.get("currentTravelTime"),
        "free_flow_travel_time": flow.get("freeFlowTravelTime"),
        "confidence": flow.get("confidence"),
        "road_closure": flow.get("roadClosure"),
        "frc": flow.get("frc"),
        "source": "tomtom",
        "schema_version": SCHEMA_VERSION,
        "collected_at": format_slot(datetime.now(UTC)),
    }


def fetch_weather(zone: dict, slot: datetime, api_key: str) -> dict:
    """Call OpenWeather Current Weather for one zone and build a weather event."""
    resp = requests.get(
        OPENWEATHER_URL,
        params={"lat": zone["lat"], "lon": zone["lon"], "units": "metric", "appid": api_key},
        timeout=TIMEOUT_S,
    )
    resp.raise_for_status()
    data = resp.json()
    main = data.get("main", {})
    return {
        "event_id": make_event_id(zone["id"], slot),
        "zone_id": zone["id"],
        "slot_ts": format_slot(slot),
        "temp_c": main.get("temp"),
        "humidity": main.get("humidity"),
        "wind_ms": data.get("wind", {}).get("speed"),
        "rain_1h_mm": data.get("rain", {}).get("1h", 0), 
        "visibility_m": data.get("visibility"),
        "condition_code": (data.get("weather") or [{}])[0].get("id"),
        "source": "openweather",
        "schema_version": SCHEMA_VERSION,
        "collected_at": format_slot(datetime.now(UTC)),
    }

def write_to_file(queue: str, events: list[dict]) -> None:
    """Append events as JSON lines to scripts/out/events/<queue>.jsonl."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / f"{queue}.jsonl").open("a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

def full_namespace(name: str) -> str:
    """Return the fully qualified Service Bus namespace.

    Accepts 'sb-flowcast' or 'sb-flowcast.servicebus.windows.net'.
    """
    name = name.strip()
    return name if "." in name else name + SERVICEBUS_SUFFIX


def send_to_service_bus(queue: str, events: list[dict]) -> None:
    """Send one message per event, with message_id = event_id."""
    # Imported here so SINK=file works without Azure credentials.
    from azure.identity import DefaultAzureCredential
    from azure.servicebus import ServiceBusClient, ServiceBusMessage

    namespace = full_namespace(os.environ["SERVICEBUS_NAMESPACE"])
    with (
        ServiceBusClient(namespace, DefaultAzureCredential()) as client,
        client.get_queue_sender(queue) as sender,
    ):
        sender.send_messages(
            [
                ServiceBusMessage(
                    json.dumps(e), message_id=e["event_id"], content_type="application/json"
                )
                for e in events
            ]
        )


def send(queue: str, events: list[dict], sink: str) -> None:
    """Send events to the chosen sink ('file' or Service Bus)."""
    if not events:
        return
    if sink == "file":
        write_to_file(queue, events)
    else:
        send_to_service_bus(queue, events)
    log.info("Sent %d events to %s (sink=%s)", len(events), queue, sink)

def collect(locations, fetch, schema, slot, api_key, label) -> list[dict]:
    """Fetch and validate every location. A failed location is logged and skipped."""
    events = []
    for loc in locations:
        try:
            event = fetch(loc, slot, api_key)
            jsonschema.validate(event, schema)
            events.append(event)
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            log.error(
                "%s %s: request failed (%s, status=%s)",
                label, loc["id"], type(exc).__name__, status,
            )
        except (KeyError, ValueError, jsonschema.ValidationError) as exc:
            log.error("%s %s: bad data (%s)", label, loc["id"], type(exc).__name__)
    return events

def main() -> int:
    sink = os.environ.get("SINK", "servicebus").strip().lower()
    if sink not in ("file", "servicebus"):
        log.error("SINK must be 'file' or 'servicebus'")
        return 1
    tomtom_key = os.environ.get("TOMTOM_API_KEY")
    weather_key = os.environ.get("OPENWEATHER_API_KEY")
    if not tomtom_key or not weather_key:
        log.error("TOMTOM_API_KEY and OPENWEATHER_API_KEY must be set")
        return 1

    slot = compute_slot()
    log.info("Starting run: slot=%s sink=%s", format_slot(slot), sink)

    segments = load_locations("segments.yml", "segments")
    zones = load_locations("zones.yml", "zones")

    traffic = collect(segments, fetch_traffic, load_schema("traffic_event.schema.json"),
                      slot, tomtom_key, "segment")
    weather = collect(zones, fetch_weather, load_schema("weather_event.schema.json"),
                      slot, weather_key, "zone")

    ok = True
    for queue, events in ((TRAFFIC_QUEUE, traffic), (WEATHER_QUEUE, weather)):
        try:
            send(queue, events, sink)
        except Exception as exc:
            log.error("send to %s failed (%s)", queue, type(exc).__name__)
            ok = False

    log.info("Done: %d/%d traffic, %d/%d weather", 
             len(traffic), len(segments), len(weather), len(zones))
    return 0 if (ok and (traffic or weather)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
