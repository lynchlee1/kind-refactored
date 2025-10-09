#!/usr/bin/env python3
"""
Simple Flask server to handle developer settings for the HTML pages
"""

from flask import Flask, jsonify, request
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

def get_system_constants_path():
    """Get the path to system_constants.json"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'system_constants.json')

def load_system_constants():
    """Load system constants from JSON file"""
    try:
        path = get_system_constants_path()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading system constants: {e}")
        return {}

def save_system_constants(data):
    """Save system constants to JSON file"""
    try:
        path = get_system_constants_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving system constants: {e}")
        return False

@app.route('/dev-settings')
def get_dev_settings():
    """Get developer settings"""
    try:
        settings = load_system_constants()
        # Only return timing and selectors sections
        filtered_settings = {
            'timing': settings.get('timing', {}),
            'selectors': settings.get('selectors', {})
        }
        return jsonify(filtered_settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save-dev-settings', methods=['POST'])
def save_dev_settings():
    """Save developer settings"""
    try:
        new_settings = request.get_json()
        
        # Load current settings
        current_settings = load_system_constants()
        
        # Update only the timing and selectors sections
        if 'timing' in new_settings:
            current_settings['timing'] = new_settings['timing']
        if 'selectors' in new_settings:
            current_settings['selectors'] = new_settings['selectors']
        
        # Save back to file
        if save_system_constants(current_settings):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/reset-dev-settings', methods=['POST'])
def reset_dev_settings():
    """Reset developer settings to default"""
    try:
        default_settings = {
            "defaults": {
                "company_name": "",
                "from_date": "2025-09-01",
                "to_date": ""
            },
            "files": {
                "results_json": "results.json",
                "saved_json_hist": "database_hist.json",
                "saved_json_prc": "database_prc.json"
            },
            "selectors": {
                "company_input_selector": "#AKCKwd",
                "from_date_selector": "input[name='fromDate']",
                "to_date_selector": "input[name='toDate']",
                "keyword_input_selector": "#reportNmTemp",
                "reset_selector": "#bfrDsclsType",
                "first_idx_selector": "#main-contents > section.scrarea.type-00 > table > tbody > tr.first.active > td.first.txc",
                "iframe_selector": "iframe[name='docViewFrm']",
                "next_page_selector": "#main-contents > section.paging-group > div.paging.type-00 > a.next",
                "result_row_selector": "table.list.type-00",
                "search_button_selector": "#searchForm > section.search-group.type-00 > div > div.btn-group.type-bt > a.btn-sprite.type-00.vmiddle.search-btn",
                "table_selector": "table, iframe"
            },
            "timing": {
                "buffer_time": 0.4,
                "long_loadtime": 3,
                "short_loadtime": 2,
                "waitcount": 10,
                "timeout": 1
            },
            "urls": {
                "details_url": "https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain#viewer"
            },
            "others": {}
        }
        
        if save_system_constants(default_settings):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to reset settings'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/')
def index():
    """Serve the API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Developer Settings API Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #e9e9e9; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>⚙️ Developer Settings API Server</h1>
        <p>This server provides developer settings management for the HTML pages.</p>
        
        <h2>Available Endpoints:</h2>
        <div class="endpoint">
            <strong>GET</strong> <code>/dev-settings</code><br>
            Get current developer settings (timing and selectors only)
        </div>
        
        <div class="endpoint">
            <strong>POST</strong> <code>/save-dev-settings</code><br>
            Save developer settings to system_constants.json
        </div>
        
        <div class="endpoint">
            <strong>POST</strong> <code>/reset-dev-settings</code><br>
            Reset developer settings to default values
        </div>
        
        <p><strong>Note:</strong> This server reads from and writes to system_constants.json file.</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("⚙️ Starting Developer Settings API Server...")
    print("📂 Reading from:", get_system_constants_path())
    print("🌐 Open http://localhost:5002 to view the API documentation")
    print("🔧 API endpoints:")
    print("   - GET  http://localhost:5002/dev-settings")
    print("   - POST http://localhost:5002/save-dev-settings")
    print("   - POST http://localhost:5002/reset-dev-settings")
    app.run(host='localhost', port=5002, debug=True)
