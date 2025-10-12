#!/usr/bin/env python3
"""
Analyze the target value that doesn't match
"""

import json
import os
from datetime import datetime

def analyze_target_value():
    print("Analyzing the target value 7,849,958,400...")
    
    # Read the database directly
    db_path = os.path.join('resources', 'database_hist.json')
    
    with open(db_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Get 한울소재과학 data
    company_data = database.get('한울소재과학', {})
    data_list = company_data.get('data', [])
    
    # Filter for Round 5 only
    round5_data = [item for item in data_list if str(item.get('round', '')).strip() == '5']
    
    # Parse dates and sort chronologically
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return datetime.min
    
    round5_data.sort(key=lambda x: (parse_date(x.get('date', '')), x.get('round', '')))
    
    print("Round 5 entries in chronological order:")
    for i, item in enumerate(round5_data):
        date = item.get('date', '')
        shares_str = item.get('additional_shares', '')
        price_str = item.get('issue_price', '')
        
        try:
            shares = int(shares_str.replace(',', '')) if shares_str else 0
            price = int(price_str.replace(',', '')) if price_str else 0
            amount = shares * price
            print(f"{i+1}. {date}: {shares:,} shares @ {price:,} = {amount:,}")
        except:
            print(f"{i+1}. {date}: ERROR parsing")
    
    # Calculate target value difference
    target_value = 7849958400
    my_calculated = 7999960320
    
    print(f"\nTarget: {target_value:,}")
    print(f"My calculation: {my_calculated:,}")
    print(f"Difference: {my_calculated - target_value:,}")
    
    # Check if this difference corresponds to any specific entry
    difference = my_calculated - target_value
    print(f"\nLooking for an entry with amount {difference:,}...")
    
    for i, item in enumerate(round5_data):
        shares_str = item.get('additional_shares', '')
        price_str = item.get('issue_price', '')
        
        try:
            shares = int(shares_str.replace(',', '')) if shares_str else 0
            price = int(price_str.replace(',', '')) if price_str else 0
            amount = shares * price
            
            if amount == difference:
                print(f"Found! Entry {i+1}: {amount:,}")
                break
        except:
            pass

if __name__ == "__main__":
    analyze_target_value()
