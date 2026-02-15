import os
import time
import random
import requests
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from openbb import obb

# Configuration
OUTPUT_DIR = "fig/finviz_new_high"
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def setup_session():
    """Configure a requests session with retries for robustness."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def get_headers():
    """Generate headers to mimic a real browser."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://finviz.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

def download_chart(symbol, sector, industry, timeframe, session):
    """
    Download chart for a symbol and timeframe.
    timeframe: 'w' for weekly, 'm' for monthly
    """
    # Sanitize industry and sector for filenames
    safe_sector = sector.replace("/", "_").replace(" ", "_")
    safe_industry = industry.replace("/", "_").replace(" ", "_")
    filename = f"{safe_sector}_{safe_industry}_{symbol}_{timeframe}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    BASE_URL = "https://charts2-node.finviz.com/chart.ashx"

    if os.path.exists(filepath):
        return True

    params = {
        "cs": "m",
        "t": symbol,
        "tf": timeframe,
        "s": "linear",
        "pm": "0",
        "am": "0",
        "ct": "candle_stick",
        "tm": "m",
        "sf": "2 2x"
    }
    
    headers = get_headers()

    try:
        response = session.get(BASE_URL, params=params, headers=headers, timeout=20)
        
        if response.status_code == 403:
            print(f"\nBlocked (403) for {symbol} ({timeframe}). Pausing for 60 seconds...")
            time.sleep(60)
            session = setup_session()
            response = session.get(BASE_URL, params=params, headers=get_headers(), timeout=20)
            
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"\nError downloading {timeframe} chart for {symbol}: {e}")
        return False

def clean_performance(df):
    cols = ['performance_1m', 'performance_3m']
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.rstrip('%').replace('nan', '0').replace('-', '0').astype(float)
    return df

def main():
    # Clear output directory
    import shutil
    if os.path.exists(OUTPUT_DIR):
        print(f"Clearing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching sector and industry performance...")
    # 1. Fetch and filter Sectors (1M and 3M positive)
    df_sectors = obb.equity.compare.groups(group="sector", metric="performance", provider="finviz").to_df()
    df_sectors = clean_performance(df_sectors)
    qualified_sectors = df_sectors[(df_sectors['performance_1m'] > 0) & (df_sectors['performance_3m'] > 0)]['name'].tolist()
    print(f"Qualified Sectors: {qualified_sectors}")

    # 2. Fetch and filter Industries (1M positive)
    df_industries = obb.equity.compare.groups(group="industry", metric="performance", provider="finviz").to_df()
    df_industries = clean_performance(df_industries)
    qualified_industries = df_industries[df_industries['performance_1m'] > 0]['name'].tolist()
    print(f"Number of Qualified Industries: {len(qualified_industries)}")

    # 3. Run Screener with specified filters
    print("Running screener...")
    filters = {
        'Average Volume': 'Over 300K',
        '52-Week High/Low': 'New High',
        'Performance': 'Week Up',
        'Performance 2': 'Quarter +10%',
        '20-Day Simple Moving Average': 'SMA20 above SMA50',
        '200-Day Simple Moving Average': 'Price above SMA200',
        '50-Day Simple Moving Average': 'SMA50 below SMA20'
    }

    results = obb.equity.screener(
        provider='finviz',
        mktcap='mid_over',
        filters_dict=filters
    ).to_df()

    # 4. Filter by Qualified Sectors and Industries
    filtered_results = results[
        results['sector'].isin(qualified_sectors) & 
        results['industry'].isin(qualified_industries)
    ].copy()

    # 4.1 Generate Summary and Filter for Top 10 Industries
    if not filtered_results.empty:
        summary_table = filtered_results.groupby(['sector', 'industry']).size().reset_index(name='counts')
        summary_table = summary_table.sort_values(by='counts', ascending=False)
        print("\n--- Sector and Industry Summary (Filtered Stocks) ---")
        print(summary_table.to_string(index=False))
        print("-" * 50)
        
        # Get top 10 industries by count
        top_10_industries = summary_table.head(10)['industry'].tolist()
        filtered_results = filtered_results[filtered_results['industry'].isin(top_10_industries)]

    # Sort by sector as per URL parameter o=sector
    filtered_results = filtered_results.sort_values(by='sector')
    
    symbols = filtered_results['symbol'].tolist()
    print(f"Found {len(filtered_results)} matching stocks in top 10 industries. Downloading charts for top 10: {symbols}")

    if not symbols:
        print("No stocks matched the criteria.")
        return

    # 5. Download Charts
    session = setup_session()
    
    # Get top 10 rows to get symbol, sector, and industry
    download_list = filtered_results.to_dict('records')
    
    for item in tqdm(download_list):
        symbol = item['symbol']
        sector = item['sector']
        industry = item['industry']
        
        # Download weekly
        download_chart(symbol, sector, industry, "w", session)
        time.sleep(random.uniform(1.0, 2.5))
        
        # Download monthly
        download_chart(symbol, sector, industry, "m", session)
        time.sleep(random.uniform(1.0, 2.5))

    print(f"\nCharts downloaded to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
