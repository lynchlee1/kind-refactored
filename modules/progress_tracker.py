import requests
import time
import os
from settings import get

# Progress tracking for web interface
def send_progress_update(current=0, total=0, message="Processing...", completed=False):
    """Send progress update to the web interface"""
    try:
        # Get the port from environment variable or try common ports
        port = os.environ.get('WEB_UI_PORT', '5000')
        url = f'http://127.0.0.1:{port}/progress'
        
        # Try to send progress update to web interface
        requests.post(url, 
                     json={
                         'current': current,
                         'total': total,
                         'message': message,
                         'completed': completed
                     }, timeout=1)
    except Exception as e:
        # Ignore if web interface is not available
        pass

def send_page_progress(page_num, total_pages=None):
    """Send page processing progress"""
    if total_pages:
        message = f"Processing page {page_num} of {total_pages}..."
    else:
        message = f"Processing page {page_num}..."
    send_progress_update(current=page_num, total=total_pages, message=message)

def send_report_progress(current, total, message=None):
    """Send report processing progress"""
    if message is None:
        message = f"Processing report {current} of {total}..."
    send_progress_update(current=current, total=total, message=message)

def send_completion(message="Scraping completed successfully!"):
    """Send completion status"""
    send_progress_update(message=message, completed=True)
