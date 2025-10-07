import requests
import os

def update_progress(percentage, first_report_number=None):
    try:
        port = os.environ.get('WEB_UI_PORT')
        url = f'http://127.0.0.1:{port}/progress'
        data = {'percentage': percentage}
        if first_report_number:
            data['first_report_number'] = first_report_number
        requests.post(url, json=data, timeout=1)
    except: pass
