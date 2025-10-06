"""
Web-based user interface module
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import webbrowser
import threading
import time
import sys
import os
import socket
import threading
import time
from settings import get

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIND Project - Configuration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            background: linear-gradient(135deg, #1D79B0 0%, #1D5D8C 50%, #344B79 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 650px;
            min-height: 700px;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo {
            width: 320px;
            height: 100px;
            border-radius: 15px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }
        
        .logo img {
            width: 320px;
            height: 100px;
            object-fit: contain;
            border-radius: 10px;
        }
        
        .title {
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #6c757d;
            font-size: 16px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #007bff;
            background: white;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        
        .date-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        .checkbox {
            width: 20px;
            height: 20px;
            accent-color: #007bff;
        }
        
        .checkbox-label {
            color: #2c3e50;
            font-size: 14px;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.3);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .progress-container {
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            border-radius: 10px;
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .progress-percentage {
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #007bff;
        }
        
        .dev-mode-container {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
        
        .dev-settings {
            display: grid;
            gap: 15px;
        }
        
        .dev-setting-group {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        
        .dev-setting-group h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        }
        
        .dev-setting-item {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .dev-setting-label {
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        }
        
        .dev-setting-input {
            padding: 8px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            font-size: 12px;
        }
        
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/logo.jpg" alt="Logo">
            </div>
            <h1 class="title">KIND 행사내역 조회 프로그램</h1>
            <p class="subtitle">타임폴리오 대체투자본부</p>
        </div>
        
        <form id="configForm">
            <div class="form-group">
                <label class="form-label" for="company">기업명</label>
                <input type="text" id="company" name="company" class="form-input" 
                       value="" required>
            </div>
            
            <div class="form-group">
                <div class="date-row">
                    <div>
                        <label class="form-label" for="fromDate">시작일</label>
                        <input type="date" id="fromDate" name="fromDate" class="form-input" 
                               value="2024-09-20" required>
                    </div>
                    <div>
                        <label class="form-label" for="toDate">To Date</label>
                        <input type="date" id="toDate" name="toDate" class="form-input" 
                               value="2025-09-30" required>
                    </div>
                </div>
            </div>
            
            
            <div class="checkbox-group">
                <input type="checkbox" id="headless" name="headless" class="checkbox">
                <label for="headless" class="checkbox-label">Run in background (headless mode)</label>
            </div>
            
            <div class="button-group">
                <button type="button" class="btn btn-secondary" onclick="cancel()">Cancel</button>
                <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">Developer Mode</button>
                <button type="submit" class="btn btn-primary">Start Scraping</button>
            </div>
            
            <div class="progress-container" id="progressContainer" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-percentage" id="progressPercentage">0%</div>
            </div>
            
            <div class="dev-mode-container" id="devModeContainer" style="display: none;">
                <h3 style="margin-bottom: 20px; color: #2c3e50;">Developer Settings</h3>
                <div class="dev-settings" id="devSettings">
                    <!-- Developer settings will be loaded here -->
                </div>
                <div class="button-group" style="margin-top: 20px;">
                    <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">Save Settings</button>
                    <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">Reset to Default</button>
                    <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">Close</button>
                </div>
            </div>
        </form>
    </div>
    
    <script>
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                company_name: formData.get('company'),
                from_date: formData.get('fromDate'),
                to_date: formData.get('toDate'),
                headless: formData.has('headless')
            };
            
            // Validate dates
            const fromDate = new Date(data.from_date);
            const toDate = new Date(data.to_date);
            
            if (fromDate > toDate) {
                showStatus('From date cannot be after To date', 'error');
                return;
            }
            
            document.querySelector('.progress-container').style.display = 'block';
            document.querySelector('.button-group').style.display = 'none';
            
            checkForCompletion();
            
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                } else {
                    showStatus('Error: ' + result.message, 'error');
                    document.querySelector('.progress-container').style.display = 'none';
                    document.querySelector('.button-group').style.display = 'flex';
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
                document.querySelector('.progress-container').style.display = 'none';
                document.querySelector('.button-group').style.display = 'flex';
            });
        });
        
        function cancel() {
            fetch('/cancel', { method: 'POST' })
            .then(() => {
                console.log('Operation cancelled');
            });
        }
        
        function updateProgressBar(percentage) {
            const progressFill = document.getElementById('progressFill');
            const progressPercentage = document.getElementById('progressPercentage');
            
            progressFill.style.width = percentage + '%';
            progressPercentage.textContent = Math.round(percentage) + '%';
        }
        
        function toggleDevMode() {
            const container = document.getElementById('devModeContainer');
            if (container.style.display === 'none') {
                loadDevSettings();
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }
        
        function loadDevSettings() {
            fetch('/dev-settings')
            .then(response => response.json())
            .then(data => {
                const settingsContainer = document.getElementById('devSettings');
                settingsContainer.innerHTML = '';
                
                // Only show timing and selectors sections
                const allowedSections = ['timing', 'selectors'];
                
                Object.entries(data).forEach(([section, settings]) => {
                    if (allowedSections.includes(section)) {
                        const groupDiv = document.createElement('div');
                        groupDiv.className = 'dev-setting-group';
                        
                        const title = document.createElement('h4');
                        title.textContent = section.charAt(0).toUpperCase() + section.slice(1);
                        groupDiv.appendChild(title);
                        
                        // Sort settings by characteristic groups
                        const sortedEntries = Object.entries(settings).sort(([keyA], [keyB]) => {
                            // Define characteristic groups for better organization
                            const groups = {
                                'time': ['buffer_time', 'short_loadtime', 'long_loadtime', 'load_timeout', 'timeout'],
                                'wait': ['short_waitcount', 'long_waitcount'],
                                'date': ['from_date_selector', 'to_date_selector'],
                                'form': ['reset_selector', 'company_input_selector'],
                                'navigation': ['market_measures_selector', 'new_stock_selector', 'search_button_selector', 'next_page_selector'],
                                'content': ['result_row_selector', 'table_selector', 'iframe_selector', 'first_idx_selector']
                            };
                            
                            // Find group index for each key
                            const getGroupIndex = (key) => {
                                for (const [groupName, keys] of Object.entries(groups)) {
                                    if (keys.includes(key)) return Object.keys(groups).indexOf(groupName);
                                }
                                return 999; // Unknown keys go to end
                            };
                            
                            const groupIndexA = getGroupIndex(keyA);
                            const groupIndexB = getGroupIndex(keyB);
                            
                            // First sort by group, then alphabetically within group
                            if (groupIndexA !== groupIndexB) {
                                return groupIndexA - groupIndexB;
                            }
                            return keyA.localeCompare(keyB);
                        });
                        
                        sortedEntries.forEach(([key, value]) => {
                            const itemDiv = document.createElement('div');
                            itemDiv.className = 'dev-setting-item';
                            
                            const label = document.createElement('div');
                            label.className = 'dev-setting-label';
                            label.textContent = key;
                            
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.className = 'dev-setting-input';
                            input.value = value;
                            input.dataset.section = section;
                            input.dataset.key = key;
                            
                            itemDiv.appendChild(label);
                            itemDiv.appendChild(input);
                            groupDiv.appendChild(itemDiv);
                        });
                        
                        settingsContainer.appendChild(groupDiv);
                    }
                });
            })
            .catch(error => {
                console.error('Error loading dev settings:', error);
                showStatus('Error loading developer settings', 'error');
            });
        }
        
        function saveDevSettings() {
            const inputs = document.querySelectorAll('.dev-setting-input');
            const settings = {};
            
            // Get current full settings to preserve unchanged sections
            fetch('/dev-settings')
            .then(response => response.json())
            .then(fullSettings => {
                // Start with full settings
                Object.assign(settings, fullSettings);
                
                // Update only the editable sections
                inputs.forEach(input => {
                    const section = input.dataset.section;
                    const key = input.dataset.key;
                    
                    if (settings[section]) {
                        settings[section][key] = input.value;
                    }
                });
                
                return fetch('/save-dev-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(settings)
                });
            })
            .then(response => response.json())
            .then(result => { console.log('Developer settings save result:', result); })
            .catch(error => { console.error('Error saving dev settings:', error); });
        }
        
        function resetDevSettings() {
            if (confirm('Are you sure you want to reset all developer settings to default?')) {
                fetch('/reset-dev-settings', { method: 'POST' })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        loadDevSettings();
                        console.log('Developer settings reset to default');
                    } else {
                        console.error('Error resetting settings:', result.message);
                    }
                })
                .catch(error => {
                    console.error('Error resetting dev settings:', error);
                });
            }
        }
        
        function showCompletion() {
            updateProgressBar(100);
            document.querySelector('.progress-container').style.display = 'none';
            document.querySelector('.button-group').style.display = 'flex';
        }
        
        function checkForCompletion() {
            fetch('/check-status')
            .then(response => response.json())
            .then(data => {
                const percentage = (data && data.progress && data.progress.percentage) ? data.progress.percentage : 0;
                updateProgressBar(percentage);
                if (percentage >= 100) {
                    showCompletion();
                } else {
                    setTimeout(checkForCompletion, 3000);
                }
            })
            .catch(error => {
                setTimeout(checkForCompletion, 10000);
            });
        }
        
        
    </script>
</body>
</html>
'''

# Global variables to store the result and process status
result_data = None
server_running = False
current_port = None
progress_data = {
    'percentage': 0
}

def find_available_port(start_port=5000):
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/logo.jpg')
def logo():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(current_dir, 'logo.jpg')

@app.route('/submit', methods=['POST'])
def submit():
    global result_data, progress_data
    try:
        data = request.get_json()
        
        if not data.get('company_name'):
            return jsonify({'success': False, 'message': 'Company name is required'})
        
        
        progress_data = {'percentage': 0}
        result_data = data
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cancel', methods=['POST'])
def cancel():
    global result_data
    result_data = None
    return jsonify({'success': True})

@app.route('/progress', methods=['POST'])
def update_progress():
    global progress_data
    try:
        data = request.get_json()
        
        progress_data.update({ 'percentage': data.get('percentage', 0) })
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/check-status', methods=['GET'])
def check_status():
    global progress_data
    return jsonify({ 'progress': progress_data })

@app.route('/dev-settings', methods=['GET'])
def get_dev_settings():
    """Get developer settings"""
    try:
        from settings import SYSTEM
        return jsonify(SYSTEM)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save-dev-settings', methods=['POST'])
def save_dev_settings():
    """Save developer settings"""
    try:
        data = request.get_json()
        
        # Coerce numeric timing values to proper numbers
        try:
            timing = data.get('timing', {}) or {}
            numeric_keys = [
                'buffer_time', 'short_loadtime', 'long_loadtime',
                'long_waitcount', 'short_waitcount', 'load_timeout', 'timeout'
            ]
            for key in numeric_keys:
                if key in timing:
                    val = timing[key]
                    if isinstance(val, str):
                        # Try int first, then float
                        try:
                            if val.strip().isdigit():
                                timing[key] = int(val)
                            else:
                                timing[key] = float(val)
                        except Exception:
                            # Leave as-is if not parseable
                            pass
            data['timing'] = timing
        except Exception:
            # If anything goes wrong, proceed without coercion
            pass

        # Save to system_constants.json
        with open('system_constants.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/reset-dev-settings', methods=['POST'])
def reset_dev_settings():
    """Reset developer settings to default"""
    try:
        # Load default settings from backup or recreate them
        default_settings = {
            "urls": {
                "details_url": "https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain#viewer"
            },
            "files": {
                "output_json_file": "details_links.json",
                "output_excel_file": "results.xlsx"
            },
            "application": {
                "target_keywords": ["CB", "EB", "BW"]
            },
            "defaults": {
                "company_name": "",
                "from_date": "2025-09-16",
                "to_date": "2025-09-30"
            },
            "timing": {
                "buffer_time": 0.5,
                "short_loadtime": 2,
                "long_loadtime": 3,
                "long_waitcount": 10,
                "short_waitcount": 10,
                "load_timeout": 10,
                "timeout": 1
            },
            "selectors": {
                "reset_selector": "#bfrDsclsType",
                "market_measures_selector": "//a[contains(text(), '시장조치') or contains(@title, '시장조치')]",
                "new_stock_selector": "//input[@type='checkbox']/following-sibling::*[contains(text(), '신규/추가/변경/재상장')]/preceding-sibling::input[@type='checkbox']",
                "search_button_selector": "//form[@id='searchForm']//section[contains(@class, 'search-group')]//div[@class='btn-group type-bt']//a[contains(@class, 'search-btn')]",
                "result_row_selector": "table.list.type-00",
                "company_input_selector": "#AKCKwd",
                "from_date_selector": "input[name='fromDate']",
                "to_date_selector": "input[name='toDate']",
                "next_page_selector": "#main-contents > section.paging-group > div.paging.type-00 > a.next",
                "table_selector": "table, iframe",
                "iframe_selector": "iframe[name='docViewFrm']",
                "first_idx_selector": "#main-contents > section.scrarea.type-00 > table > tbody > tr.first.active > td.first.txc"
            }
        }
        
        with open('system_constants.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def start_server():
    global server_running, current_port
    server_running = True
    current_port = find_available_port()
    os.environ['WEB_UI_PORT'] = str(current_port)
    
    print(f"Starting server on port {current_port}")
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=current_port, debug=False, use_reloader=False)

def get_user_input():
    global result_data, server_running, current_port
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(get("buffer_time"))
    if current_port: webbrowser.open(f'http://127.0.0.1:{current_port}')
    else: return None
    while server_running:
        if result_data is not None:
            break
        time.sleep(0.1)
    return result_data

if __name__ == "__main__":
    result = get_user_input()
    if result:
        print("User input:", result)
    else:
        print("User cancelled")
