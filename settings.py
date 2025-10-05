import json
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running as script, use current directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_json(filename):
    try:
        file_path = get_resource_path(filename)
        with open(file_path, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filename}: {e}")
        return {}
        
SYSTEM = load_json("system_constants.json")
USER = load_json("user_settings.json")


def save_json(filename, data):
    try:
        file_path = get_resource_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f: 
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Warning: Could not save {filename}: {e}")
        return False


def get(key, default=None):
    if key in USER: return USER[key]
    for section in SYSTEM.values(): 
        if isinstance(section, dict) and key in section: return section[key]
    return default


def set_user(key, value):
    USER[key] = value
    save_json("user_settings.json", USER)
