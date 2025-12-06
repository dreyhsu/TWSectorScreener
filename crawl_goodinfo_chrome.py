import pandas as pd
from io import StringIO
import traceback
import time
import os

# Import undetected_chromedriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def selenium_crawl(driver=None):
    # Use your URL (truncated for brevity, ensure you use the full URL from your code)
    url_1year_high = 'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=%E6%88%90%E4%BA%A4%E9%87%91%E9%A1%8D+%28%E7%99%BE%E8%90%AC%29&FL_VAL_S0=10&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE1=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E5%89%B5%E4%B8%80%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E5%89%B5%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E4%B8%80%E5%B9%B4&FL_RULE2=&FL_RULE3=&FL_RULE4=&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    
    url = url_1year_high
    
    try:
        driver.get(url)

        # Anti-detection: Sometimes a random small sleep helps Goodinfo process the header
        time.sleep(3) 

        # Wait for the JavaScript to fetch and display the table
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'tblStockList'))
        )

        # Once the table is present, locate it
        table = driver.find_element(By.ID, 'tblStockList')

        # Parse the table using pandas
        table_html = table.get_attribute('outerHTML')
        df = pd.read_html(StringIO(table_html), flavor='bs4')[0]

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Display the DataFrame
        df.to_pickle('data/screener_data.pkl')
        print("Data scraped successfully!")
        print(df.head())

    except Exception as e:
        print(f"An error occurred during selenium_crawl: {e}")
        traceback.print_exc()    
        
    return 0

def get_headless_driver():
    """
    Creates an undetected chrome driver optimized for headless server environments.
    """
    options = uc.ChromeOptions()
    
    # IMPORTANT: The '--headless=new' flag is much better than the old '--headless'
    # It renders the page more accurately and is harder to detect.
    options.add_argument('--headless=new') 
    
    # Essential for running as root/admin on Linux servers
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Set a window size so elements are rendered correctly
    options.add_argument('--window-size=1920,1080')
    
    # Initialize the driver
    # version_main allows you to specify a version if auto-detection fails
    driver = uc.Chrome(options=options)
    
    return driver

if __name__ == '__main__':
    driver = None
    try:
        print("Initializing Headless Chrome...")
        driver = get_headless_driver()
        
        selenium_crawl(driver=driver)
        
    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        if driver:
            print("Closing driver...")
            driver.quit()