import os
import time
import random
import requests
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
INPUT_CSV = "data/finviz/screener_results.csv"
BASE_URL = "https://charts2-node.finviz.com/chart.ashx"
OUTPUT_DIR = "fig/finviz_holding"

# List of common User-Agents to rotate
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
        backoff_factor=2, # Increased backoff factor
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

def download_chart(symbol, timeframe, session):
    """
    Download chart for a symbol and timeframe.
    timeframe: 'w' for weekly, 'm' for monthly
    """
    filename = f"{symbol}_{timeframe}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Skip if file already exists
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
    
    # Get fresh headers for each request (or at least rotate UA)
    headers = get_headers()

    try:
        response = session.get(BASE_URL, params=params, headers=headers, timeout=20)
        
        if response.status_code == 403:
            print(f"\nBlocked (403) for {symbol} ({timeframe}). Pausing for 60 seconds...")
            time.sleep(60)
            # Try once more with a new session
            session = setup_session()
            response = session.get(BASE_URL, params=params, headers=get_headers(), timeout=20)
            
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"\nError downloading {timeframe} chart for {symbol}: {e}")
        return False

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    # Ensure output directory exists (without deleting existing files)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_time = time.time()
    try:
        df = pd.read_csv(INPUT_CSV)
        if "symbol" not in df.columns:
            print("Error: 'symbol' column not found in CSV.")
            return
            
        symbols = df["symbol"].tolist()
        symbols = [
            "ACMR", "ALAB", "AMZN", "BEAM", "BRZE", "EOSE", 
            "GDXJ", "GH", "GOOG", "MIST", "ODD", "TDY", "UUUU"
        ]
        # ["ALAB", "BEAM", "EOSE", "GH"]
        print(f"Found {len(symbols)} symbols. Starting download...")
        
        session = setup_session()
        
        for symbol in tqdm(symbols):
            # Download weekly
            download_chart(symbol, "w", session)
            # Random delay 1.5s to 3.5s
            time.sleep(random.uniform(1.5, 3.5))
            
            # Download monthly
            download_chart(symbol, "m", session)
            # Random delay 1.5s to 3.5s
            time.sleep(random.uniform(1.5, 3.5))
            
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\nDownload complete! Total time taken: {elapsed_time:.2f} seconds")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()