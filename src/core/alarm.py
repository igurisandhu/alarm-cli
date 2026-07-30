"""Alarm dataclass representing a single alarm."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Alarm:
    """Represents a single alarm with a unique ID, time, label, and state.

    Attributes:
        alarm_id: Unique identifier (UUID string).
        time: Alarm time in HH:MM (24-hour) format.
        label: Optional human-readable label for the alarm.
        active: Whether the alarm is currently enabled.
        created_at: ISO-format timestamp of when the alarm was created.
    """

    time: str
    label: str = ""
    active: bool = True
    alarm_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # ──────────────────────────────────────────────
    # Prevents accidental field ordering mistakes
    # ──────────────────────────────────────────────
    def __post_init__(self) -> None:
        if not isinstance(self.time, str) or ":" not in self.time:
            raise ValueError(f"Invalid time format: {self.time!r}")

    def deactivate(self) -> None:
        """Mark the alarm as inactive (used after trigger)."""
        self.active = False

    def toggle(self) -> None:
        """Toggle the active state."""
        self.active = not self.active

    def to_dict(self) -> dict:
        """Serialize alarm to a dictionary for JSON storage."""
        return {
            "alarm_id": self.alarm_id,
            "time": self.time,
            "label": self.label,
            "active": self.active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Alarm:
        """Deserialize a dictionary back into an Alarm instance."""
        return cls(
            alarm_id=data.get("alarm_id", uuid.uuid4().hex[:8]),
            time=data["time"],
            label=data.get("label", ""),
            active=data.get("active", True),
            created_at=data.get("created_at", ""),
        )

    def __str__(self) -> str:
        status = "\N{BELL}" if self.active else "\N{CROSS MARK}"
        label_part = f" - {self.label}" if self.label else ""
        return f"[{self.alarm_id}] {self.time}  {status} {label_part}"