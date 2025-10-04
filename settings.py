import json

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}
SYSTEM = load_json("system_constants.json")
USER = load_json("user_settings.json")


def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except: return False


def get(key, default=None):
    if key in USER: return USER[key]
    for section in SYSTEM.values(): 
        if isinstance(section, dict) and key in section: return section[key]
    return default


def set_user(key, value):
    USER[key] = value
    save_json("user_settings.json", USER)
