from flask import Flask, render_template_string, request, jsonify, send_from_directory
import webbrowser
import threading
import time
import sys
import os
import socket
import json
from modules.kind_scraper import KINDScraper
from modules.search_modes import get_search_mode, SEARCH_MODES
from modules.settings import get
from modules.excel_reader import read_holdings_from_excel, update_system_constants_with_excel
from modules.html_to_excel import convert_database_to_excel, get_database_summary
from designlib.generate_pages_simple import main_page, dev_mode_page
from modules.search_modes import hist_page, prc_page, hist_dataset_page, prc_dataset_page

app = Flask(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

result_data = None
server_running = False
current_port = None
ui_opened = False

def find_available_port(start_port=5000):
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")

@app.route('/')
def index(): return main_page()

@app.route('/main_page.html')
def serve_main_page(): return main_page()

# Simplified routes - all redirect to main page
@app.route('/hist_page.html')
def hist_page_route(): return main_page()

@app.route('/prc_page.html')
def prc_page_route(): return main_page()

@app.route('/dev_mode.html')
def dev_mode_page_route(): return main_page()

@app.route('/hist_page_dataset.html')
def hist_dataset_page_route(): return main_page()

@app.route('/prc_page_dataset.html')
def prc_dataset_page_route(): return main_page()

@app.route('/logo.jpg')
def logo(): return send_from_directory(os.path.join(ROOT_DIR, 'resources'), 'logo.jpg')

@app.route('/submit', methods=['POST'])
def submit():
    global result_data
    try:
        data = request.get_json()
        if not data.get('company_name'):
            return jsonify({'success': False, 'message': 'Company name is required'})
        result_data = data
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@app.route('/api/run-all-companies', methods=['POST'])
def run_all_companies_api():
    """New simplified API endpoint for running all companies"""
    try:
        data = request.get_json() or {}
        
        user_input = {
            'from_date': data.get('from_date', '2021-01-01'),
            'to_date': data.get('to_date', '2025-01-01'),
            'headless': data.get('headless', False)
        }
        
        def run_scraper():
            try:
                run_all_companies_simplified(user_input)
            except Exception as e:
                print(f"Error in scraper: {e}")
        
        thread = threading.Thread(target=run_scraper)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': '전체 실행이 시작되었습니다'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def run_all_companies(user_input):
    try:
        try:
            from modules.excel_reader import read_holdings_from_excel
            holdings_data = read_holdings_from_excel()
            if holdings_data:
                # Handle both old format (list of strings) and new format (list of dicts)
                if isinstance(holdings_data[0], dict):
                    holdings = [item['company'] for item in holdings_data]
                    print(f"✅ Read {len(holdings_data)} company+round combinations from Excel: {holdings_data}")
                else:
                    holdings = holdings_data
                    print(f"✅ Read {len(holdings)} companies from Excel: {holdings}")
            else:
                holdings = get("holdings", [])
                print(f"⚠️ Excel read failed, using existing holdings: {holdings}")
        except Exception as e:
            holdings = get("holdings", [])
            print(f"⚠️ Excel read failed: {e}, using existing holdings: {holdings}")
        if not holdings: 
            print("❌ No holdings found in settings or Excel")
            return
        
        for i, company_name in enumerate(holdings, 1):
            print(f"✅ Processing company {i}/{len(holdings)}: {company_name}")
            company_user_input = user_input.copy()
            company_user_input['company_name'] = company_name
            
            try:
                run_once(company_user_input)
                print(f"✅ Completed: {company_name}")
            except Exception as e:
                print(f"❌ Failed for {company_name}: {e}")
                continue        
        print(f"✅ All companies processing completed!")
    except Exception as e:
        print(f"❌ Error in run_all_companies: {e}")

def run_all_companies_simplified(user_input):
    """Simplified function to run all companies from Excel"""
    try:
        from modules.excel_reader import read_holdings_from_excel
        holdings_data = read_holdings_from_excel()
        
        if not holdings_data:
            print("❌ No holdings found in Excel file")
            return
        
        # Handle both old format (list of strings) and new format (list of dicts)
        if isinstance(holdings_data[0], dict):
            print(f"✅ Read {len(holdings_data)} company+round combinations from Excel")
            # Use the new company+round algorithm
            run_with_company_round_combinations_simplified(user_input, holdings_data)
        else:
            print(f"✅ Read {len(holdings_data)} companies from Excel (legacy format)")
            # Use simple company processing
            for i, company_name in enumerate(holdings_data, 1):
                print(f"✅ Processing company {i}/{len(holdings_data)}: {company_name}")
                company_user_input = user_input.copy()
                company_user_input['company_name'] = company_name
                
                try:
                    run_with_original_algorithm(company_user_input, 'hist', get_search_mode('hist'))
                    print(f"✅ Completed: {company_name}")
                except Exception as e:
                    print(f"❌ Failed for {company_name}: {e}")
                    continue
        
    except Exception as e:
        print(f"❌ Error in run_all_companies_simplified: {e}")

def run_with_company_round_combinations_simplified(user_input, holdings_data):
    """Simplified version of company+round processing"""
    from modules.search_modes import get_search_mode
    
    mode = 'hist'  # Default mode
    search_mode = get_search_mode(mode)
    
    print(f"✅ Found {len(holdings_data)} company+round combinations to process")
    
    all_processed_data = []
    
    for i, combination in enumerate(holdings_data, 1):
        company = combination['company']
        round_num = combination['round']
        keyword = combination['keyword']
        
        print(f"✅ Processing combination {i}/{len(holdings_data)}: {company} - {round_num}")
        
        config = {
            'from_date': user_input['from_date'],
            'to_date': user_input['to_date'],
            'company': company,
            'keyword': keyword
        }

        scraper = KINDScraper(
            config=config,
            headless=user_input['headless'],
            process_type=mode
        )

        try:
            # Use the new details algorithm
            items = scraper.run_with_details_algorithm()
            
            if items:
                # Process the data
                data_processor = search_mode.data_processor_class()
                processed_data = data_processor.process_raw_data(items)
                
                # Add company and round info to each record
                for record in processed_data:
                    record['company'] = company
                    record['round'] = round_num
                
                all_processed_data.extend(processed_data)
                print(f"✅ Processed {len(processed_data)} records for {company} - {round_num}")
            else:
                print(f"⚠️ No data found for {company} - {round_num}")
                
        except Exception as e:
            print(f"❌ Failed to process {company} - {round_num}: {e}")
            continue
    
    # Save all processed data to database
    if all_processed_data:
        save_config = {
            'company': '전체 기업',
            'processed_data': all_processed_data,
            'key_list': search_mode.columns,
            'from_date': user_input['from_date'],
            'to_date': user_input['to_date'],
            'db_filename': search_mode.database_name
        }

        data_processor = search_mode.data_processor_class()
        data_processor.save_to_database(save_config)
        print(f"✅ 작업이 완료되었습니다! ({len(all_processed_data)} records processed)")
    else:
        print(f"❌ No data was processed for any combinations")

def run_refresh_database(user_input):
    try:
        # Read holdings directly from Excel file without updating system constants
        print("🔍 Reading holdings list from Excel file...")
        try:
            from modules.excel_reader import read_holdings_from_excel
            holdings_data = read_holdings_from_excel()
            if holdings_data:
                # Handle both old format (list of strings) and new format (list of dicts)
                if isinstance(holdings_data[0], dict):
                    holdings = [item['company'] for item in holdings_data]
                    print(f"✅ Read {len(holdings_data)} company+round combinations from Excel: {holdings_data}")
                else:
                    holdings = holdings_data
                    print(f"✅ Read {len(holdings)} companies from Excel: {holdings}")
            else:
                # Fallback to existing holdings if Excel read fails
                holdings = get("holdings", [])
                print(f"⚠️ Excel read failed, using existing holdings: {holdings}")
        except Exception as e:
            # Fallback to existing holdings if Excel read fails
            holdings = get("holdings", [])
            print(f"⚠️ Excel read failed: {e}, using existing holdings: {holdings}")
        
        if not holdings: 
            print("❌ No holdings found in settings or Excel")
            return
        
        mode = user_input.get('mode', 'hist')
        search_mode = get_search_mode(mode)
        if not search_mode:
            raise Exception(f"❌ Unknown search mode: {mode}")
        
        root_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(root_dir, 'resources', search_mode.database_name)
        
        database = {}
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        database = json.loads(content)
                    else:
                        print(f"⚠️ Database file {db_path} is empty, starting with empty database")
                        database = {}
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON in database file {db_path}: {e}, starting with empty database")
                database = {}
            except Exception as e:
                print(f"⚠️ Error reading database file {db_path}: {e}, starting with empty database")
                database = {}
        
        print(f"✅ Starting database refresh for {len(holdings)} companies...")
        
        for i, company_name in enumerate(holdings, 1):
            print(f"✅ Refreshing company {i}/{len(holdings)}: {company_name}")
            
            last_date = None
            original_first_date = '2023-01-01'  # Default original search range
            original_last_date = '2025-01-01'   # Default original search range
            
            if company_name in database:
                company_data = database[company_name]
                
                original_first_date = company_data.get('first_date', '2023-01-01')
                original_last_date = company_data.get('last_date', '2025-12-31')
                
                last_date = company_data.get('last_date', '')
            
            if not last_date:
                last_date = original_first_date
            
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            if last_date == today:
                print(f"✅ Skipping {company_name}: already up-to-date")
                continue
            
            company_user_input = user_input.copy()
            company_user_input['company_name'] = company_name
            company_user_input['from_date'] = last_date
            company_user_input['to_date'] = today
            company_user_input['original_search_first_date'] = original_first_date
            company_user_input['original_search_last_date'] = original_last_date
            
            print(f"   ✅ Date range: {last_date} ~ {company_user_input['to_date']}")
            
            try:
                run_once(company_user_input)
                print(f"✅ Refreshed: {company_name}")
            except Exception as e:
                print(f"❌ Failed to refresh {company_name}: {e}")
                continue
        
        print(f"✅ Database refresh completed for all companies!")
        
    except Exception as e:
        print(f"❌ Error in run_refresh_database: {e}")

def run_once(user_input):
    mode = user_input.get('mode', 'hist')
    search_mode = get_search_mode(mode)
    if not search_mode:
        raise Exception(f"❌ Unknown search mode: {mode}")

    # Check if we have company+round data from Excel
    from modules.excel_reader import read_holdings_from_excel
    holdings_data = read_holdings_from_excel()
    
    if holdings_data and isinstance(holdings_data[0], dict):
        # Use the new algorithm for company+round combinations
        run_with_company_round_combinations(user_input, holdings_data, mode, search_mode)
    else:
        # Use the original algorithm for single company searches
        run_with_original_algorithm(user_input, mode, search_mode)

def run_with_company_round_combinations(user_input, holdings_data, mode, search_mode):
    """Run scraper for each company+round combination using the details algorithm"""
    company_name = user_input['company_name']
    
    # Filter holdings for the specific company if not running for all companies
    if company_name != '전체 기업':
        target_combinations = [item for item in holdings_data if item['company'] == company_name]
        if not target_combinations:
            print(f"❌ No company+round combinations found for {company_name}")
            return
    else:
        target_combinations = holdings_data
    
    print(f"✅ Found {len(target_combinations)} company+round combinations to process")
    
    all_processed_data = []
    
    for i, combination in enumerate(target_combinations, 1):
        company = combination['company']
        round_num = combination['round']
        keyword = combination['keyword']
        
        print(f"✅ Processing combination {i}/{len(target_combinations)}: {company} - {round_num}")
        
        config = {
            'from_date': user_input['from_date'],
            'to_date': user_input['to_date'],
            'company': company,
            'keyword': keyword
        }

        scraper = KINDScraper(
            config=config,
            headless=user_input['headless'],
            process_type=mode
        )

        try:
            # Use the new details algorithm
            items = scraper.run_with_details_algorithm()
            
            if items:
                # Process the data
                data_processor = search_mode.data_processor_class()
                processed_data = data_processor.process_raw_data(items)
                
                # Add company and round info to each record
                for record in processed_data:
                    record['company'] = company
                    record['round'] = round_num
                
                all_processed_data.extend(processed_data)
                print(f"✅ Processed {len(processed_data)} records for {company} - {round_num}")
            else:
                print(f"⚠️ No data found for {company} - {round_num}")
                
        except Exception as e:
            print(f"❌ Failed to process {company} - {round_num}: {e}")
            continue
    
    # Save all processed data to database
    if all_processed_data:
        save_config = {
            'company': user_input['company_name'],
            'processed_data': all_processed_data,
            'key_list': search_mode.columns,
            'from_date': user_input['from_date'],
            'to_date': user_input['to_date'],
            'db_filename': search_mode.database_name
        }
        
        if 'original_search_first_date' in user_input:
            save_config['original_search_first_date'] = user_input['original_search_first_date']
            save_config['original_search_last_date'] = user_input['original_search_last_date']

        data_processor = search_mode.data_processor_class()
        data_processor.save_to_database(save_config)
        print(f"✅ {search_mode.title} 작업이 완료되었습니다! ({len(all_processed_data)} records processed)")
    else:
        print(f"❌ No data was processed for any combinations")

def run_with_original_algorithm(user_input, mode, search_mode):
    """Run scraper using the original algorithm for single company searches"""
    keyword = search_mode.keyword
    config = {
        'from_date': user_input['from_date'],
        'to_date': user_input['to_date'],
        'company': user_input['company_name'],
        'keyword': keyword
    }

    scraper = KINDScraper(
        config=config,
        headless=user_input['headless'],
        process_type=mode
    )

    items = scraper.run_with_details_algorithm()

    config = {
        'from_date': user_input['from_date'],
        'to_date': user_input['to_date'],
        'mode': mode,
        'db_filename': search_mode.database_name
    }

    data_processor = search_mode.data_processor_class()

    input_json = get("results_json")
    with open(input_json, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)

    processed_data = data_processor.process_raw_data(raw_items)

    save_config = {
        'company': user_input['company_name'],
        'processed_data': processed_data,
        'key_list': search_mode.columns,
        'from_date': user_input['from_date'],
        'to_date': user_input['to_date'],
        'db_filename': search_mode.database_name
    }
    
    if 'original_search_first_date' in user_input:
        save_config['original_search_first_date'] = user_input['original_search_first_date']
        save_config['original_search_last_date'] = user_input['original_search_last_date']

    data_processor.save_to_database(save_config)
    print(f"✅ {search_mode.title} 작업이 완료되었습니다!")

# Simplified API - only keep essential endpoints

@app.route('/api/export-to-excel', methods=['POST'])
def export_to_excel():
    try:
        data = request.get_json() or {}
        use_holdings_filter = data.get('use_holdings_filter', True)
        
        result = convert_database_to_excel(use_holdings_filter=use_holdings_filter)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/database-summary', methods=['GET'])
def get_database_summary_api():
    try:
        summary = get_database_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Removed complex dev settings and company management APIs for simplification

def start_server():
    global server_running, current_port
    server_running = True
    current_port = find_available_port()
    
    print(f"Starting HTML server on port {current_port}")
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=current_port, debug=False, use_reloader=False)

def get_user_input():
    global result_data, server_running, current_port, ui_opened
    
    if not server_running:
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()

    start_time = time.time()
    while not current_port and time.time() - start_time < 5:
        time.sleep(0.05)
    
    if current_port and not ui_opened:
        webbrowser.open(f'http://127.0.0.1:{current_port}')
        ui_opened = True
        print(f"✅ HTML UI opened at http://127.0.0.1:{current_port}")
    elif not current_port:
        return None
    
    while server_running:
        if result_data is not None:
            result = result_data
            result_data = None
            return result
        time.sleep(0.1)
    
    return None

def main():
    """Main function - starts web server and opens HTML interface"""
    global server_running
    try:
        print("✅ Starting application...")
        
        # Start server and open HTML interface
        user_input = get_user_input()
        if user_input:
            print(f"✅ Received input: {user_input}")
            # Process the input if needed (for backward compatibility)
        
        # Keep the server running
        while server_running:
            time.sleep(1)
            
    except Exception as e: 
        print(f"❌ Application failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        server_running = False

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
        server_running = False
    except Exception as e:
        print(f"❌ Server error: {e}")
        server_running = False
