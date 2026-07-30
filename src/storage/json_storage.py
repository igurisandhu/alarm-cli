"""JSON-based persistence layer for alarms.

Stores alarms in ``~/.alarm-cli/alarms.json`` to keep the user's project
directory free of runtime artifacts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from src.core.alarm import Alarm

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_CONFIG_DIR = Path.home() / ".alarm-cli"
_DB_PATH = _CONFIG_DIR / "alarms.json"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _ensure_config_dir() -> None:
    """Create the config directory (and parents) if it doesn't exist."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_db() -> List[dict]:
    """Read the JSON file and return a list of alarm dicts.

    Returns an empty list if the file doesn't exist or is corrupt.
    """
    if not _DB_PATH.exists():
        return []

    try:
        with open(_DB_PATH, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def _write_db(alarms: List[dict]) -> None:
    """Atomically write a list of alarm dicts to the JSON file."""
    _ensure_config_dir()
    with open(_DB_PATH, "w") as f:
        json.dump(alarms, f, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load_alarms() -> List[Alarm]:
    """Load all alarms from the JSON storage file.

    Returns:
        A list of ``Alarm`` instances (may be empty).
    """
    raw_list = _read_db()
    alarms: List[Alarm] = []
    for item in raw_list:
        try:
            alarms.append(Alarm.from_dict(item))
        except (KeyError, ValueError, TypeError):
            # Silently skip corrupt entries
            continue
    return alarms


def save_alarms(alarms: List[Alarm]) -> None:
    """Persist a list of ``Alarm`` instances to the JSON file.

    Args:
        alarms: The alarms to persist.
    """
    _write_db([a.to_dict() for a in alarms])


def add_alarm(alarm: Alarm) -> None:
    """Append a single alarm to storage.

    Args:
        alarm: The ``Alarm`` to persist.
    """
    alarms = load_alarms()
    alarms.append(alarm)
    save_alarms(alarms)


def delete_alarm(alarm_id: str) -> bool:
    """Remove an alarm by its ID.

    Args:
        alarm_id: The 8-character hex ID of the alarm to remove.

    Returns:
        ``True`` if the alarm was found and removed, ``False`` otherwise.
    """
    alarms = load_alarms()
    before = len(alarms)
    alarms = [a for a in alarms if a.alarm_id != alarm_id]
    if len(alarms) == before:
        return False
    save_alarms(alarms)
    return True


def get_alarm_by_id(alarm_id: str) -> Optional[Alarm]:
    """Fetch a single alarm by ID (or ``None``)."""
    for a in load_alarms():
        if a.alarm_id == alarm_id:
            return a
    return None