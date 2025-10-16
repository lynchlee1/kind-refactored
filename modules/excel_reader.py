import pandas as pd
import os
import sys

def read_holdings_from_excel(excel_path=None):
    try:
        if excel_path is None:
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            excel_path = os.path.join(root_dir, 'results.xlsx')
        
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        df = pd.read_excel(excel_path, sheet_name='Holdings')
        if '기업명' not in df.columns:
            raise ValueError(f"'기업명' column not found in 'Holdings' sheet. Available columns: {list(df.columns)}")
        holdings = df['기업명'].dropna().tolist()        
        holdings = [str(company).strip() for company in holdings if str(company).strip()]
        print(f"✅ Successfully read {len(holdings)} companies from Excel file:")
        return holdings
    except Exception: return []

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
