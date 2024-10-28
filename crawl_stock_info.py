import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_stock_info(stock_id, driver=None):
    url = f"https://goodinfo.tw/tw/BasicInfo.asp?STOCK_ID={stock_id}"
    
    # Set up the Selenium Edge WebDriver if driver is None
    if driver is None:
        driver_path = r'driver\edgedriver_win32\msedgedriver.exe'
        # Set up Edge options
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Instantiate the Edge WebDriver with the service and options
        service = Service(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)
        driver_started = True
    else:
        driver_started = False

    try:
        # Open the URL and wait for the page to load
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # Get page source after JavaScript has executed
        page_source = driver.page_source
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the target table by class name
        target_table = soup.find('table', class_='b0v1h1 p4_6', width='100%')

        if not target_table:
            print(f"Target table not found for stock {stock_id}")
            return None

        # Extract the required information from the target table
        rows = target_table.find_all('tr')
        data = []
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            cell_values = [cell.get_text(strip=True) for cell in cells]
            data.append(cell_values)

        # Create a DataFrame with specific columns: 股票代號, 產業別, 主要業務
        stock_id_value = None
        industry_type = None
        main_service = None
        
        for row in data:
            if '股票代號' in row:
                idx = row.index('股票代號')
                if idx + 1 < len(row):
                    stock_id_value = row[idx + 1]
            if '產業別' in row:
                idx = row.index('產業別')
                if idx + 1 < len(row):
                    industry_type = row[idx + 1]
            if '主要業務' in row:
                idx = row.index('主要業務')
                if idx + 1 < len(row):
                    main_service = row[idx + 1]

        df = pd.DataFrame([{
            '股票代號': stock_id_value,
            '產業別': industry_type,
            '主要業務': main_service
        }])
        
        # Return the DataFrame
        return df

    except Exception as e:
        print(f"Error fetching stock info for {stock_id}: {e}")
        return None
    finally:
        if driver_started:
            driver.quit()

if __name__ == "__main__":
    stock_id = "2330"
    stock_info = get_stock_info(stock_id)
    print(stock_info)
