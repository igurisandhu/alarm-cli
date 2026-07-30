"""CLI entry point for the Alarm Clock application.

Usage::

    # One-shot commands (quick operations)
    python3 -m src.main add 14:30 --label "Meeting"
    python3 -m src.main add 14:36
    python3 -m src.main list
    python3 -m src.main delete a1b2c3d4
    python3 -m src.main toggle a1b2c3d4

    # Interactive mode (scheduler runs, alarms fire)
    python3 -m src.main run
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import List, Optional

from src.core.alarm import Alarm
from src.core.scheduler import AlarmScheduler
from src.storage.json_storage import add_alarm, delete_alarm, load_alarms, save_alarms
from src.utilities.validator import validate_alarm_time, validate_alarm_id, validate_label


# ─────────────────────────────────────────────────────────────────────────────
# One-shot command handlers
# ─────────────────────────────────────────────────────────────────────────────
def cmd_add(args: argparse.Namespace) -> None:
    """Add a new alarm: ``alarm add HH:MM --label "..."``"""
    is_valid, err = validate_alarm_time(args.time)
    if not is_valid:
        print(f"❌ {err}")
        sys.exit(1)

    label = args.label or ""
    if label:
        is_valid, err = validate_label(label)
        if not is_valid:
            print(f"⚠  {err} — label ignored.")
            label = ""

    alarm = Alarm(time=args.time, label=label)
    add_alarm(alarm)
    print(f"✅ Alarm created: [{alarm.alarm_id}] {alarm.time}")


def cmd_list(_args: argparse.Namespace) -> None:
    """List all alarms: ``alarm list``"""
    alarms = load_alarms()
    if not alarms:
        print("📭 No alarms saved.")
        return

    print(f"  {'ID':<10} {'Time':<8} {'Active':<8}  Label")
    print(f"  {'-'*10} {'-'*8} {'-'*8}  {'-'*20}")
    for a in alarms:
        active_str = "🔔 ON" if a.active else "⛔ OFF"
        label = a.label if a.label else "(no label)"
        print(f"  {a.alarm_id:<10} {a.time:<8} {active_str:<8}  {label}")


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete an alarm by ID: ``alarm delete <id>``"""
    is_valid, err = validate_alarm_id(args.alarm_id)
    if not is_valid:
        print(f"❌ {err}")
        sys.exit(1)

    if delete_alarm(args.alarm_id):
        print(f"✅ Alarm {args.alarm_id} deleted.")
    else:
        print(f"❌ No alarm found with ID {args.alarm_id}.")
        sys.exit(1)


def cmd_toggle(args: argparse.Namespace) -> None:
    """Toggle an alarm on/off: ``alarm toggle <id>``"""
    alarms = load_alarms()
    for alarm in alarms:
        if alarm.alarm_id == args.alarm_id:
            alarm.toggle()
            save_alarms(alarms)
            status = "ON" if alarm.active else "OFF"
            print(f"✅ Alarm {args.alarm_id} is now {status}.")
            return

    print(f"❌ No alarm found with ID {args.alarm_id}.")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Interactive mode (scheduler + menu)
# ─────────────────────────────────────────────────────────────────────────────
MENU = """
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


def cmd_run(_args: argparse.Namespace) -> None:
    """Run the alarm clock interactively with the scheduler active.

    Alarms will fire in the background while you manage them via the menu.
    Press Ctrl+C or choose option 5 to quit.
    """
    scheduler = AlarmScheduler()
    scheduler.start()
    print("⏰ Alarm scheduler running in background — alarms will fire!\n")

    try:
        while True:
            _print_header()
            print(MENU)
            choice = input("  Choose an option (1-5): ").strip()

            if choice == "1":
                _interactive_create()
            elif choice == "2":
                _interactive_list()
            elif choice == "3":
                _interactive_delete()
            elif choice == "4":
                _interactive_toggle()
            elif choice == "5":
                print("\n  👋 Goodbye!")
                scheduler.stop()
                sys.exit(0)
            else:
                print(f"\n  ❌ Invalid option: {choice!r}. Enter 1-5.")

            input("\n  Press Enter to continue...")
    except KeyboardInterrupt:
        print("\n\n  👋 Goodbye!")
        scheduler.stop()
        sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# Interactive menu helpers
# ─────────────────────────────────────────────────────────────────────────────
def _clear_screen() -> None:
    """Clear the terminal screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def _print_header() -> None:
    _clear_screen()
    now = time.strftime("%H:%M:%S")
    print("=" * 50)
    print("          PYTHON CLI ALARM CLOCK")
    print("=" * 50)
    print(f"  System time:  {now}")
    print("=" * 50)


