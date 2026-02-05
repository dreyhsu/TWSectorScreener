import pandas as pd
import yfinance as yf
import mplfinance as mpf
import os
import logging

# Suppress yfinance logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

def main():
    # Configuration
    DATA_DIR = "data/screener"
    FIG_DIR = "fig/today"
    INPUT_FILE = "data/screener_data.csv"
    
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    
    # Read input file
    try:
        df = pd.read_csv(INPUT_FILE, dtype={'代號': str})
    except FileNotFoundError:
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    if '代號' not in df.columns:
        print("Error: Column '代號' not found in input file.")
        return

    symbols = df['代號'].tolist()
    print(f"Found {len(symbols)} symbols to process.")

    for symbol in symbols:
        symbol = symbol.strip()
        if not symbol or "代號" in symbol:
            continue
            
        print(f"Processing {symbol}...")
        
        # Try TWSE first, then TPEx
        ticker_suffixes = ['.TW', '.TWO']
        data = pd.DataFrame()
        found_suffix = None
        
        for suffix in ticker_suffixes:
            ticker = f"{symbol}{suffix}"
            try:
                # Use Ticker.history to avoid "Failed download" noise from yf.download
                t = yf.Ticker(ticker)
                # auto_adjust=True is the default for history(), and avoids the FutureWarning from download()
                temp_data = t.history(period="5d", interval="30m")
                
                if not temp_data.empty:
                    # Check if data is actually valid
                    if len(temp_data) > 0:
                        data = temp_data
                        found_suffix = suffix
                        break
            except Exception:
                # Suppress errors for invalid suffixes
                continue
        
        if data.empty:
            print(f"  No data found for {symbol} (tried .TW and .TWO)")
            continue

        # Handle MultiIndex columns if present (yfinance specific)
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten columns. Usually Level 0 is 'Price' (Open, High, etc.) and Level 1 is Ticker
            # We want Level 0.
            try:
                data.columns = data.columns.get_level_values(0)
            except IndexError:
                pass

        # Ensure we have required columns for mplfinance
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
             print(f"  Missing required columns for {symbol}. Columns found: {data.columns}")
             continue

        # Ensure numeric types
        for col in required_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Drop rows with NaN in required columns
        data.dropna(subset=required_cols, inplace=True)
        
        if data.empty:
             print(f"  Data empty after cleaning for {symbol}")
             continue

        # Save to CSV
        csv_path = os.path.join(DATA_DIR, f"{symbol}_30min.csv")
        data.to_csv(csv_path)
        print(f"  Saved data to {csv_path}")
        
        # Plot
        try:
            # Filename like 8096_4_30min
            # Assuming '4' is a fixed index as per existing files in fig/today
            chart_filename = f"{symbol}_4_30min.png"
            chart_path = os.path.join(FIG_DIR, chart_filename)
            
            # Create a custom style or use 'yahoo'
            # volume=True adds volume bars
            mpf.plot(
                data, 
                type='candle', 
                style='yahoo', 
                volume=True, 
                savefig=chart_path,
                title=f"{symbol} 30min (Last 5 Days)"
            )
            print(f"  Saved chart to {chart_path}")
        except Exception as e:
            print(f"  Error plotting {symbol}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
