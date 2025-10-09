import json
import os
from abc import ABC, abstractmethod
from .settings import get

class BaseDataProcessor(ABC):
    def __init__(self, mode_name): self.mode_name = mode_name
        
    @abstractmethod
    def process_raw_data(self, items): pass
    
    @abstractmethod
    def get_database_filename(self): pass
    
    def save_to_database(self, config):
        try:
            company_name = config.get('company')
            processed_data = config.get('processed_data')
            key_list = config.get('key_list')
            fd_new = config.get('from_date')
            ld_new = config.get('to_date')
            
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            db_filename = self.get_database_filename()
            db_path = os.path.join(root_dir, db_filename)
            
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

            seen = {make_key(x, key_list) for x in existing_data}
            merged_data = list(existing_data)
            if processed_data:
                for item in processed_data:
                    if not item: continue
                    k = make_key(item, key_list)
                    if k not in seen:
                        merged_data.append(item)
                        seen.add(k)
            # We should call _update_date_ranges when there were no datas, too.
            self._update_date_ranges(db, company_name, existing_entry, fd_new, ld_new, merged_data)
            return True
        except Exception as e: raise Exception(f"❌ JSON saving failed: {e}")
    
    def _update_date_ranges(self, db, company_name, existing_entry, fd_new, ld_new, merged_data):
        def _ranges_overlap(fd1, ld1, fd2, ld2):
            if not all([fd1, ld1, fd2, ld2]): return False
            return fd1 <= ld2 and fd2 <= ld1
        
        def _safe_min(a, b):
            if a is None: return b
            if b is None: return a
            return min(a, b)
        
        def _safe_max(a, b):
            if a is None: return b
            if b is None: return a
            return max(a, b)
   
        fd_old = existing_entry.get('first_date')
        ld_old = existing_entry.get('last_date')
        if fd_old is None or ld_old is None:
            fd_fin, ld_fin = fd_new, ld_new
        elif _ranges_overlap(fd_old, ld_old, fd_new, ld_new):
            fd_fin, ld_fin = _safe_min(fd_old, fd_new), _safe_max(ld_old, ld_new)
        
        modules_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(modules_dir)
        db_filename = self.get_database_filename()
        db_path = os.path.join(root_dir, db_filename)
        
        db[company_name] = {
            'first_date': fd_fin,
            'last_date': ld_fin,
            'data': merged_data
        }
        with open(db_path, 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=2)

class HistDataProcessor(BaseDataProcessor):
    def __init__(self): super().__init__('hist')
    def get_database_filename(self): return get('saved_json_hist')
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
    def get_database_filename(self): return get('saved_json_prc')
    def process_raw_data(self, items):
        processed_data = []
        processed_data = items
        return processed_data

class SearchMode:    
    def __init__(self, config):
        self.name                 = config.get('name')
        self.display_name         = config.get('display_name')
        self.keyword              = config.get('keyword')
        self.keywords_list        = config.get('keywords_list')
        self.main_menu_selector   = config.get('main_menu_selector')
        self.sub_menu_selector    = config.get('sub_menu_selector')
        self.data_processor_class = config.get('data_processor_class')
        self.database_file        = config.get('database_file')
        self.description          = config.get('description')
        self.columns              = config.get('columns')

SEARCH_MODES = {
    'hist': SearchMode({
        'name': 'hist',
        'display_name': '전환기록 조회',
        'keyword': None,
        'keywords_list': ['CB', 'EB', 'BW'],
        'main_menu_selector': '#dsclsType02',
        'sub_menu_selector': '#dsclsLayer02_25',
        'data_processor_class': HistDataProcessor,
        'database_file': get('saved_json_hist'),
        'description': '전환기록 조회',
        'columns': ['company', 'date', 'round', 'additional_shares', 'issue_price'],
    }),
    'prc': SearchMode({
        'name': 'prc',
        'display_name': '전환가액 변동기록 조회',
        'keyword': '조정',
        'keywords_list': None,
        'main_menu_selector': '#dsclsType04',
        'sub_menu_selector': '#dsclsLayer04_17',
        'data_processor_class': PrcDataProcessor,
        'database_file': get('saved_json_prc'),
        'description': '전환가액 변동기록 조회',
        'columns': ['full_data'],
    })
}
def get_all_modes(): return SEARCH_MODES
def get_search_mode(mode_name): return SEARCH_MODES.get(mode_name)
