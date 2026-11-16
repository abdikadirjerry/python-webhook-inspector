import json
from pathlib import Path

EVENTS_FILE = Path("data/events.json")
MAX_EVENTS = 100

def load_events() -> list[dict]:
    if not EVENTS_FILE.exists():
        return []
    return json.loads(EVENTS_FILE.read_text(encoding="utf-8"))

def save_event(event: dict) -> dict:
    events = load_events()
    events.insert(0, event)
    events = events[:MAX_EVENTS]
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_FILE.write_text(json.dumps(events, indent=2), encoding="utf-8")
    return event

def clear_all_events() -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_FILE.write_text("[]", encoding="utf-8")