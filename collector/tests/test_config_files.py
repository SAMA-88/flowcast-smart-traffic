"""Starter test: config files are valid. Add collector tests next to this file."""

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parents[2] / "config"


def _ids(name: str, key: str) -> list[str]:
    data = yaml.safe_load((CONFIG / name).read_text(encoding="utf-8"))
    return [item["id"] for item in data[key]]


def test_segment_and_zone_ids_are_unique():
    for name, key in [("segments.yml", "segments"), ("zones.yml", "zones")]:
        ids = _ids(name, key)
        assert len(ids) == len(set(ids)), f"duplicate id in {name}"


def test_daily_api_quota():
    assert len(_ids("segments.yml", "segments")) * 96 <= 2500  # TomTom free tier
    assert len(_ids("zones.yml", "zones")) * 96 <= 1000
