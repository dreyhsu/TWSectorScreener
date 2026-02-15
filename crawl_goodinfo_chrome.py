import time
import random
import pandas as pd
from io import StringIO
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def selenium_crawl():
    # Your URL
    url_breakout = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=MACD%7C%7CDIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0%40%40%E6%97%A5MACD%E8%90%BD%E9%BB%9E%40%40DIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0&FL_RULE1=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE2=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A820%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%4020%E6%97%A5%E7%B7%9A&FL_RULE3=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%8D%8A%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E5%8D%8A%E5%B9%B4&FL_RULE4=RSI%7C%7C%E6%97%A5RSI6%E4%BB%8B%E6%96%BC50%7E80%40%40%E6%97%A5RSI%E8%90%BD%E9%BB%9E%40%40RSI6%E4%BB%8B%E6%96%BC50%7E80&FL_RULE5=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C20%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%4020%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    url_momentum_trade = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C100%E6%97%A5%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40100%E6%97%A5%E7%B7%9A&FL_RULE1=MACD%7C%7C%E9%80%B1MACD+%E2%86%97%40%40%E9%80%B1MACD%E8%B5%B0%E5%8B%A2%40%40MACD+%E2%86%97&FL_RULE2=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E6%BC%B25%25%E8%82%A1&FL_RULE3=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A85%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%405%E6%97%A5%E7%B7%9A&FL_RULE4=K%E7%B7%9A%E5%9E%8B%E6%85%8B%7C%7C%E6%97%A5K%E7%B7%9A%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E2%80%93%E6%97%A5K%E7%B7%9A%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83%2F%E8%88%88%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    url_half_year_new_high = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=自訂篩選&INDUSTRY_CAT=我的條件&FL_ITEM0=成交價創近期新高%2F新低–還原權值–創近n月新高&FL_VAL_S0=6&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=&FL_RULE1=&FL_RULE2=&FL_RULE3=&FL_RULE4=&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=年獲利能力&FL_SHEET2=獲利能力&FL_MARKET=上市%2F上櫃%2F興櫃&FL_QRY=查++詢'
    url = url_half_year_new_high
    # Initialize Chrome with Anti-Detection features
    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument('--no-first-run')
    
    # Use Undetected Chromedriver (Magic fix for Goodinfo)
    driver = uc.Chrome(options=options, version_main=144)

    try:
        driver.maximize_window()

        # 2. Go to target
        driver.get(url)
        
        # 3. Handle Ad (Using your ID)
        print("Checking for ads...")
        time.sleep(15) # Wait for ad animation as it often shows up with 2-3s delay

        try:
            # Strategy A: Primary - Click the specific button ID
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "ats-interstitial-button"))
            ).click()
            print("Ad closed via ID: ats-interstitial-button")
            time.sleep(1)
        except:
            # Strategy B: Backup - Press ESC key
            try:
                print("Primary ID not found, trying ESC key...")
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
            except:
                pass
            
            # Strategy C: Nuclear - Javascript removal
            try:
                print("Trying JS removal as last resort...")
                driver.execute_script("""
                    var overlays = document.querySelectorAll('div[class*="modal"], div[class*="ad"], iframe[id*="google_ads"], [id*="ats-interstitial"]');
                    overlays.forEach(function(element) { element.remove(); });
                """)
            except:
                pass

        # 4. Get Table
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'tblStockList'))
        )
        table = driver.find_element(By.ID, 'tblStockList')
        df = pd.read_html(StringIO(table.get_attribute('outerHTML')), flavor='bs4')[0]
        
        print(df.tail(10))
        df.to_pickle('data/screener_data.pkl')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    selenium_crawl()