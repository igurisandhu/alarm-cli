"""Input validation utilities for alarm time and user input."""

from __future__ import annotations

import re
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_HHMM_PATTERN = re.compile(r"^\d{2}:\d{2}$")


def validate_alarm_time(raw: str) -> Tuple[bool, Optional[str]]:
    """Validate that *raw* is a valid 24-hour HH:MM time string.

    Args:
        raw: User-supplied time string (e.g. ``"07:30"``, ``"23:59"``).

    Returns:
        A ``(is_valid, error_message)`` tuple.  If valid the error is ``None``.
    """
    if not raw or not raw.strip():
        return False, "Time cannot be empty."

    stripped = raw.strip()

    if not _HHMM_PATTERN.match(stripped):
        return False, "Invalid format. Use HH:MM (e.g. 07:30, 23:59)."

    try:
        hours_str, minutes_str = stripped.split(":")
        hours = int(hours_str)
        minutes = int(minutes_str)
    except ValueError:
        return False, "Hours and minutes must be whole numbers."

    if hours < 0 or hours > 23:
        return False, f"Hours must be between 00 and 23 (got {hours:02d})."

    if minutes < 0 or minutes > 59:
        return False, f"Minutes must be between 00 and 59 (got {minutes:02d})."

    return True, None


def validate_alarm_id(raw: str) -> Tuple[bool, Optional[str]]:
    """Validate that *raw* looks like a plausible 8-hex-char alarm ID."""
    if not raw or not raw.strip():
        return False, "Alarm ID cannot be empty."
    raw = raw.strip()
    if not re.match(r"^[0-9a-f]{8}$", raw):
        return False, "Alarm ID must be an 8-character hex string (e.g. a1b2c3d4)."
    return True, None


def validate_label(raw: str, max_length: int = 50) -> Tuple[bool, Optional[str]]:
    """Validate an optional alarm label."""
    if len(raw) > max_length:
        return False, f"Label must be {max_length} characters or fewer."
    return True, None