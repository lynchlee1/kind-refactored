from __future__ import annotations

import json
import time
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

DETAILS_URL = "https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain#viewer"

# Progress tracking
progress_port = None

def send_progress_update(current_report, total_reports, message="Processing...", first_report_number=None, completed=False):
    """Send progress update to the web interface"""
    global progress_port
    if progress_port:
        try:
            requests.post(f'http://127.0.0.1:{progress_port}/progress', 
                         json={
                             'current_report': current_report,
                             'total_reports': total_reports,
                             'message': message,
                             'first_report_number': first_report_number,
                             'completed': completed
                         }, timeout=1)
        except:
            pass  # Ignore if web interface is not available

# Default values (will be overridden by user input)
company_name = "에스티팜"
from_date = "2024-09-20"
to_date = "2025-09-30"
max_rows = 4
headless_mode = False
debug_mode = False

try:
    from settings import (SHORT_LOADTIME, LONG_LOADTIME, BUFFER_TIME, LONG_WAITCOUNT, 
                           SHORT_WAITCOUNT, SEARCH_BUTTON_SELECTOR, 
                           RESULT_ROW_SELECTOR, COMPANY_INPUT_SELECTOR, FROM_DATE_SELECTOR, 
                           TO_DATE_SELECTOR, NEXT_PAGE_SELECTOR, TABLE_SELECTOR, IFRAME_SELECTOR)
except ImportError:
    # Fallback values if settings not available
    SHORT_LOADTIME = 0.5
    LONG_LOADTIME = 1.0
    BUFFER_TIME = 0.05
    LONG_WAITCOUNT = 30
    SHORT_WAITCOUNT = 20
    LONG_LOADTIME = 3.0
    # Default selectors
    SEARCH_BUTTON_SELECTOR = "button[type='submit']"
    RESULT_ROW_SELECTOR = "tr[onclick*='viewDetail']"
    COMPANY_INPUT_SELECTOR = "input[name='companyName']"
    FROM_DATE_SELECTOR = "input[name='fromDate']"
    TO_DATE_SELECTOR = "input[name='toDate']"
    NEXT_PAGE_SELECTOR = "a.paging_next"
    TABLE_SELECTOR = "table, iframe"
    IFRAME_SELECTOR = "iframe[name='viewer']" 

def setup_driver(headless: bool = False) -> tuple[webdriver.Chrome, WebDriverWait]:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1600,1000")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(BUFFER_TIME)
    wait = WebDriverWait(driver, 20)
    return driver, wait

from driverslib import find_result_rows, extract_table_data, click_next_page

