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

@app.route('/hist_page.html')
def hist_page_route(): return hist_page()

@app.route('/prc_page.html')
def prc_page_route(): return prc_page()

@app.route('/dev_mode.html')
def dev_mode_page_route(): return dev_mode_page()

@app.route('/hist_page_dataset.html')
def hist_dataset_page_route(): 
    company_name = request.args.get('company')
    round_filter = request.args.get('round', '')
    return hist_dataset_page(company_name, round_filter)

@app.route('/prc_page_dataset.html')
def prc_dataset_page_route(): 
    company_name = request.args.get('company')
    round_filter = request.args.get('round', '')
    return prc_dataset_page(company_name, round_filter)

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

@app.route('/api/run/<function_name>', methods=['POST'])
def run_function(function_name):
    global result_data
    try:
        data = request.get_json()
        if not data.get('company_name'): return jsonify({'success': False, 'message': 'Company name is required'})
        
        function_to_mode = {
            'run_hist_scraper': 'hist',
            'run_prc_scraper': 'prc'
        }
        
        mode = function_to_mode.get(function_name)
        if not mode:
            return jsonify({'success': False, 'message': f'Unknown function: {function_name}'})
        
        # Prepare user input for run_once function
        user_input = {
            'mode': mode,
            'company_name': data['company_name'],
            'from_date': data.get('from_date', '2024-01-01'),
            'to_date': data.get('to_date', '2025-01-01'),
            'headless': data.get('headless', False)
        }
        
        # Execute the scraper function in a separate thread
        def run_scraper():
            try:
                if data.get('refresh_mode', False):
                    # Handle refresh mode - update database with new data from last date to today
                    run_refresh_database(user_input)
                elif user_input['company_name'] == '전체 기업':
                    # Handle all companies mode
                    run_all_companies(user_input)
                else:
                    # Handle single company mode
                    run_once(user_input)
            except Exception as e:
                print(f"Error in scraper: {e}")
        
        thread = threading.Thread(target=run_scraper)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': f'{function_name} started'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def run_all_companies(user_input):
    """Execute scraping for all companies in holdings list"""
    try:
        # Get holdings list from settings
        holdings = get("holdings", [])
        if not holdings:
            print("❌ No holdings list found in settings")
            return
        
        print(f"✅ Starting scraping for {len(holdings)} companies...")
        
        for i, company_name in enumerate(holdings, 1):
            print(f"✅ Processing company {i}/{len(holdings)}: {company_name}")
            
            # Create user input for this specific company
            company_user_input = user_input.copy()
            company_user_input['company_name'] = company_name
            
            try:
                # Run scraper for this company
                run_once(company_user_input)
                print(f"✅ Completed: {company_name}")
            except Exception as e:
                print(f"❌ Failed for {company_name}: {e}")
                continue
        
        print(f"🎉 All companies processing completed!")
        
    except Exception as e:
        print(f"❌ Error in run_all_companies: {e}")

def run_refresh_database(user_input):
    """Execute database refresh - scrape new data from last date to today for all companies"""
    try:
        # Get holdings list from settings
        holdings = get("holdings", [])
        if not holdings:
            print("❌ No holdings list found in settings")
            return
        
        mode = user_input.get('mode', 'hist')
        search_mode = get_search_mode(mode)
        if not search_mode:
            raise Exception(f"❌ Unknown search mode: {mode}")
        
        # Get database file path
        root_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(root_dir, 'resources', search_mode.database_name)
        
        # Load existing database
        database = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
        
        print(f"🔄 Starting database refresh for {len(holdings)} companies...")
        
        for i, company_name in enumerate(holdings, 1):
            print(f"✅ Refreshing company {i}/{len(holdings)}: {company_name}")
            
            last_date = None
            original_first_date = '2024-01-01'  # Default original search range
            original_last_date = '2025-01-01'   # Default original search range
            
            if company_name in database:
                company_data = database[company_name]
                
                # Use the last_date from database metadata (not actual data dates)
                last_date = company_data.get('last_date', '')
                
                # Preserve original search ranges
                original_first_date = company_data.get('first_date', '2024-01-01')
                original_last_date = company_data.get('last_date', '2025-12-31')
            
            # If no last date, use a default starting date
            if not last_date:
                last_date = '2023-01-01'  # Default start date if no previous data
            
            # Always use today's date as the end date for refresh
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Create company-specific user input with updated date range
            company_user_input = user_input.copy()
            company_user_input['company_name'] = company_name
            company_user_input['from_date'] = last_date
            company_user_input['to_date'] = today
            # Store original search ranges to preserve them
            company_user_input['original_search_first_date'] = original_first_date
            company_user_input['original_search_last_date'] = original_last_date
            
            print(f"   ✅ Date range: {last_date} ~ {company_user_input['to_date']}")
            
            try:
                run_once(company_user_input)
                print(f"✅ Refreshed: {company_name}")
            except Exception as e:
                print(f"❌ Failed to refresh {company_name}: {e}")
                continue
        
        print(f"🎉 Database refresh completed for all companies!")
        
    except Exception as e:
        print(f"❌ Error in run_refresh_database: {e}")

