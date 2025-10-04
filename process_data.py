
import json
import pandas as pd

with open('details_links.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

results = {}
for item in items:
	results[item['date']] = {}
	results[item['date']]['data'] = []
	report_datas = item['table_data'][2]['rows']
	report_datas_len = len(report_datas) - 1
	for i in range(report_datas_len):
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
df.to_excel('results.xlsx', index=False, engine='openpyxl')

print("Data saved to results.xlsx")
