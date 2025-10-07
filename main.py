import modules.web_ui as web_ui
from modules.web_ui import get_user_input
import json, os, time, threading
from modules.process_data import process_to_excel, process_to_json
from modules.progress_tracker import update_progress
from scraping.kind_scraper import KINDScraper

def main():
    try:
        user_input = get_user_input()
        if not user_input: return

        scraper = KINDScraper(
            company_name=user_input['company_name'],
            from_date=user_input['from_date'],
            to_date=user_input['to_date'],
            headless=user_input['headless']
        )
        items = scraper.run()
        if items:
            process_to_excel()
            process_to_json({
                'from_date': user_input['from_date'],
                'to_date': user_input['to_date']
            })
            
            # Set progress to 100% after all processing is complete
            update_progress(100)
            print("✅ 모든 작업이 완료되었습니다!")
            
            # Wait a moment for the web UI to update before returning
            time.sleep(2)
        else:
            # No items found - still set to 100%
            update_progress(100)
            print("⚠️ 검색 결과가 없습니다.")
            time.sleep(2)
            
    except Exception as e: 
        print(f"❌ Scraping failed: {e}")
        # Even on error, set to 100%
        update_progress(100)
        time.sleep(2)
        
    # Keep the web UI running until user clicks Close button
    print("웹 인터페이스가 열려있습니다. '닫기' 버튼을 눌러 종료하세요.")
    
    # Keep the main thread alive so the web UI continues running
    while getattr(web_ui, 'server_running', False):
        time.sleep(1)
    print("프로그램을 종료합니다.")

if __name__ == "__main__":  
    main()
