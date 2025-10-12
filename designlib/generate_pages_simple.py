try:
    from .ui_components import BasicPage
except ImportError:
    from ui_components import BasicPage

SERVER_PORT = 5001

# Done: Extendable main page
def main_page():
    page = BasicPage(title="KIND Project", container_width="650px", container_height="700px")
    page.add_element(page.element_header(title="KIND 자동화 프로그램", subtitle="타임폴리오 대체투자본부", show_logo=True, show_subtitle=True))

    buttons = [
        {
            "button_id": "run_hist", "button_text": "추가상장 기록 조회", "button_type": "button", 
            "button_class": "btn btn-primary btn-long", "onclick": "window.location.href='hist_page.html'", 
            "style": "width:100%;"
        },
        {
            "button_id": "run_prc", "button_text": "전환가액 변동 조회", "button_type": "button", 
            "button_class": "btn btn-primary btn-long", "onclick": "window.location.href='prc_page.html'", 
            "style": "width:100%;"
        },
    ]
    page.add_element(page.element_button_group(buttons))

    page.add_element(page.element_button(
        button_id="dev_mode",
        button_text="개발자 설정",
        button_type="button",
        button_class="btn btn-secondary",
        onclick="window.location.href='dev_mode.html'",
        style="position:absolute; right: 20px; bottom: 20px;"
    ))
    
    page.add_element(page.element_button(
        button_id="excel_update",
        button_text="보유자산 업데이트",
        button_type="button",
        button_class="btn btn-primary",
        onclick="refreshHoldingsFromExcel()",
        style="position:absolute; right: 20px; bottom: 80px;"
    ))
    
    page.add_element(page.element_button(
        button_id="export_excel",
        button_text="데이터 Excel 내보내기",
        button_type="button",
        button_class="btn btn-success",
        onclick="exportToExcel()",
        style="position:absolute; right: 20px; bottom: 140px;"
    ))
    
    # Add Excel functionality script
    page.add_script('''
        async function refreshHoldingsFromExcel() {
            if (confirm('Excel 파일(results.xlsx)에서 Holdings 목록을 업데이트하시겠습니까?')) {
                try {
                    const response = await fetch('/api/refresh-holdings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(result.message + '\\n\\n업데이트된 회사 목록:\\n' + result.holdings.join(', '));
                    } else {
                        alert('Excel 업데이트 실패: ' + result.message);
                    }
                } catch (error) {
                    console.error('Excel 업데이트 오류:', error);
                    alert('Excel 업데이트 중 오류가 발생했습니다: ' + error.message);
                }
            }
        }
        
        async function exportToExcel() {
            const button = document.getElementById('export_excel');
            const originalText = button.textContent;
            
            try {
                // Show loading message
                button.textContent = '내보내는 중...';
                button.disabled = true;
                
                // Use Holdings sheet for filtering (default behavior)
                const requestBody = { use_holdings_filter: true };
                
                const response = await fetch('/api/export-to-excel', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(result.message + '\\n\\n파일 위치: results.xlsx\\n\\n' + 
                          'Holdings 시트: ' + result.companies_count + '개 회사\\n' +
                          'HIST 데이터: ' + result.hist_count + '건\\n' +
                          'PRC 데이터: ' + result.prc_count + '건');
                } else {
                    alert('Excel 내보내기 실패: ' + result.message);
                }
            } catch (error) {
                console.error('Excel 내보내기 오류:', error);
                alert('Excel 내보내기 중 오류가 발생했습니다: ' + error.message);
            } finally {
                // Always restore button state
                button.textContent = originalText;
                button.disabled = false;
            }
        }
    ''')
    
    return page.generate_html()

