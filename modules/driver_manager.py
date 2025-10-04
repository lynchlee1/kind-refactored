"""
Web driver management and utilities
"""

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from settings import get

def setup_driver(headless: bool = False) -> tuple[webdriver.Chrome, WebDriverWait]:
    """Setup Chrome driver with optimized settings"""
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
    
    # JavaScript is enabled by default
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(get("implicit_wait"))
        driver.set_page_load_timeout(30)  # Add page load timeout
        wait = WebDriverWait(driver, 20)
        print("✅ Chrome driver setup successful")
        return driver, wait
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        raise

def find_result_rows(driver):
    """Find result rows in the search results table"""
    result_selectors = get("result_row_selector")
    
    # Handle both string and array formats
    if isinstance(result_selectors, str):
        result_selectors = [result_selectors]
    
    for selector in result_selectors:
        tables = driver.find_elements(By.CSS_SELECTOR, selector)
        for table in tables:
            table_location = table.location
            # Prevent from selecting the table in the top of the page
            if table_location['y'] > 300:
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr") or table.find_elements(By.TAG_NAME, "tr")
                print(f"✅ {selector} used for find_result_rows - found {len(rows)} rows")
                return rows
    return []

def extract_from_iframe(driver, wait):
    """Extract table data from iframe"""
    iframe_selectors = get("iframe_selector")
    
    # Handle both string and array formats
    if isinstance(iframe_selectors, str):
        iframe_selectors = [iframe_selectors]
    
    iframe = None
    for selector in iframe_selectors:
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            print(f"✅ Found iframe with selector: {selector}")
            break
        except Exception:
            continue
    
    if not iframe:
        print("❌ No iframe found with given selectors")
        return []    
        
    driver.switch_to.frame(iframe)
    try:
        print("⏳ Waiting for table content...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("✅ Found table content")
        
        all_tables_data = []
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) > 0:
                table_data = []
                
                # Extract all rows from this table (optimized with JavaScript)
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: 
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        # Use JavaScript for faster text extraction
                        try:
                            row_data = driver.execute_script("""
                                var cells = arguments[0];
                                var result = [];
                                for (var i = 0; i < cells.length; i++) {
                                    result.push(cells[i].textContent.trim());
                                }
                                return result;
                            """, cells)
                        except:
                            # Fallback to Python extraction
                            row_data = [cell.text.strip() for cell in cells]
                        
                        # Only add non-empty rows
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
                    print(f"✅ Table {table_idx}: {len(table_data)} rows extracted")
        
        print(f"📊 Total tables extracted from iframe: {len(all_tables_data)}")
        return all_tables_data
                    
    except Exception as e: 
        print(f"❌ Error extracting from iframe: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.switch_to.default_content()
            print("✅ Switched back to main content")
        except Exception as e:
            print(f"⚠️ Error switching back to main content: {e}")
    
    return []

def extract_direct_tables(driver, wait):
    """Extract table data directly from main page"""
    try:
        print("🔍 Extracting tables directly from main page...")
        
        # Wait for any tables to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        all_tables_data = []
        table_selector = get("table_selector")
        tables = driver.find_elements(By.CSS_SELECTOR, table_selector)
        print(f"📊 Found {len(tables)} tables on main page")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"📋 Table {table_idx}: {len(rows)} rows")
            
            if len(rows) > 0:
                table_data = []
                
                # Extract all rows from this table (optimized with JavaScript)
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: 
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        # Use JavaScript for faster text extraction
                        try:
                            row_data = driver.execute_script("""
                                var cells = arguments[0];
                                var result = [];
                                for (var i = 0; i < cells.length; i++) {
                                    result.push(cells[i].textContent.trim());
                                }
                                return result;
                            """, cells)
                        except:
                            # Fallback to Python extraction
                            row_data = [cell.text.strip() for cell in cells]
                        
                        # Only add non-empty rows
                        if any(cell.strip() for cell in row_data):
                            table_data.append({
                                "row_index": row_idx,
                                "data": row_data
                            })
                
                # Only include tables with actual data
                if table_data:
                    all_tables_data.append({
                        "table_index": table_idx,
                        "rows": table_data,
                        "row_count": len(table_data)
                    })
                    print(f"✅ Table {table_idx}: {len(table_data)} rows extracted")
                else:
                    print(f"⚠️ Table {table_idx} has no data")
        
        print(f"📊 Total tables extracted from main page: {len(all_tables_data)}")
        return all_tables_data
                    
    except Exception as e: 
        print(f"❌ Error extracting direct tables: {e}")
        import traceback
        traceback.print_exc()
    
    return []

