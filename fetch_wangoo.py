import requests
import pandas as pd
from bs4 import BeautifulSoup
import io

def fetch_wantgoo_data(stock_code):
    url = f"https://www.wantgoo.com/stock/{stock_code}/major-investors/concentration"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Fetching data for {stock_code}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # The data for the chart is usually mirrored in a semantic HTML table for accessibility/SEO
    # We look for the main table on the page
    tables = pd.read_html(io.StringIO(str(soup)))
    
    if not tables:
        print("No tables found on the page.")
        return None

    # Usually the first major table contains the concentration data
    # It typically has columns like '日期', '1000張以上', etc.
    df = tables[0]
    
    # Clean up the dataframe (optional)
    print("Data Fetched Successfully!")
    print(df.head())
    
    return df

# --- Fetch the specific stock from your link ---
stock_id = "6275" # From your link
df = fetch_wantgoo_data(stock_id)

# If you want to save it to CSV
if df is not None:
    df.to_csv(f"data/{stock_id}_concentration.csv", index=False, encoding='utf-8-sig')
    print(f"Saved to {stock_id}_concentration.csv")