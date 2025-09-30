import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "theme_config.json")

THEMES = {
    "emerald_glass": {
        "border_primary": "#10B981",
        "border_info": "#34D399",
        "border_success": "#059669",
        "border_warning": "#A3E635",
        "border_error": "#EF4444",
        "text_title": "bold #ECFDF5",
        "text_sub": "bold #34D399",
        "text_ok": "bold #22C55E",
        "text_warn": "bold #A3E635",
        "text_err": "bold #F87171",
        "text_body": "#D1FAE5",
        "text_key": "#6EE7B7",
        "text_value": "bold #F0FDFA",
        "text_money": "bold #22C55E",
        "text_date": "bold #A3E635",
        "text_number": "#10B981",
        "gradient_start": "#34D399",
        "gradient_end": "#A7F3D0"
    },
    "sunset_blaze": {
        "border_primary": "#F97316",
        "border_info": "#FDBA74",
        "border_success": "#EA580C",
        "border_warning": "#FACC15",
        "border_error": "#DC2626",
        "text_title": "bold #FFEDD5",
        "text_sub": "bold #FB923C",
        "text_ok": "bold #F59E0B",
        "text_warn": "bold #FBBF24",
        "text_err": "bold #F87171",
        "text_body": "#FFF7ED",
        "text_key": "#FDBA74",
        "text_value": "bold #FFFBEB",
        "text_money": "bold #F59E0B",
        "text_date": "bold #FBBF24",
        "text_number": "#F97316",
        "gradient_start": "#FB923C",
        "gradient_end": "#FDE68A"
    },
    "ocean_wave": {
        "border_primary": "#0EA5E9",
        "border_info": "#38BDF8",
        "border_success": "#0284C7",
        "border_warning": "#FCD34D",
        "border_error": "#EF4444",
        "text_title": "bold #E0F2FE",
        "text_sub": "bold #38BDF8",
        "text_ok": "bold #0EA5E9",
        "text_warn": "bold #FCD34D",
        "text_err": "bold #F87171",
        "text_body": "#BAE6FD",
        "text_key": "#7DD3FC",
        "text_value": "bold #E0F2FE",
        "text_money": "bold #0EA5E9",
        "text_date": "bold #FCD34D",
        "text_number": "#0284C7",
        "gradient_start": "#38BDF8",
        "gradient_end": "#A5F3FC"
    },
    "midnight_shadow": {
        "border_primary": "#4B5563",
        "border_info": "#6B7280",
        "border_success": "#374151",
        "border_warning": "#FBBF24",
        "border_error": "#DC2626",
        "text_title": "bold #F9FAFB",
        "text_sub": "bold #9CA3AF",
        "text_ok": "bold #6EE7B7",
        "text_warn": "bold #FBBF24",
        "text_err": "bold #F87171",
        "text_body": "#D1D5DB",
        "text_key": "#9CA3AF",
        "text_value": "bold #F3F4F6",
        "text_money": "bold #6EE7B7",
        "text_date": "bold #FBBF24",
        "text_number": "#4B5563",
        "gradient_start": "#6B7280",
        "gradient_end": "#9CA3AF"
    },
    "lavender_dream": {
        "border_primary": "#A78BFA",
        "border_info": "#C4B5FD",
        "border_success": "#8B5CF6",
        "border_warning": "#FDE68A",
        "border_error": "#F87171",
        "text_title": "bold #F3E8FF",
        "text_sub": "bold #C4B5FD",
        "text_ok": "bold #A78BFA",
        "text_warn": "bold #FDE68A",
        "text_err": "bold #F87171",
        "text_body": "#EDE9FE",
        "text_key": "#DDD6FE",
        "text_value": "bold #FAF5FF",
        "text_money": "bold #A78BFA",
        "text_date": "bold #FDE68A",
        "text_number": "#8B5CF6",
        "gradient_start": "#C4B5FD",
        "gradient_end": "#E9D5FF"
    },
    "dark_neon": {
        "border_primary": "#7C3AED",
        "border_info": "#06B6D4",
        "border_success": "#10B981",
        "border_warning": "#F59E0B",
        "border_error": "#EF4444",
        "text_title": "bold #E5E7EB",
        "text_sub": "bold #22D3EE",
        "text_ok": "bold #34D399",
        "text_warn": "bold #FBBF24",
        "text_err": "bold #F87171",
        "text_body": "#D1D5DB",
        "text_key": "#A78BFA",
        "text_value": "bold #F3F4F6",
        "text_money": "bold #34D399",
        "text_date": "bold #FBBF24",
        "text_number": "#C084FC",
        "gradient_start": "#22D3EE",
        "gradient_end": "#A78BFA",
    }
}

def _load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"active_theme": "emerald_glass"}

def _save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def get_active_theme_name():
    config = _load_config()
    return config.get("active_theme", "emerald_glass")

def get_theme():
    theme_name = get_active_theme_name()
    return THEMES.get(theme_name, THEMES["emerald_glass"])

def set_theme(name):
    if name in THEMES:
        _save_config({"active_theme": name})
        return True
    return False

def get_all_presets():
    return THEMES
