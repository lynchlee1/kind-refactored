import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Browser-specific services and options (imported conditionally as used)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Driver managers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

SYSCONST = {
    "details_url": "https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/bond/BIP_CNTS03024V.xml&menuNo=416",
    "prc_url": "https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/bond/BIP_CNTS03025V.xml&menuNo=417",
    "search_button_selector": "#bd_input2_image1",
    "company_input_selector": "#search_string",
    "company_search_selector": "#image2",
    "popup_selector": "#visDiv",
    "popup_iframe": "#iframeIsin",
    "from_date_selector": "#inputCalendar1_input",
    "to_date_selector": "#inputCalendar2_input",
    "buffer_time": 0.4,
    "long_loadtime": 5,
    "short_loadtime": 1.5,
}
def get(variable):
    return SYSCONST[variable]

class SCRAPER:
    def __init__(self, config, headless = False, process_type = None, display = False):
        # Config contains from_date, to_date, company, key
        self.config = config 
        self.headless = headless
        self.driver = None
        self.wait = None
        self.display = display

    def setup(self): 
        self.driver, self.wait = self.setup_driver(headless=self.headless)

    def cleanup(self): 
        if self.driver: self.driver.quit()
    
    def _click_button(self, selector, in_iframe=False):
        if in_iframe:
            iframe_selector = get("popup_iframe")
            iframe = self.driver.find_element(By.CSS_SELECTOR, iframe_selector)
            self.driver.switch_to.frame(iframe)
            if self.display:
                print(f"Switched to iframe: {iframe_selector}")
        
        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        self.driver.execute_script("arguments[0].click();", button)
        if self.display:
            print(f"CSS {selector} button clicked")
        time.sleep(get("buffer_time"))
        
        if in_iframe:
            self.driver.switch_to.default_content()
            if self.display:
                print(f"Switched back to main frame")

    def _fill_input(self, selector, value, in_iframe=False):
        if value is None: return
        if in_iframe:
            iframe_selector = get("popup_iframe")
            iframe = self.driver.find_element(By.CSS_SELECTOR, iframe_selector)
            self.driver.switch_to.frame(iframe)
            if self.display:
                print(f"Switched to iframe: {iframe_selector}")
        input = self.driver.find_element(By.CSS_SELECTOR, selector)
        if self.display:
            print(f"CSS {selector} input completed")
        
        # Use JavaScript click to bypass popup overlay
        self.driver.execute_script("arguments[0].click();", input)
        time.sleep(get("buffer_time"))
        input.clear()
        input.send_keys(value)
        time.sleep(get("buffer_time"))
        
        if in_iframe:
            self.driver.switch_to.default_content()
            if self.display:
                print(f"Switched back to main frame")
    
    def _fill_dates(self):
        try:
            self._fill_input(get("from_date_selector"), self.config.get('from_date'))
            self._fill_input(get("to_date_selector"), self.config.get('to_date'))
        except Exception as e: raise Exception(f"❌ 날짜 입력 실패: {e}")

    def setup_driver(self, headless):
        browser = "chrome"
        long_timeout = get("long_loadtime")

        try:
            options = ChromeOptions()
            if headless: options.add_argument("--headless=new")
            self._apply_chrome_like_options(options)
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            if self.display:
                print("Chrome driver 로딩 완료")

            driver.set_page_load_timeout(long_timeout)
            wait = WebDriverWait(driver, long_timeout)
            return driver, wait
        except Exception as e: raise Exception(f"WebDriver 로딩 실패 ({browser}): {e}")

    def _apply_chrome_like_options(self, options):
        # Stability and crash prevention options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        
        # Memory and performance options
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # Logging and notifications
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        try:
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
        except Exception:
            pass
        
        # Window and user agent
        options.add_argument("--window-size=1600,1000")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )

def fmtkey(key):
    key=str(key).replace(' ','')
    types_str = [
        'EB', 'eb',
        'CB', 'cb',
        'BW', 'bw',
    ]
    for abbr in types_str: key=key.replace(abbr,'')
    idx=key.find('(')
    if idx!=-1: key=key[:idx]
    return key

