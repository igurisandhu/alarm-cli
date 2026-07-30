"""Unit tests for input validation utilities."""

from __future__ import annotations

import pytest

from src.utilities.validator import (
    validate_alarm_time,
    validate_alarm_id,
    validate_label,
)


class TestValidateAlarmTime:
    """Tests for the ``validate_alarm_time`` function."""

    # ── Valid inputs ───────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        "time_str",
        [
            "00:00",
            "07:30",
            "12:00",
            "23:59",
            " 07:30 ",  # whitespace should be trimmed
        ],
    )
    def test_valid_times(self, time_str: str) -> None:
        is_valid, err = validate_alarm_time(time_str)
        assert is_valid is True
        assert err is None

    # ── Invalid inputs ─────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        "time_str, expected_substring",
        [
            ("", "empty"),
            ("   ", "empty"),
            ("7:30", "HH:MM"),       # single-digit hour
            ("07:5", "HH:MM"),       # single-digit minute
            ("25:00", "Hours"),      # hour out of range
            ("-1:00", "HH:MM"),      # negative hour → pattern mismatch
            ("07:60", "Minutes"),    # minute out of range
            ("07:-1", "HH:MM"),      # negative minute
            ("abc", "HH:MM"),        # non-numeric
            ("12:34:56", "HH:MM"),   # too many parts
        ],
    )
    def test_invalid_times(self, time_str: str, expected_substring: str) -> None:
        is_valid, err = validate_alarm_time(time_str)
        assert is_valid is False
        assert err is not None
        assert expected_substring.lower() in err.lower()


class TestValidateAlarmId:
    """Tests for the ``validate_alarm_id`` function."""

    def test_valid_id(self) -> None:
        assert validate_alarm_id("a1b2c3d4") == (True, None)

    def test_empty(self) -> None:
        assert validate_alarm_id("") == (False, "Alarm ID cannot be empty.")

    def test_whitespace_only(self) -> None:
        assert validate_alarm_id("   ") == (False, "Alarm ID cannot be empty.")

    def test_too_short(self) -> None:
        is_valid, err = validate_alarm_id("abc")
        assert is_valid is False
        assert "hex" in err

    def test_invalid_chars(self) -> None:
        is_valid, err = validate_alarm_id("zzzzzzzz")
        assert is_valid is False


class TestValidateLabel:
    """Tests for the ``validate_label`` function."""

    def test_empty_label_is_valid(self) -> None:
        assert validate_label("") == (True, None)

    def test_short_label(self) -> None:
        assert validate_label("Meeting") == (True, None)

    def test_label_exceeds_max_length(self) -> None:
        long_label = "a" * 51
        is_valid, err = validate_label(long_label, max_length=50)
        assert is_valid is False
        assert "50" in err