def extract_table_data(driver, wait):
    """Extract table data from iframe or main page"""
    print("🔍 Starting table data extraction...")
    
    # First try to extract from iframe
    iframe_data = extract_from_iframe(driver, wait)
    if iframe_data:
        return iframe_data
    
    # If iframe fails, try direct extraction from main page
    print("🔄 Iframe extraction failed, trying direct extraction...")
    return extract_direct_tables(driver, wait)

def click_next_page(driver, wait):
    """Click next page button and verify page change"""
    try:
        print("🔍 Attempting to click next page...")
        
        # Check if next button exists and is clickable
        next_page_selector = get("next_page_selector")
        next_button_selectors = [
            next_page_selector,
            "#main-contents > section.paging-group > div.paging.type-00 > a.next",
            "a.next",
            ".paging a.next",
            "//a[contains(@class, 'next')]",
            "//a[contains(text(), '다음')]"
        ]
        
        next_button = None
        for selector in next_button_selectors:
            try:
                if selector.startswith("//"):
                    next_button = driver.find_element(By.XPATH, selector)
                else:
                    next_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                # Check if button is enabled and visible
                if next_button.is_enabled() and next_button.is_displayed():
                    print(f"✅ Found next button with selector: {selector}")
                    break
                else:
                    print(f"⚠️ Next button found but not clickable: {selector}")
                    next_button = None
            except Exception:
                continue
        
        if not next_button:
            print("❌ No next button found - likely on last page")
            return False
        
        # Get current report number before clicking (optional, for verification)
        current_report_number = ""
        try:
            current_report_cell = driver.find_element(By.CSS_SELECTOR, "#main-contents > section.scrarea.type-00 > table > tbody > tr.first.active > td.first.txc")
            current_report_number = current_report_cell.text.strip()
            print(f"📄 Current report number: {current_report_number}")
        except Exception:
            print("⚠️ Could not get current report number")
        
        # Uncheck init checkbox if selected
        try:
            init_checkbox = driver.find_element(By.CSS_SELECTOR, "#bfrDsclsType")
            if init_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", init_checkbox)
                time.sleep(1)
                print("✅ Unchecked init checkbox")
        except Exception:
            pass
        
        # Click the next button
        print("🖱️ Clicking next button...")
        try:
            driver.execute_script("arguments[0].click();", next_button)
            print("✅ Clicked next button (JavaScript)")
        except Exception:
            try:
                next_button.click()
                print("✅ Clicked next button (direct)")
            except Exception:
                try:
                    ActionChains(driver).move_to_element(next_button).click().perform()
                    print("✅ Clicked next button (ActionChains)")
                except Exception as e:
                    print(f"❌ Failed to click next button: {e}")
                    return False
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(2)  # Give it time to load
        
        # Check if we're still on the same page (simple check)
        try:
            # Wait for the page content to be present
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-contents")))
            
            # Check if we have a new report number
            new_report_cell = driver.find_element(By.CSS_SELECTOR, "#main-contents > section.scrarea.type-00 > table > tbody > tr.first.active > td.first.txc")
            new_report_number = new_report_cell.text.strip()
            
            if current_report_number and new_report_number != current_report_number:
                print(f"✅ Page changed! New report number: {new_report_number}")
                return True
            elif not current_report_number:
                # If we couldn't get the original number, assume success
                print("✅ Page navigation completed (no previous number to compare)")
                return True
            else:
                print(f"⚠️ Page may not have changed. Old: {current_report_number}, New: {new_report_number}")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not verify page change: {e}")
            # Still return True as the click might have worked
            return True
            
    except Exception as e:
        print(f"❌ Error in click_next_page: {e}")
        return False
