# 📁 HTML Pages with Database Integration

This folder contains standalone HTML pages that can check and display database information for the KIND Project.

## 🗂️ Files

- **`main_page.html`** - Main landing page with company input, mode selection, and developer settings
- **`hist_page.html`** - Additional listing records query page (checks `database_hist.json`)
- **`prc_page.html`** - Conversion price change query page (checks `database_prc.json`)
- **`database_server.py`** - Flask API server for database queries
- **`dev_settings_server.py`** - Flask API server for developer settings management
- **`designlib/generate_pages.py`** - Script to generate the HTML pages

## 🚀 Usage

### Option 1: Standalone HTML Pages (Basic)
1. Open `main_page.html` in your browser
2. Enter a company name and select a mode
3. The pages will show placeholder database information

### Option 2: With API Servers (Full Functionality)

#### For Database Information:
1. Start the database server:
   ```bash
   cd html_pages
   python3 database_server.py
   ```

2. Open `main_page.html` in your browser
3. Enter a company name and select a mode
4. The pages will show real database information including:
   - ✅ **Data exists** (green panel)
   - ❌ **No data** (red panel) 
   - 🔄 **Loading state** (yellow panel)
   - ⚠️ **API server not running** (gray panel)

#### For Developer Settings:
1. Start the developer settings server:
   ```bash
   cd html_pages
   python3 dev_settings_server.py
   ```

2. Click the **"개발자 모드"** button on the main page
3. Modify timing and selector settings
4. Use **"저장"** to save changes to `system_constants.json`
5. Use **"되돌리기"** to reset to default values

## 📊 Database Information Display

When a company name is provided, the pages will show:

- **Company Name**: The searched company
- **Database**: Which database file is being checked (`database_hist.json` or `database_prc.json`)
- **Status**: Whether data exists or not
- **First Date**: The earliest date in the database for this company
- **Last Date**: The most recent date in the database for this company
- **Data Count**: Number of records for this company

## 🔧 API Endpoints

### Database Server (Port 5001):
- `GET /api/company/{company_name}/hist` - Check company in `database_hist.json`
- `GET /api/company/{company_name}/prc` - Check company in `database_prc.json`

### Developer Settings Server (Port 5002):
- `GET /dev-settings` - Get current developer settings
- `POST /save-dev-settings` - Save developer settings to `system_constants.json`
- `POST /reset-dev-settings` - Reset developer settings to default values

## 📝 Database Structure

The system expects JSON databases with this structure:

```json
{
  "회사명": {
    "first_date": "2023-01-01",
    "last_date": "2023-12-31", 
    "data": [
      // ... array of records
    ]
  }
}
```

## 🎨 Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Database Checking**: Fetches live data from JSON files
- **Developer Settings Management**: Edit system constants through web interface
- **Fallback Handling**: Shows appropriate messages when API servers are not running
- **Loading States**: Visual feedback during database queries and settings loading
- **Color-coded Status**: Green (data exists), Red (no data), Yellow (loading), Gray (API error)
- **Organized Settings**: Grouped settings by category (timing, selectors, etc.)
- **Real-time Persistence**: Changes saved directly to `system_constants.json`

## 🔄 Regenerating Pages

To update the HTML pages after making changes to `generate_pages.py`:

```bash
python3 designlib/generate_pages.py
```

This will recreate all HTML files in the `html_pages/` folder with the latest changes.
