"""Data contract: event schemas are valid and accept the documented example events."""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMAS = Path(__file__).resolve().parents[2] / "infra" / "schemas"

TRAFFIC = {
    "event_id": "S06_2026-11-25T14:15:00Z",
    "segment_id": "S06",
    "slot_ts": "2026-11-25T14:15:00Z",
    "current_speed": 14,
    "free_flow_speed": 37,
    "confidence": 0.92,
    "road_closure": False,
    "source": "tomtom",
    "schema_version": 1,
    "collected_at": "2026-11-25T14:15:07Z",
}

WEATHER = {
    "event_id": "Z2_2026-11-25T14:15:00Z",
    "zone_id": "Z2",
    "slot_ts": "2026-11-25T14:15:00Z",
    "temp_c": 21.5,
    "rain_1h_mm": 0,
    "source": "openweather",
    "schema_version": 1,
    "collected_at": "2026-11-25T14:15:09Z",
}


def _schema(name: str) -> dict:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


@pytest.mark.parametrize(
    ("name", "event"),
    [("traffic_event.schema.json", TRAFFIC), ("weather_event.schema.json", WEATHER)],
)
def test_example_event_is_valid(name, event):
    jsonschema.validate(event, _schema(name))


def test_unknown_field_is_rejected():
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**TRAFFIC, "api_key": "x"}, _schema("traffic_event.schema.json"))


def test_slot_must_be_on_a_quarter_hour():
    bad = {**TRAFFIC, "event_id": "S06_2026-11-25T14:20:00Z"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, _schema("traffic_event.schema.json"))
