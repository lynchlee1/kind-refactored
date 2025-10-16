try:
    from .ui_components import BasicPage
except ImportError:
    from ui_components import BasicPage

SERVER_PORT = 5001

# Simplified main page with only whole run and export
def main_page():
    page = BasicPage(title="KIND Project", container_width="650px", container_height="300px")
    page.add_element(page.element_header(title="세이브로 자동 조회 프로그램", subtitle="", show_logo=True, show_subtitle=True))

    # Main buttons
    main_buttons = [
        {
            "button_id": "run_all", "button_text": "전체 실행", "button_type": "button", 
            "button_class": "btn btn-primary", "onclick": "runAllCompanies()", 
            "style": "width:45%;margin-bottom:10px;"
        },
        {
            "button_id": "export_excel", "button_text": "Excel 내보내기", "button_type": "button",
            "button_class": "btn btn-secondary", "onclick": "exportToExcel()",
            "style": "width:45%;margin-left:10px;margin-bottom:10px;"
        }
    ]
    page.add_element(page.element_button_group(main_buttons))
    page.add_element(page.element_checkbox("headless", "headless", "백그라운드에서 실행하기", False))
    
    page.add_script('''
        async function runAllCompanies() {
            if (confirm('Excel 파일의 모든 기업에 대해 데이터를 수집하시겠습니까?\\n\\n1. Excel에서 Holdings 목록을 읽어옵니다\\n2. 각 기업+회차 조합에 대해 데이터를 수집합니다\\n3. 백그라운드에서 실행됩니다.')) {
                const button = document.getElementById('run_all');
                const originalText = button.textContent;
                button.textContent = '실행 중...';
                button.disabled = true;
                
                try {
                    console.log('Starting whole run...');
                    const response = await fetch('/api/run-all-companies', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            from_date: '2021-01-01',
                            to_date: '2025-01-01',
                            headless: document.getElementById('headless').checked
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('전체 실행이 시작되었습니다!\\n\\nExcel에서 읽은 모든 기업에 대해 백그라운드에서 데이터 수집이 진행됩니다.\\n완료되면 데이터베이스가 업데이트됩니다.');
                    } else {
                        alert('전체 실행 실패: ' + result.message);
                    }
                } catch (error) {
                    console.error('전체 실행 오류:', error);
                    alert('전체 실행 중 오류가 발생했습니다: ' + error.message);
                } finally {
                    // Always restore button state
                    button.textContent = originalText;
                    button.disabled = false;
                }
            }
        }
        
        async function exportToExcel() {
            if (confirm('데이터베이스를 Excel 파일로 내보내시겠습니까?')) {
                const button = document.getElementById('export_excel');
                const originalText = button.textContent;
                button.textContent = '내보내는 중...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/api/export-to-excel', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            use_holdings_filter: true
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('Excel 내보내기가 완료되었습니다!\\n\\n파일: ' + result.filename + '\\n위치: ' + result.filepath);
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
        }
    ''')
    
    return page.generate_html()

# Keep other functions for compatibility but mark as deprecated
def hist_page(): 
    return main_page()  # Redirect to main page

def prc_page(): 
    return main_page()  # Redirect to main page

def dev_mode_page(): 
    return main_page()  # Redirect to main page

def hist_dataset_page(company_name, round_filter): 
    return main_page()  # Redirect to main page

def prc_dataset_page(company_name, round_filter): 
    return main_page()  # Redirect to main page