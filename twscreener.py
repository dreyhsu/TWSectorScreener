from crawl_goodinfo_chrome import selenium_crawl
# from snapshot_goodinfo_canvas import snapshot_canvas
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
    url_breakout = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=MACD%7C%7CDIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0%40%40%E6%97%A5MACD%E8%90%BD%E9%BB%9E%40%40DIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0&FL_RULE1=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE2=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A820%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%4020%E6%97%A5%E7%B7%9A&FL_RULE3=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%8D%8A%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E5%8D%8A%E5%B9%B4&FL_RULE4=RSI%7C%7C%E6%97%A5RSI6%E4%BB%8B%E6%96%BC50%7E80%40%40%E6%97%A5RSI%E8%90%BD%E9%BB%9E%40%40RSI6%E4%BB%8B%E6%96%BC50%7E80&FL_RULE5=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C20%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%4020%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    url_momentum_trade = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C100%E6%97%A5%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40100%E6%97%A5%E7%B7%9A&FL_RULE1=MACD%7C%7C%E9%80%B1MACD+%E2%86%97%40%40%E9%80%B1MACD%E8%B5%B0%E5%8B%A2%40%40MACD+%E2%86%97&FL_RULE2=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E6%BC%B25%25%E8%82%A1&FL_RULE3=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A85%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%405%E6%97%A5%E7%B7%9A&FL_RULE4=K%E7%B7%9A%E5%9E%8B%E6%85%8B%7C%7C%E6%97%A5K%E7%B7%9A%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E2%80%93%E6%97%A5K%E7%B7%9A%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83%2F%E8%88%88%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    url_half_year_new_high = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=自訂篩選&INDUSTRY_CAT=我的條件&FL_ITEM0=成交價創近期新高%2F新低–還原權值–創近n月新高&FL_VAL_S0=6&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=&FL_RULE1=&FL_RULE2=&FL_RULE3=&FL_RULE4=&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=年獲利能力&FL_SHEET2=獲利能力&FL_MARKET=上市%2F上櫃%2F興櫃&FL_QRY=查++詢'
    url_foreign = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=自訂篩選&INDUSTRY_CAT=我的條件&FL_ITEM0=法人連買日數–外資&FL_VAL_S0=3&FL_VAL_E0=&FL_ITEM1=漲跌幅+%28%25%29&FL_VAL_S1=3&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=均線位置%7C%7C100日線向上走揚%40%40均價線向上走揚%40%40100日線&FL_RULE1=MACD%7C%7C週MACD+↗%40%40週MACD走勢%40%40MACD+↗&FL_RULE2=&FL_RULE3=均線位置%7C%7C成交量在5日線之上%40%40成交量在均量線之上%40%405日線&FL_RULE4=交易狀況%7C%7C上漲股&FL_RULE5=法人買賣%7C%7C外資連買+–+週%40%40外資連續買超%40%40外資連續買超+–+週&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=交易狀況&FL_SHEET2=日&FL_MARKET=上市%2F上櫃%2F興櫃&FL_QRY=查++詢'
    # df1 = selenium_crawl(url_foreign)
    screener_df = selenium_crawl(url_half_year_new_high)
    # screener_df = pd.concat([df1, df2], ignore_index=True)

    # screener_df = pd.read_pickle('data/screener_data.pkl')
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
    screener_df = screener_df.drop_duplicates(subset=['代號'])
    print(f"Downloading charts for {len(screener_df)} stocks from today's screener to fig/today/...")
    
    for _, row in screener_df.iterrows():
        # Convert to string first to handle numeric types
        stock_id = str(row['代號']).strip()
        
        # Check if the length is exactly 4
        if len(stock_id) == 4:
            print(f"Downloading: {stock_id}")
            download_stock_charts(stock_id, 'fig/today')

    # Filter tracked list for pullbacks
    filtered_tracked_df = manager.process_and_filter_tracked_stocks(tracked_df)

    # Download charts for filtered tracked list
    print(f"Downloading charts for {len(filtered_tracked_df)} filtered stocks to fig/filter/...")
    for _, row in filtered_tracked_df.iterrows():
        stock_id = str(row['stock_id'])
        download_stock_charts(stock_id, 'fig/filter')
        # snapshot_canvas(stock_id, 'fig/filter')
    
    # Download charts for holdings
    print("Processing holdings...")
    holdings = load_holdings()
    if holdings:
        print(f"Downloading charts for {len(holdings)} holdings to fig/holdings/...")
        holdings_folder = os.path.join(fig_folder_path, 'holdings')
        for stock_id in holdings:
            download_stock_charts(stock_id, holdings_folder)
            # snapshot_canvas(stock_id, holdings_folder)
    else:
        print("No holdings found in config.")

    # 6. Save updated master list
    tracked_df.to_csv(TRACKED_FILE, index=False, encoding='utf-8-sig')
    print(f"Finished. Tracked list saved to {TRACKED_FILE}.")
    print("Charts saved in 'fig/filter/' (pullbacks), 'fig/today/' (daily screen results), and 'fig/holdings/'.")

    # 7. Additional processing
    # print("Fetching 30-minute data and analyzing themes...")
    # fetch_30min()
    analyze_themes()

if __name__ == '__main__':
    twscreener()
