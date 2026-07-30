"""CLI entry point for the Alarm Clock application.

Run::

    python -m src.main
"""

from __future__ import annotations

import sys
import time
from typing import List, Optional

from src.core.alarm import Alarm
from src.core.scheduler import AlarmScheduler
from src.storage.json_storage import add_alarm, delete_alarm, load_alarms
from src.utilities.validator import validate_alarm_time, validate_alarm_id, validate_label

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
MENU_OPTIONS = """
╔══════════════════════════════════╗
║       ALARM CLOCK — CLI         ║
╠══════════════════════════════════╣
║  1.  Create a new alarm         ║
║  2.  List all alarms            ║
║  3.  Delete an alarm            ║
║  4.  Toggle alarm (on/off)      ║
║  5.  Quit                       ║
╚══════════════════════════════════╝
"""


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def _clear_screen() -> None:
    """Clear the terminal screen (cross-platform)."""
    import os
    os.system("cls" if os.name == "nt" else "clear")


def _print_header() -> None:
    _clear_screen()
    print("=" * 50)
    print("          PYTHON CLI ALARM CLOCK")
    print("=" * 50)
    now = time.strftime("%H:%M:%S")
    print(f"  System time:  {now}")
    print("=" * 50)


# ─────────────────────────────────────────────────────────────────────────────
# Menu handlers
# ─────────────────────────────────────────────────────────────────────────────
def handle_create() -> None:
    """Prompt user for time and optional label, then save a new alarm."""
    print("\n--- Create a New Alarm ---")

    # ── Time ───────────────────────────────────────────────────────────────
    while True:
        raw = input("  Enter time (HH:MM, 24-hour format): ").strip()
        is_valid, err = validate_alarm_time(raw)
        if is_valid:
            alarm_time = raw
            break
        print(f"  ❌ {err}")

    # ── Label (optional) ──────────────────────────────────────────────────
    raw_label = input("  Enter label (optional, press Enter to skip): ").strip()
    if raw_label:
        is_valid, err = validate_label(raw_label)
        if not is_valid:
            print(f"  ⚠  {err} — label will be ignored.")
            raw_label = ""

    alarm = Alarm(time=alarm_time, label=raw_label)
    add_alarm(alarm)
    print(f"\n  ✅ Alarm created: [{alarm.alarm_id}] {alarm.time}")


def handle_list() -> None:
    """Display all stored alarms."""
    alarms = load_alarms()
    print("\n--- Active Alarms ---")
    if not alarms:
        print("  (no alarms saved)")
        return

    print(f"  {'ID':<10} {'Time':<8} {'Active':<8}  Label")
    print(f"  {'-'*10} {'-'*8} {'-'*8}  {'-'*20}")
    for a in alarms:
        active_str = "🔔 ON" if a.active else "⛔ OFF"
        label = a.label if a.label else "(no label)"
        print(f"  {a.alarm_id:<10} {a.time:<8} {active_str:<8}  {label}")


def handle_delete() -> None:
    """Delete an alarm by ID."""
    alarms = load_alarms()
    if not alarms:
        print("\n  📭 No alarms to delete.")
        return

    handle_list()
    print("\n--- Delete an Alarm ---")
    alarm_id = input("  Enter alarm ID to delete: ").strip()

    is_valid, err = validate_alarm_id(alarm_id)
    if not is_valid:
        print(f"  ❌ {err}")
        return

    if delete_alarm(alarm_id):
        print(f"  ✅ Alarm {alarm_id} deleted.")
    else:
        print(f"  ❌ No alarm found with ID {alarm_id}.")


def handle_toggle() -> None:
    """Toggle an alarm's active state."""
    alarms = load_alarms()
    if not alarms:
        print("\n  📭 No alarms to toggle.")
        return

    handle_list()
    print("\n--- Toggle Alarm ---")
    alarm_id = input("  Enter alarm ID to toggle: ").strip()

    for alarm in alarms:
        if alarm.alarm_id == alarm_id:
            alarm.toggle()
            status = "ON" if alarm.active else "OFF"
            from src.storage.json_storage import save_alarms
            save_alarms(alarms)
            print(f"  ✅ Alarm {alarm_id} is now {status}.")
            return

    print(f"  ❌ No alarm found with ID {alarm_id}.")


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Run the interactive CLI alarm clock."""
    scheduler = AlarmScheduler()
    scheduler.start()

    while True:
        _print_header()
        print(MENU_OPTIONS)
        choice = input("  Choose an option (1-5): ").strip()

        if choice == "1":
            handle_create()
        elif choice == "2":
            handle_list()
        elif choice == "3":
            handle_delete()
        elif choice == "4":
            handle_toggle()
        elif choice == "5":
            print("\n  👋 Goodbye! Alarms cleared from memory.")
            scheduler.stop()
            sys.exit(0)
        else:
            print(f"\n  ❌ Invalid option: {choice!r}. Enter 1-5.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()