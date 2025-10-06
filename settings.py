import json
import os
import sys

def get_resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_json(filename):
    try:
        file_path = get_resource_path(filename)
        with open(file_path, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except: return {}
        
def save_json(filename, data):
    try:
        file_path = get_resource_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except: return False

SYSTEM = load_json("system_constants.json")

def get(key, default=None):
    for section in SYSTEM.values():
        if isinstance(section, dict) and key in section:
            return section[key]
    return default
