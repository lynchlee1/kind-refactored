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
