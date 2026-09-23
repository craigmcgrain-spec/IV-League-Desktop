import os
import json
from .db import DB_DIR

_SETTINGS_PATH = os.path.join(DB_DIR, "settings.json")

def _load():
    if os.path.exists(_SETTINGS_PATH):
        try:
            with open(_SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save(data):
    with open(_SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get(key, default=None):
    data = _load()
    return data.get(key, default)

def set_value(key, value):
    data = _load()
    data[key] = value
    _save(data)
