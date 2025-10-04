import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Import configurable selectors
try:
    from dev_config import RESULT_ROW_SELECTOR, NEXT_PAGE_SELECTOR, TABLE_SELECTOR, IFRAME_SELECTOR
except ImportError:
    # Default selectors
    RESULT_ROW_SELECTOR = "tr[onclick*='viewDetail']"
    NEXT_PAGE_SELECTOR = "a.paging_next"
    TABLE_SELECTOR = "table, iframe"
    IFRAME_SELECTOR = "iframe[name='viewer']"

BUFFER = 0.5
LIGHT_LOADING_TIME = 2
HEAVY_LOADING_TIME = 3

# Can add/modify multiple selectors to be fail-safe.
def find_result_rows(driver):
    result_table_selectors = ["table.list.type-00", RESULT_ROW_SELECTOR]
    rows = []
    
    for selector in result_table_selectors:
        try:
            tables = driver.find_elements(By.CSS_SELECTOR, selector)
            for table in tables:
                table_location = table.location
                # Prevent from selecting the table in the top of the page
                if table_location['y'] > 300:
                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr") or table.find_elements(By.TAG_NAME, "tr")
                    print(f"{selector} used for find_result_rows")
        except Exception:
            continue
    return rows

def extract_from_iframe(driver, wait):
    try:
        # Wait for iframe to load - try multiple selectors
        print("⏳ Waiting for iframe...")
        iframe_selectors = [
            IFRAME_SELECTOR,
            "iframe[name='docViewFrm']",
            "iframe[name='viewer']", 
            "iframe[name='content']",
            "iframe",
            "iframe[src*='viewer']",
            "iframe[src*='doc']"
        ]
        
        iframe = None
        for selector in iframe_selectors:
            try:
                iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Found iframe with selector: {selector}")
                break
            except Exception:
                continue
        
        if not iframe:
            print("❌ No iframe found with any selector")
            return []
            
        print("✅ Switching to iframe...")
        driver.switch_to.frame(iframe)
        
        # Wait for content to load inside iframe
        print("⏳ Waiting for table content...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("✅ Found table content")
        
        all_tables_data = []
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Found {len(tables)} tables in iframe")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"📋 Table {table_idx}: {len(rows)} rows")
            
            if len(rows) > 0:
                table_data = []
                
                # Extract all rows from this table
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: 
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        # Only add non-empty rows
                        if any(cell.strip() for cell in row_data):
                            table_data.append({
                                "row_index": row_idx,
                                "data": row_data
                            })
                            print(f"  Row {row_idx}: {row_data[:3]}...")  # Show first 3 cells
                
                # Only include tables with actual data
                if table_data:
                    all_tables_data.append({
                        "table_index": table_idx,
                        "rows": table_data,
                        "row_count": len(table_data)
                    })
                    print(f"✅ Table {table_idx} added with {len(table_data)} rows")
                else:
                    print(f"⚠️ Table {table_idx} has no data")
        
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

def extract_table_data(driver, wait):
    print("🔍 Starting table data extraction...")
    
    # First try to extract from iframe
    iframe_data = extract_from_iframe(driver, wait)
    if iframe_data:
        return iframe_data
    
    # If iframe fails, try direct extraction from main page
    print("🔄 Iframe extraction failed, trying direct extraction...")
    return extract_direct_tables(driver, wait)


def extract_direct_tables(driver, wait):
    try:
        print("🔍 Extracting tables directly from main page...")
        
        # Wait for any tables to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        all_tables_data = []
        tables = driver.find_elements(By.CSS_SELECTOR, TABLE_SELECTOR)
        print(f"📊 Found {len(tables)} tables on main page")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"📋 Table {table_idx}: {len(rows)} rows")
            
            if len(rows) > 0:
                table_data = []
                
                # Extract all rows from this table
                for row_idx, row in enumerate(rows):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: 
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        # Only add non-empty rows
                        if any(cell.strip() for cell in row_data):
                            table_data.append({
                                "row_index": row_idx,
                                "data": row_data
                            })
                            print(f"  Row {row_idx}: {row_data[:3]}...")  # Show first 3 cells
                
                # Only include tables with actual data
                if table_data:
                    all_tables_data.append({
                        "table_index": table_idx,
                        "rows": table_data,
                        "row_count": len(table_data)
                    })
                    print(f"✅ Table {table_idx} added with {len(table_data)} rows")
                else:
                    print(f"⚠️ Table {table_idx} has no data")
        
        print(f"📊 Total tables extracted from main page: {len(all_tables_data)}")
        return all_tables_data
                    
    except Exception as e: 
        print(f"❌ Error extracting direct tables: {e}")
        import traceback
        traceback.print_exc()
    
    return []

def click_next_page(driver, wait):
    try:
        print("🔍 Attempting to click next page...")
        
        # Check if next button exists and is clickable
        next_button_selectors = [
            NEXT_PAGE_SELECTOR,
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
