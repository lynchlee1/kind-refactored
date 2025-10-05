from modules.web_ui import get_user_input, set_scraping_completed
from modules.data_processor import process_data_to_excel
from modules.progress_tracker import send_progress_update, send_completion
from scraping.kind_scraper import KINDScraper

def main():
    try:
        user_input = get_user_input()      
        if user_input is None: return
        
        scraper = KINDScraper(
            company_name=user_input['company_name'],
            from_date=user_input['from_date'],
            to_date=user_input['to_date'],
            max_rows=user_input['max_rows'],
            headless=user_input['headless'],
            debug_mode=user_input.get('debug_mode', False)
        )
        items = scraper.run()
        
        if items:
            send_progress_update(message="Processing data and saving to Excel...")
            if process_data_to_excel(): 
                print("✅ Data processing completed!")
                send_completion("Data processing completed successfully!")
                set_scraping_completed(True)  # Signal completion to web interface
            else: 
                print("❌ Data processing failed!")
                send_completion("Data processing failed!")
                set_scraping_completed(True)  # Signal completion even on failure
        else:
            print("⚠️ No items found to process")
            send_completion("No items found to process")
            set_scraping_completed(True)  # Signal completion even with no items
    
    except Exception as e: 
        print(f"❌ Error: {e}")
        send_completion(f"Scraping failed: {e}")
        set_scraping_completed(True)  # Signal completion even on error

if __name__ == "__main__":
    main()
