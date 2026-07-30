# Architecture Diagrams — Python CLI Alarm Clock

## 1. Component Dependency Graph

```text
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│  (CLI menu loop, user I/O, dispatches to handlers)          │
└──┬────────────┬──────────────┬───────────────┬──────────────┘
   │            │              │               │
   ▼            ▼              ▼               ▼
┌────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│ core/  │ │ core/    │ │ storage/     │ │ utilities/   │
│ alarm  │ │scheduler │ │json_storage  │ │ validator    │
└────────┘ └────┬─────┘ └──────┬───────┘ └──────────────┘
                │              │
                │     ┌────────▼───────┐
                │     │ utilities/     │
                └─────► audio          │
                      └────────────────┘
```

---

## 2. Class / Module Hierarchy

```text
core/
  └── Alarm (dataclass)
        • alarm_id : str
        • time : str
        • label : str
        • active : bool
        • created_at : str
        ├── to_dict() → dict
        ├── from_dict(dict) → Alarm
        ├── deactivate()
        ├── toggle()
        └── __str__()

  └── AlarmScheduler
        ├── start()
        ├── stop()
        ├── is_running : bool
        └── _run_loop()  [daemon thread]

storage/
  └── json_storage
        ├── load_alarms() → List[Alarm]
        ├── save_alarms(alarms)
        ├── add_alarm(alarm)
        ├── delete_alarm(alarm_id) → bool
        └── get_alarm_by_id(alarm_id) → Optional[Alarm]

utilities/
  ├── validator
  │     ├── validate_alarm_time(raw) → (bool, str|None)
  │     ├── validate_alarm_id(raw) → (bool, str|None)
  │     └── validate_label(raw) → (bool, str|None)
  │
  └── audio
        └── trigger_alarm(message)
              ├── print()         # terminal banner
              ├── sys.stdout      # bell character
              └── subprocess      # macOS "say"
```

---

## 3. Sequence Diagram — Create Alarm

```text
User              main.py           validator        json_storage
 │                  │                  │                 │
 │  1. Choose "1"   │                  │                 │
 │─────────────────►│                  │                 │
 │                  │                  │                 │
 │  2. Enter time   │                  │                 │
 │─────────────────►│                  │                 │
 │                  │  3. validate()   │                 │
 │                  │─────────────────►│                 │
 │                  │◄──── ok ─────────│                 │
 │                  │                  │                 │
 │  4. Enter label  │                  │                 │
 │─────────────────►│                  │                 │
 │                  │  5. validate()   │                 │
 │                  │─────────────────►│                 │
 │                  │◄──── ok ─────────│                 │
 │                  │                  │                 │
 │                  │  6. add_alarm()  │                 │
 │                  │──────────────────────────────────►│
 │                  │◄─── saved ────────────────────────│
 │                  │                  │                 │
 │  "Alarm created" │                  │                 │
 │◄─────────────────│                  │                 │
```

---

## 4. Sequence Diagram — Alarm Fires

```text
Clock tick        AlarmScheduler     json_storage      audio         User
 (every 1s)           │                  │               │            │
     │                │                  │               │            │
     │   1. tick      │                  │               │            │
     │───────────────►│                  │               │            │
     │                │  2. load_alarms  │               │            │
     │                │─────────────────►│               │            │
     │                │◄─── alarm list ──│               │            │
     │                │                  │               │            │
     │                │  3. HH:MM match? │               │            │
     │                │  YES (14:30)     │               │            │
     │                │                  │               │            │
     │                │  4. trigger()    │               │            │
     │                │────────────────────────────────►│            │
     │                │                  │               │  print()   │
     │                │                  │               │  bell \a   │
     │                │                  │               │  say cmd   │
     │                │                  │               │            │
     │                │  5. deactivate   │               │            │
     │                │  + save_alarms() │               │            │
     │                │─────────────────►│               │            │
     │                │◄─── saved ───────│               │            │
```

---

## 5. State Diagram — Alarm Lifecycle

```text
                         ┌─────────────┐
                         │   CREATED   │
                         │  active=True │
                         └──────┬──────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
          ┌──────────────┐           ┌──────────────┐
          │   MANUAL     │           │   TIME       │
          │   TOGGLE     │           │   MATCHED    │
          └──────┬───────┘           └──────┬───────┘
                 │                          │
                 ▼                          ▼
          ┌──────────────┐           ┌──────────────┐
          │  INACTIVE    │           │  FIRED       │
          │  active=False│           │  active=False│
          └──────┬───────┘           └──────┬───────┘
                 │                          │
                 │  toggle()                │
                 └──► CREATED ◄─────────────┘
                          (if re-enabled)

                          ┌──────────────┐
                          │   DELETED    │
                          │  (removed    │
                          │   from JSON) │
                          └──────────────┘
```

---

## 6. Data Model (JSON Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["alarm_id", "time"],
    "properties": {
      "alarm_id": {
        "type": "string",
        "pattern": "^[0-9a-f]{8}$",
        "description": "8-character hex identifier"
      },
      "time": {
        "type": "string",
        "pattern": "^(?:[01]\\d|2[0-3]):[0-5]\\d$",
        "description": "24-hour HH:MM format"
      },
      "label": {
        "type": "string",
        "maxLength": 50,
        "description": "Optional human-readable label"
      },
      "active": {
        "type": "boolean",
        "default": true,
        "description": "Whether the alarm is enabled"
      },
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "ISO 8601 timestamp"
      }
    }
  }
}
```

---

## 7. Execution Flow (threading model)

```text
┌──────────────────────────────────────────────────────────────┐
│                     MAIN THREAD                              │
│                                                              │
│  while True:                                                 │
│      _print_header()                                         │
│      display_menu()                                          │
│      choice = input()                                        │
│                                                              │
│      if choice == '1':  handle_create()     ───► add_alarm() │
│      if choice == '2':  handle_list()       ───► load_alarms │
│      if choice == '3':  handle_delete()     ───► delete()    │
│      if choice == '4':  handle_toggle()     ───► save()      │
│      if choice == '5':  sys.exit(0)                          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                   SCHEDULER THREAD (daemon)                  │
│                                                              │
│  while not stop_event:                                       │
│      alarms = load_alarms()                                  │
│      for alarm in alarms:                                    │
│          if alarm.active and alarm.time == now:              │
│              trigger_alarm()                                 │
│              alarm.deactivate()                              │
│      save_alarms(alarms)                                     │
│      stop_event.wait(1.0)                                    │
└──────────────────────────────────────────────────────────────┘