# Working: Loading, variable selection, server port, ...
def dev_mode_page():
    page = BasicPage(title="개발자 설정", container_width="800px", container_height="800px")
    page.add_element(page.element_header(title="개발자 설정", subtitle="타임폴리오 대체투자본부"))
    
    page.add_element('''
        <div class="dev-mode-container" id="devModeContainer" style="display: block;">
            <div id="loadingSpinner" class="loading-spinner">
                <div class="spinner"></div>
                <p>개발자 설정을 불러오는 중...</p>
            </div>
            <div class="dev-settings" id="devSettings" style="display: none;">
                <!-- Developer settings will be loaded here -->
            </div>
            <div class="button-group" style="margin-top: 20px;">
                <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">저장</button>
                <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">되돌리기</button>
                <button type="button" class="btn btn-secondary" onclick="window.location.href='main_page.html'">뒤로</button>
            </div>
        </div>
    ''')
    
    # Add CSS styles for dev settings
    page.add_element('''
        <style>
            .dev-mode-container {
                margin: 20px 0;
            }
            
            .dev-setting-group {
                margin-bottom: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .dev-setting-group h4 {
                margin: 0 0 15px 0;
                color: #2c3e50;
                font-size: 1.2em;
                border-bottom: 2px solid #007bff;
                padding-bottom: 8px;
            }
            
            .dev-setting-item {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                padding: 8px;
                background: #fff;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
            
            .dev-setting-label {
                min-width: 200px;
                font-weight: 500;
                color: #495057;
                margin-right: 15px;
            }
            
            .dev-setting-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                background: #fff;
            }
            
            .dev-setting-input:focus {
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
            
            .loading-spinner {
                text-align: center;
                padding: 40px;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 20px;
            }
            
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #5a6268;
            }
            
            .btn-primary {
                background: #007bff;
                color: white;
            }
            
            .btn-primary:hover {
                background: #0056b3;
            }
        </style>
    ''')
    
    page.add_script('''
        const SERVER_PORT = ''' + str(SERVER_PORT) + ''';
        
        async function loadDevSettings() {
            const settingsContainer = document.getElementById('devSettings');
            const loadingSpinner = document.getElementById('loadingSpinner');

            // Show loading spinner, hide settings
            loadingSpinner.style.display = 'block';
            settingsContainer.style.display = 'none';

            // Try to fetch from API server
            // Call same server (html_server.py)
            fetch(`/api/dev-settings`)
            .then(response => response.json())
            .then(data => {
                // Hide spinner, show settings
                loadingSpinner.style.display = 'none';
                settingsContainer.style.display = 'block';
                renderSettings(data);
            })
            .catch(error => {
                console.error('API server not available, using fallback settings:', error);
                const mockSettings = {
                    "timing": {
                        "buffer_time": 0.5,
                        "short_loadtime": 2,
                        "long_loadtime": 3,
                        "waitcount": 10,
                        "timeout": 1
                    },
                    "selectors": {
                        "company_input_selector": "#AKCKwd",
                        "from_z_selector": "input[name='fromDate']",
                        "to_date_selector": "input[name='toDate']",
                        "keyword_input_selector": "#reportNmTemp",
                        "reset_selector": "#bfrDsclsType",
                        "first_idx_selector": "#main-contents > section.scrarea.type-00 > table > tbody > tr.first.active > td.first.txc",
                        "iframe_selector": "iframe[name='docViewFrm']",
                        "next_page_selector": "#main-contents > section.paging-group > div.paging.type-00 > a.next",
                        "result_row_selector": "table.list.type-00",
                        "search_button_selector": "#searchForm > section.search-group.type-00 > div > div.btn-group.type-bt > a.btn-sprite.type-00.vmiddle.search-btn",
                        "table_selector": "table, iframe"
                    }
                };
                // Hide spinner, show settings
                loadingSpinner.style.display = 'none';
                settingsContainer.style.display = 'block';
                renderSettings(mockSettings);
            });
        }
        
        function renderSettings(settingsData) {
            const settingsContainer = document.getElementById('devSettings');
            settingsContainer.innerHTML = '';
            
            const allowedSections = ['timing', 'selectors'];
            
            Object.entries(settingsData).forEach(([section, settings]) => {
                if (allowedSections.includes(section)) {
                    const groupDiv = document.createElement('div');
                    groupDiv.className = 'dev-setting-group';
                    
                    const title = document.createElement('h4');
                    title.textContent = section.charAt(0).toUpperCase() + section.slice(1);
                    groupDiv.appendChild(title);
                    
                    const sortedEntries = Object.entries(settings).sort(([keyA], [keyB]) => {
                        const groups = {
                            'time': ['buffer_time', 'short_loadtime', 'long_loadtime'],
                            'wait': ['waitcount', 'timeout'],
                            'date': ['from_date_selector', 'to_date_selector'],
                            'form': ['reset_selector', 'company_input_selector', 'keyword_input_selector'],
                            'navigation': ['search_button_selector', 'next_page_selector'],
                            'content': ['result_row_selector', 'table_selector', 'iframe_selector', 'first_idx_selector']
                        };
                        
                        const getGroupIndex = (key) => {
                            for (const [groupName, keys] of Object.entries(groups)) {
                                if (keys.includes(key)) return Object.keys(groups).indexOf(groupName);
                            }
                            return 999;
                        };
                        
                        const groupIndexA = getGroupIndex(keyA);
                        const groupIndexB = getGroupIndex(keyB);
                        
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
        }
        
        async function saveDevSettings() {
            const inputs = document.querySelectorAll('.dev-setting-input');
            const settings = {};
            
            inputs.forEach(input => {
                const section = input.dataset.section;
                const key = input.dataset.key;
                
                if (!settings[section]) {
                    settings[section] = {};
                }
                settings[section][key] = input.value;
            });
            
            fetch(`/api/save-dev-settings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('개발자 설정이 system_constants.json에 저장되었습니다.');
                } else {
                    alert('저장 실패: ' + (result.message || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('API server not available:', error);
                alert('개발자 설정이 저장되었습니다. (API 서버 연결 실패)');
            });
        }
        
        async function resetDevSettings() {
            if (confirm('selectors와 timing 설정을 default_constants.json의 기본값으로 되돌리시겠습니까?')) {
                fetch(`/api/reset-dev-settings`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('개발자 설정이 기본값으로 초기화되었습니다.');
                        loadDevSettings(); // Reload the settings
                    } else {
                        alert('초기화 실패: ' + (result.message || '알 수 없는 오류'));
                    }
                })
                .catch(error => {
                    console.error('API server not available:', error);
                    alert('개발자 설정을 초기화했습니다. (API 서버 연결 실패)');
                    loadDevSettings(); // Reload with fallback settings
                });
            }
        }
        
        async function refreshHoldingsFromExcel() {
            if (confirm('Excel 파일(results.xlsx)에서 Holdings 목록을 업데이트하시겠습니까?')) {
                try {
                    const response = await fetch('/api/refresh-holdings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(result.message + '\\n\\n업데이트된 회사 목록:\\n' + result.holdings.join(', '));
                    } else {
                        alert('Excel 업데이트 실패: ' + result.message);
                    }
                } catch (error) {
                    console.error('Excel 업데이트 오류:', error);
                    alert('Excel 업데이트 중 오류가 발생했습니다: ' + error.message);
                }
            }
        }
        
        // Load dev settings when page loads
        document.addEventListener('DOMContentLoaded', function() {
            loadDevSettings();
        });
    ''')
    return page.generate_html()

