import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .settings import get
from .search_modes import get_search_mode

# Driver setup imports
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class KINDScraper:
    def __init__(self, config, headless = False, process_type = None):
        self.config = config # from_date, to_date, company, keyword
        self.headless = headless
        self.process_type = process_type
        self.driver = None
        self.wait = None

    def setup(self):
        self.driver, self.wait = self._setup_driver(headless=self.headless)

    def cleanup(self):
        if self.driver: self.driver.quit()

    def search(self):
        try:
            self._disable_reset_button()
            search_mode = get_search_mode(self.process_type)

            company = self.config.get('company')
            if company: self._fill_input_CSS(get("company_input_selector"), company)

            keyword = self.config.get('keyword')
            if keyword: self._fill_input_CSS(get("keyword_input_selector"), keyword)

            self._fill_dates()

            main_menu_selector = search_mode.main_menu_selector
            if main_menu_selector: self._click_button_CSS(main_menu_selector)
            sub_menu_selector = search_mode.sub_menu_selector
            if sub_menu_selector: self._click_button_CSS(sub_menu_selector)
            
            search_button_selector = get("search_button_selector")
            if search_button_selector: self._click_button_CSS(search_button_selector)
            results = self._process_results()
            return results
        except Exception as e: raise Exception(f"❌ 검색 실패: {e}")

    def _disable_reset_button(self):
        try:
            reset_checkbox = self.driver.find_element(By.CSS_SELECTOR, get("reset_selector"))
            self.driver.execute_script("""
                var checkbox = arguments[0];
                checkbox.checked = false;
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                checkbox.dispatchEvent(new Event('click', { bubbles: true }));
            """, reset_checkbox)
            final_state = reset_checkbox.is_selected()
            if not final_state: print("✅ 공시유형 초기화 해제 완료")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ 공시유형 초기화 해제 실패: {e}")

    def _click_button_XPATH(self, selector):
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            button.click()
            print(f"✅ XPATH {selector} 버튼 클릭 완료")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ XPATH {selector} 버튼 클릭 실패: {e}")
    
    def _click_button_CSS(self, selector):
        try:
            button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            self.driver.execute_script("arguments[0].click();", button)
            print(f"✅ CSS {selector} 버튼 클릭 완료")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ CSS {selector} 클릭 실패: {e}")

    def _click_button(self, css_selector, xpath_selector):
        try: self._click_button_CSS(css_selector)
        except Exception: self._click_button_XPATH(xpath_selector)

    def _fill_input_XPATH(self, selector, value):
        if value is None: return
        try:
            input = self.driver.find_element(By.XPATH, selector)
            input.clear()
            input.send_keys(value)
            print(f"✅ XPATH {selector} 입력 완료")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ XPATH {selector} 입력 실패: {e}")

    def _fill_input_CSS(self, selector, value):
        if value is None: return
        try:
            input = self.driver.find_element(By.CSS_SELECTOR, selector)
            input.clear()
            input.send_keys(value)
            print(f"✅ CSS {selector} 입력 완료")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ CSS {selector} 입력 실패: {e}")

    def _fill_input(self, css_selector, xpath_selector, value):
        if value is None: return
        try: self._fill_input_CSS(css_selector, value)
        except Exception: self._fill_input_XPATH(xpath_selector, value)
    
    def _fill_dates(self):
        try:
            self._fill_input_CSS(get("from_date_selector"), self.config.get('from_date'))
            self._fill_input_CSS(get("to_date_selector"), self.config.get('to_date'))
        except Exception as e: raise Exception(f"❌ 날짜 입력 실패: {e}")

    def _click_next_page(self):
        current_report_number = ""
        try:
            current_report_number = self.driver.find_element(By.CSS_SELECTOR, get("first_idx_selector")).text.strip()
        except Exception: return False

        next_button = None
        try: next_button = self.driver.find_element(By.CSS_SELECTOR, get("next_page_selector"))
        except Exception: raise Exception(f"❌ 다음 페이지 버튼 찾기 실패")
        time.sleep(get("buffer_time"))

        try: self.driver.execute_script("arguments[0].click();", next_button)
        except Exception: raise Exception(f"❌ 다음 페이지 버튼 클릭 실패")
        time.sleep(get("short_loadtime"))

        try: 
            new_report_number = self.driver.find_element(By.CSS_SELECTOR, get("first_idx_selector")).text.strip()            
            if current_report_number and new_report_number != current_report_number:
                print(f"✅ 다음 페이지 클릭 완료")
                return True
            else: return False
        except Exception as e: raise Exception(f"❌ 페이지 변경 오류: {e}")

    def _process_results(self):
        all_results = []
        first_report_number = None
        try:
            first_report_number = self._get_first_report_number()
            page_num = 1
            while True:
                result_rows = self._find_result_rows(self.driver)                
                if not result_rows: break
                page_results = self._process_page_rows(result_rows)
                all_results.extend(page_results)
                if not self._click_next_page(): break # End of results
                page_num += 1
                time.sleep(get("buffer_time"))
            
            print(f"✅ 데이터 수집 완료: 총 {len(all_results)}개 항목")
            return all_results
        except Exception as e: raise Exception(f"❌ 결과 처리 실패: {e}")

    def _get_first_report_number(self):
        try:
            first_idx_element = self.driver.find_element(By.CSS_SELECTOR, get("first_idx_selector"))
            first_report_number = int(first_idx_element.text.strip())
            return first_report_number
        except Exception: return None

    def _process_page_rows(self, result_rows):
        page_results = []
        for idx, row in enumerate(result_rows):
            try:
                row_data = self._process_single_row(row)
                if row_data is not None: 
                    page_results.append(row_data)
            except Exception as e: 
                print(f"❌ 행 처리 중 오류: {e}")
                continue
        return page_results

    def _process_single_row(self, row):
        try:
            row_data = self._extract_row_basic_data(row)
            if not self._should_process_row(row_data):
                print(f"{row_data['title']}: 키워드 없음")
                return None
            print(f"{row_data['title']}: 키워드 있음")
            table_data = self._click_and_extract_data(row, row_data['title'])
            if table_data: 
                row_data['table_data'] = table_data
                return row_data
            else:
                row_data['table_data'] = []
                return row_data
        except Exception: return None

    def _click_and_extract_data(self, row, title):
        buffertime = get("buffer_time")
        base_handle = self.driver.current_window_handle        
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            anchors = []
            if len(cells) >= 4: anchors = cells[3].find_elements(By.TAG_NAME, "a")
            if not anchors: return None
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
                        before = set(self.driver.window_handles)
                        self.driver.execute_script("arguments[0].click();", a)
                        for _ in range(get("waitcount")): 
                            time.sleep(buffertime)
                            after = set(self.driver.window_handles)
                            if len(after) > len(before): break
                        
                        new_handles = [h for h in self.driver.window_handles if h not in before]
                        if new_handles:
                            self.driver.switch_to.window(new_handles[0])
                            time.sleep(buffertime)
                            viewer_url = self.driver.current_url
                            for _ in range(get("waitcount")):
                                time.sleep(buffertime)
                                cur = self.driver.current_url
                                if cur != viewer_url:
                                    viewer_url = cur
                            table_data = self._extract_table_data(self.driver, self.wait)
                            self.driver.close()
                            self.driver.switch_to.window(base_handle)
                            if table_data:
                                return table_data
                            else:
                                return None
                except Exception:
                    try: self.driver.switch_to.window(base_handle)
                    except Exception: pass
                    continue
        except Exception as e:
            try: self.driver.switch_to.window(base_handle)
            except Exception: pass
        return None

    def _should_process_row(self, row_data):
        try:
            search_mode = get_search_mode(self.process_type)
            if not search_mode.keywords_list: return True
            title = row_data.get('title')
            return any(keyword in title for keyword in search_mode.keywords_list)
        except Exception: return False

    def _extract_row_basic_data(self, row):
        try:
            cells = row.find_elements(By.TAG_NAME, "td")

            idx = cells[0].text.strip()
            date = cells[1].text.strip()
            company = cells[2].text.strip()
            title = cells[3].text.strip()
            
            viewer_link = row.find_element(By.CSS_SELECTOR, "a")
            viewer_url = viewer_link.get_attribute("href")
            
            return {
                'idx': idx,
                'date': date,
                'company': company,
                'title': title,
                'viewer_url': viewer_url
            }
        except Exception as e: raise Exception(f"❌ 행 데이터 추출 실패: {e}")

    def run(self):
        try:
            self.setup()
            self.driver.get(get("details_url"))
            print(f"✅ 접속 완료")
            time.sleep(get("buffer_time"))
            
            results = self.search()
            time.sleep(get("buffer_time"))

            self._save_results(results)
            print(f"✅ 실행 완료")
            return results
        except Exception as e: raise Exception(f"❌ 실행 실패: {e}")
        finally: self.cleanup()

    def _save_results(self, results):
        try:
            output_file = get("results_json")
            with open(output_file, 'w', encoding='utf-8') as f: json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ {output_file}에 저장 완료")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")

    def _setup_driver(self, headless):
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
        
        chrome_options.add_argument("--window-size=1600,1000")

        try:
            # Set Chrome binary path for macOS
            chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            # Try to use ChromeDriver directly without webdriver-manager
            print("🔍 Chrome driver 시작 중...")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(get("long_loadtime"))
            wait = WebDriverWait(driver, get("long_loadtime"))
            print("✅ Chrome driver 로딩 완료")
            return driver, wait
        except Exception as e: 
            print(f"❌ Chrome driver 실패: {e}")
            # Fallback: try with webdriver-manager as last resort
            try:
                print("🔄 Fallback: ChromeDriverManager 사용 시도...")
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.set_page_load_timeout(get("long_loadtime"))
                wait = WebDriverWait(driver, get("long_loadtime"))
                print("✅ Chrome driver 로딩 완료 (ChromeDriverManager)")
                return driver, wait
            except Exception as e2:
                raise Exception(f"❌ Chrome driver 로딩 실패: {e2}")

    def _find_result_rows(self, driver):
        result_selector = get("result_row_selector")
        tables = driver.find_elements(By.CSS_SELECTOR, result_selector)
        for table in tables:
            if table.location['y'] > 300: # Prevent from selecting table in the top of the page
                rows = table.find_elements(By.CSS_SELECTOR, "tbody tr") or table.find_elements(By.TAG_NAME, "tr")
                return rows
        return []

    def _extract_from_iframe(self, driver, wait):
        iframe = None
        iframe_selector = get("iframe_selector")        
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))    
            if not iframe: return []
            driver.switch_to.frame(iframe)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print(f"표 발견됨")
            all_tables_data = []
        except Exception as e:
            print(f"❌ iframe 처리 실패: {e}")
            return []
        
        try:
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
        except Exception as e: 
            raise Exception(f"❌ Error extracting from iframe: {e}")
        finally:
            try: driver.switch_to.default_content()
            except Exception as e: raise Exception(f"❌ Error switching back to main content: {e}")

    def _extract_direct_tables(self, driver, wait):
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
                    else: raise Exception(f"❌ Table {table_idx} has no data")
            return all_tables_data                    
        except Exception as e: raise Exception(f"❌ Error extracting direct tables: {e}")

    # WILL BE REMOVED: replace with iframe method
    def _extract_table_data(self, driver, wait):
        iframe_data = self._extract_from_iframe(driver, wait)
        if iframe_data: return iframe_data
        return self._extract_direct_tables(driver, wait)
