import pandas as pd
import os
import json
import sys
from datetime import datetime

try:
    from .settings import get
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from settings import get

def get_latest_cumulative_values(company_name, hist_df):
    try:
        company_data = hist_df[hist_df['회사명'] == company_name]
        if company_data.empty: return (0, 0)
        
        # Get the most recent entry (first row after sorting by date descending)
        latest_entry = company_data.iloc[0]
        
        latest_누적_총액 = latest_entry.get('누적_총액', 0)
        latest_누적_추가주식수 = latest_entry.get('누적_추가주식수', 0)
        
        # Convert to int if possible, otherwise return 0
        try:
            latest_누적_총액 = int(str(latest_누적_총액).replace(',', '')) if latest_누적_총액 else 0
        except:
            latest_누적_총액 = 0
            
        try:
            latest_누적_추가주식수 = int(str(latest_누적_추가주식수).replace(',', '')) if latest_누적_추가주식수 else 0
        except:
            latest_누적_추가주식수 = 0
        
        return (latest_누적_총액, latest_누적_추가주식수)
    except Exception as e:
        print(f"⚠️ Error getting cumulative values for {company_name}: {e}")
        return (0, 0)

def get_conversion_price_history(company_name, round_value, prc_df):
    """
    Get the conversion price change history for a company and round from PRC data
    Returns formatted string like "7,905(2024-01-08 13:07), 6,900(2024-11-06 14:12), ..."
    """
    try:
        # Filter PRC data for the specific company and round
        company_round_data = prc_df[
            (prc_df['회사명'] == company_name) & 
            (prc_df['회차'] == str(round_value))
        ]
        
        if company_round_data.empty:
            return ""
        
        # Sort by date (oldest first to show chronological progression)
        company_round_data = company_round_data.sort_values('날짜', ascending=True)
        
        # Create the formatted string
        price_changes = []
        for _, row in company_round_data.iterrows():
            current_price = str(row.get('현재_전환가', '')).strip()
            date = str(row.get('날짜', '')).strip()
            
            # Format the date (remove time if it's just 00:00)
            if ' 00:00' in date:
                date = date.replace(' 00:00', '')
            
            if current_price and current_price != 'nan' and date and date != 'nan':
                price_changes.append(f"{current_price}({date})")
        
        return ", ".join(price_changes)
    except Exception as e:
        print(f"⚠️ Error getting conversion price history for {company_name} {round_value}: {e}")
        return ""

def read_holdings_from_excel():
    """
    Read company names and rounds from the Holdings sheet in results.xlsx
    Returns a list of dictionaries with company names and rounds
    """
    try:
        excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results.xlsx')
        
        if not os.path.exists(excel_path):
            print(f"❌ Excel file not found at: {excel_path}")
            return []
        
        # Read the Holdings sheet
        holdings_df = pd.read_excel(excel_path, sheet_name='Holdings')
        
        if '기업명' not in holdings_df.columns:
            print("❌ '기업명' column not found in Holdings sheet")
            return []
        
        # If there's a '회차' column, use it; otherwise create empty list
        if '회차' in holdings_df.columns:
            holdings_data = []
            for _, row in holdings_df.iterrows():
                holdings_data.append({
                    'company_name': str(row['기업명']).strip(),
                    'round': str(row['회차']).strip() if pd.notna(row['회차']) else ''
                })
            print(f"✅ Successfully read {len(holdings_data)} companies with rounds from Holdings sheet")
        else:
            # Fallback: just company names without rounds
            holdings_data = []
            for _, row in holdings_df.iterrows():
                holdings_data.append({
                    'company_name': str(row['기업명']).strip(),
                    'round': ''
                })
            print(f"✅ Successfully read {len(holdings_data)} companies from Holdings sheet (no rounds)")
        
        return holdings_data
        
    except Exception as e:
        print(f"❌ Error reading Holdings sheet: {e}")
        return []

