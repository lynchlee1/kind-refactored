# KIND Scraper

Web scraping tool for extracting event history data from KIND

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python main.py
```

3. **Use the web interface** to configure and start scraping.

## Output Files

- `details_links.json` - Raw scraped data
- `results.xlsx` - Processed Excel file

## Project Structure

```
kind-project/
├── modules/           # Core modules
├── scraping/         # Scraping logic  
├── main.py          # Entry point
└── requirements.txt # Dependencies
```