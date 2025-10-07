import json
import pandas as pd
import os
from settings import get

def process_to_json(config):
    # Structure: { "<company>": { "first_date": str, "last_date": str, "data": [processed_items...] } }
    try:
        if not config: raise Exception("Config is required but was None")
        
        input_json = get("output_json_file")
        with open(input_json, 'r', encoding='utf-8') as f: items = json.load(f)
        if not items: return True
        
        processed_data = []
        for item in items:
            if not item:
                print(f"Warning: Found None item in items list")
                continue
                
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

        if not processed_data: 
            print("No processed data found")
            return True

        company_name = processed_data[0].get('company')
        
        modules_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(modules_dir)
        # Use separate db per mode if provided
        mode = (config.get('mode') or 'default').strip()
        db_filename = 'database_conv.json' if mode == 'conv' else 'database.json'
        db_path = os.path.join(root_dir, db_filename)
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f: db = json.load(f)
            existing_entry = db.get(company_name)
            if existing_entry:
                existing_data = existing_entry.get('data', [])
            else:
                existing_entry = { 'first_date': None, 'last_date': None, 'data': [] }
                existing_data = []
        except Exception as e: 
            db = {}
            existing_entry = { 'first_date': None, 'last_date': None, 'data': [] }
            existing_data = []

        def make_key(x):
            if not x:
                print(f"Warning: make_key called with None item")
                return ""
            # Use full row identity to allow multiple rows on the same date
            return (
                f"{x.get('company','')}|{x.get('date','')}|{x.get('round','')}|"
                f"{x.get('additional_shares','')}|{x.get('issue_price','')}"
            )
        
        seen = { make_key(x) for x in existing_data }
        merged = list(existing_data)
        
        for i, it in enumerate(processed_data):
            if not it:
                continue
            k = make_key(it)
            if k not in seen:
                merged.append(it)
                seen.add(k)

        def _ranges_overlap(fd1, ld1, fd2, ld2):
            if not all([fd1, ld1, fd2, ld2]):
                return False
            return fd1 <= ld2 and fd2 <= ld1

        def _safe_min(a, b):
            if a is None: return b
            if b is None: return a
            return min(a, b)
        
        def _safe_max(a, b):
            if a is None: return b
            if b is None: return a
            return max(a, b)

        fd_new = config.get('from_date')
        ld_new = config.get('to_date')

        fd_old = existing_entry.get('first_date')
        ld_old = existing_entry.get('last_date')

        if fd_old is None or ld_old is None: 
            fd_fin, ld_fin = fd_new, ld_new
        elif _ranges_overlap(fd_old, ld_old, fd_new, ld_new): 
            fd_fin, ld_fin = _safe_min(fd_old, fd_new), _safe_max(ld_old, ld_new)
        else: 
            fd_fin, ld_fin = fd_old, ld_old

        db[company_name] = {
            'first_date': fd_fin,
            'last_date': ld_fin,
            'data': merged
        }

        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        raise Exception(f"❌ JSON 저장 중 오류: {e}")