def click_and_capture_links(driver, max_rows_limit = 200):
    results = []
    rows = find_result_rows(driver)
    if not rows: return results

    base_handle = driver.current_window_handle
    total_rows = len(rows[:max_rows_limit])
    first_report_number = None
    
    for i, row in enumerate(rows[:max_rows_limit], start=1):
        # Extract report number from the first row to use as total
        if i == 1:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 1:
                    first_report_number = cells[0].text.strip()
            except:
                first_report_number = "1"
        
        # Send progress update with report number format
        if first_report_number:
            send_progress_update(i, total_rows, f"Processing report {i} of {total_rows}", first_report_number)
        else:
            send_progress_update(i, total_rows, f"Processing row {i} of {total_rows}")
        
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            date_txt = cells[1].text.strip() if len(cells) >= 2 else ""
            company_txt = cells[2].text.strip() if len(cells) >= 3 else ""
            title_txt = cells[3].text.strip() if len(cells) >= 4 else row.text.strip()

            target_keywords = ["CB", "EB", "BW"]
            has_keyword = any(keyword in title_txt for keyword in target_keywords)
            if not has_keyword: continue

            anchors = []
            if len(cells) >= 4:
                anchors = cells[3].find_elements(By.TAG_NAME, "a")
            if not anchors:
                anchors = row.find_elements(By.TAG_NAME, "a")

            viewer_url = None
            for a in anchors:
                try:
                    href = (a.get_attribute("href") or "").lower()
                    onclick = (a.get_attribute("onclick") or "").lower()
                    title_attr = (a.get_attribute("title") or "").lower()

                    if (
                        "viewer" in href
                        or "details" in href
                        or "window.open" in onclick
                        or "viewer" in onclick
                        or "보기" in title_attr
                        or href.startswith("javascript:")
                        or not href
                    ):
                        before = set(driver.window_handles)
                        driver.execute_script("arguments[0].click();", a)
                        # Wait for popup or same-tab nav
                        for _ in range(30):
                            time.sleep(BUFFER_TIME)
                            after = set(driver.window_handles)
                            if len(after) > len(before):
                                break
                        new_handles = [h for h in driver.window_handles if h not in before]
                        if new_handles:
                            driver.switch_to.window(new_handles[0])
                            time.sleep(0.5)
                            viewer_url = driver.current_url
                            # settle URL changes
                            for _ in range(20):
                                time.sleep(BUFFER_TIME)
                                cur = driver.current_url
                                if cur != viewer_url:
                                    viewer_url = cur
                            
                            # Extract table data from the disclosure viewer
                            print(f"🔍 Extracting table data for: {title_txt}")
                            print(f"🔍 Current URL: {driver.current_url}")
                            
                            # TARGET THE ACTUAL DOCUMENT CONTENT
                            print("🔍 TARGETING DOCUMENT CONTENT - Looking for the real data...")
                            table_data = []
                            
                            try:
                                # Look for the actual document content in iframes
                                print("🔍 Looking for document content in iframes...")
                                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                                print(f"📄 Found {len(iframes)} iframes")
                                
                                for iframe_idx, iframe in enumerate(iframes):
                                    try:
                                        print(f"🔍 Checking iframe {iframe_idx}...")
                                        driver.switch_to.frame(iframe)
                                        
                                        # Look for the actual document content
                                        page_text = driver.find_element(By.TAG_NAME, "body").text
                                        print(f"📄 Iframe {iframe_idx} text length: {len(page_text)}")
                                        print(f"📄 Iframe {iframe_idx} first 200 chars: {page_text[:200]}")
                                        
                                        # Check if this iframe has the actual document content
                                        if any(keyword in page_text for keyword in ["회사명", "추가주식", "발행내역", "에스티팜"]):
                                            print(f"✅ Found document content in iframe {iframe_idx}!")
                                            
                                            # Extract tables from this iframe
                                            tables = driver.find_elements(By.TAG_NAME, "table")
                                            print(f"📊 Found {len(tables)} tables in document iframe")
                                            
                                            for table_idx, table in enumerate(tables):
                                                rows = table.find_elements(By.TAG_NAME, "tr")
                                                print(f"📋 Document Table {table_idx}: {len(rows)} rows")
                                                
                                                if len(rows) > 0:
                                                    table_rows = []
                                                    for row_idx, row in enumerate(rows):
                                                        cells = row.find_elements(By.TAG_NAME, "td")
                                                        if not cells:
                                                            cells = row.find_elements(By.TAG_NAME, "th")
                                                        
                                                        if cells:
                                                            row_data = [cell.text.strip() for cell in cells]
                                                            if any(cell.strip() for cell in row_data):
                                                                table_rows.append({
                                                                    "row_index": row_idx,
                                                                    "data": row_data
                                                                })
                                                                print(f"  Row {row_idx}: {row_data[:3]}...")
                                                    
                                                    if table_rows:
                                                        table_data.append({
                                                            "table_index": table_idx,
                                                            "rows": table_rows,
                                                            "row_count": len(table_rows)
                                                        })
                                                        print(f"✅ Added document table {table_idx} with {len(table_rows)} rows")
                                            
                                            # Found the content, break out of iframe loop
                                            driver.switch_to.default_content()
                                            break
                                        
                                        driver.switch_to.default_content()
                                        
                                    except Exception as e:
                                        print(f"⚠️ Error checking iframe {iframe_idx}: {e}")
                                        driver.switch_to.default_content()
                                        continue
                                
                                # If no document content found, try direct extraction from main page
                                if not table_data:
                                    print("⚠️ No document content found in iframes, trying main page...")
                                    tables = driver.find_elements(By.TAG_NAME, "table")
                                    print(f"📊 Found {len(tables)} tables on main page")
                                    
                                    for table_idx, table in enumerate(tables):
                                        rows = table.find_elements(By.TAG_NAME, "tr")
                                        print(f"📋 Main Table {table_idx}: {len(rows)} rows")
                                        
                                        if len(rows) > 0:
                                            table_rows = []
                                            for row_idx, row in enumerate(rows):
                                                cells = row.find_elements(By.TAG_NAME, "td")
                                                if not cells:
                                                    cells = row.find_elements(By.TAG_NAME, "th")
                                                
                                                if cells:
                                                    row_data = [cell.text.strip() for cell in cells]
                                                    if any(cell.strip() for cell in row_data):
                                                        table_rows.append({
                                                            "row_index": row_idx,
                                                            "data": row_data
                                                        })
                                                        print(f"  Row {row_idx}: {row_data[:3]}...")
                                            
                                            if table_rows:
                                                table_data.append({
                                                    "table_index": table_idx,
                                                    "rows": table_rows,
                                                    "row_count": len(table_rows)
                                                })
                                                print(f"✅ Added main table {table_idx} with {len(table_rows)} rows")
                                
                                # If still no data, create fallback
                                if not table_data:
                                    print("❌ No document content found anywhere")
                                    table_data = [{
                                        "table_index": 0,
                                        "rows": [{
                                            "row_index": 0,
                                            "data": ["NO_DOCUMENT_CONTENT", "FOUND", "ONLY_NAVIGATION"]
                                        }],
                                        "row_count": 1
                                    }]
                                
                                print(f"📊 FINAL RESULT: {len(table_data)} tables extracted")
                                
                            except Exception as e:
                                print(f"❌ Error in document extraction: {e}")
                                import traceback
                                traceback.print_exc()
                                table_data = [{
                                    "table_index": 0,
                                    "rows": [{
                                        "row_index": 0,
                                        "data": ["ERROR", "EXTRACTION_FAILED", str(e)[:50]]
                                    }],
                                    "row_count": 1
                                }]
                            
                            driver.close()
                            driver.switch_to.window(base_handle)
                        else:
                            # same-tab attempt
                            current_url = driver.current_url
                            if ("details" in current_url) or ("viewer" in current_url):
                                viewer_url = current_url
                            # go back regardless to keep row context
                            try:
                                driver.back()
                                time.sleep(BUFFER_TIME)
                            except Exception:
                                pass
                        if viewer_url:
                            break
                except Exception:
                    try:
                        driver.switch_to.window(base_handle)
                    except Exception:
                        pass
                    continue

            if viewer_url and not any(x.get("viewer_url") == viewer_url for x in results):
                results.append(
                    {
                        "idx": i,
                        "date": date_txt,
                        "company": company_txt,
                        "title": title_txt,
                        "viewer_url": viewer_url,
                        "table_data": table_data if 'table_data' in locals() and table_data else [],
                    }
                )
        except Exception:
            try:
                driver.switch_to.window(base_handle)
            except Exception:
                pass
            continue

    return results

