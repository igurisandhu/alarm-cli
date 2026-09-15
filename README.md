# ⏰ Python CLI Alarm Clock

A fully-featured command-line alarm clock application written in **Python 3.14+**
using only the standard library. Manage alarms with simple subcommands —
the scheduler fires audible alerts when the system clock matches an alarm time.

---

## Features

### Two usage modes

**One-shot commands** — quick operations that exit immediately:
- `alarm add 14:30 --label "Meeting"`
- `alarm list`
- `alarm delete a1b2c3d4`
- `alarm toggle a1b2c3d4`

**Interactive mode** — scheduler runs in the background, alarms fire:
- `alarm run`

### Other features
- **Persistent storage** — alarms saved to `~/.alarm-cli/alarms.json`.
- **Graceful error handling** — invalid input prints a clear error and exits
  with code 1 — never crashes.
- **Audible + visual alerts** — terminal bell + macOS `say` speech synthesis.

---

## Project Structure

```
alarm-cli/
├── README.md
├── setup.py                   # Package installer (optional, for `alarm` command)
├── src/
│   ├── main.py                # CLI entry point (argparse subcommands)
│   ├── __main__.py            # Allows `python -m src run`
│   ├── core/
│   │   ├── alarm.py            # Alarm dataclass (model)
│   │   └── scheduler.py        # Background polling thread
│   ├── storage/
│   │   └── json_storage.py     # JSON file persistence
│   └── utilities/
│       ├── validator.py        # Input validation (HH:MM, IDs, labels)
│       └── audio.py            # Audible/terminal alert helpers
├── tests/
│   ├── test_alarm.py
│   ├── test_validator.py
│   └── test_storage.py
└── doc/
    ├── architecture.md          # Full architecture documentation
    └── diagrams.md              # ASCII diagrams (component, sequence, state)
```

---

## Setup

No dependencies to install — everything uses Python's standard library.

### Option A: Use via `python -m src` (always works)

```bash
cd alarm-cli
python3 -m src.main --help        # See all commands
python3 -m src.main run           # Run interactive mode
```

### Option B: Install globally (for `alarm` command)

```bash
cd alarm-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .                  # Install `alarm` command
alarm --help                      # Now `alarm` works in this terminal
```

---

## Usage

### Command reference

```
usage: alarm [-h] {add,list,delete,toggle,run} ...

positional arguments:
  {add,list,delete,toggle,run}
    add                 Create a new alarm
    list                List all alarms
    delete              Delete an alarm by ID
    toggle              Toggle an alarm on/off
    run                 Run interactive mode with background scheduler

options:
  -h, --help            show this help message and exit
```

### Creating an alarm

```bash
# Simple alarm — fires at 07:30 every day
alarm add 07:30
python3 -m src.main add 07:30

# Alarm with a label
alarm add 14:30 --label "Standup meeting"
python3 -m src.main add 14:30 --label "Standup meeting"

# Shorthand: -l instead of --label
alarm add 23:59 -l "Before midnight"
```

### Listing alarms

```bash
alarm list

# Output:
#   ID         Time     Active    Label
#   ---------- -------- --------  --------------------
#   a1b2c3d4   07:30    🔔 ON     (no label)
#   e5f6g7h8   14:30    🔔 ON     Standup meeting
```

### Deleting an alarm

```bash
alarm delete a1b2c3d4
# ✅ Alarm a1b2c3d4 deleted.
```

### Toggling an alarm

```bash
# Turn off an alarm (it stays in storage, won't fire)
alarm toggle a1b2c3d4
# ✅ Alarm a1b2c3d4 is now OFF.

# Turn it back on
alarm toggle a1b2c3d4
# ✅ Alarm a1b2c3d4 is now ON.
```

### Running interactively (scheduler + menu)

```bash
# Start the alarm clock with background scheduler and interactive menu
# Manage alarms while the scheduler monitors and fires them
# Press Ctrl+C or choose option 5 to quit
alarm run
python3 -m src.main run

# Output:
#   ⏰ Alarm scheduler running in background — alarms will fire!
#
#   ==================================================
#             PYTHON CLI ALARM CLOCK
#   ==================================================
#     System time:  14:55:00
#   ==================================================
#   ... menu ...
```

When an alarm fires:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!  🔔 ALARM at 07:30 (Meeting)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

(The terminal bell rings, and on macOS the computer speaks "ALARM!")
```

---

## Running Tests

```bash
# Install pytest (one-time setup)
pip install pytest

# Run all 43 tests
python3 -m pytest tests/ -v

# Sample output:
#   tests/test_alarm.py .........                          [ 12 passed]
#   tests/test_storage.py .........                        [  9 passed]
#   tests/test_validator.py ...............                 [ 15 passed]
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
| **Subcommand-based CLI** | Uses `argparse` — natural for a true CLI tool with add/list/delete/toggle/run. |
| **Daemon thread scheduler** | Polls every 1s in the background; auto-exits when the main program ends. |
| **JSON in `~/.alarm-cli/`** | Runtime data stays out of the project tree; human-readable for debugging. |
| **UUID short IDs** | 8-char hex IDs (from `uuid.hex[:8]`) avoid collision issues with simple integers. |

---

## License

MIT# aws-job-alert
