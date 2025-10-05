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
            headless=user_input['headless']
        )
        items = scraper.run()
        
        if items:
            send_progress_update(percentage=90)
            if process_data_to_excel(): 
                print("✅ Data processing completed!")
                send_completion()
                set_scraping_completed(True)
            else: 
                print("❌ Data processing failed!")
                send_completion()
                set_scraping_completed(True)
        else:
            print("❌ No items found to process")
            send_completion()
            set_scraping_completed(True)
    
    except Exception as e: 
        print(f"❌ Scraping failed: {e}")
        send_completion()
        set_scraping_completed(True)

if __name__ == "__main__":  
    main()