def run_once(user_input):
    """Execute one scraping run - integrated from main.py"""
    mode = user_input.get('mode', 'hist')
    search_mode = get_search_mode(mode)
    if not search_mode:
        raise Exception(f"❌ Unknown search mode: {mode}")

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

    items = scraper.run()

    # Process data using mode-specific processor
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
    
    # If this is a refresh operation, preserve original search ranges
    if 'original_search_first_date' in user_input:
        save_config['original_search_first_date'] = user_input['original_search_first_date']
        save_config['original_search_last_date'] = user_input['original_search_last_date']

    data_processor.save_to_database(save_config)
    print(f"✅ {search_mode.title} 작업이 완료되었습니다!")

@app.route('/api/company-info', methods=['GET'])
def get_company_info():
    """Get company information from database"""
    try:
        company = request.args.get('company', '').strip()
        mode = request.args.get('mode', 'hist').strip().lower()
        
        if not company:
            return jsonify({'found': False})
        
        # Get database path based on mode
        search_mode = get_search_mode(mode)
        if not search_mode:
            return jsonify({'found': False, 'error': f'Unknown mode: {mode}'})
        
        db_filename = search_mode.database_name
        db_path = os.path.join(ROOT_DIR, 'resources', db_filename)
        
        if not os.path.exists(db_path):
            return jsonify({'found': False})
        
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entry = data.get(company, {})
        if not entry:
            return jsonify({'found': False})
        
        return jsonify({
            'found': True,
            'first_date': entry.get('first_date'),
            'last_date': entry.get('last_date'),
            'count': len(entry.get('data', []))
        })
        
    except Exception as e:
        return jsonify({'found': False, 'error': str(e)})

