import designlib.web_ui as web_ui
from designlib.web_ui import get_user_input
import time
from modules.progress_tracker import update_progress
from modules.kind_scraper import KINDScraper
from modules.search_modes import get_search_mode

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

    # Process data using mode-specific processor
    config = {
        'from_date': user_input['from_date'],
        'to_date': user_input['to_date'],
        'mode': mode
    }

    data_processor = search_mode.data_processor_class()

    from modules.settings import get
    import json
    input_json = get("results_json")
    with open(input_json, 'r', encoding='utf-8') as f:
        raw_items = json.load(f)

    processed_data = data_processor.process_raw_data(raw_items)

    # Prepare config for save_to_database method
    save_config = {
        'company': user_input['company_name'],
        'processed_data': processed_data,
        'key_list': search_mode.columns,
        'from_date': user_input['from_date'],
        'to_date': user_input['to_date']
    }

    data_processor.save_to_database(save_config)
    update_progress(100)
    print(f"✅ {search_mode.display_name} 작업이 완료되었습니다!")
    time.sleep(1)

def main():
    try:
        # Loop to support multiple runs until the UI is closed
        while True:
            user_input = get_user_input()
            if not user_input:
                break
            try:
                run_once(user_input)
            except Exception as e:
                print(f"(오류) 데이터 처리 실패: {e}")
                update_progress(100)
                time.sleep(1)
        print("프로그램을 종료합니다.")
    except Exception as e: 
        print(f"(오류) 실행 실패: {e}")
        update_progress(100)
        time.sleep(1)

if __name__ == "__main__":  
    main()