def process_all_pages(driver, wait):
    all_results = []
    page_num = 1
    
    while True:
        print(f"Processing page {page_num}...")
        send_progress_update(40, 100, f"Processing page {page_num}...")
        page_results = click_and_capture_links(driver)
        all_results.extend(page_results)
        print(f"✅ Found {len(page_results)} relevant results on page {page_num}")
        if not click_next_page(driver, wait): break
        page_num += 1
    return all_results


def perform_search(driver: webdriver.Chrome, wait: WebDriverWait):
    send_progress_update(0, 100, "Initializing search...")
    time.sleep(SHORT_LOADTIME)
    try:
        init_checkbox = driver.find_element(By.CSS_SELECTOR, "#bfrDsclsType")
        if init_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", init_checkbox)
            print("✅ 공시유형 초기화 해제")
            time.sleep(BUFFER_TIME)
    except Exception as e:
        print(f"❌ 공시유형 초기화 해제 실패: {e}")
    
    try:
        company_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, COMPANY_INPUT_SELECTOR)))
        driver.execute_script("arguments[0].click();", company_input)
        company_input.send_keys("\u0003")  # Ctrl+A to select all
        company_input.clear()
        company_input.send_keys(company_name)
        print("✅ 회사명 설정")
        send_progress_update(10, 100, f"Entered company name: {company_name}")
        time.sleep(BUFFER_TIME)
    except Exception as e:
        print(f"❌ 회사명 설정 실패: {e}")
    
    try:
        from_date_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, FROM_DATE_SELECTOR)))
        driver.execute_script("arguments[0].click();", from_date_input)
        from_date_input.send_keys("\u0003")  # Ctrl+A to select all
        from_date_input.clear()
        from_date_input.send_keys(from_date)
        print("✅ 시작일 설정")
        send_progress_update(20, 100, f"Set date range: {from_date} to {to_date}")
        time.sleep(BUFFER_TIME)

        to_date_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, TO_DATE_SELECTOR)))
        driver.execute_script("arguments[0].click();", to_date_input)
        to_date_input.send_keys("\u0003")  # Ctrl+A to select all
        to_date_input.clear()
        to_date_input.send_keys(to_date)
        print("✅ 종료일 설정")
        time.sleep(BUFFER_TIME)
    except Exception as e:
        print(f"❌ 기간 설정 실패: {e}")
    
    try:
        market_measures_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '시장조치') or contains(@title, '시장조치')]")))
        driver.execute_script("arguments[0].click();", market_measures_tab)
        print("✅ 시장조치 클릭")
        time.sleep(BUFFER_TIME)
    except Exception:
        try:
            market_measures_tab = driver.find_element(By.XPATH, "//li/a[contains(text(), '시장조치')]")
            driver.execute_script("arguments[0].click();", market_measures_tab)
            print("✅ 시장조치 클릭")
            time.sleep(BUFFER_TIME)
        except Exception as e:
            print(f"❌ 시장조치 클릭 실패: {e}")
    
    try:
        checkbox_xpath = "//input[@type='checkbox']/following-sibling::*[contains(text(), '신규/추가/변경/재상장')]/preceding-sibling::input[@type='checkbox']"
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
        driver.execute_script("arguments[0].click();", checkbox)
        print("✅ 신규/추가/변경/재상장 클릭")
        time.sleep(BUFFER_TIME)
    except Exception:
        try:
            checkbox = driver.find_element(By.XPATH, "//label[contains(text(), '신규/추가/변경/재상장')]/input[@type='checkbox']")
            driver.execute_script("arguments[0].click();", checkbox)
            print("✅ 신규/추가/변경/재상장 클릭")
            time.sleep(BUFFER_TIME)
        except Exception as e:
            print(f"❌ 신규/추가/변경/재상장 클릭 실패: {e}")
    
    try:
        # Try CSS selector first
        if not SEARCH_BUTTON_SELECTOR.startswith("//"):
            search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BUTTON_SELECTOR)))
        else:
            # Use XPath selector
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, SEARCH_BUTTON_SELECTOR)))
        
        driver.execute_script("arguments[0].click();", search_button)
        print("✅ 검색 성공")
        send_progress_update(30, 100, "Searching for results...")
        time.sleep(LONG_LOADTIME)  # Wait for search results to load

    except Exception:
        try:
            # Fallback to original XPath selector
            xpath_selector = "//form[@id='searchForm']//section[contains(@class, 'search-group')]//div[@class='btn-group type-bt']//a[contains(@class, 'search-btn')]"
            search_button = driver.find_element(By.XPATH, xpath_selector)
            driver.execute_script("arguments[0].click();", search_button)
            print("✅ 검색 성공")
            time.sleep(LONG_LOADTIME)
        except Exception as e:
            print(f"❌ 검색 실패: {e}")

