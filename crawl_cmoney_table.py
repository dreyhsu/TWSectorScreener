import time
import pandas as pd
from io import StringIO
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_cmoney():
    url = "https://www.cmoney.tw/finance/f00016.aspx?o=1&o2=4"
    
    # Initialize Chrome with Anti-Detection features
    options = uc.ChromeOptions()
    # CMoney sometimes behaves better with a visible window, but let's try to keep it simple
    # options.add_argument('--headless') 
    
    # Use Undetected Chromedriver
    driver = uc.Chrome(options=options, version_main=144)

    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for the table with class 'tb-out' to appear
        print("Waiting for table with class 'tb-out'...")
        wait = WebDriverWait(driver, 20)
        table_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "tb-out"))
        )
        
        # Get the HTML of the table
        table_html = table_element.get_attribute('outerHTML')
        
        # Parse the table using pandas
        # Use StringIO to avoid the FutureWarning in newer pandas
        df = pd.read_html(StringIO(table_html))[0]
        
        print("DataFrame Head:")
        print(df.head())
        
        # Save to csv in data/ directory with Traditional Chinese encoding (utf-8-sig for Excel compatibility)
        df.to_csv("data/cmoney_data.csv", index=False, encoding='utf-8-sig')
        print("Data saved to data/cmoney_data.csv")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_cmoney()
