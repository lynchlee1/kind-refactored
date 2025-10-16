import json
import os
import sys
from abc import ABC, abstractmethod

try:
    from .settings import get
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from settings import get

try:
    from ..designlib.ui_components import BasicPage
except ImportError:
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from designlib.ui_components import BasicPage  # type: ignore

class BaseDataProcessor(ABC):
    def __init__(self, mode_name): self.mode_name = mode_name
        
    @abstractmethod
    def process_raw_data(self, items): pass
    
    def save_to_database(self, config):
        try:
            company_name = config.get('company')
            processed_data = config.get('processed_data')
            key_list = config.get('key_list')
            fd_new = config.get('from_date')
            ld_new = config.get('to_date')
            db_filename = config.get('db_filename')
            
            # Debug and validate required parameters
            if not db_filename:
                raise Exception(f"❌ db_filename is required but got: {repr(db_filename)}")
            if not company_name:
                raise Exception(f"❌ company_name is required but got: {repr(company_name)}")
            if not key_list:
                raise Exception(f"❌ key_list is required but got: {repr(key_list)}")
            
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            db_path = os.path.join(root_dir, 'resources', db_filename)
            
            try:
                with open(db_path, 'r', encoding='utf-8') as f: db = json.load(f)
                existing_entry = db.get(company_name)
                if existing_entry:
                    existing_data = existing_entry.get('data', [])
                else:
                    existing_entry = {'first_date': None, 'last_date': None, 'data': []}
                    existing_data = []
            except Exception:
                db = {}
                existing_entry = {'first_date': None, 'last_date': None, 'data': []}
                existing_data = []
            
            def make_key(x, keys):
                if not x: return ""
                return "|".join(str(x.get(key, '')) for key in keys)

            seen = set(make_key(item, key_list) for item in existing_data)
            merged_data = list(existing_data)
            if processed_data:
                for item in processed_data:
                    if not item: continue
                    k = make_key(item, key_list)
                    if k not in seen:
                        merged_data.append(item)
                        seen.add(k)
            # Check if we should preserve original search ranges (for refresh operations)
            if 'original_search_first_date' in config:
                self._preserve_original_ranges = True
                self._original_first_date = config['original_search_first_date']
                self._original_last_date = config['original_search_last_date']
            else:
                self._preserve_original_ranges = False
            
            # We should call _update_date_ranges when there were no datas, too.
            self._update_date_ranges(db, company_name, existing_entry, fd_new, ld_new, merged_data, db_filename)
            return True
        except Exception as e: raise Exception(f"❌ JSON saving failed: {e}")
    
    def _update_date_ranges(self, db, company_name, existing_entry, fd_new, ld_new, merged_data, db_filename):
        # Use the search date ranges as first_date and last_date (not actual data dates)
        # For refresh operations, preserve original first_date but update last_date to today
        if hasattr(self, '_preserve_original_ranges') and self._preserve_original_ranges:
            fd_fin = getattr(self, '_original_first_date', fd_new)  # Preserve original first_date
            ld_fin = ld_new  # Update last_date to today's date (from refresh search)
        else:
            fd_fin = fd_new  # Search from_date
            ld_fin = ld_new  # Search to_date
        
        modules_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(modules_dir)
        db_path = os.path.join(root_dir, 'resources', db_filename)
        
        db[company_name] = {
            'first_date': fd_fin,
            'last_date': ld_fin,
            'data': merged_data
        }
        with open(db_path, 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=2)

class HistDataProcessor(BaseDataProcessor):
    def __init__(self): super().__init__('hist')
    def process_raw_data(self, items):
        processed_data = []
        for item in items:
            if not item: continue
            company_name = item.get('company', '')
            date = item.get('date', '')
            table_data = item.get('table_data', [])
            if len(table_data) > 2:
                rows = table_data[2].get('rows', [])
                report_datas_len = len(rows) - 1
                for i in range(report_datas_len):
                    if i + 1 < len(rows) and len(rows[i+1].get('data', [])) >= 5:
                        report_data = rows[i+1]['data'][2:5]
                        processed_data.append({
                            'company': company_name,
                            'date': date,
                            'round': report_data[0],
                            'additional_shares': report_data[1],
                            'issue_price': report_data[2]
                        })
        return processed_data

