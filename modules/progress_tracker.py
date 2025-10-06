import requests
import os

def update_progress(percentage):
    try:
        port = os.environ.get('WEB_UI_PORT')
        url = f'http://127.0.0.1:{port}/progress'
        requests.post(url, json={'percentage': percentage}, timeout=1)
    except: pass
