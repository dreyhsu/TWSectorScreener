from fugle_marketdata import RestClient
import time
import schedule

# 輸入您的 API Key
client = RestClient(api_key='您的_Fugle_API_Key')

def get_fugle_price():
    stock_id = '2330'
    stock = client.stock.intraday.quote(symbol=stock_id)
    
    price = stock['lastPrice'] # 最新成交價
    change = stock['change']   # 漲跌
    
    print(f"=== {time.strftime('%H:%M:%S')} ===")
    print(f"{stock_id} 台積電: {price} (漲跌: {change})")

# 設定每 3 分鐘
schedule.every(3).minutes.do(get_fugle_price)

while True:
    schedule.run_pending()
    time.sleep(1)