# Almost Done: Connect functionality to UI
def execution_setup_page(config):
    page = BasicPage(title=config.get("title"), container_width="650px", container_height="700px")
    page.add_element(page.element_header(title=config.get("title")))
    page.add_element(page.element_form_group("기업명", "text", "corp_name", "corp_name", "기업명을 입력하세요", "", False))
    page.add_element(page.element_checkbox(
        checkbox_id="all_companies", 
        checkbox_name="all_companies", 
        label_text="전체 기업 선택하기", 
        checked=False,
        as_button=True,
        position="absolute",
        top="95px",
        right="40px",
        width="120px",
        height="28px"
    ))
    page.add_element(page.element_info_panel())
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    page.add_element(page.element_info_panel())
    buttons = [
        {"button_id": "runBtn", "button_text": "실행", "button_type": "submit", "button_class": "btn btn-primary"},
        {"button_id": "refreshBtn", "button_text": "데이터베이스 최신화", "button_type": "button", "button_class": "btn btn-primary", "onclick": "refreshDatabase()"},
        {"button_id": "dbBtn", "button_text": "데이터베이스 조회", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "checkDatabaseFromInput()"}
    ]
    page.add_element(page.element_button_group(buttons))
    page.add_element(page.element_button(
        button_id="backBtn",
        button_text="뒤로",
        button_type="button",
        button_class="btn btn-secondary",
        onclick="window.location.href='main_page.html'",
        position="absolute",
        bottom="20px",
        left="20px"
    ))

    # Get configuration values
    execution_message = config.get("execution_message", "기능을 실행합니다.\\n대상: ${searchTarget}\\n\\n기능이 구현되지 않았습니다.")
    run_function = config.get("run_function", None)
    database_address = config.get("database_address", "")

    page.add_script('''
        const SERVER_PORT = ''' + str(SERVER_PORT) + ''';
        const urlParams = new URLSearchParams(window.location.search);
        const corpName = urlParams.get('corp_name');
        const infoPanel = document.getElementById('companyInfo');

        const CONFIG = {
            runFunction: ''' + (f'"{run_function}"' if run_function else 'null') + ''',
            databaseAddress: ''' + f'"{database_address}"' + ''',
        };

        // '전체 기업 선택하기' 기능
        document.addEventListener('DOMContentLoaded', () => {
            const allCheck = document.getElementById('all_companies');
            const corpInput = document.getElementById('corp_name');
            function syncCorpInputState() {
                const disabled = allCheck.checked;
                corpInput.disabled = disabled;
                corpInput.style.background = disabled ? '#e9ecef' : '#f8f9fa';
            }
            allCheck.addEventListener('change', syncCorpInputState);
            syncCorpInputState();
        });

        function checkDatabaseFromInput() {
            const corpInput = document.getElementById('corp_name');
            const allCompaniesCheck = document.getElementById('all_companies');
            const companyName = corpInput.value.trim();
            
            if (!companyName && !allCompaniesCheck.checked) {
                alert('회사명을 입력하거나 "전체 기업 선택하기"를 체크해주세요.');
                return;
            }

            const urlParams = new URLSearchParams(window.location.search);
            const currentMode = urlParams.get('mode');
    
            // 전체 기업 데이터 조회 기능 넣기
            if (allCompaniesCheck.checked) {
                alert('데이터베이스 조회를 위해서는 기업을 선택해야 합니다.');
                return;
            }
            
            const datasetUrl = new URL(window.location.href);
            datasetUrl.pathname = datasetUrl.pathname.replace('.html', '_dataset.html');
            datasetUrl.searchParams.set('company', companyName);
            datasetUrl.searchParams.set('mode', currentMode);
            
            window.open(datasetUrl.toString(), '_blank');
        }
        
        // Function to execute the run function
        function executeRunFunction() {
            const corpInput = document.getElementById('corp_name');
            const allCompaniesCheck = document.getElementById('all_companies');
            const companyName = corpInput.value.trim();            
            const fromDate = document.getElementById('fromDate').value;
            const toDate = document.getElementById('toDate').value;
            const headless = document.getElementById('headless').checked;
            
            if (!companyName && !allCompaniesCheck.checked) {
                alert('회사명을 입력하거나 "전체 기업 선택하기"를 체크해주세요.');
                return false;
            }
            
            const searchTarget = allCompaniesCheck.checked ? '전체 기업' : companyName;
            
            // Prepare parameters for the run function
            const params = {
                company_name: searchTarget,
                from_date: fromDate,
                to_date: toDate,
                headless: headless,
                mode: urlParams.get('mode') || 'default'
            };
            
            // Call the configured run function if available
            if (CONFIG.runFunction) {
                // Show initial message
                alert(`''' + execution_message + '''\\n\\nRun Function: ${CONFIG.runFunction}\\nParameters: ${JSON.stringify(params, null, 2)}`);
                
                // Make API call to execute the run function
                fetch(`/api/run/${CONFIG.runFunction}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert(`${CONFIG.runFunction} 실행이 시작되었습니다.\\n\\n진행상황은 서버 콘솔에서 확인할 수 있습니다.`);
                    } else {
                        alert(`실행 실패: ${result.message}`);
                    }
                })
                .catch(error => {
                    alert(`API 호출 오류: ${error.message}`);
                });
            } else {
                alert(`''' + execution_message + '''\\n\\nNo run function configured.`);
            }
            
            return false;
        }
        
        function validateAndExecute() {
            return executeRunFunction();
        }
        
        function refreshDatabase() {
            const headless = document.getElementById('headless').checked;
            
            const urlParams = new URLSearchParams(window.location.search);
            const currentMode = urlParams.get('mode') || 'hist';
            
            // Prepare parameters for refresh function
            const params = {
                company_name: '전체 기업',  // Always use all companies for refresh
                from_date: '2024-01-01',    // Will be overridden by each company's last_date
                to_date: '2025-12-31',      // Will be overridden by today's date
                headless: headless,
                mode: currentMode,
                refresh_mode: true  // Flag to indicate this is a refresh operation
            };
            
            if (CONFIG.runFunction) {
                alert(`데이터베이스 최신화를 시작합니다.\\n\\n모든 기업의 최신 데이터를 수집합니다.\\n각 기업의 마지막 날짜부터 오늘까지 자동으로 설정됩니다.\\n\\n실행 함수: ${CONFIG.runFunction}`);
                
                // Make API call to execute the refresh function
                fetch(`/api/run/${CONFIG.runFunction}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert(`${CONFIG.runFunction} 데이터베이스 최신화가 시작되었습니다.`);
                    } else {
                        alert(`오류: ${result.message}`);
                    }
                })
                .catch(error => {
                    alert(`API 호출 오류: ${error.message}`);
                });
            } else {
                alert('데이터베이스 최신화 기능이 구현되지 않았습니다.');
            }
        }
        
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            validateAndExecute();
        });
    ''')
    return page.generate_html()