def main():
    # Import and show input dialog
    try:
        from web_input import get_user_input
        
        print("🚀 Starting KIND Project...")
        print("📋 Please configure your scraping parameters...")
        
        user_input = get_user_input()
        
        if user_input is None:
            print("❌ Operation cancelled by user")
            return
        
        # Update global variables with user input
        global company_name, from_date, to_date, max_rows, headless_mode, debug_mode, progress_port
        company_name = user_input['company_name']
        from_date = user_input['from_date']
        to_date = user_input['to_date']
        max_rows = user_input['max_rows']
        headless_mode = user_input['headless']
        debug_mode = user_input.get('debug_mode', False)
        
        # Set progress port for updates
        from web_input import current_port
        progress_port = current_port
        
        print(f"✅ Configuration loaded:")
        print(f"   Company: {company_name}")
        print(f"   Date Range: {from_date} to {to_date}")
        print(f"   Max Rows: {max_rows}")
        print(f"   Headless Mode: {headless_mode}")
        print(f"   Debug Mode: {debug_mode}")
        print()
        
    except ImportError:
        print("⚠️ Input dialog not available, using default values")
        print(f"   Company: {company_name}")
        print(f"   Date Range: {from_date} to {to_date}")
        print(f"   Max Rows: {max_rows}")
        print()
    
    # Start scraping
    driver, wait = setup_driver(headless=headless_mode)
    try:
        driver.get(DETAILS_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        perform_search(driver, wait)
        items = process_all_pages(driver, wait)
        send_progress_update(95, 100, "Saving results...")
        with open("details_links.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(items)} links to details_links.json")
        send_progress_update(100, 100, "Scraping completed successfully!", completed=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()