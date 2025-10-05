import requests
import time
import os
from settings import get

def send_progress_update(percentage=0, completed=False):
    try:
        port = os.environ.get('WEB_UI_PORT')
        url = f'http://127.0.0.1:{port}/progress'
        requests.post(url, 
                     json={
                         'percentage': percentage,
                         'completed': completed
                     }, timeout=1)
    except: pass

def send_report_progress(current, total):
    percentage = (current / total) * 100 if total > 0 else 0
    send_progress_update(percentage=percentage)

def send_completion():
    send_progress_update(percentage=100, completed=True)
