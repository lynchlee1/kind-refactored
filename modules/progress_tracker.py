import requests
from settings import get

progress_port = None
def set_progress_port(port):
    global progress_port
    progress_port = port

# Send progress text to interface
def send_progress_update(message="Processing...", completed=False):
    global progress_port
    if progress_port: # When web interface is available
        try:
            requests.post(f'http://127.0.0.1:{progress_port}/progress', 
                         json={
                             'message': message,
                             'completed': completed
                         }, timeout = get("timeout"))
        except: pass
