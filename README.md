# KIND Scraper Project

A web scraping tool for extracting event history data from KIND (Korea Exchange Information Disclosure System).

## Project Structure

The project has been reconstructed into a clean, organized structure:

```
kind-project/
├── constants/           # Configuration constants
│   ├── __init__.py
│   ├── config.py       # Main configuration constants
│   └── dev_config.py   # Developer settings
├── modules/            # Reusable modules
│   ├── __init__.py
│   ├── web_ui.py       # Web-based user interface
│   ├── driver_manager.py # Web driver management
│   ├── data_processor.py # Data processing utilities
│   └── progress_tracker.py # Progress tracking
├── scraping/           # Scraping logic
│   ├── __init__.py
│   └── kind_scraper.py # Main scraper implementation
├── main.py            # Main entry point
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate.bat  # Windows
# or
source venv/bin/activate   # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python main.py
```

This will:
1. Open a web-based configuration interface
2. Allow you to set scraping parameters (company name, date range, etc.)
3. Perform the scraping operation
4. Save results to JSON and Excel files

## Configuration

### Basic Settings
- **Company Name**: Target company to search for
- **Date Range**: From and to dates for the search
- **Max Rows**: Maximum number of rows to process per page
- **Headless Mode**: Run browser in background
- **Debug Mode**: Show detailed logging

### Advanced Settings
Developer settings can be configured through the web interface when developer mode is enabled.

## Output Files

- `details_links.json`: Raw scraped data in JSON format
- `results.xlsx`: Processed data in Excel format
- `dev_settings.json`: Developer configuration (auto-generated)

## Features

- **Web-based UI**: Modern, responsive interface
- **Progress Tracking**: Real-time progress updates
- **Data Processing**: Automatic conversion to Excel format
- **Error Handling**: Robust error handling and recovery
- **Modular Design**: Clean separation of concerns

## Development

The project is organized into three main parts:

1. **Constants**: Configuration values and settings
2. **Modules**: Reusable components (UI, driver management, data processing)
3. **Scraping**: Core scraping logic

This structure makes the codebase maintainable and extensible.
