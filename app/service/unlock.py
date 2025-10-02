import os
import json

UNLOCK_FILE = os.path.join(os.path.dirname(__file__), "unlock_status.json")

def load_unlock_status():
    """Membaca status unlock dari file JSON."""
    if not os.path.exists(UNLOCK_FILE):
        return {"is_unlocked": False}
    try:
        with open(UNLOCK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"is_unlocked": False}

def save_unlock_status(status: bool):
    """Menyimpan status unlock ke file JSON."""
    with open(UNLOCK_FILE, "w") as f:
        json.dump({"is_unlocked": status}, f, indent=2)
