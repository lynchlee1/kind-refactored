"""
Developer Configuration File
Stores developer-level settings that can be adjusted through the popup interface
"""

import json
import os

# Default developer settings
DEFAULT_DEV_SETTINGS = {
    "buffer_time": 0.05,
    "light_loading_time": 0.5,
    "heavy_loading_time": 1.0,
    "max_wait_iterations": 30,
    "url_settle_iterations": 20,
    "content_load_wait": 0.5,
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "window_switch_timeout": 10,
    "debug_mode": False,
    # CSS Selectors
    "search_button_selector": "button[type='submit']",
    "result_row_selector": "tr[onclick*='viewDetail']",
    "company_input_selector": "input[name='companyName']",
    "from_date_selector": "input[name='fromDate']",
    "to_date_selector": "input[name='toDate']",
    "next_page_selector": "a.paging_next",
    "table_selector": "table, iframe",
    "iframe_selector": "iframe[name='viewer']"
}

DEV_CONFIG_FILE = "dev_settings.json"

def load_dev_settings():
    """Load developer settings from file, create default if not exists"""
    if os.path.exists(DEV_CONFIG_FILE):
        try:
            with open(DEV_CONFIG_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_settings = DEFAULT_DEV_SETTINGS.copy()
                merged_settings.update(settings)
                return merged_settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error loading dev settings: {e}, using defaults")
            return DEFAULT_DEV_SETTINGS.copy()
    else:
        # Create default file
        save_dev_settings(DEFAULT_DEV_SETTINGS)
        return DEFAULT_DEV_SETTINGS.copy()

def save_dev_settings(settings):
    """Save developer settings to file"""
    try:
        with open(DEV_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"⚠️ Error saving dev settings: {e}")
        return False

def update_dev_setting(key, value):
    """Update a single developer setting"""
    settings = load_dev_settings()
    settings[key] = value
    return save_dev_settings(settings)

def get_dev_setting(key, default=None):
    """Get a single developer setting"""
    settings = load_dev_settings()
    return settings.get(key, default)

# Load settings on import
DEV_SETTINGS = load_dev_settings()

# Export commonly used settings
BUFFER_TIME = DEV_SETTINGS["buffer_time"]
LIGHT_LOADING_TIME = DEV_SETTINGS["light_loading_time"]
HEAVY_LOADING_TIME = DEV_SETTINGS["heavy_loading_time"]
MAX_WAIT_ITERATIONS = DEV_SETTINGS["max_wait_iterations"]
URL_SETTLE_ITERATIONS = DEV_SETTINGS["url_settle_iterations"]
CONTENT_LOAD_WAIT = DEV_SETTINGS["content_load_wait"]
IMPLICIT_WAIT = DEV_SETTINGS["implicit_wait"]
PAGE_LOAD_TIMEOUT = DEV_SETTINGS["page_load_timeout"]
WINDOW_SWITCH_TIMEOUT = DEV_SETTINGS["window_switch_timeout"]
DEBUG_MODE = DEV_SETTINGS["debug_mode"]

# Export CSS selectors
SEARCH_BUTTON_SELECTOR = DEV_SETTINGS["search_button_selector"]
RESULT_ROW_SELECTOR = DEV_SETTINGS["result_row_selector"]
COMPANY_INPUT_SELECTOR = DEV_SETTINGS["company_input_selector"]
FROM_DATE_SELECTOR = DEV_SETTINGS["from_date_selector"]
TO_DATE_SELECTOR = DEV_SETTINGS["to_date_selector"]
NEXT_PAGE_SELECTOR = DEV_SETTINGS["next_page_selector"]
TABLE_SELECTOR = DEV_SETTINGS["table_selector"]
IFRAME_SELECTOR = DEV_SETTINGS["iframe_selector"]
