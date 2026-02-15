from crawl_goodinfo_chrome import selenium_crawl
from wearn_downloader import download_stock_charts
from finmind_data_download import StockDataManager
from fetch_30min_data import main as fetch_30min
from analyze_screener_themes import main as analyze_themes
import pandas as pd
import os
import shutil
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.safari.options import Options

fig_folder_path = r'fig'
TRACKED_FILE = 'data/tracked_stocks.csv'
HOLDINGS_CONFIG_FILE = 'holdings.json'

def delete_files_in_filter_folder():
    """Clear old pullback charts in the fig/filter folder"""
    filter_folder = os.path.join(fig_folder_path, 'filter')
    if os.path.exists(filter_folder):
        shutil.rmtree(filter_folder)
    os.makedirs(filter_folder)

def delete_files_in_today_folder():
    """Clear charts in fig/today folder"""
    today_folder = os.path.join(fig_folder_path, 'today')
    if os.path.exists(today_folder):
        shutil.rmtree(today_folder)
    os.makedirs(today_folder)

def delete_files_in_holdings_folder():
    """Clear charts in fig/holdings folder"""
    holdings_folder = os.path.join(fig_folder_path, 'holdings')
    if os.path.exists(holdings_folder):
        shutil.rmtree(holdings_folder)
    os.makedirs(holdings_folder)

def load_or_create_tracked_list():
    """Load the master tracking file or create empty if not exists"""
    if os.path.exists(TRACKED_FILE):
        df = pd.read_csv(TRACKED_FILE)
        df['add_date'] = pd.to_datetime(df['add_date'])
        df['stock_id'] = df['stock_id'].astype(str).apply(lambda x: x.zfill(4) if x.isdigit() else x)
        return df
    else:
        return pd.DataFrame(columns=['stock_id', 'name', 'add_date', 'initial_open'])

def load_holdings():
    """Load holdings from the JSON config file."""
    if not os.path.exists(HOLDINGS_CONFIG_FILE):
        print(f"Config file {HOLDINGS_CONFIG_FILE} not found.")
        return []
    
    try:
        with open(HOLDINGS_CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get('holdings', [])
    except json.JSONDecodeError:
        print(f"Error decoding {HOLDINGS_CONFIG_FILE}. Please check the JSON format.")
        return []

def twscreener():
    # 1. Setup and Cleanup
    delete_files_in_filter_folder()
    delete_files_in_today_folder()
    delete_files_in_holdings_folder()
    
    # 2. Run Crawl
    # options = Options()
    # driver = webdriver.Safari(options=options)
    # try:
    print("Fetching screener list...")
    selenium_crawl()
    
    screener_df = pd.read_pickle('data/screener_data.pkl')
    screener_df['代號'] = screener_df['代號'].astype(str).apply(lambda x: '00' + x if len(x) < 4 else x)

    # Save today's raw screener data to CSV
    daily_csv_name = f'data/screener_data.csv'
    screener_df.to_csv(daily_csv_name, index=False, encoding='utf-8-sig')
    print(f"Saved daily screener dump to {daily_csv_name}")

    # finally:
    #     driver.quit()

    # 3. Manage Tracked List (Accumulate history)
    print("Updating tracked stock list...")
    tracked_df = load_or_create_tracked_list()
    today = datetime.now()
    
    new_entries = []
    existing_ids = tracked_df['stock_id'].astype(str).tolist()
    
    for _, row in screener_df.iterrows():
        stock_id = str(row['代號'])
        stock_name = row['名稱']
        
        if stock_id not in existing_ids:
            new_entries.append({
                'stock_id': stock_id,
                'name': stock_name,
                'add_date': today,
                'initial_open': None
            })
            print(f"New stock added to watchlist: {stock_id} {stock_name}")
    
    if new_entries:
        new_df = pd.DataFrame(new_entries)
        tracked_df = pd.concat([tracked_df, new_df], ignore_index=True)

    # 4. Remove stocks older than 20 days
    cutoff_date = today - timedelta(days=20)
    original_count = len(tracked_df)
    tracked_df = tracked_df[tracked_df['add_date'] >= cutoff_date]
    if len(tracked_df) < original_count:
        print(f"Dropped {original_count - len(tracked_df)} stocks older than 20 days.")

    # 5. Process Data: Filter stocks and download charts
    print("Processing data...")
    
    # Initialize StockDataManager
    manager = StockDataManager(api_token=os.getenv('FINMIND_TOKEN'))
    
    # Download charts for today's screener results
    print(f"Downloading charts for {len(screener_df)} stocks from today's screener to fig/today/...")
    for _, row in screener_df.iterrows():
        stock_id = str(row['代號'])
        download_stock_charts(stock_id, 'fig/today')

    # Filter tracked list for pullbacks
    filtered_tracked_df = manager.process_and_filter_tracked_stocks(tracked_df)

    # Download charts for filtered tracked list
    print(f"Downloading charts for {len(filtered_tracked_df)} filtered stocks to fig/filter/...")
    for _, row in filtered_tracked_df.iterrows():
        stock_id = str(row['stock_id'])
        download_stock_charts(stock_id, 'fig/filter')
    
    # Download charts for holdings
    print("Processing holdings...")
    holdings = load_holdings()
    if holdings:
        print(f"Downloading charts for {len(holdings)} holdings to fig/holdings/...")
        holdings_folder = os.path.join(fig_folder_path, 'holdings')
        for stock_id in holdings:
            download_stock_charts(stock_id, holdings_folder)
    else:
        print("No holdings found in config.")

    # 6. Save updated master list
    tracked_df.to_csv(TRACKED_FILE, index=False, encoding='utf-8-sig')
    print(f"Finished. Tracked list saved to {TRACKED_FILE}.")
    print("Charts saved in 'fig/filter/' (pullbacks), 'fig/today/' (daily screen results), and 'fig/holdings/'.")

    # 7. Additional processing
    print("Fetching 30-minute data and analyzing themes...")
    fetch_30min()
    analyze_themes()

if __name__ == '__main__':
    twscreener()