def _interactive_create() -> None:
    """Prompt user for time and optional label, then save."""
    print("\n--- Create a New Alarm ---")

    while True:
        raw = input("  Enter time (HH:MM, 24-hour format): ").strip()
        is_valid, err = validate_alarm_time(raw)
        if is_valid:
            alarm_time = raw
            break
        print(f"  ❌ {err}")

    raw_label = input("  Enter label (optional, press Enter to skip): ").strip()
    if raw_label:
        is_valid, err = validate_label(raw_label)
        if not is_valid:
            print(f"  ⚠  {err} — label ignored.")
            raw_label = ""

    alarm = Alarm(time=alarm_time, label=raw_label)
    add_alarm(alarm)
    print(f"\n  ✅ Alarm created: [{alarm.alarm_id}] {alarm.time}")
    print("  🔔 The scheduler will fire this alarm when the time is reached.")


def _interactive_list() -> None:
    """Display all stored alarms."""
    alarms = load_alarms()
    print("\n--- All Alarms ---")
    if not alarms:
        print("  📭 No alarms saved.")
        return

    print(f"  {'ID':<10} {'Time':<8} {'Active':<8}  Label")
    print(f"  {'-'*10} {'-'*8} {'-'*8}  {'-'*20}")
    for a in alarms:
        active_str = "🔔 ON" if a.active else "⛔ OFF"
        label = a.label if a.label else "(no label)"
        print(f"  {a.alarm_id:<10} {a.time:<8} {active_str:<8}  {label}")


def _interactive_delete() -> None:
    """Delete an alarm by ID."""
    alarms = load_alarms()
    if not alarms:
        print("\n  📭 No alarms to delete.")
        return

    _interactive_list()
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


def _interactive_toggle() -> None:
    """Toggle an alarm's active state."""
    alarms = load_alarms()
    if not alarms:
        print("\n  📭 No alarms to toggle.")
        return

    _interactive_list()
    print("\n--- Toggle Alarm ---")
    alarm_id = input("  Enter alarm ID to toggle: ").strip()

    for alarm in alarms:
        if alarm.alarm_id == alarm_id:
            alarm.toggle()
            save_alarms(alarms)
            status = "ON" if alarm.active else "OFF"
            print(f"  ✅ Alarm {alarm_id} is now {status}.")
            return

    print(f"  ❌ No alarm found with ID {alarm_id}.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI argument parser
# ─────────────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    """Construct and return the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="alarm",
        description="Python CLI Alarm Clock — manage and monitor alarms.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- add ---
    add_parser = subparsers.add_parser("add", help="Create a new alarm")
    add_parser.add_argument("time", help="Time in HH:MM 24-hour format (e.g. 14:30)")
    add_parser.add_argument(
        "--label", "-l",
        default="",
        help="Optional label for the alarm",
    )

    # --- list ---
    subparsers.add_parser("list", help="List all alarms")

    # --- delete ---
    del_parser = subparsers.add_parser("delete", help="Delete an alarm by ID")
    del_parser.add_argument("alarm_id", help="8-character hex alarm ID")

    # --- toggle ---
    toggle_parser = subparsers.add_parser("toggle", help="Toggle an alarm on/off")
    toggle_parser.add_argument("alarm_id", help="8-character hex alarm ID")

    # --- run (interactive with scheduler) ---
    subparsers.add_parser("run", help="Run interactive mode with background scheduler")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Entry point: parse args and dispatch to the appropriate handler."""
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "delete": cmd_delete,
        "toggle": cmd_toggle,
        "run": cmd_run,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)


if __name__ == "__main__":
    main()