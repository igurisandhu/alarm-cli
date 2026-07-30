# Architecture Documentation — Python CLI Alarm Clock

## Overview

The Alarm Clock is a **Python 3.14** command-line application that lets users
create, list, delete, and toggle alarms.  Alarms are persisted to a local JSON
file and monitored by a background thread that triggers audible alerts when the
system time matches an alarm time.

---

## Project Structure

```
alarm-cli/
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                  # CLI entry point & interactive menu
│   ├── core/
│   │   ├── __init__.py
│   │   ├── alarm.py             # Alarm dataclass
│   │   └── scheduler.py         # Background polling thread
│   ├── storage/
│   │   ├── __init__.py
│   │   └── json_storage.py      # JSON file CRUD operations
│   └── utilities/
│       ├── __init__.py
│       ├── validator.py          # Input validation (HH:MM format, etc.)
│       └── audio.py              # Audible/terminal alert helpers
├── tests/
│   ├── __init__.py
│   ├── test_alarm.py
│   ├── test_validator.py
│   └── test_storage.py
└── doc/
    ├── architecture.md           # This file
    └── diagrams.md               # ASCII architecture + sequence diagrams
```

---

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       main.py  (CLI Menu)                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Create    │  │ List      │  │ Delete    │  │ Toggle    │  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
│        │              │              │              │          │
├────────┼──────────────┼──────────────┼──────────────┼─────────┤
│        ▼              ▼              ▼              ▼          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  validator.py  (sanitize)                  │ │
│  └─────────────────────────┬─────────────────────────────────┘ │
│                            │                                    │
│  ┌─────────────────────────▼─────────────────────────────────┐ │
│  │              json_storage.py  (persist / load)             │ │
│  └──────────┬──────────────────────────────────┬─────────────┘ │
│             │                                  │                │
│  ┌──────────▼──────────┐          ┌───────────▼─────────────┐  │
│  │   ~/.alarm-cli/    │          │  AlarmScheduler          │  │
│  │   alarms.json      │          │  (daemon thread, 1s)     │  │
│  └─────────────────────┘          └───────────┬─────────────┘  │
│                                                │                │
│                                     ┌──────────▼─────────────┐  │
│                                     │    audio.py + print     │  │
│                                     │  (terminal alert + say) │  │
│                                     └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Core (``src/core/alarm.py``)

- ``Alarm`` — a frozen-style dataclass holding:
  - ``alarm_id``: 8-character hex string (UUID4 short).
  - ``time``: 24-hour ``HH:MM`` string.
  - ``label``: optional human-readable description.
  - ``active``: boolean flag (``True`` = enabled).
  - ``created_at``: ISO-format timestamp.
- Provides ``to_dict()`` / ``from_dict()`` for JSON serialisation.
- Provides ``deactivate()`` and ``toggle()`` state transitions.

### Core (``src/core/scheduler.py``)

- ``AlarmScheduler`` — a class that manages a **daemon thread**.
- Polls ``load_alarms()`` every 1 second.
- When current ``HH:MM`` matches an active alarm → calls ``audio.trigger_alarm()``
  and deactivates the alarm.
- Uses an internal set to avoid double-firing within the same minute.

### Storage (``src/storage/json_storage.py``)

- Five public functions:
  - ``load_alarms() → List[Alarm]``
  - ``save_alarms(alarms)``
  - ``add_alarm(alarm)``
  - ``delete_alarm(alarm_id) → bool``
  - ``get_alarm_by_id(alarm_id) → Optional[Alarm]``
- Storage path: ``~/.alarm-cli/alarms.json``
- Gracefully handles missing / corrupt files by returning an empty list.

### Utilities (``src/utilities/validator.py``)

- ``validate_alarm_time(raw) → (bool, Optional[str])``
  - Accepts ``HH:MM`` in 24-hour format.
  - Rejects empty, malformed, out-of-range values.
- ``validate_alarm_id(raw) → (bool, Optional[str])``
- ``validate_label(raw) → (bool, Optional[str])``

### Utilities (``src/utilities/audio.py``)

- ``trigger_alarm(message)`` — prints a prominent terminal banner, emits the
  terminal bell, and on macOS uses the ``say`` speech synthesizer.

---

## Data Flow

```text
User input ──→ main.py (menu)
                  │
                  ▼
            validator.py (validate time)
                  │
                  ▼
            json_storage (save to ~/.alarm-cli/alarms.json)
                  │
                  ▼
            AlarmScheduler (daemon thread polls every 1s)
                  │
                  ▼
            current time matches alarm time?
                  │
           ┌──────┴──────┐
          YES             NO
           │              (wait 1s)
           ▼
    trigger_alarm()
      •  Terminal banner + bell
      •  macOS: say "ALARM!"
      •  Deactivate alarm
      •  Save to JSON
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Interactive menu vs argparse** | Continuous daemon-like app — a ``while True`` loop with ``input()`` is more natural than one-shot commands. |
| **Daemon thread scheduler** | Simplest approach for background polling; auto-exits when main thread exits. |
| **UUID4 short IDs** | ``uuid.hex[:8]`` gives collision-resistant 8-char IDs without database auto-increment complexity. |
| **JSON in ``~/.alarm-cli/``** | Keeps runtime artifacts out of the project directory; human-readable for debugging. |
| **Standard library only** | Zero external dependencies — works out of the box with any Python 3.14+ installation. |

---

## Test Strategy

| Test file | What it covers |
|---|---|
| ``test_alarm.py`` | Alarm creation with various args, state transitions (deactivate/toggle), serialisation round-trip, ``__post_init__`` guards. |
| ``test_validator.py`` | Valid/invalid HH:MM patterns, edge cases, ID validation, label length limits. |
| ``test_storage.py`` | CRUD operations, corrupt file handling, empty-state behaviour (uses temp dir fixture to isolate from real data). |

---

## Future Improvements

- **Repeating alarms** (daily, weekdays-only).
- **Snooze** feature.
- **``asyncio``-based scheduler** for lower resource usage.
- **Time-zone awareness** via ``zoneinfo``.