#!/usr/bin/env python3
"""
Simple Flask server to serve database information for the HTML pages
"""

from flask import Flask, jsonify, request
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

def get_company_database_info(company_name, database_file):
    """Read database file and return company information"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), database_file)
    
    if not os.path.exists(db_path):
        return None
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if company_name in data:
            company_data = data[company_name]
            return {
                'found': True,
                'first_date': company_data.get('first_date', '-'),
                'last_date': company_data.get('last_date', '-'),
                'count': len(company_data.get('data', []))
            }
        else:
            return {'found': False}
    except Exception as e:
        print(f"Error reading database {db_path}: {e}")
        return None

@app.route('/api/company/<company_name>/<mode>')
def get_company_info(company_name, mode):
    """Get company information from the appropriate database"""
    try:
        if mode == 'hist':
            database_file = 'database_hist.json'
        elif mode == 'prc':
            database_file = 'database_prc.json'
        else:
            return jsonify({'error': 'Invalid mode'}), 400
        
        db_info = get_company_database_info(company_name, database_file)
        
        if db_info is None:
            return jsonify({'error': 'Database file not found or read error'}), 500
        
        return jsonify({
            'company_name': company_name,
            'database': database_file,
            'info': db_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve the main page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database API Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            code { background: #e9e9e9; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🗄️ Database API Server</h1>
        <p>This server provides database information for the HTML pages.</p>
        
        <h2>Available Endpoints:</h2>
        <div class="endpoint">
            <strong>GET</strong> <code>/api/company/{company_name}/{mode}</code><br>
            Get company information from the database<br>
            <em>Parameters:</em> company_name (string), mode (hist|prc)
        </div>
        
        <h2>Examples:</h2>
        <ul>
            <li><a href="/api/company/삼성전자/hist">/api/company/삼성전자/hist</a></li>
            <li><a href="/api/company/삼성전자/prc">/api/company/삼성전자/prc</a></li>
        </ul>
        
        <p><strong>Note:</strong> This server reads from database_hist.json and database_prc.json files.</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Starting Database API Server...")
    print("📂 Serving from:", os.path.dirname(os.path.abspath(__file__)))
    print("🌐 Open http://localhost:5001 to view the API documentation")
    print("📊 API endpoint: http://localhost:5001/api/company/{company_name}/{mode}")
    app.run(host='localhost', port=5001, debug=True)
