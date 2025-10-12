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
        
        user_input = {
            'mode': mode,
            'company_name': data['company_name'],
            'from_date': data.get('from_date', '2022-01-01'),
            'to_date': data.get('to_date', '2024-12-31'),
            'headless': data.get('headless', False)
        }
        
        def run_scraper():
            try:
                if data.get('refresh_mode', False): # Renew database
                    if user_input['company_name'] == 'holdings_refresh':
                        user_input['company_name'] = '전체 기업'
                    run_refresh_database(user_input)
                elif user_input['company_name'] == '전체 기업':
                    run_all_companies(user_input)
                else:
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
    try:
        holdings = get("holdings", [])
        if not holdings: return
        print(f"✅ Starting scraping for {len(holdings)} companies...")
        
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

def run_refresh_database(user_input):
    try:
        holdings = get("holdings", [])
        if not holdings: return
        
        mode = user_input.get('mode', 'hist')
        search_mode = get_search_mode(mode)
        if not search_mode:
            raise Exception(f"❌ Unknown search mode: {mode}")
        
        root_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(root_dir, 'resources', search_mode.database_name)
        
        database = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
        
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

@app.route('/api/company-info', methods=['GET'])
def get_company_info():
    try:
        company = request.args.get('company', '').strip()
        mode = request.args.get('mode', 'hist').strip().lower()
        
        if not company:
            return jsonify({'found': False})
        
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
    try:
        data = request.get_json() or {}
        excel_path = data.get('excel_path')  # Optional custom path
        
        holdings = read_holdings_from_excel(excel_path)
        
        if not holdings:
            return jsonify({
                'success': False, 
                'message': 'No holdings found in Excel file. Please check the \'Holdings\' sheet and \'기업명\' column.'
            })
        
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

@app.route('/api/dev-settings', methods=['GET'])
def get_dev_settings():
    try:
        from modules.settings import get_section
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
    try:
        data = request.get_json()
        
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

        settings_path = os.path.join(ROOT_DIR, 'resources', 'system_constants.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reset-dev-settings', methods=['POST'])
def reset_dev_settings():
    try:
        default_file = os.path.join(ROOT_DIR, 'resources', 'default_constants.json')
        
        with open(default_file, 'r', encoding='utf-8') as f:
            default_settings = json.load(f)
        
        settings_path = os.path.join(ROOT_DIR, 'resources', 'system_constants.json')
        with open(settings_path, 'r', encoding='utf-8') as f:
            current_settings = json.load(f)
        
        current_settings['timing'] = default_settings.get('timing', {})
        current_settings['selectors'] = default_settings.get('selectors', {})
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discard-company-data', methods=['POST'])
def discard_company_data():
    """Delete a company's data from the database"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        mode = data.get('mode', 'hist')
        
        if not company_name:
            return jsonify({'success': False, 'message': 'Company name is required'})
        
        # Get the appropriate database file based on mode
        search_mode = get_search_mode(mode)
        if not search_mode:
            return jsonify({'success': False, 'message': f'Unknown mode: {mode}'})
        
        db_path = os.path.join(ROOT_DIR, 'resources', search_mode.database_name)
        
        # Load existing database
        database = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
        
        # Check if company exists in database
        if company_name not in database:
            return jsonify({'success': False, 'message': f'Company "{company_name}" not found in {mode} database'})
        
        # Remove the company from database
        del database[company_name]
        
        # Save updated database
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        mode_text = '추가상장 기록' if mode == 'hist' else '전환가액 변동'
        return jsonify({
            'success': True, 
            'message': f'Successfully deleted {company_name} from {mode_text} database'
        })
        
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
    global server_running
    try:
        while True:
            user_input = get_user_input()
            if not user_input:
                break
            try:
                mode = user_input.get('mode', 'hist')
                if mode not in ['hist', 'prc']:
                    mode = 'hist'
                
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
    try: main()
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
        server_running = False
    except Exception as e:
        print(f"❌ Server error: {e}")
        server_running = False
