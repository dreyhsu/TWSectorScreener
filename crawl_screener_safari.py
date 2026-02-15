import time
import random
import traceback
import pandas as pd
from io import StringIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def selenium_crawl(driver=None):
    # --- URL DEFINITIONS ---
    url_breakout = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=MACD%7C%7CDIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0%40%40%E6%97%A5MACD%E8%90%BD%E9%BB%9E%40%40DIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0&FL_RULE1=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE2=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A820%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%4020%E6%97%A5%E7%B7%9A&FL_RULE3=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%8D%8A%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E5%8D%8A%E5%B9%B4&FL_RULE4=RSI%7C%7C%E6%97%A5RSI6%E4%BB%8B%E6%96%BC50%7E80%40%40%E6%97%A5RSI%E8%90%BD%E9%BB%9E%40%40RSI6%E4%BB%8B%E6%96%BC50%7E80&FL_RULE5=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C20%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%4020%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    url_momentum_trade = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C100%E6%97%A5%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%90%91%E4%B8%8A%E8%B5%B0%E6%8F%9A%40%40100%E6%97%A5%E7%B7%9A&FL_RULE1=MACD%7C%7C%E9%80%B1MACD+%E2%86%97%40%40%E9%80%B1MACD%E8%B5%B0%E5%8B%A2%40%40MACD+%E2%86%97&FL_RULE2=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E6%BC%B25%25%E8%82%A1&FL_RULE3=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A85%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%405%E6%97%A5%E7%B7%9A&FL_RULE4=K%E7%B7%9A%E5%9E%8B%E6%85%8B%7C%7C%E6%97%A5K%E7%B7%9A%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E2%80%93%E6%97%A5K%E7%B7%9A%40%40%E8%B7%B3%E7%A9%BA%E4%B8%8A%E6%BC%B2%E6%94%B6%E7%B4%85K&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83%2F%E8%88%88%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    
    url = url_momentum_trade

    try:
        # --- 1. COOKIE WARM-UP (Bypassing Anti-Scraping) ---
        # Goodinfo blocks direct access if you have no cookies.
        # We visit the homepage first to establish a session.
        print("Initiating anti-scraping bypass (Cookie Warm-up)...")
        driver.get("https://goodinfo.tw/tw/index.asp")
        
        # Random sleep to look like a human reading the homepage
        sleep_time = random.uniform(5, 8)
        print(f"Waiting {sleep_time:.2f} seconds to establish session...")
        time.sleep(sleep_time)
        
        # --- 2. NAVIGATE TO TARGET URL ---
        print(f"Navigating to target screener: {url}")
        driver.get(url)

        # --- 3. AD BLOCKING HANDLING ---
        print("Checking for ads...")
        time.sleep(3) # Wait for ad animation

        # Strategy A: Primary - Click the specific button ID from your screenshot
        try:
            close_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "ats-interstitial-button"))
            )
            close_btn.click()
            print("Ad closed via ID: ats-interstitial-button")
            time.sleep(1.5)
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
        
        # --- 4. EXTRACT TABLE ---
        print("Waiting for stock table to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'tblStockList'))
        )

        table = driver.find_element(By.ID, 'tblStockList')
        
        # Pandas read_html needs string input
        table_html = table.get_attribute('outerHTML')
        df = pd.read_html(StringIO(table_html), flavor='bs4')[0]

        # Display and Save
        df.to_pickle('data/screener_data.pkl')
        print("\nData successfully saved to 'data/screener_data.pkl'")
        print(df.tail())

    except Exception as e:
        print(f"\n[Error] An error occurred during selenium_crawl: {e}")
        traceback.print_exc()    
    return 0

if __name__ == '__main__':
    # Initialize Safari
    # Note: Ensure "Allow Remote Automation" is enabled in Safari > Develop Menu
    print("Launching Safari Driver...")
    driver = webdriver.Safari()
    driver.maximize_window() # Fullscreen helps avoid layout issues

    try:
        selenium_crawl(driver=driver)
    finally:
        # Close the browser after 5 seconds so you can see the result briefly
        time.sleep(5)
        driver.quit()
        print("Browser closed.")