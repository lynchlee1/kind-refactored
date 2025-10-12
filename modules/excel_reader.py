import pandas as pd
import os
import sys

def read_holdings_from_excel(excel_path=None):
    """
    Read holdings list from Excel file 'Holdings' sheet, '기업명' column
    
    Args:
        excel_path (str): Path to Excel file. If None, uses 'results.xlsx' in project root
        
    Returns:
        list: List of company names from the '기업명' column
    """
    try:
        # Default to results.xlsx in project root if no path provided
        if excel_path is None:
            modules_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(modules_dir)
            excel_path = os.path.join(root_dir, 'results.xlsx')
        
        # Check if file exists
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        # Read the 'Holdings' sheet
        df = pd.read_excel(excel_path, sheet_name='Holdings')
        
        # Check if '기업명' column exists
        if '기업명' not in df.columns:
            raise ValueError(f"'기업명' column not found in 'Holdings' sheet. Available columns: {list(df.columns)}")
        
        # Extract company names from '기업명' column
        # Remove any NaN values and convert to list
        holdings = df['기업명'].dropna().tolist()
        
        # Convert to strings and strip whitespace
        holdings = [str(company).strip() for company in holdings if str(company).strip()]
        
        print(f"✅ Successfully read {len(holdings)} companies from Excel file:")
        for i, company in enumerate(holdings, 1):
            print(f"   {i}. {company}")
        
        return holdings
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return []

def update_system_constants_with_excel(excel_path=None):
    """
    Update system_constants.json with holdings list from Excel file
    
    Args:
        excel_path (str): Path to Excel file. If None, uses 'results.xlsx' in project root
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read holdings from Excel
        holdings = read_holdings_from_excel(excel_path)
        
        if not holdings:
            print("❌ No holdings found in Excel file")
            return False
        
        # Update system_constants.json
        modules_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(modules_dir)
        constants_path = os.path.join(root_dir, 'resources', 'system_constants.json')
        
        # Read existing constants
        import json
        with open(constants_path, 'r', encoding='utf-8') as f:
            constants = json.load(f)
        
        # Update holdings
        constants['holdings'] = {'holdings': holdings}
        
        # Write back to file
        with open(constants_path, 'w', encoding='utf-8') as f:
            json.dump(constants, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated system_constants.json with {len(holdings)} companies from Excel")
        return True
        
    except Exception as e:
        print(f"❌ Error updating system constants: {e}")
        return False

if __name__ == "__main__":
    # Test the Excel reading functionality
    print("🧪 Testing Excel reading functionality...")
    
    # Read and display holdings
    holdings = read_holdings_from_excel()
    
    if holdings:
        print(f"\n✅ Found {len(holdings)} companies in Excel file:")
        for i, company in enumerate(holdings, 1):
            print(f"   {i}. {company}")
        
        # Update system constants
        print(f"\n🔄 Updating system_constants.json...")
        success = update_system_constants_with_excel()
        
        if success:
            print("✅ Excel integration test completed successfully!")
        else:
            print("❌ Excel integration test failed!")
    else:
        print("❌ No companies found in Excel file")
