"""Unit tests for the Alarm dataclass."""

from __future__ import annotations

import pytest

from src.core.alarm import Alarm


class TestAlarmCreation:
    """Tests for creating Alarm instances with various inputs."""

    def test_create_minimal_alarm(self) -> None:
        """An alarm with just a time should have sensible defaults."""
        alarm = Alarm(time="07:30")
        assert alarm.time == "07:30"
        assert alarm.label == ""
        assert alarm.active is True
        assert len(alarm.alarm_id) == 8  # hex[:8]
        assert alarm.created_at is not None

    def test_create_with_label(self) -> None:
        """Label should be stored as-is."""
        alarm = Alarm(time="12:00", label="Lunch break")
        assert alarm.label == "Lunch break"

    def test_create_with_custom_id(self) -> None:
        """Explicit alarm_id should be honoured."""
        alarm = Alarm(time="23:59", alarm_id="deadbeef")
        assert alarm.alarm_id == "deadbeef"

    def test_create_inactive(self) -> None:
        """An alarm can start in inactive state."""
        alarm = Alarm(time="06:00", active=False)
        assert alarm.active is False


class TestAlarmState:
    """Tests for state transitions (deactivate, toggle)."""

    def test_deactivate(self) -> None:
        alarm = Alarm(time="08:00")
        alarm.deactivate()
        assert alarm.active is False

    def test_toggle_on_to_off(self) -> None:
        alarm = Alarm(time="09:00")
        alarm.toggle()
        assert alarm.active is False

    def test_toggle_off_to_on(self) -> None:
        alarm = Alarm(time="10:00", active=False)
        alarm.toggle()
        assert alarm.active is True


class TestAlarmSerialization:
    """Tests for to_dict / from_dict round-trip."""

    def test_round_trip(self) -> None:
        original = Alarm(time="14:30", label="Meeting", active=True)
        data = original.to_dict()
        restored = Alarm.from_dict(data)
        assert restored.time == original.time
        assert restored.label == original.label
        assert restored.active == original.active
        assert restored.alarm_id == original.alarm_id
        assert restored.created_at == original.created_at

    def test_from_dict_missing_optional(self) -> None:
        """from_dict should survive missing optional keys."""
        data = {"time": "11:11"}
        alarm = Alarm.from_dict(data)
        assert alarm.time == "11:11"
        assert alarm.label == ""
        assert alarm.active is True

    def test_str_representation(self) -> None:
        alarm = Alarm(time="06:00", label="Wake up")
        s = str(alarm)
        assert "06:00" in s
        assert "Wake up" in s
        assert alarm.alarm_id in s


class TestAlarmValidation:
    """Tests for the __post_init__ guard."""

    def test_invalid_time_no_colon(self) -> None:
        with pytest.raises(ValueError, match="Invalid time format"):
            Alarm(time="0600")

    def test_invalid_time_wrong_type(self) -> None:
        with pytest.raises(ValueError, match="Invalid time format"):
            Alarm(time=1230)  # type: ignore[arg-type]