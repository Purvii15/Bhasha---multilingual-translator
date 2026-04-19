"""
history.py — Save and load translation history to a local JSON file.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = "translation_history.json"


def load_history() -> list:
    """Load translation history from JSON file. Returns empty list if not found."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_to_history(src: str, tgt: str, input_text: str, output_text: str):
    """Append a translation entry to the history file."""
    history = load_history()
    history.append({
        "src":    src,
        "tgt":    tgt,
        "input":  input_text,
        "output": output_text,
        "time":   datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep only last 100 entries to avoid bloat
    history = history[-100:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clear_history():
    """Delete the history file."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
