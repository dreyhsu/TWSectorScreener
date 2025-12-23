from crawl_goodinfo_chrome import selenium_crawl
from finmind_data_download import finmind_data_download
import pandas as pd
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.safari.options import Options

fig_folder_path = r'fig'
TRACKED_FILE = 'data/tracked_stocks.csv'

def delete_files_in_fig_folder():
    """Clear old pullback charts in the main fig folder"""
    if not os.path.exists(fig_folder_path):
        os.makedirs(fig_folder_path)
    file_list = os.listdir(fig_folder_path)
    for file in file_list:
        # Only delete files, not directories like 'today'
        file_path = os.path.join(fig_folder_path, file)
        if os.path.isfile(file_path) and file.endswith(".png"):
            os.remove(file_path)

def delete_files_in_today_folder():
    """Clear charts in fig/today folder"""
    today_folder = os.path.join(fig_folder_path, 'today')
    if not os.path.exists(today_folder):
        os.makedirs(today_folder)
    for file in os.listdir(today_folder):
        file_path = os.path.join(today_folder, file)
        if os.path.isfile(file_path) and file.endswith(".png"):
            os.remove(file_path)

def load_or_create_tracked_list():
    """Load the master tracking file or create empty if not exists"""
    if os.path.exists(TRACKED_FILE):
        df = pd.read_csv(TRACKED_FILE)
        df['add_date'] = pd.to_datetime(df['add_date'])
        df['stock_id'] = df['stock_id'].astype(str).apply(lambda x: x.zfill(4) if x.isdigit() else x)
        return df
    else:
        return pd.DataFrame(columns=['stock_id', 'name', 'add_date', 'initial_open'])

def twscreener():
    # 1. Setup and Cleanup
    delete_files_in_fig_folder()
    delete_files_in_today_folder()
    
    # 2. Run Crawl
    # options = Options()
    # driver = webdriver.Safari(options=options)
    # try:
    print("Fetching screener list...")
    # selenium_crawl()
    
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

    # 5. Process Data: Plot today's picks AND analyze tracked list for pullbacks
    print("Processing data...")
    # Pass both the long-term tracked list AND today's specific list
    final_tracked_df = finmind_data_download(tracked_df, screener_df)
    
    # 6. Save updated master list
    final_tracked_df.to_csv(TRACKED_FILE, index=False, encoding='utf-8-sig')
    print(f"Finished. Tracked list saved to {TRACKED_FILE}.")
    print("Charts saved in 'fig/' (pullbacks) and 'fig/today/' (daily screen results).")

if __name__ == '__main__':
    twscreener()