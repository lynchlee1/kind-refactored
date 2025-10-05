"""
Main KIND scraper implementation
"""

import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from settings import get

from modules.driver_manager import setup_driver, find_result_rows, extract_table_data, click_next_page
from modules.progress_tracker import send_progress_update, send_page_progress, send_report_progress, send_completion


class KINDScraper:
    def __init__(self, company_name=None, from_date=None, to_date=None, max_rows=None, headless=False, debug_mode=False):
        self.company_name = company_name or get("company_name")
        self.from_date = from_date or get("from_date")
        self.to_date = to_date or get("to_date")
        self.max_rows = max_rows or get("max_rows")
        self.headless = headless
        self.debug_mode = debug_mode
        
        self.driver = None
        self.wait = None

    def setup(self):
        self.driver, self.wait = setup_driver(headless=self.headless)

    def cleanup(self):
        if self.driver: self.driver.quit()

    def perform_search(self):
        buffertime = get("buffer_time")
        # Using multiple selectors may be fail-safe, but it lacks performance and could send keys to wrong element.
        # Change to CSS key if XPATH returns error someday.
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
            time.sleep(buffertime)
        except Exception as e: raise Exception(f"❌ 공시유형 초기화 해제 실패: {e}")
        
        try:
            company_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, get("company_input_selector"))))
            self.driver.execute_script("arguments[0].click();", company_input)
            self.driver.execute_script("arguments[0].value = '';", company_input)
            company_input.send_keys(self.company_name)
            print("✅ 회사명 설정")
            time.sleep(buffertime)
        except Exception as e: raise Exception(f"❌ 회사명 설정 실패: {e}")
        
        try:
            from_date_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, get("from_date_selector"))))
            self.driver.execute_script("arguments[0].click();", from_date_input)
            from_date_input.send_keys("\u0003")
            from_date_input.clear()
            from_date_input.send_keys(self.from_date)
            print("✅ 시작일 설정")
            time.sleep(buffertime)
        except Exception as e: raise Exception(f"❌ 시작일 설정 실패: {e}")
        
        try:
            to_date_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, get("to_date_selector"))))
            self.driver.execute_script("arguments[0].click();", to_date_input)
            to_date_input.send_keys("\u0003")
            to_date_input.clear()
            to_date_input.send_keys(self.to_date)
            print("✅ 종료일 설정")
            time.sleep(buffertime)
        except Exception as e: raise Exception(f"❌ 종료일 설정 실패: {e}")
        
        try:
            market_measures_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, get("market_measures_selector"))))
            self.driver.execute_script("arguments[0].click();", market_measures_tab)
            print("✅ 시장조치 클릭")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ 시장조치 클릭 실패: {e}")
        
        try:
            checkbox = self.wait.until(EC.element_to_be_clickable((By.XPATH, get("new_stock_selector"))))
            self.driver.execute_script("arguments[0].click();", checkbox)
            print("✅ 신규/추가/변경/재상장 클릭")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ 신규/추가/변경/재상장 클릭 실패: {e}")
        
        try:
            search_button = self.driver.find_element(By.XPATH, get("search_button_selector"))
            self.driver.execute_script("arguments[0].click();", search_button)
            print("✅ 검색 성공")
            time.sleep(get("buffer_time"))
        except Exception as e: raise Exception(f"❌ 검색 실패: {e}")

    def click_and_capture_links(self, max_rows_limit=get("max_rows")):
        buffertime = get("buffer_time")
        results = []
        rows = find_result_rows(self.driver)
        if not rows: return results # When no return is found

        base_handle = self.driver.current_window_handle
        total_rows = len(rows[:max_rows_limit])
        first_report_number = None
        
        for i, row in enumerate(rows[:max_rows_limit], start=1):
            if i == 1:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 1: first_report_number = cells[0].text.strip()      

            # Send progress update every 5 reports or on the last report
            if (i + 1) % 5 == 0 or (i + 1) == total_rows:
                send_report_progress(i + 1, total_rows, f"Processing report {i + 1} of {total_rows}")
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                print(cells)
                date_txt = cells[1].text.strip() if len(cells) >= 2 else ""
                company_txt = cells[2].text.strip() if len(cells) >= 3 else ""
                title_txt = cells[3].text.strip() if len(cells) >= 4 else row.text.strip()

                # Filter by target keywords
                target_keywords = get("target_keywords")
                has_keyword = any(keyword in title_txt for keyword in target_keywords)
                if not has_keyword: 
                    continue

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
                            before = set(self.driver.window_handles)
                            self.driver.execute_script("arguments[0].click();", a)
                            # Wait for popup or same-tab nav (reduced wait)
                            for _ in range(get("long_waitcount")): 
                                time.sleep(buffertime)
                                after = set(self.driver.window_handles)
                                if len(after) > len(before):
                                    break
                            new_handles = [h for h in self.driver.window_handles if h not in before]
                            if new_handles:
                                self.driver.switch_to.window(new_handles[0])
                                time.sleep(buffertime)
                                viewer_url = self.driver.current_url
                                # settle URL changes (reduced wait)
                                for _ in range(get("short_waitcount")):
                                    time.sleep(buffertime)
                                    cur = self.driver.current_url
                                    if cur != viewer_url:
                                        viewer_url = cur

                                table_data = extract_table_data(self.driver, self.wait)
                                
                                self.driver.close()
                                self.driver.switch_to.window(base_handle)
                            else:
                                # same-tab attempt
                                current_url = self.driver.current_url
                                if ("details" in current_url) or ("viewer" in current_url):
                                    viewer_url = current_url
                                # go back regardless to keep row context
                                try:
                                    self.driver.back()
                                    time.sleep(buffertime)
                                except Exception:
                                    pass
                            if viewer_url:
                                break
                    except Exception:
                        try:
                            self.driver.switch_to.window(base_handle)
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
                    self.driver.switch_to.window(base_handle)
                except Exception:
                    pass
                continue

        return results

    def process_all_pages(self):
        """Process all pages of search results"""
        all_results = []
        page_num = 1
        
        while True:
            print(f"📄 Processing page {page_num}...")
            # Send page progress update
            send_page_progress(page_num)
            page_results = self.click_and_capture_links(self.max_rows)
            all_results.extend(page_results)
            print(f"✅ Found {len(page_results)} relevant results on page {page_num}")
            if not click_next_page(self.driver, self.wait): 
                break
            page_num += 1
        return all_results

    def run(self):
        """Run the complete scraping process"""
        try:
            self.setup()
            self.driver.get(get("details_url"))
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.perform_search()
            items = self.process_all_pages()
            print("💾 Saving results...")
            send_progress_update(message="Saving results to JSON file...")
            
            # Save results to JSON
            output_file = get("output_json_file")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved {len(items)} links to {output_file}")
            print("✅ Scraping completed successfully!")
            
            return items
            
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            raise  # BREAK ON FAILURE
        finally:
            self.cleanup()