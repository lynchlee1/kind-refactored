# kind_ui.py
import webbrowser
import threading
import time
import os
import socket
import json

# Flask imports will be done conditionally when needed
try:
    from flask import Flask, render_template_string, request, jsonify, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    render_template_string = None
    request = None
    jsonify = None
    send_from_directory = None

app = None
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _ensure_flask():
    """Ensure Flask is available and app is initialized"""
    global app
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is not available. Please install it with: pip install flask")
    if app is None:
        app = Flask(__name__)
    return app

class BasicPage:
    def __init__(self, title="Page", container_width="650px", container_height="700px"):
        self.title = title
        self.container_width = container_width
        self.container_height = container_height
        self.elements = []
        self.scripts = []
    
    def element_header(self, logo_url="/logo.jpg", logo_width="320px", logo_height="100px", 
                      title="KIND 행사내역 조회 프로그램", subtitle="타임폴리오 대체투자본부"):
        return f'''
        <div class="header">
            <div class="logo">
                <img src="{logo_url}" alt="Logo" style="width:{logo_width};height:{logo_height};object-fit:contain;border-radius:10px;">
            </div>
            <h1 class="title">{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        '''
    
    def element_form_group(self, label_text, input_type="text", input_id="", input_name="", 
                          input_placeholder="", input_value="", required=False, input_class="form-input"):
        required_attr = "required" if required else ""
        return f'''
        <div class="form-group">
            <label class="form-label" for="{input_id}">{label_text}</label>
            <input type="{input_type}" id="{input_id}" name="{input_name}" 
                   class="{input_class}" placeholder="{input_placeholder}" 
                   value="{input_value}" {required_attr}>
        </div>
        '''
    
    def element_date(self, from_date_label="시작일", to_date_label="종료일", 
                        from_date_id="fromDate", to_date_id="toDate", 
                        from_date_value="2024-01-01", to_date_value="2025-01-01"):
        return f'''
        <div class="form-group">
            <div class="date-row">
                <div>
                    <label class="form-label" for="{from_date_id}">{from_date_label}</label>
                    <input type="date" id="{from_date_id}" name="{from_date_id}" class="form-input" 
                           value="{from_date_value}" required>
                </div>
                <div>
                    <label class="form-label" for="{to_date_id}">{to_date_label}</label>
                    <input type="date" id="{to_date_id}" name="{to_date_id}" class="form-input" 
                           value="{to_date_value}" required>
                </div>
            </div>
        </div>
        '''
    
    def element_checkbox(self, checkbox_id, checkbox_name, label_text, checked=False):
        checked_attr = "checked" if checked else ""
        return f'''
        <div class="checkbox-group">
            <input type="checkbox" id="{checkbox_id}" name="{checkbox_name}" class="checkbox" {checked_attr}>
            <label for="{checkbox_id}" class="checkbox-label">{label_text}</label>
        </div>
        '''
    
    def element_button(self, button_id, button_text, button_type="button", 
                      button_class="btn btn-primary", onclick="", style="", hidden=False):
        hidden_style = "display:none" if hidden else ""
        combined_style = f"{hidden_style};{style}" if style else hidden_style
        style_attr = f'style="{combined_style}"' if combined_style else ""
        onclick_attr = f'onclick="{onclick}"' if onclick else ""
        return f'''
        <button id="{button_id}" type="{button_type}" class="{button_class}" 
                {onclick_attr} {style_attr}>{button_text}</button>
        '''
    
    def element_button_group(self, buttons):
        button_html = ""
        for button in buttons:
            button_html += self.element_button(**button)
        return f'''
        <div class="button-group">
            {button_html}
        </div>
        '''
    
    def element_progress_container(self, container_id="progressContainer", hidden=True):
        display_style = "display: none;" if hidden else ""
        return f'''
        <div class="progress-container" id="{container_id}" style="{display_style}">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-percentage" id="progressPercentage">0%</div>
        </div>
        '''
    
    def element_info_panel(self, panel_id="companyInfo", hidden=True):
        display_style = "display: none;" if hidden else ""
        return f'''
        <div id="{panel_id}" class="info-panel" style="{display_style}"></div>
        '''
    
    def element_dev_settings(self, hidden=True):
        display_style = "display: none;" if hidden else ""
        return f'''
        <div class="dev-mode-container" id="devModeContainer" style="{display_style}">
            <h3 style="margin-bottom: 20px; color: #2c3e50;">Developer Settings</h3>
            <div class="dev-settings" id="devSettings">
                <!-- Developer settings will be loaded here -->
            </div>
            <div class="button-group" style="margin-top: 20px;">
                <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">저장</button>
                <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">초기화</button>
                <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">닫기</button>
            </div>
        </div>
        '''
    
    def add_element(self, element_html):
        self.elements.append(element_html)
    
    def add_script(self, script_content):
        self.scripts.append(script_content)
    
    def generate_html(self, form_id="configForm"):
        elements_html = "\n".join(self.elements)
        scripts_html = "\n".join(self.scripts)
        
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            background: linear-gradient(135deg, #1D79B0 0%, #1D5D8C 50%, #344B79 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .button-group {{ 
            display: flex; 
            gap: 12px; 
            justify-content: center; 
            flex-wrap: wrap; 
        }}
        .btn {{ 
            white-space: nowrap; 
            min-width: 110px; 
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: {self.container_width};
            min-height: {self.container_height};
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .logo {{
            width: 320px;
            height: 100px;
            border-radius: 15px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }}
        
        .title {{
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            color: #6c757d;
            font-size: 16px;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        .form-label {{
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .form-input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: #007bff;
            background: white;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }}
        
        .date-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .checkbox-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
        }}
        
        .checkbox {{
            width: 20px;
            height: 20px;
            accent-color: #007bff;
        }}
        
        .checkbox-label {{
            color: #2c3e50;
            font-size: 14px;
        }}
        
        .button-group {{
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.3);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
            transform: translateY(-2px);
        }}
        
        .status {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            display: none;
        }}
        
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .info-panel {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 12px;
            background: #eef7ff;
            border: 1px solid #cfe6ff;
            color: #0c4a6e;
            display: none;
            font-size: 14px;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            margin-top: 20px;
        }}
        
        .progress-container {{
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            border-radius: 10px;
            transition: width 0.3s ease;
            width: 0%;
        }}
        
        .progress-percentage {{
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #007bff;
        }}
        
        .dev-mode-container {{
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }}
        
        .dev-settings {{
            display: grid;
            gap: 15px;
        }}
        
        .dev-setting-group {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        
        .dev-setting-group h4 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .dev-setting-item {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .dev-setting-label {{
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        }}
        
        .dev-setting-input {{
            padding: 8px;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <form id="{form_id}">
            {elements_html}
        </form>
    </div>
    
    <script>
        {scripts_html}
    </script>
</body>
</html>
        '''

def main_page():
    page = BasicPage(title="KIND Project", container_width="650px", container_height="700px")
    page.add_element(page.element_header(title="KIND 자동 다운로드 프로그램", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_form_group("기업명", "text", "corp_name", "corp_name", "기업명을 입력하세요", "", True))

    buttons = [
        {"button_id": "run_hist", "button_text": "추가상장 기록 조회", "button_type": "submit", "button_class": "btn btn-primary"},
        {"button_id": "run_prc", "button_text": "전환가액 변동 조회", "button_type": "submit", "button_class": "btn btn-primary"},
    ]
    page.add_element(page.element_button_group(buttons))

    page.add_script('''
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const corpName = document.getElementById('corp_name').value.trim();
            if (!corpName) {
                alert('기업명을 입력해주세요.');
                return;
            }
                
            const clickedButton = document.activeElement.id;
            if (clickedButton === 'run_hist') {
                window.location.href = `/hist_page?corp_name=${encodeURIComponent(corpName)}`;
            } else if (clickedButton === 'run_prc') {
                window.location.href = `/prc_page?corp_name=${encodeURIComponent(corpName)}`;
            }
        });
    ''')
    return page.generate_html()

def hist_page():
    page = BasicPage(title="추가상장 기록 조회", container_width="800px", container_height="900px")
    page.add_element(page.element_header(title="추가상장 기록 조회", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_form_group("기업명", "text", "company", "company", "기업명을 입력하세요", "", True))
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    page.add_element(page.element_info_panel())
    return page.generate_html()
    
def prc_page():
    page = BasicPage(title="전환가액 변동 조회", container_width="800px", container_height="900px")
    page.add_element(page.element_header(title="전환가액 변동 조회", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_form_group("기업명", "text", "company", "company", "기업명을 입력하세요", "", True))
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    page.add_element(page.element_info_panel())
    return page.generate_html()

def create_data_entry_page():
    """Example: Create a data entry page"""
    page = BasicPage(title="Data Entry", container_width="800px", container_height="900px")
    
    # Add header
    page.add_element(page.element_header())
    
    # Add form elements
    page.add_element(page.element_form_group("기업명", "text", "company", "company", "기업명을 입력하세요", "", True))
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    
    # Add info panel
    page.add_element(page.element_info_panel())
    
    # Add buttons
    buttons = [
        {"button_id": "backBtn", "button_text": "이전", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "history.back()"},
        {"button_id": "runBtn", "button_text": "실행", "button_type": "submit", "button_class": "btn btn-primary"},
        {"button_id": "devBtn", "button_text": "개발자 설정", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "toggleDevMode()"}
    ]
    page.add_element(page.element_button_group(buttons))
    
    # Add progress container
    page.add_element(page.element_progress_container())
    
    # Add dev settings
    page.add_element(page.element_dev_settings())
    
    return page.generate_html()


def create_settings_page():
    """Example: Create a settings configuration page"""
    page = BasicPage(title="Settings", container_width="700px", container_height="800px")
    
    # Add header
    page.add_element(page.element_header(title="설정", subtitle="시스템 설정을 변경하세요"))
    
    # Add various form elements
    page.add_element(page.element_form_group("서버 주소", "url", "server", "server", "https://example.com", "https://localhost:8080"))
    page.add_element(page.element_form_group("포트 번호", "number", "port", "port", "포트 번호", "8080"))
    page.add_element(page.element_form_group("데이터베이스 경로", "text", "dbpath", "dbpath", "데이터베이스 파일 경로", "/data/database.db"))
    
    # Add checkbox for auto-save
    page.add_element(page.element_checkbox("autosave", "autosave", "자동 저장 활성화", True))
    
    # Add buttons
    buttons = [
        {"button_id": "saveBtn", "button_text": "저장", "button_type": "submit", "button_class": "btn btn-primary"},
        {"button_id": "resetBtn", "button_text": "초기화", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "resetSettings()"},
        {"button_id": "cancelBtn", "button_text": "취소", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "history.back()"}
    ]
    page.add_element(page.element_button_group(buttons))
    
    # Add JavaScript
    page.add_script('''
        function resetSettings() {
            if (confirm('설정을 초기값으로 되돌리시겠습니까?')) {
                document.getElementById('server').value = 'https://localhost:8080';
                document.getElementById('port').value = '8080';
                document.getElementById('dbpath').value = '/data/database.db';
                document.getElementById('autosave').checked = true;
            }
        }
        
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('설정이 저장되었습니다.');
        });
    ''')
    
    return page.generate_html()

def create_simple_login_page():
    """Create a simple login page using BasicPage"""
    page = BasicPage(title="Login", container_width="500px", container_height="600px")
    
    # Add header
    page.add_element(page.element_header(title="로그인", subtitle="시스템에 접속하세요"))
    
    # Add form elements
    page.add_element(page.element_form_group("사용자명", "text", "username", "username", "사용자명을 입력하세요", "", True))
    page.add_element(page.element_form_group("비밀번호", "password", "password", "password", "비밀번호를 입력하세요", "", True))
    
    # Add buttons
    buttons = [
        {"button_id": "loginBtn", "button_text": "로그인", "button_type": "submit", "button_class": "btn btn-primary"},
        {"button_id": "cancelBtn", "button_text": "취소", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "history.back()"}
    ]
    page.add_element(page.element_button_group(buttons))
    
    # Add form validation JavaScript
    page.add_script('''
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!username || !password) {
                alert('사용자명과 비밀번호를 모두 입력해주세요.');
                return;
            }
            
            // Here you would typically send the credentials to your server
            alert('로그인 기능이 구현되지 않았습니다.\\n사용자명: ' + username + '\\n비밀번호: ' + password);
        });
    ''')
    
    return page.generate_html()


result_data = None
server_running = False
current_port = None
progress_data = {
    'percentage': 0,
    'first_report_number': None
}
ui_opened = False

DATABASE_UNIV_FILE = os.path.join(ROOT_DIR, "database_map.json")

def find_available_port(start_port=5000):
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")


def _load_modes():
    if not os.path.exists(DATABASE_UNIV_FILE):
        return {}
    try:
        with open(DATABASE_UNIV_FILE, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
            # ensure keys are strings and values are strings
            cleaned = {}
            for k, v in data.items():
                if isinstance(k, str) and isinstance(v, str):
                    cleaned[k.strip()] = v.strip()
            return cleaned
    except Exception:
        return {}


def _db_path_for_mode(mode):
    """
    Resolve the database file path for a given mode via database_univ.json.
    If missing, fallback to database_<mode>.json in ROOT_DIR.
    """
    modes = _load_modes()
    rel = modes.get(mode)
    if rel:
        return os.path.join(ROOT_DIR, rel)
    # Fallback
    return os.path.join(ROOT_DIR, f"database_{mode}.json")


def _load_db(mode):
    try:
        path = _db_path_for_mode(mode)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


# -----------------------------
# HTML Templates
# -----------------------------

MAIN_PAGE_HTML = '''
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
        
        .button-group { 
            display: flex; 
            gap: 12px; 
            justify-content: center; 
            flex-wrap: wrap; 
        }
        .btn { 
            white-space: nowrap; 
            min-width: 110px; 
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
        .info-panel {
            margin: 20px 0;
            padding: 15px;
            border-radius: 12px;
            background: #eef7ff;
            border: 1px solid #cfe6ff;
            color: #0c4a6e;
            display: none;
            font-size: 14px;
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
            <div class="form-group" id="companyGroup">
                <label class="form-label" for="company">기업명</label>
                <input type="text" id="company" name="company" class="form-input" 
                       value="" required>
    </div>
            <div id="companyInfo" class="info-panel"></div>

    <div class="form-group">
                <div class="date-row" id="dateRow">
                    <div>
                        <label class="form-label" for="fromDate">검색 시작일</label>
                        <input type="date" id="fromDate" name="fromDate" class="form-input" 
                               value="2024-09-20" required>
        </div>
                    <div>
                        <label class="form-label" for="toDate">검색 종료일</label>
                        <input type="date" id="toDate" name="toDate" class="form-input" 
                               value="2025-09-30" required>
      </div>
    </div>
            </div>
            
            
            <div class="checkbox-group" id="headlessRow">
                <input type="checkbox" id="headless" name="headless" class="checkbox">
                <label for="headless" class="checkbox-label">Chrome 팝업 없이 실행하기</label>
            </div>
            
            <div class="button-group">
                <button id="backBtn" type="button" class="btn btn-secondary" onclick="goBack()">이전</button>
                <button id="devBtn" type="button" class="btn btn-secondary" onclick="toggleDevMode()" style="display:none">개발자 설정</button>
                <button id="runBtn" type="submit" class="btn btn-primary" style="display:none">실행</button>
                <button id="nextBtn" type="button" class="btn btn-primary" onclick="goNext()">전환내역</button>
                <button id="convBtn" type="button" class="btn btn-primary" onclick="goNext('conv')">전환가액</button>
                <button id="recordsBtn" type="button" class="btn btn-primary" onclick="openRecords()" style="display:none">기록 보기</button>
                <button id="closeBtn" type="button" class="btn btn-secondary" onclick="closeApplication()" style="display:none">닫기</button>
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
                    <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">저장</button>
                    <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">되돌리기</button>
                    <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">닫기</button>
                </div>
            </div>
        </form>
  </div>

<script>
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Only submit if we're on the second page (company info is visible)
            const companyInfo = document.getElementById('companyInfo');
            if (!companyInfo || companyInfo.style.display === 'none' || companyInfo.style.display === '') {
                // On first page - trigger Next button instead
                goNext();
                return;
            }
            
            const formData = new FormData(this);
            const data = {
                company_name: formData.get('company'),
                from_date: formData.get('fromDate'),
                to_date: formData.get('toDate'),
                headless: formData.has('headless'),
                mode: (new URL(window.location.href)).searchParams.get('mode') || 'hist'
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
                    // start polling only after server accepted submission
                    setTimeout(checkForCompletion, 150);
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
        
        function goBack() {
            const url = new URL(window.location.href);
            if (url.searchParams.has('company')) {
                url.searchParams.delete('company');
                window.location.href = url.toString();
                return;
            }
            window.history.back();
        }
        
        function closeApplication() {
            fetch('/close', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.close();
                }
            })
            .catch(error => {
                console.error('Error closing application:', error);
                window.close();
            });
        }
        
        function updateProgressBar(percentage, firstReportNumber) {
            const progressFill = document.getElementById('progressFill');
            const progressPercentage = document.getElementById('progressPercentage');
            
            progressFill.style.width = percentage + '%';
            let text = Math.round(percentage) + '%';
            if (firstReportNumber) {
                text += ` (전체 ${firstReportNumber}개 발견됨)`;
            }
            progressPercentage.textContent = text;
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
        function openRecords() {
            const company = getQueryParam('company');
            // Ask for 회차 before navigating
            const round = window.prompt('회차를 입력하세요 (비워두면 전체 표시)');
            const url = new URL(window.location.href);
            url.pathname = '/records';
            if (company) url.searchParams.set('company', company);
            // pass mode from query if present
            const mode = getQueryParam('mode') || 'hist';
            url.searchParams.set('mode', mode);
            if (round && round.trim().length > 0) url.searchParams.set('round', round.trim());
            window.location.href = url.toString();
        }
        function getQueryParam(name) {
            const url = new URL(window.location.href);
            return url.searchParams.get(name);
        }
        document.addEventListener('DOMContentLoaded', function() {
            const hasCompany = !!getQueryParam('company');
            const dateRow = document.getElementById('dateRow');
            const headlessRow = document.getElementById('headlessRow');
            if (dateRow) dateRow.style.display = hasCompany ? 'grid' : 'none';
            if (headlessRow) headlessRow.style.display = hasCompany ? 'flex' : 'none';
        });
        function goNext(mode){
            const name = document.getElementById('company').value.trim();
            if (!name) return;
            const url = new URL(window.location.href);
            url.searchParams.set('company', name);
            if (mode && typeof mode === 'string') {
                url.searchParams.set('mode', mode);
            } else if (!url.searchParams.get('mode')) {
                url.searchParams.set('mode', 'hist');
            }
            // Always navigate to ensure second page is shown
            window.location.href = url.toString();
        }
        function initCompanyView() {
            const company = getQueryParam('company');
            const companyInput = document.getElementById('company');
            const infoPanel = document.getElementById('companyInfo');
            const runBtn = document.getElementById('runBtn');
            const devBtn = document.getElementById('devBtn');
            const nextBtn = document.getElementById('nextBtn');
            const convBtn = document.getElementById('convBtn');
            const backBtn = document.getElementById('backBtn');
            const dateRow = document.getElementById('dateRow');
            const headlessRow = document.getElementById('headlessRow');
            const companyGroup = document.getElementById('companyGroup');
            const recordsBtn = document.getElementById('recordsBtn');

            // ensure mode is set in URL
            const currentUrl = new URL(window.location.href);
            if (!currentUrl.searchParams.get('mode')) {
                currentUrl.searchParams.set('mode', 'hist');
                window.history.replaceState({}, '', currentUrl.toString());
            }
            const mode = currentUrl.searchParams.get('mode') || 'hist';

            if (company) {
                companyInput.value = company;
                // Show run/dev/records and hide next
                runBtn.style.display = 'inline-block';
                devBtn.style.display = 'inline-block';
                nextBtn.style.display = 'none';
                if (convBtn) convBtn.style.display = 'none';
                if (backBtn) backBtn.style.display = 'inline-block';
                if (recordsBtn) recordsBtn.style.display = 'inline-block';
                if (dateRow) dateRow.style.display = 'grid';
                if (headlessRow) headlessRow.style.display = 'flex';
                if (companyGroup) companyGroup.style.display = 'none';

                const fromInput = document.getElementById('fromDate');
                const toInput = document.getElementById('toDate');
                const today = new Date();
                const yyyy = today.getFullYear();
                const mm = String(today.getMonth() + 1).padStart(2, '0');
                const dd = String(today.getDate()).padStart(2, '0');
                const todayStr = `${yyyy}-${mm}-${dd}`;
                if (toInput) toInput.value = todayStr;

                fetch(`/company-info?name=${encodeURIComponent(company)}&mode=${encodeURIComponent(mode)}`)
                    .then(r => r.json())
                    .then(info => {
                        if (info && info.found) {
                            // Populate fromDate with stored last_date (last renew date); keep toDate as today
                            if (info.last_date && fromInput) fromInput.value = info.last_date;
                            infoPanel.innerHTML = `<b>${company}</b> : ${info.first_date || '-'} ~ ${info.last_date || '-'} 저장됨 (${info.count || 0}개 발견)`;
                        } else {
                            infoPanel.innerHTML = `저장된 데이터가 없습니다.`;
                        }
                        infoPanel.style.display = 'block';
                    })
                    .catch(() => {
                        infoPanel.innerHTML = `저장된 데이터를 불러올 수 없습니다.`;
                        infoPanel.style.display = 'block';
                    });
            } else {
                runBtn.style.display = 'none';
                devBtn.style.display = 'none';
                nextBtn.style.display = 'inline-block';
                if (convBtn) convBtn.style.display = 'inline-block';
                if (backBtn) backBtn.style.display = 'none';
                if (recordsBtn) recordsBtn.style.display = 'none';
                infoPanel.style.display = 'none';
                if (dateRow) dateRow.style.display = 'none';
                if (headlessRow) headlessRow.style.display = 'none';
                if (companyGroup) companyGroup.style.display = 'block';
            }
        }
        // Initialize view on load
        initCompanyView();
        
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
                                'time': ['buffer_time', 'short_loadtime', 'long_loadtime'],
                                'wait': ['waitcount', 'timeout'],
                                'date': ['from_date_selector', 'to_date_selector'],
                                'form': ['reset_selector', 'company_input_selector', 'keyword_input_selector'],
                                'navigation': ['search_button_selector', 'next_page_selector'],
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
            const progressContainer = document.querySelector('.progress-container');
            if (progressContainer) progressContainer.style.display = 'none';
            const buttonGroup = document.querySelector('.button-group');
            if (buttonGroup) buttonGroup.style.display = 'flex';

            const runBtn = document.getElementById('runBtn');
            const devBtn = document.getElementById('devBtn');
            const nextBtn = document.getElementById('nextBtn');
            const backBtn = document.getElementById('backBtn');
            const convBtn = document.getElementById('convBtn');
            const recordsBtn = document.getElementById('recordsBtn');
            const closeBtn = document.getElementById('closeBtn');

            if (runBtn) runBtn.style.display = 'none';
            if (devBtn) devBtn.style.display = 'none';
            if (nextBtn) nextBtn.style.display = 'inline-block';
            if (convBtn) convBtn.style.display = 'inline-block';
            if (recordsBtn) recordsBtn.style.display = 'none';
            if (backBtn) backBtn.style.display = 'none';
            if (closeBtn) closeBtn.style.display = 'none';

            // Go to FIRST page state
            const companyGroup = document.getElementById('companyGroup');
            const dateRow = document.getElementById('dateRow');
            const headlessRow = document.getElementById('headlessRow');
            const companyInfo = document.getElementById('companyInfo');
            if (companyGroup) companyGroup.style.display = 'block';
            if (dateRow) dateRow.style.display = 'none';
            if (headlessRow) headlessRow.style.display = 'none';
            if (companyInfo) { companyInfo.style.display = 'none'; companyInfo.innerHTML = ''; }

            // Remove company from URL
            const url = new URL(window.location.href);
            url.searchParams.delete('company');
            window.history.replaceState({}, '', url.toString());
            const input = document.getElementById('company');
            if (input) input.value = '';
        }
        
        function checkForCompletion() {
            fetch('/check-status')
            .then(response => response.json())
            .then(data => {
                const percentage = (data && data.progress && data.progress.percentage) ? data.progress.percentage : 0;
                const firstReportNumber = (data && data.progress && data.progress.first_report_number) ? data.progress.first_report_number : null;
                updateProgressBar(percentage, firstReportNumber);
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

PAGE2_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KIND UI · {{ mode }} · Page 2</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{
    font-family:'Segoe UI','Microsoft YaHei','Malgun Gothic',Arial,sans-serif;
    background:#f5f7fb;min-height:100vh;padding:20px;display:flex;align-items:flex-start;justify-content:center
  }
  .container{
    background:#fff;border-radius:20px;padding:24px;max-width:880px;width:100%;min-height:500px;
    border:1px solid #e6ecff;box-shadow:0 8px 22px rgba(13,110,253,.06)
  }
  .top{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:10px}
  .title{font-size:28px;font-weight:700;color:#1d2a3a}
  .sub{color:#51606e}
  .panel{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}
  .card{background:#f9fbff;border:1px solid #e3ecff;border-radius:12px;padding:16px}
  .label{display:block;font-weight:600;color:#1f2d3d;margin-bottom:8px;font-size:14px}
  .input{width:100%;padding:15px;border:1.5px solid #dfe7fb;border-radius:10px;font-size:16px;background:#fff;font-family:'Segoe UI','Microsoft YaHei','Malgun Gothic',Arial,sans-serif}
  .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .btn{border:none;border-radius:12px;padding:15px 30px;font-size:16px;font-weight:600;cursor:pointer;transition:.2s}
  .btn-primary{background:linear-gradient(135deg,#007bff,#0056b3);color:#fff}
  .btn-secondary{background:#6c757d;color:#fff}
  .btn:hover{transform:translateY(-2px)}
  .kvs{font-size:13px;color:#5b6b7a;margin-top:6px}
  .badge{display:inline-block;background:#eef5ff;color:#0c4a6e;border:1px solid #cfe1ff;border-radius:999px;padding:4px 10px;font-size:12px}
  .progress{margin-top:16px;background:#f1f5ff;border:1px solid #d9e5ff;border-radius:12px;padding:12px;display:none}
  .bar{height:18px;background:#e7efff;border-radius:10px;overflow:hidden}
  .fill{height:100%;width:0%;background:linear-gradient(90deg,#007bff,#4b7bfd);transition:width .3s}
  .pct{text-align:center;font-weight:900;color:#2152a3;margin-top:8px}
  .note{font-size:13px;color:#51606e;margin-top:8px}
</style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div>
        <div class="badge">Page 2 · Mode: {{ mode }}</div>
        <h1 class="title" style="margin-top:6px">{{ company or '-' }}</h1>
        <div class="sub">해당 모드 전용 페이지입니다. 데이터베이스 파일은 <b>{{ db_rel }}</b> 입니다.</div>
      </div>
      <div class="row">
        <button class="btn btn-secondary" onclick="history.back()">이전</button>
        <a class="btn btn-secondary" href="/" style="text-decoration:none;display:inline-block">처음으로</a>
      </div>
    </div>

    <div class="panel">
      <div class="card">
        <label class="label">검색 시작일</label>
        <input id="fromDate" class="input" type="date" />
        <div class="kvs">오늘 날짜를 기본 종료일로 설정합니다.</div>
      </div>
      <div class="card">
        <label class="label">검색 종료일</label>
        <input id="toDate" class="input" type="date" />
      </div>
    </div>

    <div class="row" style="margin-top:10px">
      <button id="openDbBtn" class="btn btn-secondary">데이터베이스 열기</button>
      <button id="runBtn" class="btn btn-primary">실행</button>
    </div>

    <div id="progressBox" class="progress">
      <div class="bar"><div id="fill" class="fill"></div></div>
      <div id="pct" class="pct">0%</div>
      <div class="note">작업이 완료되면 자동으로 초기화됩니다.</div>
    </div>
  </div>

<script>
  const params = new URLSearchParams(location.search);
  const company = params.get('company') || '';
  const mode = "{{ mode }}";

  function setToday(){
    const to = document.getElementById('toDate');
    const d = new Date();
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth()+1).padStart(2,'0');
    const dd = String(d.getDate()).padStart(2,'0');
    to.value = `${yyyy}-${mm}-${dd}`;
  }

  function setDefaultFrom(){
    const from = document.getElementById('fromDate');
    // default: 1 year ago
    const d = new Date();
    d.setFullYear(d.getFullYear()-1);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth()+1).padStart(2,'0');
    const dd = String(d.getDate()).padStart(2,'0');
    from.value = `${yyyy}-${mm}-${dd}`;
  }

  function openDb(){
    window.open(`/database?mode=${encodeURIComponent(mode)}`,'_blank');
  }

  function showProgressBox(show){
    document.getElementById('progressBox').style.display = show ? 'block' : 'none';
  }

  function updateProgress(pct, total){
    const fill = document.getElementById('fill');
    const pctEl = document.getElementById('pct');
    const p = Math.max(0, Math.min(100, Math.round(pct||0)));
    fill.style.width = p + '%';
    let text = p + '%';
    if(total) text += ` (전체 ${total}개)`;
    pctEl.textContent = text;
  }

  function poll(){
    fetch('/check-status')
      .then(r=>r.json())
      .then(data=>{
        const pg = (data && data.progress) ? data.progress : {percentage:0};
        updateProgress(pg.percentage, pg.first_report_number);
        if(pg.percentage >= 100){
          // Reset UI to initial state for this page
          setTimeout(()=>{
            updateProgress(0);
            showProgressBox(false);
          }, 300);
        }else{
          setTimeout(poll, 2500);
        }
      })
      .catch(()=>{
        setTimeout(poll, 8000);
      });
  }

  function run(){
    const from = document.getElementById('fromDate').value;
    const to = document.getElementById('toDate').value;
    if(!company){ alert('회사명이 비어있습니다. Page 1에서 회사명을 입력해 주세요.'); return; }
    if(!from || !to){ alert('날짜 범위를 선택하세요.'); return; }
    if(new Date(from) > new Date(to)){ alert('시작일이 종료일 이후일 수 없습니다.'); return; }

    showProgressBox(true);
    updateProgress(1);

    fetch('/submit', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        company_name: company,
        from_date: from,
        to_date: to,
        mode: mode
      })
    })
    .then(r=>r.json())
    .then(res=>{
      if(res && res.success){
        setTimeout(poll, 200);
      }else{
        alert('에러: ' + (res && res.message ? res.message : 'unknown'));
        showProgressBox(false);
      }
    })
    .catch(err=>{
      alert('에러: ' + err.message);
      showProgressBox(false);
    });
  }

  document.getElementById('openDbBtn').addEventListener('click', openDb);
  document.getElementById('runBtn').addEventListener('click', run);
  setToday();
  setDefaultFrom();
</script>
</body>
</html>
"""


DB_VIEW_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Database · {{ mode }}</title>
<style>
  body{font-family:'Segoe UI','Microsoft YaHei','Malgun Gothic',Arial,sans-serif;background:#f5f7fb;padding:22px}
  .wrap{background:#fff;border:1px solid #e2e8ff;border-radius:16px;max-width:1024px;margin:0 auto;padding:18px}
  h1{margin:6px 0 2px;font-size:28px;font-weight:700}
  .sub{color:#5a6b7c;margin-bottom:12px}
  table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}
  th,td{padding:10px 12px;border-bottom:1px solid #edf2ff;text-align:left;font-size:16px}
  th{background:#f0f4ff;color:#2c3e50}
  tr:hover{background:#fafcff}
  .small{font-size:12px;color:#6b7a88}
  .pill{display:inline-block;padding:4px 8px;border-radius:999px;border:1px solid #dbe6ff;background:#f3f7ff;color:#1f3862;font-size:12px}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Database Preview <span class="pill">{{ mode }}</span></h1>
    <div class="sub">File: <b>{{ db_rel }}</b> · Keys: {{ key_count }}</div>

    {% if rows|length == 0 %}
      <div class="small">데이터가 없습니다. (빈 파일이거나 존재하지 않습니다)</div>
    {% else %}
      <table>
        <thead><tr><th>#</th><th>Key</th><th>Value Type</th><th>Summary</th></tr></thead>
        <tbody>
          {% for i, k, v, s in rows %}
            <tr>
              <td style="text-align:center">{{ i }}</td>
              <td>{{ k }}</td>
              <td>{{ s.type }}</td>
              <td class="small">{{ s.summary }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}
  </div>
</body>
</html>
"""

def _setup_routes():
    """Setup Flask routes - only called when Flask is available"""
    _ensure_flask()
    
    @app.route('/logo.jpg')
    def logo():
        return send_from_directory(os.path.dirname(ROOT_DIR), 'logo.jpg')


@app.route('/modes')
def list_modes():
    """
    Return available modes and default mode (first key).
    """
    modes = _load_modes()
    default = next(iter(modes.keys()), None)
    return jsonify({"modes": modes, "default": default})


@app.route('/')
def page1():
    return render_template_string(MAIN_PAGE_HTML)


@app.route('/login')
def login_page():
    """Example route using BasicPage for login"""
    return render_template_string(create_simple_login_page())


@app.route('/data-entry')
def data_entry_page():
    """Example route using BasicPage for data entry"""
    return render_template_string(create_data_entry_page())


@app.route('/settings')
def settings_page():
    """Example route using BasicPage for settings"""
    return render_template_string(create_settings_page())


@app.route('/mode/<mode>')
def page2(mode):
    """
    Page 2 (per-mode): date range + open DB + run
    """
    company = (request.args.get('company') or '').strip()
    db_rel = os.path.relpath(_db_path_for_mode(mode), ROOT_DIR)
    return render_template_string(PAGE2_HTML, mode=mode, company=company, db_rel=db_rel)


@app.route('/database')
def open_database():
    """
    Render a simple read-only view for a mode's database.
    """
    mode = (request.args.get('mode') or '').strip()
    if not mode:
        return "Mode is required", 400
    db_path = _db_path_for_mode(mode)
    db_rel = os.path.relpath(db_path, ROOT_DIR)
    data = _load_db(mode)

    # Build a compact summary for each top-level key
    rows = []
    try:
        if isinstance(data, dict):
            keys = list(data.keys())
            for idx, k in enumerate(keys, start=1):
                v = data.get(k)
                vtype = type(v).__name__
                summary = ""
                if isinstance(v, dict):
                    # show sub-keys count and common fields
                    sub_keys = list(v.keys())
                    summary = f"dict with {len(sub_keys)} keys: " + ", ".join(sub_keys[:6]) + ("..." if len(sub_keys) > 6 else "")
                elif isinstance(v, list):
                    summary = f"list with {len(v)} items"
                else:
                    # basic truncation
                    s = str(v)
                    summary = s[:120] + ("..." if len(s) > 120 else "")
                rows.append((idx, k, v, {"type": vtype, "summary": summary}))
    except Exception:
        rows = []

    return render_template_string(DB_VIEW_HTML, mode=mode, db_rel=db_rel, key_count=len(rows), rows=rows)


@app.route('/submit', methods=['POST'])
def submit():
    """
    Start process: we only capture the request and reset progress here.
    Your worker should read /check-status and POST to /progress (or reuse this endpoint).
    """
    global result_data, progress_data
    try:
        data = request.get_json() or {}
        if not data.get('company_name'):
            return jsonify({'success': False, 'message': 'company_name is required'}), 200
        if not data.get('mode'):
            return jsonify({'success': False, 'message': 'mode is required'}), 200
        if not data.get('from_date') or not data.get('to_date'):
            return jsonify({'success': False, 'message': 'from_date/to_date are required'}), 200

        # Reset progress and stash the request
        progress_data = {'percentage': 0, 'first_report_number': None}
        result_data = data
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/progress', methods=['POST'])
def progress():
    """
    External (your worker) can POST here to update progress bar.
    Accepts: {"percentage": <int/float>, "first_report_number": <int optional>}
    """
    global progress_data
    try:
        data = request.get_json() or {}
        pct = data.get('percentage', 0)
        update = {'percentage': pct}
        if 'first_report_number' in data:
            update['first_report_number'] = data['first_report_number']
        progress_data.update(update)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/check-status', methods=['GET'])
def check_status():
    global progress_data
    return jsonify({'progress': progress_data})


@app.route('/close', methods=['POST'])
def close_app():
    global server_running
    server_running = False
    return jsonify({'success': True})


# -----------------------------
# Launch helpers (same pattern)
# -----------------------------
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

from modules.settings import get

def get_user_input():
    global result_data, server_running, current_port, ui_opened

    if not server_running:
        t = threading.Thread(target=start_server, daemon=True)
        t.start()
    for _ in range(get('waitcount')):
        if not current_port: time.sleep(get('buffer_time'))

    if current_port and not ui_opened:
        webbrowser.open(f'http://127.0.0.1:{current_port}')
        ui_opened = True
    elif not current_port: return None

    while server_running:
        if result_data is not None: break
        time.sleep(get("buffer_time"))

    result = result_data
    result_data = None
    return result

if __name__ == "__main__":
    payload = get_user_input()
