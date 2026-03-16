import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def snapshot_canvas(stock_id, output_dir='fig/today'):
    # Target URL
    url = f'https://goodinfo.tw/tw/ShowBuySaleChart.asp?STOCK_ID={stock_id}&CHT_CAT=DATE&PRICE_ADJ=T&SCROLL2Y=483'
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, f'{stock_id}_5_foreign.png')

    # Initialize Chrome with Anti-Detection features
    options = uc.ChromeOptions()
    options.headless = False # Goodinfo often detects headless
    options.add_argument('--no-first-run')
    
    # Use Undetected Chromedriver (Auto-detect version)
    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"Failed to initialize driver: {e}")
        return

    try:
        driver.maximize_window()

        # 1. Go to target
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # 2. Handle Ad (Using logic from crawl_goodinfo_chrome.py)
        print("Checking for ads...")
        time.sleep(10) # Wait for ad animation

        try:
            # Strategy A: Primary - Click the specific button ID
            WebDriverWait(driver, 10).until(
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

        # 3. Wait for Canvas and take snapshot
        print("Waiting for StockCanvas element...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'StockCanvas'))
        )
        
        canvas = driver.find_element(By.ID, 'StockCanvas')
        
        # Scroll to the element to ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", canvas)
        time.sleep(2) # Give it a moment to stabilize after scroll
        
        # Take screenshot of the element
        canvas.screenshot(output_path)
        print(f"Snapshot saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    snapshot_canvas('5386')
