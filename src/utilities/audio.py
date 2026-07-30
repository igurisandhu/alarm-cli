"""Cross-platform audible alert utilities."""

from __future__ import annotations

import os
import platform
import subprocess
import sys


def _play_system_bell() -> None:
    """Emit the terminal bell character (\\a). Works on virtually every terminal."""
    sys.stdout.write("\a")
    sys.stdout.flush()


def _speak_macos(message: str) -> None:
    """Use macOS ``say`` command to speak *message* aloud."""
    try:
        subprocess.Popen(
            ["say", message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass  # `say` not available → fall back to bell only


def trigger_alarm(message: str = "ALARM! Time is up!") -> None:
    """Play an audible alarm alert and print a prominent terminal message.

    On macOS this uses both the system bell and the ``say`` speech synthesizer.
    On other platforms it falls back to the system bell.

    Args:
        message: The text message to display (and speak on macOS).
    """
    # ── Visual alert ──────────────────────────────────────────────────────
    border = "!" * 60
    print(f"\n{border}")
    print(f"!!!  {message}")
    print(f"{border}\n")

    # ── Audible alert ─────────────────────────────────────────────────────
    _play_system_bell()

    if platform.system() == "Darwin":
        _speak_macos(message)