def convert_database_to_excel(use_holdings_filter=True):
    """
    Convert database JSON files to Excel format and save as results.xlsx
    If use_holdings_filter is True, only include data for companies/rounds in the Holdings sheet
    """
    try:
        # Get database files
        hist_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'database_hist.json')
        prc_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'database_prc.json')
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results.xlsx')
        
        # Read Holdings sheet to get valid company/round combinations
        holdings_data = []
        if use_holdings_filter:
            holdings_data = read_holdings_from_excel()
            if not holdings_data:
                print("✅  No Holdings data found, exporting all data")
        
        # Create filter sets for efficient lookup - STRICT round matching
        valid_combinations = set()
        if holdings_data:
            for item in holdings_data:
                company = item['company_name']
                round_val = item['round']
                if round_val and round_val.strip():
                    # Only add exact company+round combinations
                    valid_combinations.add((company, round_val.strip()))
                # If no round specified, skip this company entirely (strict matching)
        
        # Load data from JSON files
        hist_data = []
        prc_data = []
        
        # Load HIST data
        if os.path.exists(hist_db_path):
            with open(hist_db_path, 'r', encoding='utf-8') as f:
                hist_db = json.load(f)
                for company, data in hist_db.items():
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            company_name = company
                            round_val = str(item.get('round', ''))
                            
                            # Apply Holdings filter if enabled - STRICT round matching
                            if use_holdings_filter and valid_combinations:
                                # Check if this exact company/round combination is valid
                                is_valid = (company_name, round_val) in valid_combinations
                                if not is_valid:
                                    continue
                            
                            hist_data.append({
                                '회사명': company_name,
                                '날짜': item.get('date', ''),
                                '회차': round_val,
                                '추가주식수': item.get('additional_shares', ''),
                                '발행가액': item.get('issue_price', ''),
                                '누적_추가주식수': 0,  # Will be recalculated properly
                                '누적_총액': 0,  # Will be recalculated properly
                                '데이터_타입': 'HIST'
                            })
        
        # Load PRC data
        if os.path.exists(prc_db_path):
            with open(prc_db_path, 'r', encoding='utf-8') as f:
                prc_db = json.load(f)
                for company, data in prc_db.items():
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            company_name = company
                            round_val = str(item.get('round', ''))
                            
                            # Apply Holdings filter if enabled - STRICT round matching
                            if use_holdings_filter and valid_combinations:
                                # Check if this exact company/round combination is valid
                                is_valid = (company_name, round_val) in valid_combinations
                                if not is_valid:
                                    continue
                            
                            prc_data.append({
                                '회사명': company_name,
                                '날짜': item.get('date', ''),
                                '회차': round_val,
                                '이전_전환가': item.get('prev_prc', ''),
                                '현재_전환가': item.get('issue_price', ''),
                                '데이터_타입': 'PRC'
                            })
        
        # Convert to DataFrames for sorting
        hist_df = pd.DataFrame(hist_data)
        prc_df = pd.DataFrame(prc_data)
        
        # Calculate accumulated values using robust internal table approach
        if not hist_df.empty and '날짜' in hist_df.columns and '회사명' in hist_df.columns:
            from datetime import datetime
            
            def parse_date(date_str):
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                except:
                    try:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        return datetime.min
            
            # Create internal table with unique index for each entry
            internal_table = []
            
            # Convert DataFrame to internal table with unique index
            for idx, row in hist_df.iterrows():
                internal_entry = {
                    'original_index': idx,  # Keep track of original DataFrame index
                    'unique_key': idx,      # Use DataFrame index as unique identifier
                    '회사명': row['회사명'],
                    '날짜': row['날짜'],
                    '회차': row['회차'],
                    '추가주식수': row['추가주식수'],
                    '발행가액': row['발행가액'],
                    '데이터_타입': row['데이터_타입']
                }
                internal_table.append(internal_entry)
            
            # Process each company separately
            for company in hist_df['회사명'].unique():
                company_entries = [entry for entry in internal_table if entry['회사명'] == company]
                
                # Sort company entries chronologically with consistent tie-breaking
                company_entries.sort(key=lambda x: (
                    parse_date(x['날짜']),
                    x['회차'],
                    int(str(x['추가주식수']).replace(',', '')) if str(x['추가주식수']).replace(',', '').isdigit() else 0,
                    int(str(x['발행가액']).replace(',', '')) if str(x['발행가액']).replace(',', '').isdigit() else 0,
                    x['unique_key']  # Final tie-breaker: unique key (original DataFrame index)
                ))
                
                # Calculate cumulative values chronologically
                cumulative_shares = 0
                cumulative_amount = 0
                
                for entry in company_entries:
                    try:
                        shares_str = str(entry['추가주식수']).strip()
                        price_str = str(entry['발행가액']).strip()
                        
                        shares = int(shares_str.replace(',', '')) if shares_str and shares_str != 'nan' else 0
                        price = int(price_str.replace(',', '')) if price_str and price_str != 'nan' else 0
                        
                        # Add to cumulative values
                        cumulative_shares += shares
                        cumulative_amount += shares * price
                        
                        # Store cumulative values in the entry
                        entry['누적_추가주식수'] = cumulative_shares
                        entry['누적_총액'] = cumulative_amount
                        
                    except (ValueError, TypeError):
                        # If parsing fails, keep existing cumulative values
                        entry['누적_추가주식수'] = cumulative_shares
                        entry['누적_총액'] = cumulative_amount
            
            # Apply cumulative values back to the DataFrame using original index
            for entry in internal_table:
                original_idx = entry['original_index']
                hist_df.loc[original_idx, '누적_추가주식수'] = entry['누적_추가주식수']
                hist_df.loc[original_idx, '누적_총액'] = entry['누적_총액']
            
            # Sort for display (newest first)
            hist_df['날짜_정렬'] = pd.to_datetime(hist_df['날짜'], errors='coerce')
            hist_df = hist_df.sort_values(['회사명', '날짜_정렬'], ascending=[True, False]).drop('날짜_정렬', axis=1)
        
        if not prc_df.empty and '날짜' in prc_df.columns and '회사명' in prc_df.columns:
            # Convert date strings to datetime for proper sorting
            prc_df['날짜_정렬'] = pd.to_datetime(prc_df['날짜'], errors='coerce')
            prc_df = prc_df.sort_values(['회사명', '날짜_정렬'], ascending=[True, False]).drop('날짜_정렬', axis=1)
        
        # Read existing Holdings sheet before creating new Excel file (preserve user modifications)
        existing_holdings_df = None
        try:
            if os.path.exists(output_path):
                # Read the existing Holdings sheet completely before overwriting
                existing_holdings_df = pd.read_excel(output_path, sheet_name='Holdings', engine='openpyxl')
                print(f"✅ Found existing Holdings sheet with {len(existing_holdings_df)} rows and columns: {list(existing_holdings_df.columns)}")
        except Exception as e:
            print(f"⚠️ Could not read existing Holdings sheet: {e}")
        
        # Create Excel writer (mode='w' clears all existing sheets)
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
            # Write the preserved Holdings sheet or create new one
            if existing_holdings_df is not None:
                # Add cumulative values to existing Holdings sheet
                holdings_with_cumulative = existing_holdings_df.copy()
                
                # Add cumulative value columns if they don't exist
                if '누적_총액' not in holdings_with_cumulative.columns:
                    holdings_with_cumulative['누적_총액'] = 0
                if '누적_추가주식수' not in holdings_with_cumulative.columns:
                    holdings_with_cumulative['누적_추가주식수'] = 0
                if '전환가_변동내역' not in holdings_with_cumulative.columns:
                    holdings_with_cumulative['전환가_변동내역'] = ""
                
                # Update cumulative values and conversion price history for each company
                for idx, row in holdings_with_cumulative.iterrows():
                    company_name = row.get('기업명', '')
                    round_value = row.get('회차', '')
                    if company_name:
                        latest_누적_총액, latest_누적_추가주식수 = get_latest_cumulative_values(company_name, hist_df)
                        holdings_with_cumulative.loc[idx, '누적_총액'] = latest_누적_총액
                        holdings_with_cumulative.loc[idx, '누적_추가주식수'] = latest_누적_추가주식수
                        
                        # Get conversion price history if round is specified
                        if round_value:
                            conversion_history = get_conversion_price_history(company_name, round_value, prc_df)
                            holdings_with_cumulative.loc[idx, '전환가_변동내역'] = conversion_history
                
                holdings_with_cumulative.to_excel(writer, sheet_name='Holdings', index=False)
                print("✅ Updated existing Holdings sheet with latest cumulative values")
            else:
                # If no existing file, create Holdings sheet from Holdings data with cumulative values
                if holdings_data:
                    holdings_df = pd.DataFrame(holdings_data)
                    # Rename columns to match expected format
                    holdings_df = holdings_df.rename(columns={'company_name': '기업명', 'round': '회차'})
                    
                    # Add cumulative value and conversion price history columns
                    holdings_df['누적_총액'] = 0
                    holdings_df['누적_추가주식수'] = 0
                    holdings_df['전환가_변동내역'] = ""
                    
                    # Update cumulative values and conversion price history for each company
                    for idx, row in holdings_df.iterrows():
                        company_name = row.get('기업명', '')
                        round_value = row.get('회차', '')
                        if company_name:
                            latest_누적_총액, latest_누적_추가주식수 = get_latest_cumulative_values(company_name, hist_df)
                            holdings_df.loc[idx, '누적_총액'] = latest_누적_총액
                            holdings_df.loc[idx, '누적_추가주식수'] = latest_누적_추가주식수
                            
                            # Get conversion price history if round is specified
                            if round_value:
                                conversion_history = get_conversion_price_history(company_name, round_value, prc_df)
                                holdings_df.loc[idx, '전환가_변동내역'] = conversion_history
                    
                    holdings_df.to_excel(writer, sheet_name='Holdings', index=False)
                    print("✅ Created new Holdings sheet with latest cumulative values")
                else:
                    # Fallback: create empty Holdings sheet with cumulative columns
                    empty_holdings_df = pd.DataFrame(columns=['기업명', '회차', '누적_총액', '누적_추가주식수', '전환가_변동내역'])
                    empty_holdings_df.to_excel(writer, sheet_name='Holdings', index=False)
                    print("✅ Created empty Holdings sheet with cumulative columns")
            
            # Create HIST data sheet (using filtered and sorted DataFrame)
            hist_df.to_excel(writer, sheet_name='HIST_Data', index=False)
            
            # Create PRC data sheet (using filtered and sorted DataFrame)
            prc_df.to_excel(writer, sheet_name='PRC_Data', index=False)
            
            # Create summary sheet
            filter_text = 'Holdings 시트 기준 필터링' if use_holdings_filter else '필터 없음'
            
            summary_data = {
                '항목': [
                    'Holdings 시트 회사 수',
                    'HIST 데이터 건수 (필터링 후)',
                    'PRC 데이터 건수 (필터링 후)',
                    '적용된 필터',
                    '생성 시간',
                    '데이터베이스 파일 경로'
                ],
                '값': [
                    len(holdings_data),
                    len(hist_df),
                    len(prc_df),
                    filter_text,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    f'HIST: {hist_db_path}, PRC: {prc_db_path}'
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        filter_text = ' (Holdings 시트 기준)' if use_holdings_filter else ''
        
        return {
            'success': True,
            'message': f'Excel 파일이 성공적으로 생성되었습니다{filter_text}. (Holdings {len(holdings_data)}개 회사, HIST {len(hist_df)}건, PRC {len(prc_df)}건)',
            'file_path': output_path,
            'companies_count': len(holdings_data),
            'hist_count': len(hist_df),
            'prc_count': len(prc_df),
            'use_holdings_filter': use_holdings_filter
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Excel 파일 생성 실패: {str(e)}',
            'error': str(e)
        }

def get_database_summary(company_filter=None, round_filter=None):
    """
    Get summary information about the databases with optional filtering
    """
    try:
        hist_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'database_hist.json')
        prc_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'database_prc.json')
        
        hist_data = []
        prc_data = []
        
        # Load HIST data
        if os.path.exists(hist_db_path):
            with open(hist_db_path, 'r', encoding='utf-8') as f:
                hist_db = json.load(f)
                for company, data in hist_db.items():
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            hist_data.append({
                                '회사명': company,
                                '회차': item.get('round', ''),
                                '날짜': item.get('date', '')
                            })
        
        # Load PRC data
        if os.path.exists(prc_db_path):
            with open(prc_db_path, 'r', encoding='utf-8') as f:
                prc_db = json.load(f)
                for company, data in prc_db.items():
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            prc_data.append({
                                '회사명': company,
                                '회차': item.get('round', ''),
                                '날짜': item.get('date', '')
                            })
        
        # Convert to DataFrames and apply filters
        hist_df = pd.DataFrame(hist_data)
        prc_df = pd.DataFrame(prc_data)
        
        if not hist_df.empty:
            if company_filter and company_filter.strip():
                hist_df = hist_df[hist_df['회사명'].str.contains(company_filter, na=False, case=False)]
            if round_filter and round_filter.strip():
                hist_df = hist_df[hist_df['회차'].astype(str).str.contains(str(round_filter), na=False, case=False)]
        
        if not prc_df.empty:
            if company_filter and company_filter.strip():
                prc_df = prc_df[prc_df['회사명'].str.contains(company_filter, na=False, case=False)]
            if round_filter and round_filter.strip():
                prc_df = prc_df[prc_df['회차'].astype(str).str.contains(str(round_filter), na=False, case=False)]
        
        hist_count = len(hist_df)
        prc_count = len(prc_df)
        companies = set(hist_df['회사명'].tolist() + prc_df['회사명'].tolist())
        
        return {
            'success': True,
            'companies_count': len(companies),
            'hist_count': hist_count,
            'prc_count': prc_count,
            'total_records': hist_count + prc_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'데이터베이스 요약 정보 조회 실패: {str(e)}',
            'error': str(e)
        }

if __name__ == '__main__':
    print("🧪 Testing HTML to Excel conversion...")
    
    # Test database summary
    summary = get_database_summary()
    print(f"✅ Database Summary: {summary}")
    
    # Test Excel conversion
    result = convert_database_to_excel()
    print(f"📄 Excel Conversion Result: {result}")
    
    if result['success']:
        print(f"✅ Excel file created at: {result['file_path']}")
    else:
        print(f"❌ Excel creation failed: {result['message']}")