def run_scrape_conv(scraper, config, url = get("details_url"), is_first_company_for_url = True):
    print(f"\nStarting scrape for company: {config['company']}")
    try:
        # 1. Navigate to the main page (only if URL changed or first company)
        if is_first_company_for_url:
            scraper.driver.get(url)
            time.sleep(get("buffer_time"))

        # 2. Click the search button
        scraper._click_button(get("search_button_selector"))
        time.sleep(get("buffer_time"))

        # 3. Fill the company input in the iframe
        scraper._fill_input(get("company_input_selector"), config["company"], in_iframe=True)
        
        # 4. Click the company search button in the iframe
        scraper._click_button(get("company_search_selector"), in_iframe=True)
        time.sleep(get("buffer_time"))

        # 5. Switch to the iframe & Find matching items with retry mechanism
        iframe_selector = get("popup_iframe")
        iframe = scraper.driver.find_element(By.CSS_SELECTOR, iframe_selector)
        scraper.driver.switch_to.frame(iframe)
        
        # Keep searching until we find a match
        while True:
            try:
                container = scraper.driver.find_element(By.CSS_SELECTOR, "#group74 #group118 #isinList")
                items = container.find_elements(By.CSS_SELECTOR, '[id^="isinList_"][id$="_group178"]')
                searched_keys = []
                for _, item in enumerate(items):
                    text = scraper.driver.execute_script("return arguments[0].textContent.trim();", item) or ""
                    searched_keys.append(fmtkey(text))
                pos = [i for i in range(len(searched_keys)) if searched_keys[i] == fmtkey(config.get("keyword"))]
                
                if pos:
                    target = pos[0] # Use first match - error prevention
                    print(f"Found match: position {target}")
                    if len(pos) > 1:
                        print("Multiple matches found")
                    break
                else:
                    print("No matches found, retrying...")
                    time.sleep(get("buffer_time"))
                    
            except Exception as e:
                print(f"Error finding container, retrying... {e}")
                time.sleep(get("buffer_time"))
        
        scraper._click_button(f"#isinList_{target}_ISIN_ROW")
        scraper.driver.switch_to.default_content()

        # 6. Fill the dates (only if URL changed or first company)
        if is_first_company_for_url:
            scraper._fill_dates()
            time.sleep(get("buffer_time"))

        # 7. Click the search button
        scraper._click_button("#image2")
        time.sleep(get("short_loadtime"))

        # 8. Scrape the data
        all_rows_dicts = []
        previous_page_key = None
        page_num = 1
        while True:
            try:
                tbody = scraper.driver.find_element(By.CSS_SELECTOR, "#grid1_body_tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                page_key = None
                if rows:
                    first_row_cells = rows[0].find_elements(By.TAG_NAME, "td") or rows[0].find_elements(By.TAG_NAME, "th")
                    first_vals = scraper.driver.execute_script(
                        """
                        var result = [];
                        for (var i = 0; i < arguments[0].length; i++) {
                            result.push(arguments[0][i].textContent.trim());
                        }
                        return result;
                        """,
                        first_row_cells
                    )
                    page_key = "|".join(first_vals)
                if previous_page_key is not None and page_key == previous_page_key: break # same page, stop

                data_dicts = []
                for r_idx in range(0, len(rows)):
                    row = rows[r_idx]
                    cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
                    if not cells:
                        continue
                    
                    # Check if first column is visible - if not, skip this row
                    first_cell = cells[0]
                    if not first_cell.is_displayed():
                        continue
                        
                    values = scraper.driver.execute_script(
                        """
                        var result = [];
                        for (var i = 0; i < arguments[0].length; i++) {
                            result.push(arguments[0][i].textContent.trim());
                        }
                        return result;
                        """,
                        cells
                    )
                    print("values", values, "\n")
                    if not values or values[0] == "": 
                        continue
                    row_dict = {}
                    try:
                        if url == get("details_url"):
                            row_dict["title"] = config.get("keyword")
                            # row_dict["exc_start"] = values[3]
                            # row_dict["exc_end"] = values[4]
                            row_dict["date"] = values[5]
                            row_dict["exc_amount"] = float(values[6].replace(',', '')) if values[6] else None
                            row_dict["exc_shares"] = float(values[8].replace(',', '')) if values[8] else None
                            row_dict["exc_price"] = float(values[9].replace(',', '')) if values[9] else None
                            row_dict["listing_date"] = values[10]
                        elif url == get("prc_url"):
                            row_dict["title"] = config.get("keyword")
                            row_dict["date"] = values[1]
                            row_dict["prv_prc"] = float(values[5].replace(',', '')) if values[5] else None
                            row_dict["cur_prc"] = float(values[6].replace(',', '')) if values[6] else None
                    except Exception as e: 
                        print(f"Error creating row_dict: {e}")
                        print(f"Values: {values}")
                        pass
                    data_dicts.append(row_dict)
                all_rows_dicts.extend(data_dicts)
                previous_page_key = page_key
                try:
                    scraper._click_button("#gridPaging_next_btn")
                    time.sleep(get("short_loadtime"))
                    page_num += 1
                except Exception: break
            except Exception: break
        return all_rows_dicts
    except Exception as e:
        print(f"Error scraping {config['company']}: {e}")
        return []

from export_results import read_list_titles, save_excel, clear_excel

if __name__ == "__main__":
    clear_excel(sheet_name="DB")
    clear_excel(sheet_name="EX")
    headless_input = input("Run in headless mode? (y/n): ").strip().lower()
    display_input = input("Run in display mode? (y/n): ").strip().lower()
    base_config = {
        "from_date": "20210101",
        "to_date": time.strftime("%Y%m%d"),
        "headless": headless_input.startswith('y'),
        "display": display_input.startswith('y'),
    }
    excel = read_list_titles()
    if not excel:
        print("No companies found")
        exit()
    
    # Create a single scraper instance for all companies
    scraper = SCRAPER(base_config, headless=base_config.get("headless", False), display=base_config.get("display", False))
    scraper.setup()
    
    try:
        # Process all companies for details URL first
        print("Processing all companies for details URL...")
        for i, item in enumerate(excel):
            rows = []
            config = base_config.copy()
            config["company"] = item[1]
            config["keyword"] = item[0]
            is_first = (i == 0)
            rows = run_scrape_conv(scraper, config, get("details_url"), is_first_company_for_url=is_first)
            if rows:
                save_excel(rows, sheet_name="DB")
                print(f"Saved data for {config['company']} ({len(rows)} rows)")
            else:
                print(f"No data found for {config['company']}")
        
        # Then process all companies for prc URL
        print("Processing all companies for prc URL...")
        for i, item in enumerate(excel):
            rows = []
            config = base_config.copy()
            config["company"] = item[1]
            config["keyword"] = item[0]
            is_first = (i == 0)
            rows = run_scrape_conv(scraper, config, get("prc_url"), is_first_company_for_url=is_first)
            if rows:
                save_excel(rows, sheet_name="EX")
                print(f"Saved data for {config['company']} ({len(rows)} rows)")
            else:
                print(f"No data found for {config['company']}")
        
        print(f"All data saved to: results.xlsx")
    finally:
        # Clean up the single driver instance
        scraper.cleanup()
