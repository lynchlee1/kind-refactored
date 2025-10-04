"""
Web-based user interface module
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import webbrowser
import threading
import time
import sys
import os
import socket

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIND Project - Configuration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            background: linear-gradient(135deg, #1D79B0 0%, #1D5D8C 50%, #344B79 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 650px;
            min-height: 700px;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo {
            width: 320px;
            height: 100px;
            border-radius: 15px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }
        
        .logo img {
            width: 320px;
            height: 100px;
            object-fit: contain;
            border-radius: 10px;
        }
        
        .title {
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #6c757d;
            font-size: 16px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 16px;
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Malgun Gothic', Arial, sans-serif;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #007bff;
            background: white;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        
        .date-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        .checkbox {
            width: 20px;
            height: 20px;
            accent-color: #007bff;
        }
        
        .checkbox-label {
            color: #2c3e50;
            font-size: 14px;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.3);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .progress-container {
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #0056b3);
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .progress-fill.completed {
            background: linear-gradient(90deg, #28a745, #1e7e34);
        }
        
        .progress-text {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .progress-details {
            font-size: 12px;
            color: #6c757d;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/logo.jpg" alt="Logo">
            </div>
            <h1 class="title">KIND 행사내역 조회 프로그램</h1>
            <p class="subtitle">타임폴리오 대체투자본부</p>
        </div>
        
        <form id="configForm">
            <div class="form-group">
                <label class="form-label" for="company">Company Name</label>
                <input type="text" id="company" name="company" class="form-input" 
                       value="에스티팜" required>
            </div>
            
            <div class="form-group">
                <div class="date-row">
                    <div>
                        <label class="form-label" for="fromDate">From Date</label>
                        <input type="date" id="fromDate" name="fromDate" class="form-input" 
                               value="2024-09-20" required>
                    </div>
                    <div>
                        <label class="form-label" for="toDate">To Date</label>
                        <input type="date" id="toDate" name="toDate" class="form-input" 
                               value="2025-09-30" required>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="maxRows">Maximum Rows per Page</label>
                <input type="number" id="maxRows" name="maxRows" class="form-input" 
                       value="200" min="1" max="1000" required>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="headless" name="headless" class="checkbox">
                <label for="headless" class="checkbox-label">Run in background (headless mode)</label>
            </div>
            
            <div class="button-group">
                <button type="button" class="btn btn-secondary" onclick="cancel()">Cancel</button>
                <button type="submit" class="btn btn-primary">Start Scraping</button>
            </div>
            
            <div class="loading">
                <div class="spinner"></div>
                <p>Starting web scraping...</p>
            </div>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-text" id="progressText">Initializing...</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-details" id="progressDetails">Connecting to KIND website...</div>
            </div>
            
            <div class="status" id="status"></div>
        </form>
    </div>
    
    <script>
        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                company_name: formData.get('company'),
                from_date: formData.get('fromDate'),
                to_date: formData.get('toDate'),
                max_rows: parseInt(formData.get('maxRows')),
                headless: formData.has('headless')
            };
            
            // Validate dates
            const fromDate = new Date(data.from_date);
            const toDate = new Date(data.to_date);
            
            if (fromDate > toDate) {
                showStatus('From date cannot be after To date', 'error');
                return;
            }
            
            // Show progress
            document.querySelector('.loading').style.display = 'none';
            document.querySelector('.progress-container').style.display = 'block';
            document.querySelector('.button-group').style.display = 'none';
            
            // Start progress simulation
            simulateProgress();
            
            // Start polling for real progress updates
            startProgressPolling();
            
            // Send data to server
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Keep window open - don't close automatically
                } else {
                    showStatus('Error: ' + result.message, 'error');
                    document.querySelector('.loading').style.display = 'none';
                    document.querySelector('.button-group').style.display = 'flex';
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
                document.querySelector('.loading').style.display = 'none';
                document.querySelector('.button-group').style.display = 'flex';
            });
        });
        
        function cancel() {
            fetch('/cancel', { method: 'POST' })
            .then(() => {
                // Keep window open - let user close manually
                showStatus('Operation cancelled', 'error');
            });
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
        
        function simulateProgress() {
            let progress = 0;
            let currentStep = 0;
            const steps = [
                { text: "Connecting to KIND website...", progress: 0 },
                { text: "Navigating to search page...", progress: 0 },
                { text: "Entering company name: 에스티팜...", progress: 0 },
                { text: "Setting date range...", progress: 0 },
                { text: "Clicking search button...", progress: 0 },
                { text: "Loading search results...", progress: 0 },
                { text: "Finding result rows...", progress: 0 },
                { text: "Extracting data from reports...", progress: 0 },
                { text: "Processing extracted data...", progress: 95 },
                { text: "Finalizing and saving results...", progress: 100 }
            ];
            
            function updateProgress() {
                if (currentStep < steps.length) {
                    const step = steps[currentStep];
                    progress = step.progress;
                    
                    document.getElementById('progressFill').style.width = progress + '%';
                    document.getElementById('progressText').textContent = `Progress: ${progress}%`;
                    document.getElementById('progressDetails').textContent = step.text;
                    
                    currentStep++;
                    
                    // Simulate processing time
                    const delay = currentStep <= 5 ? 1500 : 2000; // Faster initial steps
                    setTimeout(updateProgress, delay);
                } else {
                    // Keep at 100% until process completes
                    document.getElementById('progressText').textContent = 'Progress: 100%';
                    document.getElementById('progressDetails').textContent = 'Scraping completed! Processing results...';
                }
            }
            
            updateProgress();
        }
        
        function updateProgressFromServer(currentReport, totalReports, firstReportNumber, completed) {
            if (currentReport && totalReports) {
                const progress = Math.min(95, Math.round((currentReport / totalReports) * 100));
                document.getElementById('progressFill').style.width = progress + '%';
                
                if (completed) {
                    // Show green bar when completed
                    document.getElementById('progressFill').classList.add('completed');
                    document.getElementById('progressFill').style.width = '100%';
                    document.getElementById('progressText').textContent = '100%';
                    document.getElementById('progressDetails').textContent = 'Web scraping process completed successfully!';
                } else if (firstReportNumber) {
                    // Show report number format: "X / firstReportNumber"
                    document.getElementById('progressText').textContent = `${currentReport} / ${firstReportNumber}`;
                    document.getElementById('progressDetails').textContent = `Processing report ${currentReport} of ${totalReports}...`;
                } else {
                    // Fallback to percentage format
                    document.getElementById('progressText').textContent = `Progress: ${progress}%`;
                    document.getElementById('progressDetails').textContent = `Processing report ${currentReport} of ${totalReports}...`;
                }
            }
        }
        
        function startProgressPolling() {
            let pollingInterval = setInterval(() => {
                fetch('/get-progress')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.progress) {
                        updateProgressFromServer(
                            data.progress.current_report,
                            data.progress.total_reports,
                            data.progress.first_report_number,
                            data.progress.completed
                        );
                        
                        // Stop polling if completed
                        if (data.progress.completed) {
                            clearInterval(pollingInterval);
                        }
                    }
                })
                .catch(error => {
                    console.log('Progress polling error:', error);
                });
            }, 1000); // Poll every second
            
            // Stop polling after 10 minutes to avoid infinite polling
            setTimeout(() => {
                clearInterval(pollingInterval);
            }, 600000);
        }
    </script>
</body>
</html>
'''

# Global variable to store the result
result_data = None
server_running = False
current_port = None
progress_data = None

def find_available_port(start_port=5000):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")

@app.route('/')
def index():
    print("🔍 Serving updated HTML template with debug mode checkbox")
    return render_template_string(HTML_TEMPLATE)

@app.route('/logo.jpg')
def logo():
    import os
    # Get the directory where this script is located (project root)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(current_dir, 'logo.jpg')

@app.route('/submit', methods=['POST'])
def submit():
    global result_data
    try:
        data = request.get_json()
        
        # Validate data
        if not data.get('company_name'):
            return jsonify({'success': False, 'message': 'Company name is required'})
        
        if data.get('max_rows', 0) <= 0:
            return jsonify({'success': False, 'message': 'Max rows must be greater than 0'})
        
        result_data = data
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cancel', methods=['POST'])
def cancel():
    global result_data
    result_data = None
    return jsonify({'success': True})

@app.route('/progress', methods=['POST'])
def update_progress():
    """Endpoint to receive progress updates from the scraper"""
    try:
        data = request.get_json()
        current_report = data.get('current_report')
        total_reports = data.get('total_reports')
        message = data.get('message', 'Processing...')
        first_report_number = data.get('first_report_number')
        completed = data.get('completed', False)
        
        # Store progress data globally
        global progress_data
        progress_data = {
            'current_report': current_report,
            'total_reports': total_reports,
            'message': message,
            'first_report_number': first_report_number,
            'completed': completed
        }
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get-progress', methods=['GET'])
def get_progress():
    """Endpoint to get current progress data"""
    global progress_data
    if progress_data:
        return jsonify({'success': True, 'progress': progress_data})
    else:
        return jsonify({'success': False, 'message': 'No progress data available'})

def start_server():
    global server_running, current_port
    server_running = True
    current_port = find_available_port()
    print(f"🌐 Starting server on port {current_port}")
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=current_port, debug=False, use_reloader=False)

def get_user_input():
    """Show the web-based input dialog and return the result"""
    global result_data, server_running, current_port
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start and get the port
    time.sleep(0.5)
    
    # Open browser with the actual port
    if current_port:
        webbrowser.open(f'http://127.0.0.1:{current_port}')
        print(f"🌐 Opened browser at http://127.0.0.1:{current_port}")
    else:
        print("❌ Failed to start server")
        return None
    
    # Wait for user input
    while server_running:
        if result_data is not None:
            break
        time.sleep(0.1)
    
    return result_data

if __name__ == "__main__":
    result = get_user_input()
    if result:
        print("User input:", result)
    else:
        print("User cancelled")
