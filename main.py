from modules.web_ui import get_user_input
from modules.process_data import process_to_excel
from modules.progress_tracker import update_progress
from scraping.kind_scraper import KINDScraper

def main():
    try:
        user_input = get_user_input()        
        scraper = KINDScraper(
            company_name=user_input['company_name'],
            from_date=user_input['from_date'],
            to_date=user_input['to_date'],
            headless=user_input['headless']
        )
        items = scraper.run()
        if items: process_to_excel()
    except Exception as e: print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":  
    main()
