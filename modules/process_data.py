import json
import pandas as pd
import os
from settings import get

def process_to_excel():
    try:
        with open(get("output_json_file", "details_links.json"), 'r', encoding='utf-8') as f: items = json.load(f)
        new_data_for_excel = []
        for item in items:
            company_name = item.get('company', '')
            date = item.get('date', '')
            if len(item.get('table_data', [])) > 2:
                report_datas = item['table_data'][2]['rows']
                report_datas_len = len(report_datas) - 1
                for i in range(report_datas_len):
                    if len(report_datas[i+1]['data']) >= 5:
                        report_data = report_datas[i+1]['data'][2:5]
                        new_data_for_excel.append([company_name, date] + report_data)
        if not new_data_for_excel: return True
        excel_file = get("output_excel_file")
        
        existing_data = []
        if os.path.exists(excel_file):
            try:
                existing_df = pd.read_excel(excel_file, engine='openpyxl')
                existing_data = existing_df.values.tolist()
            except Exception as e: raise Exception(f"❌ 엑셀 파일을 열 수 없습니다: {e}")
        existing_combinations = set()
        for row in existing_data:
            if len(row) >= 2:
                company_date_key = (str(row[0]), str(row[1]))
                existing_combinations.add(company_date_key)

        unique_new_data = []
        for row in new_data_for_excel:
            if len(row) >= 2:
                company_date_key = (str(row[0]), str(row[1]))
                if company_date_key not in existing_combinations: unique_new_data.append(row)

        all_data = existing_data + unique_new_data
        if not all_data: return True
        df = pd.DataFrame(all_data, columns=['회사명', '발행시간', '회차', '추가주식수(주)', '발행/전환/행사가액(원)'])
        df.to_excel(excel_file, index=False, engine='openpyxl')
        return True
    except Exception as e: raise Exception(f"❌ 데이터를 저장할 수 없습니다: {e}")


def process_to_json(config):
    # Structure: { "<company>": { "first_date": str, "last_date": str, "data": [processed_items...] } }
    try:
        if not config: raise Exception("Config is required but was None")
            
        input_json = get("output_json_file")
        with open(input_json, 'r', encoding='utf-8') as f: items = json.load(f)
        if not items: return True
        

        # Process data like process_to_excel
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
        db_path = os.path.join(root_dir, "database.json")
        
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