class PrcDataProcessor(BaseDataProcessor):
    def __init__(self): super().__init__('prc')
    def process_raw_data(self, items):
        processed_data = []
        for item in items:
            try:
                if not item: continue
                company_name = item.get('company', '')
                date = item.get('date', '')
                table_data = item.get('table_data', [])
                
                # Handle the table structure correctly
                if len(table_data) > 0 and 'rows' in table_data[0]:
                    report_data = table_data[0]['rows']
                    
                    # Find the price adjustment section (section 1)
                    in_price_section = False
                    for i in range(len(report_data)):
                        row_data = report_data[i]['data']
                        
                        # Check if this is the start of price adjustment section
                        if len(row_data) > 0 and "조정전 전환가액" in str(row_data[0]):
                            in_price_section = True
                            continue
                        
                        # Check if we've moved to the next section (share count section)
                        if len(row_data) > 0 and "전환가능주식수" in str(row_data[0]):
                            in_price_section = False
                            continue
                        
                        # Process rows only in the price adjustment section
                        if in_price_section and len(row_data) >= 4:
                            round_val = str(row_data[0]).strip()
                            # Skip header rows and non-numeric rounds
                            if round_val.isdigit():
                                prev_prc = str(row_data[2]).strip()
                                issue_price = str(row_data[3]).strip()
                                processed_data.append({
                                    'company': company_name,
                                    'date': date,
                                    'round': round_val,
                                    'prev_prc': prev_prc,
                                    'issue_price': issue_price
                                })
            except Exception as e: 
                print(f"⚠️ Error processing PRC item: {e}")
                continue
        return processed_data

