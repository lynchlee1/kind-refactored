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
import json

app = Flask(__name__)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        
        /* Ensure buttons align nicely regardless of label length */
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
                <button id="nextBtn" type="button" class="btn btn-primary" onclick="goNext()">다음</button>
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
                    <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">설정 저장하기</button>
                    <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">기본 설정으로 되돌리기</button>
                    <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">개발자 설정 닫기</button>
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
        function goNext() {
            const name = document.getElementById('company').value.trim();
            if (!name) return;
            const url = new URL(window.location.href);
            url.searchParams.set('company', name);
            window.location.href = url.toString();
        }
        function initCompanyView() {
            const company = getQueryParam('company');
            const companyInput = document.getElementById('company');
            const infoPanel = document.getElementById('companyInfo');
            const runBtn = document.getElementById('runBtn');
            const devBtn = document.getElementById('devBtn');
            const nextBtn = document.getElementById('nextBtn');
            const backBtn = document.getElementById('backBtn');
            const dateRow = document.getElementById('dateRow');
            const headlessRow = document.getElementById('headlessRow');
            const companyGroup = document.getElementById('companyGroup');
            const recordsBtn = document.getElementById('recordsBtn');

            if (company) {
                companyInput.value = company;
                // Show run/dev/records and hide next
                runBtn.style.display = 'inline-block';
                devBtn.style.display = 'inline-block';
                nextBtn.style.display = 'none';
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

                fetch(`/company-info?name=${encodeURIComponent(company)}`)
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
            
            // Show close button and hide other buttons
            const runBtn = document.getElementById('runBtn');
            const devBtn = document.getElementById('devBtn');
            const nextBtn = document.getElementById('nextBtn');
            const backBtn = document.getElementById('backBtn');
            const recordsBtn = document.getElementById('recordsBtn');
            const closeBtn = document.getElementById('closeBtn');
            
            if (runBtn) runBtn.style.display = 'none';
            if (devBtn) devBtn.style.display = 'none';
            if (nextBtn) nextBtn.style.display = 'none';
            if (backBtn) backBtn.style.display = 'none';
            if (recordsBtn) recordsBtn.style.display = 'inline-block';
            if (closeBtn) closeBtn.style.display = 'inline-block';

            // Hide original form sections
            const companyGroup = document.getElementById('companyGroup');
            const dateRow = document.getElementById('dateRow');
            const headlessRow = document.getElementById('headlessRow');
            if (companyGroup) companyGroup.style.display = 'none';
            if (dateRow) dateRow.style.display = 'none';
            if (headlessRow) headlessRow.style.display = 'none';
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

# Global variables to store the result and process status
result_data = None
server_running = False
current_port = None
progress_data = {
    'percentage': 0,
    'first_report_number': None
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

@app.route('/records')
def records():
    try:
        company = request.args.get('company', '')
        round_filter = (request.args.get('round') or '').strip()
        db_path = os.path.join(ROOT_DIR, 'database.json')
        data = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        company_key = company or next(iter(data.keys()), '')
        entry = data.get(company_key, {})
        rows = entry.get('data', [])
        if round_filter:
            rows = [r for r in rows if str(r.get('round','')).strip() == round_filter]
        first_date = entry.get('first_date') or '-'
        last_date = entry.get('last_date') or '-'
        # Simple table HTML
        table_rows = ''.join(
            f"<tr><td>{i+1}</td><td>{r.get('date','')}</td><td>{r.get('round','')}</td><td>{r.get('additional_shares','')}</td><td>{r.get('issue_price','')}</td></tr>"
            for i, r in enumerate(rows)
        )
        html = f"""
        <html><head>
        <meta charset='utf-8'>
        <title>기록 보기 - {company_key}</title>
        <style>
        body{{font-family:'Segoe UI','Malgun Gothic',Arial,sans-serif;padding:20px;background:#f5f7fb;}}
        h2{{margin-bottom:16px;color:#2c3e50;}}
        .meta{{margin-bottom:12px;color:#555;}}
        table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;}}
        th,td{{padding:10px 12px;border-bottom:1px solid #eee;text-align:left;}}
        th{{background:#f0f4ff;color:#2c3e50;}}
        tr:hover{{background:#fafcff;}}
        .topbar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;gap:12px;}}
        .btn{{background:#0d6efd;color:#fff;border:none;border-radius:8px;padding:8px 14px;cursor:pointer;}}
        .btn:active{{opacity:.9}}
        .filter{{display:flex;gap:8px;align-items:center;}}
        .input{{height:36px;padding:0 10px;border:1px solid #d8e1ff;border-radius:8px;}}
        </style></head><body>
        <div class='topbar'>
          <h2>기록 보기 - {company_key}</h2>
          <div class='filter'>
            <input id='roundInput' class='input' type='text' placeholder='회차 입력 (엔터로 검색)' value='{round_filter}'>
            <button class='btn' onclick="applyFilter()">입력</button>
            <button class='btn' onclick="history.back()">뒤로</button>
          </div>
        </div>
        <div class='meta'>총 {len(rows)} 건 ({first_date} ~ {last_date})</div>
        <table>
          <thead><tr><th>#</th><th>발행시간</th><th>회차</th><th>추가주식수(주)</th><th>발행/전환/행사가액(원)</th></tr></thead>
          <tbody>{table_rows or '<tr><td colspan=6 style="text-align:center;color:#888">데이터가 없습니다</td></tr>'}</tbody>
        </table>
        <script>
          function applyFilter(){{
            const v=document.getElementById('roundInput').value.trim();
            const url=new URL(window.location.href);
            if(v){{url.searchParams.set('round',v);}} else {{url.searchParams.delete('round');}}
            window.location.href=url.toString();
          }}
          document.getElementById('roundInput').addEventListener('keydown',function(e){{
            if(e.key==='Enter'){{applyFilter();}}
          }});
        </script>
        </body></html>
        """
        return html
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logo.jpg')
def logo():
    return send_from_directory(ROOT_DIR, 'logo.jpg')

@app.route('/submit', methods=['POST'])
def submit():
    global result_data, progress_data
    try:
        data = request.get_json()
        
        if not data.get('company_name'):
            return jsonify({'success': False, 'message': 'Company name is required'})
        
        
        progress_data = {'percentage': 0, 'first_report_number': None}
        result_data = data
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cancel', methods=['POST'])
def cancel():
    global result_data
    result_data = None
    return jsonify({'success': True})

@app.route('/close', methods=['POST'])
def close_app():
    """Close the application when user clicks close button"""
    global server_running
    server_running = False
    return jsonify({'success': True})

@app.route('/progress', methods=['POST'])
def update_progress():
    global progress_data
    try:
        data = request.get_json()
        
        update_data = { 'percentage': data.get('percentage', 0) }
        if 'first_report_number' in data:
            update_data['first_report_number'] = data['first_report_number']
        
        progress_data.update(update_data)
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

def _db_path():
    return os.path.join(ROOT_DIR, 'database.json')

def _load_db():
    try:
        path = _db_path()
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

@app.route('/company-info', methods=['GET'])
def company_info():
    try:
        name = request.args.get('name', '').strip()
        if not name:
            return jsonify({'found': False})
        db = _load_db()
        entry = db.get(name) or {}
        if not entry:
            return jsonify({'found': False})
        data = entry.get('data') or []
        return jsonify({
            'found': True,
            'first_date': entry.get('first_date'),
            'last_date': entry.get('last_date'),
            'count': len(data)
        })
    except Exception as e:
        return jsonify({'found': False, 'error': str(e)}), 200

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
