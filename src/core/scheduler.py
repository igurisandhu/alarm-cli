"""Background scheduler that monitors alarm times and triggers alerts."""

from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Callable, List, Optional

from src.core.alarm import Alarm
from src.storage.json_storage import delete_alarm, load_alarms, save_alarms
from src.utilities.audio import trigger_alarm

Callback = Callable[[Alarm], None]


class AlarmScheduler:
    """Runs a daemon thread that checks active alarms every second.

    When the current system time (HH:MM) matches an active alarm's time,
    the scheduler triggers the alarm: it fires an audible/visual alert and
    deactivates the alarm so it won't re-fire.

    Usage::

        scheduler = AlarmScheduler()
        scheduler.start()       # kicks off background thread
        # ... do other work ...
        scheduler.stop()        # signals thread to stop (optional)
    """

    def __init__(
        self,
        *,
        interval: float = 1.0,
        on_trigger: Optional[Callback] = None,
    ) -> None:
        """Initialise the scheduler.

        Args:
            interval: How often (in seconds) to poll for matching alarms.
            on_trigger: Optional callback invoked when an alarm fires.  The
                callback receives the triggered ``Alarm`` instance.
        """
        self._interval = interval
        self._on_trigger = on_trigger
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_triggered: set[str] = set()

    # ── Public API ────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        """``True`` if the scheduler thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        """Start the background polling thread (daemon)."""
        if self.is_running:
            return
        self._stop_event.clear()
        self._last_triggered.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="AlarmScheduler",
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the polling thread to stop."""
        self._stop_event.set()

    # ── Internal loop ─────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        """Main loop: poll every *interval* seconds until told to stop."""
        while not self._stop_event.is_set():
            self._check_and_fire()
            self._stop_event.wait(self._interval)

    def _check_and_fire(self) -> None:
        """Compare active alarms against current time and fire matches."""
        now = datetime.now().strftime("%H:%M")
        alarms = load_alarms()

        for alarm in alarms:
            if not alarm.active:
                continue
            if alarm.time != now:
                continue

            # Skip if we already fired this alarm in this exact minute
            trigger_key = f"{alarm.alarm_id}@{now}"
            if trigger_key in self._last_triggered:
                continue
            self._last_triggered.add(trigger_key)

            # ── Fire alarm ────────────────────────────────────────────────
            label_text = f" ({alarm.label})" if alarm.label else ""
            message = f"🔔 ALARM at {alarm.time}{label_text}"
            trigger_alarm(message)

            if self._on_trigger:
                self._on_trigger(alarm)

            # Deactivate so it doesn't fire again next poll cycle
            alarm.deactivate()

        # Persist any state changes (deactivations)
        save_alarms(alarms)

        # Trim old trigger keys (keep only last 2 minutes)
        now_key_prefix = datetime.now().strftime("%H:%M")
        self._last_triggered = {
            k for k in self._last_triggered if k.endswith(now_key_prefix)
        }