class SearchMode:    
    def __init__(self, config):
        # Display configs
        self.id = config.get('id') # id for the mode. 'hist'
        self.title = config.get('title') # title for display. '전환기록 조회'

        # Scraping configs
        self.keyword = config.get('keyword') # 검색할 키워드. 
        self.keywords_list = config.get('keywords_list') # 제목에 들어가는지 검사할 키워드 리스트.
        self.main_menu_selector = config.get('main_menu_selector') # 메인 메뉴 선택자. '시장조치'
        self.sub_menu_selector = config.get('sub_menu_selector') # 서브 메뉴 선택자. '신규발행'
        self.data_processor_class = config.get('data_processor_class') # 데이터 처리 클래스. HistDataProcessor
        self.database_name = config.get('database_name') # 데이터베이스 파일 이름. 'database_hist.json'
        self.columns = config.get('columns') # 데이터베이스 구조. ['company', 'date', ... ]
        
        # Page generation configs
        self.execution_message    = config.get('execution_message')
        self.run_function         = config.get('run_function')
    
    def generate_page(self):
        # Simplified: redirect to main page since individual company pages are no longer needed
        from designlib.generate_pages_simple import main_page
        return main_page()
    
    def generate_dataset_page(self, company_name=None, round_filter=''):
        """Generate dataset page using real data from database files"""
        page = BasicPage(title=f"{self.title}", container_width="1200px", container_height="800px")
        
        # Load real data from database file
        try:
            # Get database file path
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            db_filename = self.database_name
            db_path = os.path.join(root_dir, 'resources', db_filename)
            
            # Load database
            with open(db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Get company data
            if company_name and company_name in database:
                company_data = database[company_name]
                first_date = company_data.get('first_date', '')
                last_date = company_data.get('last_date', '')
                rows_data = company_data.get('data', [])
                display_company = company_name
            else:
                # If no specific company, show all companies data
                all_data = []
                companies = list(database.keys())
                display_company = f"전체 기업 ({len(companies)}개)" if companies else "데이터 없음"
                first_date = ""
                last_date = ""
                
                for comp_name, comp_data in database.items():
                    comp_rows = comp_data.get('data', [])
                    for row in comp_rows:
                        row_copy = row.copy()
                        row_copy['company'] = comp_name  # Ensure company name is set
                        all_data.append(row_copy)
                
                # Sort by date (most recent first)
                all_data.sort(key=lambda x: x.get('date', ''), reverse=True)
                rows_data = all_data[:100]  # Limit to 100 most recent entries
                
                if all_data:
                    first_date = all_data[-1].get('date', '')
                    last_date = all_data[0].get('date', '')
            
            # Apply round filter if specified
            if round_filter and round_filter.strip():
                rows_data = [row for row in rows_data if str(row.get('round', '')).strip() == round_filter.strip()]
            
            # Sort data in ascending order (oldest first) for proper cumulative calculation
            rows_data.sort(key=lambda x: x.get('date', ''))
            
            # Set column titles based on mode - matching the actual table structure
            if self.id == 'hist':
                # Calculate cumulative values for HIST mode
                acc_shares = 0
                acc_amount = 0
                for row in rows_data:
                    shares = self._parse_number(row.get('additional_shares', ''))
                    price = self._parse_number(row.get('issue_price', ''))
                    amount = shares * price
                    acc_shares += shares
                    acc_amount += amount
                    # Add cumulative values to each row
                    row['cumulative_shares'] = acc_shares
                    row['cumulative_amount'] = acc_amount
                column_titles = ["#", "발행시간", "회차", "추가주식수(주)", "누적 추가주식수", "발행가액(원)", "총액", "누적 총액"]
            elif self.id == 'prc':
                # PRC mode doesn't need cumulative calculations
                acc_shares = 0
                acc_amount = 0
                column_titles = ["#", "날짜", "회차", "이전 전환가", "현재 전환가"]
            else:
                # Default to HIST mode structure
                acc_shares = 0
                acc_amount = 0
                column_titles = ["#", "발행시간", "회차", "추가주식수(주)", "누적 추가주식수", "발행가액(원)", "총액", "누적 총액"]
            
        except Exception as e:
            # Fallback to empty data if database loading fails
            print(f"Warning: Could not load database for {self.id}: {e}")
            rows_data = []
            display_company = "데이터 로드 실패"
            first_date = ""
            last_date = ""
            acc_shares = 0
            acc_amount = 0
            column_titles = ["#", "발행시간", "회차", "추가주식수(주)", "누적 추가주식수", "발행가액(원)", "총액", "누적 총액"]
        
        return page.element_dataset_table_page(
            company_name=display_company,
            mode=self.id,
            mode_name=self.title,
            round_filter=round_filter,
            rows_data=rows_data,
            first_date=first_date,
            last_date=last_date,
            acc_shares=acc_shares,
            acc_amount=acc_amount,
            column_titles=column_titles
        )
    
    def _parse_number(self, text):
        """Parse number from text, handling commas and Korean number formats"""
        if not text:
            return 0
        try:
            # Remove commas and convert to int
            return int(text.replace(',', ''))
        except (ValueError, AttributeError):
            return 0

SEARCH_MODES = {
    'hist': SearchMode({
        # Display configs
        'id': 'hist',
        'title': '추가상장 기록 조회',
        
        # Scraping configs
        'keyword': None,
        'keywords_list': ['CB', 'EB', 'BW', '전환', '추가상장'],
        'main_menu_selector': '#dsclsType02',
        'sub_menu_selector': '#dsclsLayer02_25',
        'data_processor_class': HistDataProcessor,
        'database_name': 'database_hist.json',
        'columns': ['company', 'date', 'round', 'additional_shares', 'issue_price'],
        
        # Page generation configs
        'execution_message': '추가상장 기록 조회를 실행합니다.\\n대상: ${searchTarget}',
        'run_function': 'run_hist_scraper'
    }),
    'prc': SearchMode({
        # Display configs
        'id': 'prc',
        'title': '전환가액 변동 조회',
        
        # Scraping configs
        'keyword': '조정',
        'keywords_list': None,
        'main_menu_selector': '#dsclsType04',
        'sub_menu_selector': '#dsclsLayer04_17',
        'data_processor_class': PrcDataProcessor,
        'database_name': 'database_prc.json',
        'columns': ['company', 'date', 'round', 'prev_prc', 'issue_price'],
        # ["#", "날짜", "회차", "이전 전환가", "현재 전환가"]
        # Page generation configs
        'execution_message': '전환가액 변동 조회를 실행합니다.\\n대상: ${searchTarget}',
        'run_function': 'run_prc_scraper'
    })
}

def get_all_modes(): return SEARCH_MODES
def get_search_mode(mode_name): return SEARCH_MODES.get(mode_name)

def hist_page(): return SEARCH_MODES['hist'].generate_page()
def prc_page(): return SEARCH_MODES['prc'].generate_page()

def hist_dataset_page(company_name=None, round_filter=''): return SEARCH_MODES['hist'].generate_dataset_page(company_name, round_filter)
def prc_dataset_page(company_name=None, round_filter=''): return SEARCH_MODES['prc'].generate_dataset_page(company_name, round_filter)
