from ui_components import BasicPage

def main_page():
    page = BasicPage(title="KIND Project", container_width="650px", container_height="700px")
    page.add_element(page.element_header(title="KIND 자동 다운로드 프로그램", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_form_group("기업명", "text", "corp_name", "corp_name", "기업명을 입력하세요", "", True))
    
    page.add_element('''
        <div class="dev-mode-container" id="devModeContainer">
            <div class="dev-settings" id="devSettings">
                <!-- Developer settings will be loaded here -->
            </div>
            <div class="button-group" style="margin-top: 20px;">
                <button type="button" class="btn btn-secondary" onclick="saveDevSettings()">저장</button>
                <button type="button" class="btn btn-secondary" onclick="resetDevSettings()">되돌리기</button>
                <button type="button" class="btn btn-secondary" onclick="toggleDevMode()">닫기</button>
            </div>
        </div>
    ''')

    buttons = [
        {"button_id": "dev_mode", "button_text": "개발자 모드", "button_type": "button", "button_class": "btn btn-secondary"},
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
                window.location.href = `hist_page.html?corp_name=${encodeURIComponent(corpName)}`;
            } else if (clickedButton === 'run_prc') {
                window.location.href = `prc_page.html?corp_name=${encodeURIComponent(corpName)}`;
            }
        });

        // Auto-detect dev settings server port
        let devSettingsPort = null;
        async function findDevSettingsServer() {
            // Strategy 1: Check cached port first
            try {
                const cachedPort = localStorage.getItem('devSettingsPort');
                if (cachedPort) {
                    const port = parseInt(cachedPort);
                    if (port > 0 && port <= 65535) {
                        try {
                            const response = await fetch(`http://localhost:${port}/dev-settings`, {
                                method: 'GET',
                                timeout: 500
                            });
                            if (response.ok) {
                                return port;
                            }
                        } catch (e) {
                            // Cached port failed, clear it and continue
                            localStorage.removeItem('devSettingsPort');
                        }
                    }
                }
            } catch (e) {
                // Ignore localStorage errors
            }
            
            // Strategy 2: Intelligent port discovery
            async function discoverPort() {
                // Use multiple discovery methods in parallel
                const discoveryMethods = [
                    // Method 1: Check if there's a port environment variable or hint
                    async () => {
                        // Try to get port from URL parameters or other hints
                        const urlParams = new URLSearchParams(window.location.search);
                        const portParam = urlParams.get('devPort');
                        if (portParam) {
                            const port = parseInt(portParam);
                            if (port > 0 && port <= 65535) {
                                const response = await fetch(`http://localhost:${port}/dev-settings`, {
                                    method: 'GET',
                                    timeout: 500
                                });
                                if (response.ok) return port;
                            }
                        }
                        return null;
                    },
                    
                    // Method 2: Try to detect from current page's port context
                    async () => {
                        // If we're on a specific port, try nearby ports
                        const currentPort = parseInt(window.location.port);
                        if (currentPort && currentPort > 0) {
                            const nearbyPorts = [currentPort, currentPort + 1, currentPort - 1, currentPort + 10, currentPort - 10];
                            for (const port of nearbyPorts) {
                                if (port > 0 && port <= 65535) {
                                    try {
                                        const response = await fetch(`http://localhost:${port}/dev-settings`, {
                                            method: 'GET',
                                            timeout: 300
                                        });
                                        if (response.ok) return port;
                                    } catch (e) {
                                        continue;
                                    }
                                }
                            }
                        }
                        return null;
                    },
                    
                    // Method 3: Smart scanning with adaptive range
                    async () => {
                        // Start with a reasonable range and expand if needed
                        const minPort = 1025; // Above system ports
                        const maxPort = 65535;
                        
                        // Use a pseudo-random starting point based on current time
                        const seed = Date.now() % 1000;
                        const startPort = minPort + seed;
                        
                        // Check ports in batches with exponential backoff
                        let batchSize = 10;
                        let currentPort = startPort;
                        let attempts = 0;
                        const maxAttempts = 100; // Limit total attempts
                        
                        while (attempts < maxAttempts) {
                            const promises = [];
                            const batch = [];
                            
                            // Collect batch of ports to check
                            for (let i = 0; i < batchSize && currentPort <= maxPort; i++) {
                                batch.push(currentPort);
                                currentPort++;
                            }
                            
                            if (batch.length === 0) break;
                            
                            // Check batch in parallel
                            for (const port of batch) {
                                promises.push(
                                    fetch(`http://localhost:${port}/dev-settings`, {
                                        method: 'GET',
                                        timeout: 200
                                    }).then(response => response.ok ? port : null).catch(() => null)
                                );
                            }
                            
                            const results = await Promise.all(promises);
                            const foundPort = results.find(port => port !== null);
                            if (foundPort) return foundPort;
                            
                            attempts++;
                            
                            // Exponential backoff: reduce batch size as we go
                            if (attempts > 10) batchSize = Math.max(5, Math.floor(batchSize * 0.8));
                        }
                        
                        return null;
                    }
                ];
                
                // Try all discovery methods in parallel
                const results = await Promise.all(discoveryMethods.map(method => 
                    method().catch(() => null)
                ));
                
                // Return the first successful result
                return results.find(port => port !== null) || null;
            }
            
            // Execute discovery
            const foundPort = await discoverPort();
            
            // Cache the found port for future use
            if (foundPort) {
                try {
                    localStorage.setItem('devSettingsPort', foundPort.toString());
                } catch (e) {
                    // Ignore localStorage errors
                }
            }
            
            return foundPort;
        }

        function toggleDevMode() {
            const container = document.getElementById('devModeContainer');
            if (container.style.display === 'none' || container.style.display === '') {
                loadDevSettings();
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }
        
        async function loadDevSettings() {
            const settingsContainer = document.getElementById('devSettings');
            if (!devSettingsPort) {
                devSettingsPort = await findDevSettingsServer();
            }

            // Try to fetch from API server first
            if (devSettingsPort) {
                fetch(`http://localhost:${devSettingsPort}/dev-settings`)
                .then(response => response.json())
                .then(data => {
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
                        }
                    };
                    renderSettings(mockSettings);
                });
            } else {
                // No server found, use fallback settings
                console.log('No dev settings server found, using fallback settings');
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
                    }
                };
                renderSettings(mockSettings);
            }
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
            
            // Auto-detect server port if not already found
            if (!devSettingsPort) {
                devSettingsPort = await findDevSettingsServer();
            }
            
            if (devSettingsPort) {
                fetch(`http://localhost:${devSettingsPort}/save-dev-settings`, {
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
            } else {
                alert('개발자 설정 서버를 찾을 수 없습니다. 설정이 저장되지 않았습니다.');
            }
        }
        
        async function resetDevSettings() {
            if (confirm('모든 개발자 설정을 기본값으로 되돌리시겠습니까?')) {
                // Auto-detect server port if not already found
                if (!devSettingsPort) {
                    devSettingsPort = await findDevSettingsServer();
                }
                
                if (devSettingsPort) {
                    // Try to reset via API server
                    fetch(`http://localhost:${devSettingsPort}/reset-dev-settings`, {
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
                } else {
                    alert('개발자 설정 서버를 찾을 수 없습니다. 설정이 초기화되지 않았습니다.');
                }
            }
        }
        
        // Add click event listener for dev_mode button
        document.getElementById('dev_mode').addEventListener('click', toggleDevMode);
    ''')
    return page.generate_html()

def hist_page():
    page = BasicPage(title="추가상장 기록 조회", container_width="650px", container_height="700px")
    page.add_element(page.element_header(title="추가상장 기록 조회", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_info_panel())
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    page.add_element(page.element_info_panel())
    
    # Add buttons
    buttons = [
        {"button_id": "backBtn", "button_text": "뒤로", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "window.location.href='main_page.html'"},
        {"button_id": "runBtn", "button_text": "실행", "button_type": "submit", "button_class": "btn btn-primary"},
    ]
    page.add_element(page.element_button_group(buttons))
    
    page.add_script('''
        const urlParams = new URLSearchParams(window.location.search);
        const corpName = urlParams.get('corp_name');
        const infoPanel = document.getElementById('companyInfo');
    
        async function checkDatabase(companyName) {
            try {
                if (companyName) {
                    infoPanel.innerHTML = `
                        <h4 style="margin: 0 0 10px 0; color: #856404;">📊 데이터베이스 정보</h4>
                        <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                        <p style="margin: 5px 0;"><strong>데이터베이스:</strong> database_hist.json</p>
                        <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #856404;">확인 중...</span></p>
                    `;
                    infoPanel.style.display = 'block';
                    
                    // Try to fetch from API server
                    try {
                        const response = await fetch(`http://localhost:5001/api/company/${encodeURIComponent(companyName)}/hist`);
                        const data = await response.json();
                        
                        if (data.info && data.info.found) {
                            infoPanel.innerHTML = `
                        <h4 style="margin: 0 0 10px 0; color: #155724;">📊 데이터베이스 정보</h4>
                        <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                        <p style="margin: 5px 0;"><strong>데이터베이스:</strong> ${data.database}</p>
                        <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #28a745;">데이터 존재</span></p>
                        <p style="margin: 5px 0;"><strong>첫 번째 날짜:</strong> <span style="color: #155724;">${data.info.first_date}</span></p>
                        <p style="margin: 5px 0;"><strong>마지막 날짜:</strong> <span style="color: #155724;">${data.info.last_date}</span></p>
                        <p style="margin: 5px 0;"><strong>데이터 개수:</strong> <span style="color: #155724;">${data.info.count}개</span></p>
                            `;
                        } else {
                            infoPanel.innerHTML = `
                        <h4 style="margin: 0 0 10px 0; color: #721c24;">📊 데이터베이스 정보</h4>
                        <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                        <p style="margin: 5px 0;"><strong>데이터베이스:</strong> ${data.database || 'database_hist.json'}</p>
                        <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #dc3545;">데이터 없음</span></p>
                            `;
                        }
                    } catch (apiError) {
                        // Fallback to placeholder if API server is not running
                        infoPanel.innerHTML = `
                        <h4 style="margin: 0 0 10px 0; color: #495057;">📊 데이터베이스 정보</h4>
                        <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                        <p style="margin: 5px 0;"><strong>데이터베이스:</strong> database_hist.json</p>
                        <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #6c757d;">API 서버 연결 실패 (localhost:5001)</span></p>
                        `;
                    }
                }
            } catch (error) {
                infoPanel.innerHTML = `데이터베이스 확인 중 오류가 발생했습니다: ${error.message}`;
                infoPanel.style.display = 'block';
            }
        }
        
        // Initialize page
        if (corpName) {
            checkDatabase(decodeURIComponent(corpName));
        }
        
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('추가상장 기록 조회 기능이 구현되지 않았습니다.');
        });
    ''')
    return page.generate_html()
    
def prc_page():
    page = BasicPage(title="전환가액 변동 조회", container_width="650px", container_height="700px")
    page.add_element(page.element_header(title="전환가액 변동 조회", subtitle="타임폴리오 대체투자본부"))
    page.add_element(page.element_info_panel())
    page.add_element(page.element_date())
    page.add_element(page.element_checkbox("headless", "headless", "Chrome 팝업 없이 실행하기", False))
    page.add_element(page.element_info_panel())
    
    # Add buttons
    buttons = [
        {"button_id": "backBtn", "button_text": "뒤로", "button_type": "button", "button_class": "btn btn-secondary", "onclick": "window.location.href='main_page.html'"},
        {"button_id": "runBtn", "button_text": "실행", "button_type": "submit", "button_class": "btn btn-primary"},
    ]
    page.add_element(page.element_button_group(buttons))
    
    page.add_script('''
        // Get company name from URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const corpName = urlParams.get('corp_name');
        const infoPanel = document.getElementById('companyInfo');
        
        // Function to check database and display info
        async function checkDatabase(companyName) {
            try {
                if (companyName) {
                    // Show loading state
                    infoPanel.innerHTML = `
                        <div style="text-align: left; padding: 15px; background: #fff3cd; border-radius: 8px; margin: 10px 0; border: 1px solid #ffeaa7;">
                            <h4 style="margin: 0 0 10px 0; color: #856404;">📊 데이터베이스 정보</h4>
                            <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                            <p style="margin: 5px 0;"><strong>데이터베이스:</strong> database_prc.json</p>
                            <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #856404;">확인 중...</span></p>
                        </div>
                    `;
                    infoPanel.style.display = 'block';
                    
                    // Try to fetch from API server
                    try {
                        const response = await fetch(`http://localhost:5001/api/company/${encodeURIComponent(companyName)}/prc`);
                        const data = await response.json();
                        
                        if (data.info && data.info.found) {
                            infoPanel.innerHTML = `
                        <h4 style="margin: 0 0 10px 0; color: #155724;">📊 데이터베이스 정보</h4>
                        <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                        <p style="margin: 5px 0;"><strong>데이터베이스:</strong> ${data.database}</p>
                        <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #28a745;">데이터 존재</span></p>
                        <p style="margin: 5px 0;"><strong>첫 번째 날짜:</strong> <span style="color: #155724;">${data.info.first_date}</span></p>
                        <p style="margin: 5px 0;"><strong>마지막 날짜:</strong> <span style="color: #155724;">${data.info.last_date}</span></p>
                        <p style="margin: 5px 0;"><strong>데이터 개수:</strong> <span style="color: #155724;">${data.info.count}개</span></p>
                            `;
                        } else {
                            infoPanel.innerHTML = `
                                <div style="text-align: left; padding: 15px; background: #f8d7da; border-radius: 8px; margin: 10px 0; border: 1px solid #f5c6cb;">
                                    <h4 style="margin: 0 0 10px 0; color: #721c24;">📊 데이터베이스 정보</h4>
                                    <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                                    <p style="margin: 5px 0;"><strong>데이터베이스:</strong> ${data.database || 'database_prc.json'}</p>
                                    <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #dc3545;">데이터 없음</span></p>
                                </div>
                            `;
                        }
                    } catch (apiError) {
                        // Fallback to placeholder if API server is not running
                        infoPanel.innerHTML = `
                            <div style="text-align: left; padding: 15px; background: #f8f9fa; border-radius: 8px; margin: 10px 0;">
                                <h4 style="margin: 0 0 10px 0; color: #495057;">📊 데이터베이스 정보</h4>
                                <p style="margin: 5px 0;"><strong>회사명:</strong> ${companyName}</p>
                                <p style="margin: 5px 0;"><strong>데이터베이스:</strong> database_prc.json</p>
                                <p style="margin: 5px 0;"><strong>상태:</strong> <span style="color: #6c757d;">API 서버 연결 실패 (localhost:5001)</span></p>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                infoPanel.innerHTML = `데이터베이스 확인 중 오류가 발생했습니다: ${error.message}`;
                infoPanel.style.display = 'block';
            }
        }
        
        // Initialize page
        if (corpName) {
            checkDatabase(decodeURIComponent(corpName));
        }
        
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('전환가액 변동 조회 기능이 구현되지 않았습니다.');
        });
    ''')
    return page.generate_html()

# Helper function to read database and get company info
def get_company_database_info(company_name, database_file):
    """Read database file and return company information"""
    import os
    import json
    
    if not os.path.exists(database_file):
        return None
    
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if company_name in data:
            company_data = data[company_name]
            return {
                'found': True,
                'first_date': company_data.get('first_date', '-'),
                'last_date': company_data.get('last_date', '-'),
                'count': len(company_data.get('data', []))
            }
        else:
            return {'found': False}
    except Exception as e:
        print(f"Error reading database {database_file}: {e}")
        return None

# Generate HTML files
if __name__ == "__main__":
    import os
    
    # Create html_pages directory if it doesn't exist
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
    
    print("\n🎉 All HTML pages generated successfully!")
    print(f"📂 Files created in '{html_dir}/' folder:")
    print(f"   - {html_dir}/main_page.html (메인 페이지)")
    print(f"   - {html_dir}/hist_page.html (추가상장 기록 조회)")
    print(f"   - {html_dir}/prc_page.html (전환가액 변동 조회)")
    print(f"\n🌐 Open {html_dir}/main_page.html in your browser to start!")
