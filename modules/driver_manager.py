import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from settings import get

def setup_driver(headless):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    
    # Stability and crash prevention options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    
    # Memory and performance options
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # Logging and notifications
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Window and user agent
    chrome_options.add_argument("--window-size=1600,1000")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(get("long_loadtime"))
        wait = WebDriverWait(driver, get("long_loadtime"))
        print("✅ Chrome driver 로딩 완료")
        return driver, wait
    except Exception as e: raise Exception(f"❌ Chrome driver 로딩 실패: {e}")

def find_result_rows(driver):
    result_selector = get("result_row_selector")
    tables = driver.find_elements(By.CSS_SELECTOR, result_selector)
    for table in tables:
        if table.location['y'] > 300: # Prevent from selecting table in the top of the page
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr") or table.find_elements(By.TAG_NAME, "tr")
            return rows
    return []

def extract_from_iframe(driver, wait):
    iframe = None
    iframe_selector = get("iframe_selector")
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))    
    if not iframe:
        print(f"❌ iframe not found")
        return []
    driver.switch_to.frame(iframe)
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        all_tables_data = []
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 0:
                table_data = []
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: cells = row.find_elements(By.TAG_NAME, "th")
                    if cells:
                        try:
                            row_data = driver.execute_script("""
                                var cells = arguments[0];
                                var result = [];
                                for (var i = 0; i < cells.length; i++) {
                                    result.push(cells[i].textContent.trim());
                                }
                                return result;
                            """, cells)
                        except: row_data = [cell.text.strip() for cell in cells]
                        if any(cell.strip() for cell in row_data):
                            table_data.append({
                                "row_index": row_idx,
                                "data": row_data
                            })
                if table_data:
                    all_tables_data.append({
                        "table_index": table_idx,
                        "rows": table_data,
                        "row_count": len(table_data)
                    })
        return all_tables_data 
    except Exception as e: raise Exception(f"❌ Error extracting from iframe: {e}")

    finally:
        try: driver.switch_to.default_content()
        except Exception as e: raise Exception(f"⚠️ Error switching back to main content: {e}")

def extract_direct_tables(driver, wait):
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        all_tables_data = []
        table_selector = get("table_selector")
        tables = driver.find_elements(By.CSS_SELECTOR, table_selector)
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 0:
                table_data = []
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: cells = row.find_elements(By.TAG_NAME, "th")
                    if cells:
                        try:
                            row_data = driver.execute_script("""
                                var cells = arguments[0];
                                var result = [];
                                for (var i = 0; i < cells.length; i++) {
                                    result.push(cells[i].textContent.trim());
                                }
                                return result;
                            """, cells)
                        except: row_data = [cell.text.strip() for cell in cells]
                        if any(cell.strip() for cell in row_data):
                            table_data.append({
                                "row_index": row_idx,
                                "data": row_data
                            })                
                if table_data:
                    all_tables_data.append({
                        "table_index": table_idx,
                        "rows": table_data,
                        "row_count": len(table_data)
                    })
                else: raise Exception(f"⚠️ Table {table_idx} has no data")
        return all_tables_data                    
    except Exception as e: raise Exception(f"❌ Error extracting direct tables: {e}")

def extract_table_data(driver, wait):
    iframe_data = extract_from_iframe(driver, wait)
    if iframe_data: return iframe_data
    return extract_direct_tables(driver, wait)

def click_next_page(driver, wait):
    next_button = None
    next_page_selector = get("next_page_selector")
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, next_page_selector)
        print(f"✅ Found next button with selector: {next_page_selector}")
    except Exception: raise Exception(f"❌ 다음 페이지 버튼 찾기 실패")
    
    current_report_number = ""
    try:
        current_report_number = driver.find_element(By.CSS_SELECTOR, get("first_idx_selector")).text.strip()
    except Exception: raise Exception(f"❌ 현재 보고서 번호 찾기 실패")

    try:
        driver.execute_script("arguments[0].click();", next_button)
    except Exception: raise Exception(f"❌ 다음 페이지 버튼 클릭 실패")

    time.sleep(get("short_loadtime"))

    try:
        new_report_number = driver.find_element(By.CSS_SELECTOR, get("first_idx_selector")).text.strip()            
        if current_report_number and new_report_number != current_report_number: return True
        else: return False
    except Exception as e: raise Exception(f"❌ 페이지 변경 오류: {e}")
