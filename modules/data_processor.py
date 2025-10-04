"""
Data processing utilities for scraped data
"""

import json
import pandas as pd
from settings import get

def save_scraped_data(items):
    with open(get("output_json_file", "details_links.json"), "w", encoding="utf-8") as f: json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(items)} links to {get('output_json_file', 'details_links.json')}")

def process_data_to_excel():
    try:
        with open(get("output_json_file", "details_links.json"), 'r', encoding='utf-8') as f:
            items = json.load(f)

        results = {}
        for item in items:
            results[item['date']] = {}
            results[item['date']]['data'] = []
            
            # Check if table_data exists and has enough tables
            if len(item.get('table_data', [])) > 2:
                report_datas = item['table_data'][2]['rows']
                report_datas_len = len(report_datas) - 1
                
                for i in range(report_datas_len):
                    if len(report_datas[i+1]['data']) > 4:  # Ensure enough columns
                        report_data = report_datas[i+1]['data'][2:5]
                        results[item['date']]['data'].append(report_data)

        # Save to Excel
        data_for_excel = []
        for date in results:
            for data_row in results[date]['data']:
                data_for_excel.append([date] + data_row)

        # Create DataFrame
        df = pd.DataFrame(data_for_excel, columns=['발행시간', '회차', '추가주식수(주)', '발행/전환/행사가액(원)'])

        # Save to Excel file
        df.to_excel(get("output_excel_file", "results.xlsx"), index=False, engine='openpyxl')

        print(f"✅ Data processed and saved to {get('output_excel_file', 'results.xlsx')}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return False

def load_scraped_data():
    try:
        with open(get("output_json_file", "details_links.json"), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {OUTPUT_JSON_FILE} not found")
        return []
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return []
