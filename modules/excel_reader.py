import pandas as pd
import os
import sys

def read_holdings_from_excel(excel_path=None):
    try:
        if excel_path is None:
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            excel_path = os.path.join(root_dir, 'results.xlsx')
        if not os.path.exists(excel_path): raise FileNotFoundError(f"results.xlsx 파일이 없습니다.")
        
        # Read the Holdings sheet
        df = pd.read_excel(excel_path, sheet_name='Holdings')
        
        if '기업명' not in df.columns: 
            raise ValueError(f"'Holdings' 시트 혹은 '기업명' 열이 없습니다.")
        
        # If there's a '회차' column, read both columns; otherwise just company names
        if '회차' in df.columns:
            holdings_data = []
            for _, row in df.iterrows():
                company = str(row['기업명']).strip() if pd.notna(row['기업명']) else ''
                round_num = str(row['회차']).strip() if pd.notna(row['회차']) else ''
                
                if company and round_num:
                    holdings_data.append({
                        'company': company,
                        'round': round_num,
                        'keyword': f"{company}{round_num}"
                    })
            print(f"✅ Successfully read {len(holdings_data)} company+round combinations from Excel file")
            return holdings_data
        else:
            # Fallback: just company names without rounds
            holdings = df['기업명'].dropna().tolist()        
            holdings = [str(company).strip() for company in holdings if str(company).strip()]
            print(f"✅ Successfully read {len(holdings)} companies from Excel file (no rounds)")
            return holdings
    except Exception as e: 
        print(f"❌ Error reading Excel file: {e}")
        return []

def update_system_constants_with_excel(excel_path=None):
    try:
        holdings = read_holdings_from_excel(excel_path)        
        if not holdings: return False
        
        modules_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(modules_dir)
        constants_path = os.path.join(root_dir, 'resources', 'system_constants.json')
        
        import json
        with open(constants_path, 'r', encoding='utf-8') as f: constants = json.load(f)
        constants['holdings'] = {'holdings': holdings}
        with open(constants_path, 'w', encoding='utf-8') as f: json.dump(constants, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated system_constants.json with {len(holdings)} companies from Excel")
        return True
    except Exception: return False