@app.route('/api/refresh-holdings', methods=['POST'])
def refresh_holdings_from_excel():
    """Refresh holdings list from Excel file"""
    try:
        data = request.get_json() or {}
        excel_path = data.get('excel_path')  # Optional custom path
        
        # Read holdings from Excel
        holdings = read_holdings_from_excel(excel_path)
        
        if not holdings:
            return jsonify({
                'success': False, 
                'message': 'No holdings found in Excel file. Please check the \'Holdings\' sheet and \'기업명\' column.'
            })
        
        # Update system constants
        success = update_system_constants_with_excel(excel_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully updated holdings list with {len(holdings)} companies',
                'holdings': holdings
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update system constants'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get-holdings', methods=['GET'])
def get_current_holdings():
    """Get current holdings list from system constants"""
    try:
        holdings = get("holdings", [])
        return jsonify({
            'success': True,
            'holdings': holdings,
            'count': len(holdings)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/export-to-excel', methods=['POST'])
def export_to_excel():
    """Export database data to Excel file using Holdings sheet for filtering"""
    try:
        data = request.get_json() or {}
        use_holdings_filter = data.get('use_holdings_filter', True)
        
        result = convert_database_to_excel(use_holdings_filter=use_holdings_filter)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/database-summary', methods=['GET'])
def get_database_summary_api():
    """Get database summary information using Holdings sheet for filtering"""
    try:
        summary = get_database_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/dev-settings', methods=['GET'])
def get_dev_settings():
    """Get developer settings"""
    try:
        from modules.settings import get_section
        # Get timing and selectors sections from system_constants.json
        timing = get_section('timing')
        selectors = get_section('selectors')
        return jsonify({
            'timing': timing,
            'selectors': selectors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-dev-settings', methods=['POST'])
def save_dev_settings():
    """Save developer settings"""
    try:
        data = request.get_json()
        
        # Coerce numeric timing values to proper numbers
        try:
            timing = data.get('timing', {}) or {}
            numeric_keys = [
                'buffer_time', 'short_loadtime', 'long_loadtime',
            ]
            for key in numeric_keys:
                if key in timing:
                    val = timing[key]
                    if isinstance(val, str):
                        try:
                            if val.strip().isdigit():
                                timing[key] = int(val)
                            else:
                                timing[key] = float(val)
                        except Exception:
                            pass
            data['timing'] = timing
        except Exception:
            pass

        # Save to system_constants.json
        settings_path = os.path.join(ROOT_DIR, 'resources', 'system_constants.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reset-dev-settings', methods=['POST'])
def reset_dev_settings():
    """Reset developer settings to defaults from default_constants.json"""
    try:
        # Load default settings from default_constants.json
        default_file = os.path.join(ROOT_DIR, 'resources', 'default_constants.json')
        
        with open(default_file, 'r', encoding='utf-8') as f:
            default_settings = json.load(f)
        
        # Load current system_constants.json to preserve other sections
        settings_path = os.path.join(ROOT_DIR, 'resources', 'system_constants.json')
        with open(settings_path, 'r', encoding='utf-8') as f:
            current_settings = json.load(f)
        
        # Update only timing and selectors sections from default_constants.json
        current_settings['timing'] = default_settings.get('timing', {})
        current_settings['selectors'] = default_settings.get('selectors', {})
        
        # Save updated settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
    
    # Start server only if not already running
    if not server_running:
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
    
    # Wait briefly for the server to report its port
    start_time = time.time()
    while not current_port and time.time() - start_time < 5:
        time.sleep(0.05)
    
    # Open the UI exactly once
    if current_port and not ui_opened:
        webbrowser.open(f'http://127.0.0.1:{current_port}')
        ui_opened = True
        print(f"✅ HTML UI opened at http://127.0.0.1:{current_port}")
    elif not current_port:
        return None
    
    # Wait for user input (submission from web UI)
    while server_running:
        if result_data is not None:
            # Return the user input data and clear it for next run
            result = result_data
            result_data = None
            return result
        time.sleep(0.1)
    
    return None

def main():
    """Main function with loop to support multiple runs"""
    global server_running
    try:
        # Loop to support multiple runs until the UI is closed
        while True:
            user_input = get_user_input()
            if not user_input:
                break
            try:
                # Determine mode from user input
                mode = user_input.get('mode', 'hist')
                if mode not in ['hist', 'prc']:
                    mode = 'hist'  # default fallback
                
                # Update user_input with proper mode
                user_input['mode'] = mode
                
                print(f"✅ Starting {mode} scraper...")
                run_once(user_input)
                print(f"✅ {mode.upper()} scraper completed successfully!")
                
            except Exception as e:
                print(f"❌ Scraper failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("✅ Program terminated.")
        
    except Exception as e: 
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        server_running = False

if __name__ == "__main__":
    print("✅ Starting KIND Project HTML Server...")
    print("✅ Available pages:")
    print("   - Main page: http://127.0.0.1:5000/")
    print("   - Hist page: http://127.0.0.1:5000/hist_page.html")
    print("   - PRC page: http://127.0.0.1:5000/prc_page.html")
    print("   - Dev mode: http://127.0.0.1:5000/dev_mode.html")
    print("")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
        server_running = False
    except Exception as e:
        print(f"❌ Server error: {e}")
        server_running = False
