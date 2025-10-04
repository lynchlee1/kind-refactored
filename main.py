from modules.web_ui import get_user_input, current_port
from modules.progress_tracker import set_progress_port
from modules.data_processor import process_data_to_excel
from scraping.kind_scraper import KINDScraper

def main():
    try:
        user_input = get_user_input()      
        if user_input is None: return
        
        set_progress_port(current_port)
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
            if process_data_to_excel(): print("✅ Data processing completed!")
            else: print("❌ Data processing failed!")
    
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
