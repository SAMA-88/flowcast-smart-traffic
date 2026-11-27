"""Tests for the collector: slot, event_id, event shape, and the file sink (no real API calls)."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from collector import main as m


def utc(*args):
    return datetime(*args, tzinfo=UTC)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_slot_rounds_down():
    assert m.compute_slot(utc(2026, 11, 26, 10, 29, 59)) == utc(2026, 11, 26, 10, 15)


def test_slot_on_boundary_is_unchanged():
    assert m.compute_slot(utc(2026, 11, 26, 10, 30)) == utc(2026, 11, 26, 10, 30)


def test_slot_start_of_hour():
    assert m.compute_slot(utc(2026, 11, 26, 10, 14, 59)) == utc(2026, 11, 26, 10, 0)


def test_slot_has_no_seconds():
    slot = m.compute_slot(utc(2026, 11, 26, 10, 7, 33, 123456))
    assert slot.second == 0 and slot.microsecond == 0


def test_format_slot():
    assert m.format_slot(utc(2026, 11, 25, 14, 15)) == "2026-11-25T14:15:00Z"


def test_event_id_matches_repo_format():
    assert m.make_event_id("S06", utc(2026, 11, 25, 14, 15)) == "S06_2026-11-25T14:15:00Z"


def test_event_id_is_deterministic():
    slot = utc(2026, 11, 25, 14, 15)
    assert m.make_event_id("S06", slot) == m.make_event_id("S06", slot)


def test_event_id_differs_by_location_and_slot():
    s1, s2 = utc(2026, 11, 25, 14, 15), utc(2026, 11, 25, 14, 30)
    assert m.make_event_id("S06", s1) != m.make_event_id("S05", s1)
    assert m.make_event_id("S06", s1) != m.make_event_id("S06", s2)



def test_traffic_event_matches_schema(monkeypatch):
    payload = {"flowSegmentData": {
        "currentSpeed": 14, "freeFlowSpeed": 37, "currentTravelTime": 120,
        "freeFlowTravelTime": 50, "confidence": 0.92,
        "roadClosure": False, "frc": "FRC3",
    }}
    monkeypatch.setattr(m.requests, "get", lambda *a, **k: FakeResponse(payload))
    segment = {"id": "S06", "lat": 30.03, "lon": 31.47}
    event = m.fetch_traffic(segment, utc(2026, 11, 25, 14, 15), "fake-key")
    jsonschema.validate(event, m.load_schema("traffic_event.schema.json"))
    assert event["event_id"] == "S06_2026-11-25T14:15:00Z"


def test_weather_event_matches_schema_when_no_rain(monkeypatch):
    payload = {"main": {"temp": 21.5, "humidity": 40}, "wind": {"speed": 3.1},
               "visibility": 10000, "weather": [{"id": 800}]}
    monkeypatch.setattr(m.requests, "get", lambda *a, **k: FakeResponse(payload))
    zone = {"id": "Z2", "lat": 30.03, "lon": 31.46}
    event = m.fetch_weather(zone, utc(2026, 11, 25, 14, 15), "fake-key")
    jsonschema.validate(event, m.load_schema("weather_event.schema.json"))
    assert event["rain_1h_mm"] == 0


def test_config_files_load():
    assert len(m.load_locations("segments.yml", "segments")) == 15
    assert len(m.load_locations("zones.yml", "zones")) == 5



def test_file_sink_writes_json_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT_DIR", tmp_path)
    events = [{"event_id": "S01_x"}, {"event_id": "S02_x"}]
    m.send("traffic-events", events, "file")
    lines = (tmp_path / "traffic-events.jsonl").read_text().splitlines()
    assert [json.loads(line)["event_id"] for line in lines] == ["S01_x", "S02_x"]


def test_failed_location_is_skipped(monkeypatch):
    def boom(*a, **k):
        raise m.requests.ConnectionError("secret-url-with-key")

    monkeypatch.setattr(m.requests, "get", boom)
    events = m.collect([{"id": "S01", "lat": 1, "lon": 1}], m.fetch_traffic,
                       m.load_schema("traffic_event.schema.json"),
                       utc(2026, 11, 25, 14, 15), "fake-key", "segment")
    assert events == []


def test_weather_is_still_sent_when_traffic_send_fails(monkeypatch):
    sent = []

    def fake_send(queue, events, sink):
        if queue == m.TRAFFIC_QUEUE:
            raise RuntimeError("boom")
        sent.append(queue)

    monkeypatch.setenv("TOMTOM_API_KEY", "fake")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake")
    monkeypatch.setenv("SINK", "file")
    monkeypatch.setattr(m, "load_locations", lambda f, k: [{"id": "X1", "lat": 1, "lon": 1}])
    monkeypatch.setattr(m, "collect", lambda *a, **k: [{"event_id": "X1_e"}])
    monkeypatch.setattr(m, "load_schema", lambda name: {})
    monkeypatch.setattr(m, "send", fake_send)

    assert m.main() == 1               
    assert sent == [m.WEATHER_QUEUE]     

def test_full_namespace_appends_suffix_when_missing():
    assert m.full_namespace("sb-flowcast") == "sb-flowcast.servicebus.windows.net"


def test_full_namespace_keeps_full_hostname():
    full = "sb-flowcast.servicebus.windows.net"
    assert m.full_namespace(full) == full
    assert m.full_namespace(f"  {full}  ") == full

def test_invalid_sink_is_rejected(monkeypatch):
    monkeypatch.setenv("TOMTOM_API_KEY", "fake")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake")
    monkeypatch.setenv("SINK", "fil")
    called = []
    monkeypatch.setattr(m, "collect", lambda *a, **k: called.append(1) or [])

    assert m.main() == 1
    assert called == [] 


def test_sink_value_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("TOMTOM_API_KEY", "fake")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake")
    monkeypatch.setenv("SINK", "File")
    sent = []
    monkeypatch.setattr(m, "load_locations", lambda f, k: [{"id": "X1", "lat": 1, "lon": 1}])
    monkeypatch.setattr(m, "load_schema", lambda name: {})
    monkeypatch.setattr(m, "collect", lambda *a, **k: [{"event_id": "X1_e"}])
    monkeypatch.setattr(m, "send", lambda queue, events, sink: sent.append(sink))

    assert m.main() == 0
    assert sent == ["file", "file"] 