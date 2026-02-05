import requests
import pandas as pd
import os
import urllib3
from wearn_downloader import download_stock_charts

# Suppress only the single warning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Define the URL
url = "https://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZG_BD.djhtm"

# 2. Set headers to mimic a browser (optional but recommended)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def delete_files_in_folder(folder_path):
    """Clear files in the specified folder"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

try:
    # 3. Fetch the page content
    res = requests.get(url, headers=headers, verify=False)
    
    # 4. Handle Encoding (Crucial for this site)
    # The default auto-detection might fail, so we force Big5
    res.encoding = 'big5'
    
    # 5. Parse the HTML using Pandas
    # We use the 'attrs' parameter to specifically look for id="oMainTable"
    dfs = pd.read_html(res.text, attrs={'id': 'oMainTable'}, header=1)
    
    if dfs:
        # pd.read_html returns a list of dataframes, usually the first one is our target
        df = dfs[0]
        df['代號'] = df['股票名稱'].str.extract(r'^([A-Za-z0-9]+)')
        df['股票名稱'] = df['股票名稱'].str.replace(r'^[A-Za-z0-9]+\s*', '', regex=True)
        cols = ['代號', '股票名稱', '收盤價', '漲跌', '漲跌幅', '成交量', '週轉率']
        df = df[cols]
        # 6. Basic Data Cleanup (Optional)
        # Sometimes the header is repeated in the first row, you can reset it if needed
        # df.columns = df.iloc[0] 
        # df = df[1:]
        
        print("Data successfully crawled:")
        print(df.head())
        
        # Save to CSV if needed
        df.to_csv("fubon_turnover_rank.csv", index=False, encoding='utf-8-sig')

        # Download charts
        folder_path = os.path.join('fig', 'turn_over_tw')
        print(f"Cleaning folder: {folder_path}")
        delete_files_in_folder(folder_path)
        
        print(f"Downloading charts for {len(df)} stocks...")
        for _, row in df.iterrows():
            stock_id = str(row['代號'])
            download_stock_charts(stock_id, folder_path)
            
        print("Charts download complete.")
    else:
        print("Table 'oMainTable' not found.")

except Exception as e:
    print(f"An error occurred: {e}")