# Generate HTML files
if __name__ == "__main__":
    import os
    import sys
    
    # Add modules to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from modules.search_modes import hist_page, prc_page, hist_dataset_page, prc_dataset_page
        
    html_dir = "html_pages"
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
        print(f"📁 Created directory: {html_dir}")
    
    # Generate main page
    with open(f'{html_dir}/main_page.html', 'w', encoding='utf-8') as f:
        f.write(main_page())
    print("✅ main_page.html created")
    
    # Generate hist page
    with open(f'{html_dir}/hist_page.html', 'w', encoding='utf-8') as f:
        f.write(hist_page())
    print("✅ hist_page.html created")
    
    # Generate prc page
    with open(f'{html_dir}/prc_page.html', 'w', encoding='utf-8') as f:
        f.write(prc_page())
    print("✅ prc_page.html created")
    
    # Generate dev mode page
    with open(f'{html_dir}/dev_mode.html', 'w', encoding='utf-8') as f:
        f.write(dev_mode_page())
    print("✅ dev_mode.html created")
    
    # Generate dataset table pages
    with open(f'{html_dir}/hist_page_dataset.html', 'w', encoding='utf-8') as f:
        f.write(hist_dataset_page())
    print("✅ hist_page_dataset.html created")
    
    with open(f'{html_dir}/prc_page_dataset.html', 'w', encoding='utf-8') as f:
        f.write(prc_dataset_page())
    print("✅ prc_page_dataset.html created")
    
    print("\n🎉 All HTML pages generated successfully!")
    print(f"📂 Files created in '{html_dir}/' folder:")
    print(f"   - {html_dir}/main_page.html (메인 페이지)")
    print(f"   - {html_dir}/hist_page.html (추가상장 기록 조회)")
    print(f"   - {html_dir}/prc_page.html (전환가액 변동 조회)")
    print(f"   - {html_dir}/dev_mode.html (개발자 설정)")
    print(f"   - {html_dir}/hist_page_dataset.html (추가상장 기록 데이터셋)")
    print(f"   - {html_dir}/prc_page_dataset.html (전환가액 변동 데이터셋)")
    print(f"\n🌐 Open {html_dir}/main_page.html in your browser to start!")
