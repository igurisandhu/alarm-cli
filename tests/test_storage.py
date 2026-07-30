"""Unit tests for the JSON storage layer.

Uses a temporary directory to avoid polluting the real ``~/.alarm-cli`` data.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.core.alarm import Alarm
from src.storage import json_storage as store


# ---------------------------------------------------------------------------
# Fixture: swap the storage paths for a temp dir during tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolate_storage(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Redirect storage to a temporary directory for each test."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        monkeypatch.setattr(store, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(store, "_DB_PATH", tmp_path / "alarms.json")
        yield


# ===================================================================
# Tests
# ===================================================================


class TestLoadSave:
    """Tests for loading and saving alarm collections."""

    def test_load_empty_when_no_file(self) -> None:
        assert store.load_alarms() == []

    def test_save_then_load_round_trip(self) -> None:
        alarms = [
            Alarm(time="07:00", label="Wake up"),
            Alarm(time="12:00", label="Lunch"),
        ]
        store.save_alarms(alarms)
        loaded = store.load_alarms()
        assert len(loaded) == 2
        assert loaded[0].time == "07:00"
        assert loaded[1].time == "12:00"

    def test_corrupt_json_returns_empty(self) -> None:
        store._DB_PATH.write_text("{bad json}")
        assert store.load_alarms() == []


class TestAddDelete:
    """Tests for add_alarm and delete_alarm."""

    def test_add_alarm_increases_count(self) -> None:
        alarm = Alarm(time="08:00")
        store.add_alarm(alarm)
        assert len(store.load_alarms()) == 1

    def test_delete_existing_returns_true(self) -> None:
        alarm = Alarm(time="09:00")
        store.add_alarm(alarm)
        assert store.delete_alarm(alarm.alarm_id) is True
        assert store.load_alarms() == []

    def test_delete_nonexistent_returns_false(self) -> None:
        assert store.delete_alarm("deadbeef") is False

    def test_get_alarm_by_id(self) -> None:
        alarm = Alarm(time="10:00")
        store.add_alarm(alarm)
        found = store.get_alarm_by_id(alarm.alarm_id)
        assert found is not None
        assert found.time == "10:00"

    def test_get_nonexistent_returns_none(self) -> None:
        assert store.get_alarm_by_id("nope1234") is None