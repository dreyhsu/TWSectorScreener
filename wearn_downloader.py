import os
import requests
import time

def download_image(url, save_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def download_stock_charts(stock_id, folder):
    """
    Downloads Daily, Weekly, and Monthly charts for a given stock_id into the specified folder.
    """
    # Ensure folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    base_urls = {
        '1_monthly': f"https://stock.wearn.com/finance_mchart.asp?stockid={stock_id}&timekind=2&timeblock=2&sma1=&sma2=&sma3=&volume=0&indicator1=Vol&indicator2=None&indicator3=OBV",
        '2_weekly': f"https://stock.wearn.com/finance_wchart.asp?stockid={stock_id}&timekind=1&timeblock=3&sma1=&sma2=&sma3=&volume=0&indicator1=Vol&indicator2=None&indicator3=OBV",
        '3_daily': f"https://stock.wearn.com/finance_chart.asp?stockid={stock_id}&timekind=0&timeblock=270&sma1=&sma2=&sma3=&volume=0&indicator1=Vol&indicator2=None&indicator3=OBV"
    }

    for timeframe, url in base_urls.items():
        filename = f"{stock_id}_{timeframe}.png"
        save_path = os.path.join(folder, filename)
        # print(f"Downloading {timeframe} chart for {stock_id}...")
        download_image(url, save_path)
        time.sleep(0.5) # Be polite to the server
