# ⏰ Python CLI Alarm Clock

A fully-featured command-line alarm clock application written in **Python 3.14+**
using only the standard library. Create, list, toggle, and delete alarms —
the scheduler fires audible alerts when the system clock matches an alarm time.

---

## Features

- **Create alarms** with a time (24-hour `HH:MM` format) and optional label.
- **List alarms** — view all stored alarms with their status (active/inactive).
- **Delete alarms** by ID.
- **Toggle alarms** on/off without deleting them.
- **Automatic triggering** — a background daemon thread polls every second and
  fires an audible alert (terminal bell + macOS `say` command) when time matches.
- **Persistent storage** — alarms saved to `~/.alarm-cli/alarms.json`.
- **Graceful error handling** — invalid input prompts the user to retry instead
  of crashing.

---

## Project Structure

```
alarm-cli/
├── README.md
├── src/
│   ├── main.py                  # CLI entry point & interactive menu
│   ├── core/
│   │   ├── alarm.py             # Alarm dataclass (model)
│   │   └── scheduler.py         # Background polling thread
│   ├── storage/
│   │   └── json_storage.py      # JSON file persistence
│   └── utilities/
│       ├── validator.py          # Input validation (HH:MM, IDs, labels)
│       └── audio.py              # Audible/terminal alert helpers
├── tests/
│   ├── test_alarm.py
│   ├── test_validator.py
│   └── test_storage.py
└── doc/
    ├── architecture.md           # Full architecture documentation
    └── diagrams.md               # ASCII diagrams (component, sequence, state)
```

---

## Setup

No dependencies to install — everything uses Python's standard library.

```bash
# 1. Clone or cd into the project directory
cd alarm-cli

# 2. (Optional) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Run the application
python3 -m src.main
```

---

## Usage

When you run the application you'll see an interactive menu:

```
==================================================
          PYTHON CLI ALARM CLOCK
==================================================
  System time:  14:35:22
==================================================

╔══════════════════════════════════╗
║       ALARM CLOCK — CLI         ║
╠══════════════════════════════════╣
║  1.  Create a new alarm         ║
║  2.  List all alarms            ║
║  3.  Delete an alarm            ║
║  4.  Toggle alarm (on/off)      ║
║  5.  Quit                       ║
╚══════════════════════════════════╝

  Choose an option (1-5):
```

### Creating an alarm

```
Choose an option (1-5): 1

--- Create a New Alarm ---
  Enter time (HH:MM, 24-hour format): 07:30
  Enter label (optional, press Enter to skip): Morning coffee

  ✅ Alarm created: [a1b2c3d4] 07:30
```

### Listing alarms

```
Choose an option (1-5): 2

--- Active Alarms ---
  ID         Time     Active    Label
  ---------- -------- --------  --------------------
  a1b2c3d4   07:30    🔔 ON     Morning coffee
  e5f6g7h8   14:00    ⛔ OFF    Meeting
```

### Deleting an alarm

```
Choose an option (1-5): 3

--- Active Alarms ---
  ... (alarm list shown first) ...

--- Delete an Alarm ---
  Enter alarm ID to delete: a1b2c3d4

  ✅ Alarm a1b2c3d4 deleted.
```

### When an alarm fires

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!  🔔 ALARM at 07:30 (Morning coffee)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

(The terminal bell rings, and on macOS the computer speaks "ALARM!")
```

---

## Running Tests

The test suite uses `pytest`. Install it (if not already) and run:

```bash
# Install pytest (standard library test runner)
pip install pytest

# Run all tests from the project root
python3 -m pytest tests/ -v

# Run a specific test file
python3 -m pytest tests/test_validator.py -v
```

### Sample test output

```
tests/test_alarm.py .........                          [ 9 passed]
tests/test_storage.py .........                        [ 9 passed]
tests/test_validator.py ...............                 [15 passed]
```

---

## Architecture

See [`doc/architecture.md`](doc/architecture.md) for a deep dive into the
component design, data flow, and key design decisions.

See [`doc/diagrams.md`](doc/diagrams.md) for:
- Component dependency graph
- Class / module hierarchy
- Sequence diagrams (Create Alarm, Alarm Fires)
- Alarm lifecycle state diagram
- JSON schema
- Threading model

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **No external dependencies** | Uses only Python's standard library. Run without `pip install`. |
| **Interactive menu** | A continuously running alarm app is more natural with a menu loop than one-shot CLI commands. |
| **Daemon thread scheduler** | Polls every 1s in the background; auto-exits when the main program ends. |
| **JSON in `~/.alarm-cli/`** | Runtime data stays out of the project tree; human-readable for debugging. |
| **UUID short IDs** | 8-char hex IDs (from `uuid.hex[:8]`) avoid collision issues with simple integers. |

---

## License

MIT