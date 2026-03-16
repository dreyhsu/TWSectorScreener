import os
import json
import time
import random
import requests
import shutil
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from openbb import obb

# Configuration
OUTPUT_DIR = "fig/finviz_holding"
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
            print(f"Blocked (403) for {symbol} ({timeframe}). Pausing for 60 seconds...")
            time.sleep(60)
            session = setup_session()
            response = session.get(BASE_URL, params=params, headers=get_headers(), timeout=20)
            
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"Error downloading {timeframe} chart for {symbol}: {e}")
        return False

def main():
    # Load holdings
    if not os.path.exists("us_holding.json"):
        print("Error: us_holding.json not found.")
        return

    with open("us_holding.json", "r") as f:
        data = json.load(f)
    
    symbols = data.get("holdings", [])
    if not symbols:
        print("No symbols found in us_holding.json")
        return

    # Clear output directory
    if os.path.exists(OUTPUT_DIR):
        print(f"Clearing directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Fetching profiles and downloading charts for {len(symbols)} holdings...")
    session = setup_session()

    for symbol in tqdm(symbols):
        # Fetch sector and industry info
        try:
            profile = obb.equity.profile(symbol=symbol, provider='yfinance').to_df()
            if not profile.empty:
                sector = profile['sector'][0] if 'sector' in profile.columns else "Other"
                industry = profile['industry'][0] if 'industry' in profile.columns else "Other"
            else:
                sector, industry = "Other", "Other"
        except Exception:
            sector, industry = "Other", "Other"

        # Download daily
        download_chart(symbol, sector, industry, "d", session)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Download weekly
        download_chart(symbol, sector, industry, "w", session)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Download monthly
        download_chart(symbol, sector, industry, "m", session)
        time.sleep(random.uniform(1.0, 2.0))

    print(f"Charts downloaded to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
