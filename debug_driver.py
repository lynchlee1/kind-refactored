#!/usr/bin/env python3
"""
Simple debug form for testing driver_manager functions
"""

import time
from modules.driver_manager import setup_driver, find_result_rows, extract_from_iframe, extract_table_data
from settings import get

def debug_find_result_rows():
    """Test find_result_rows function"""
    print("🔍 Testing find_result_rows...")
    
    driver, wait = setup_driver(headless=False)
    
    try:
        # Navigate to the target URL
        url = get("details_url")
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait a bit for page to load
        time.sleep(3)
        
        # Test find_result_rows
        rows = find_result_rows(driver)
        print(f"📊 Found {len(rows)} result rows")
        
        # Show some details about the rows
        for i, row in enumerate(rows[:3]):  # Show first 3 rows
            try:
                cells = row.find_elements("tag name", "td") or row.find_elements("tag name", "th")
                cell_texts = [cell.text.strip() for cell in cells]
                print(f"  Row {i}: {cell_texts[:3]}...")  # Show first 3 cells
            except Exception as e:
                print(f"  Row {i}: Error reading row - {e}")
        
        input("Press Enter to continue...")
        
    finally:
        driver.quit()

def debug_extract_from_iframe():
    """Test extract_from_iframe function"""
    print("🔍 Testing extract_from_iframe...")
    
    driver, wait = setup_driver(headless=False)
    
    try:
        # Navigate to the target URL
        url = get("details_url")
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait a bit for page to load
        time.sleep(3)
        
        # Test extract_from_iframe
        iframe_data = extract_from_iframe(driver, wait)
        print(f"📊 Extracted {len(iframe_data)} tables from iframe")
        
        # Show some details about the extracted data
        for table in iframe_data:
            print(f"  Table {table['table_index']}: {table['row_count']} rows")
            for row in table['rows'][:2]:  # Show first 2 rows
                print(f"    Row {row['row_index']}: {row['data'][:3]}...")
        
        input("Press Enter to continue...")
        
    finally:
        driver.quit()

def debug_extract_table_data():
    """Test extract_table_data function (tries iframe first, then direct)"""
    print("🔍 Testing extract_table_data...")
    
    driver, wait = setup_driver(headless=False)
    
    try:
        # Navigate to the target URL
        url = get("details_url")
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        # Wait a bit for page to load
        time.sleep(3)
        
        # Test extract_table_data
        table_data = extract_table_data(driver, wait)
        print(f"📊 Extracted {len(table_data)} tables")
        
        # Show some details about the extracted data
        for table in table_data:
            print(f"  Table {table['table_index']}: {table['row_count']} rows")
            for row in table['rows'][:2]:  # Show first 2 rows
                print(f"    Row {row['row_index']}: {row['data'][:3]}...")
        
        input("Press Enter to continue...")
        
    finally:
        driver.quit()

def main():
    """Main debug menu"""
    while True:
        print("\n" + "="*50)
        print("🔧 DRIVER MANAGER DEBUG TOOL")
        print("="*50)
        print("1. Test find_result_rows()")
        print("2. Test extract_from_iframe()")
        print("3. Test extract_table_data()")
        print("4. Show current settings")
        print("0. Exit")
        print("="*50)
        
        choice = input("Choose an option (0-4): ").strip()
        
        if choice == "1":
            debug_find_result_rows()
        elif choice == "2":
            debug_extract_from_iframe()
        elif choice == "3":
            debug_extract_table_data()
        elif choice == "4":
            print("\n📋 Current Settings:")
            print(f"  details_url: {get('details_url')}")
            print(f"  result_row_selector: {get('result_row_selector')}")
            print(f"  iframe_selector: {get('iframe_selector')}")
            print(f"  table_selector: {get('table_selector')}")
            print(f"  next_page_selector: {get('next_page_selector')}")
            print(f"  implicit_wait: {get('implicit_wait')}")
            input("Press Enter to continue...")
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
