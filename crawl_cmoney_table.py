import time
import os
import shutil
import pandas as pd
from io import StringIO
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wearn_downloader import download_stock_charts

def crawl_cmoney():
    url = "https://www.cmoney.tw/finance/f00016.aspx?o=1&o2=4"
    
    # Initialize Chrome with Anti-Detection features
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
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

        # --- Implement "Up Middle" Strategy ---
        print("\n--- Applying 'Up Middle' Strategy ---")
        
        # 1. Clean data: Remove '%' and convert to float
        df['一月(%)_val'] = pd.to_numeric(df['一月(%)'].astype(str).str.replace('%', ''), errors='coerce')
        df['一季(%)_val'] = pd.to_numeric(df['一季(%)'].astype(str).str.replace('%', ''), errors='coerce')
        
        # 2. Filter: 1-Month > 0 AND 3-Month > 0
        qualified_df = df[
            (df['一月(%)_val'] > 0) & 
            (df['一季(%)_val'] > 0)
        ].copy()
        
        print(f"Qualified sectors (Positive 1M & 3M): {len(qualified_df)}")
        
        # 3. Rank: Sort by 3-Month performance (descending)
        ranked_df = qualified_df.sort_values(by='一季(%)_val', ascending=False).reset_index(drop=True)
        
        # 4. Select Middle 33%
        n = len(ranked_df)
        if n > 0:
            start_idx = int(n * 0.33)
            end_idx = int(n * 0.66)
            
            # Ensure we select at least one if possible, or handle small lists
            if start_idx == end_idx and n > 0:
                 # If list is small (e.g. 1 or 2 items), the logic might give empty range.
                 # Let's just take the middle element or the whole list if very small.
                 # For strict adherence to "middle 33%", if n < 3, it might be 0.
                 # Let's apply a minimum of 1 sector if n >= 1
                 mid_point = n // 2
                 selected_df = ranked_df.iloc[mid_point:mid_point+1]
            else:
                 selected_df = ranked_df.iloc[start_idx:end_idx]
            
            print(f"Selected {len(selected_df)} sectors (Middle 33% of {n}):")
            print(selected_df[['分類', '一月(%)', '一季(%)']])
            
            target_sectors = selected_df['分類'].tolist()
        else:
            print("No sectors qualified.")
            target_sectors = []

        symbol_sector_map = {}

        if target_sectors:
            print(f"\n--- Extracting Symbols from {len(target_sectors)} Sectors ---")
            
            # Store original window handle
            original_window = driver.current_window_handle
            
            for sector_name in target_sectors:
                try:
                    print(f"\nProcessing Sector: {sector_name}")
                    
                    # Find link by Link Text (exact match preferred, or partial)
                    # We need to find the link within the main table again in case DOM changed or scrolling needed
                    # But since we are not reloading the main page, element references might be stale if we navigated away.
                    # Best practice: Re-find the element on the main page.
                    
                    # Ensure we are on the main window
                    if driver.current_window_handle != original_window:
                        driver.switch_to.window(original_window)
                    
                    # Re-locate table or search for link directly
                    # Using partial link text might be safer if there are extra spaces
                    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, sector_name)))
                    
                    print(f"Clicking on link: {sector_name}")
                    
                    # Capture existing windows
                    existing_windows = set(driver.window_handles)
                    
                    # JavaScript click to bypass overlays
                    driver.execute_script("arguments[0].click();", link)
                    
                    # Wait for new window
                    time.sleep(2)
                    current_windows = set(driver.window_handles)
                    new_windows = current_windows - existing_windows
                    
                    target_window = None
                    is_new_window = False
                    
                    if new_windows:
                        target_window = new_windows.pop()
                        is_new_window = True
                        driver.switch_to.window(target_window)
                        print(f"Switched to new window for {sector_name}")
                    else:
                        print(f"No new window for {sector_name}. Assuming navigation in same window.")
                        target_window = driver.current_window_handle
                    
                    # --- Extraction Logic (Unified) ---
                    try:
                        # Wait for the target div 'tb-wrap tb-wrap1'
                        target_div = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.tb-wrap.tb-wrap1"))
                        )
                        
                        # Parse tables
                        div_html = target_div.get_attribute('outerHTML')
                        sub_dfs = pd.read_html(StringIO(div_html))
                        
                        print(f"Found {len(sub_dfs)} tables.")
                        
                        sector_symbols = set()
                        for sub_df in sub_dfs:
                            if '股票' in sub_df.columns:
                                # Extract symbol (assumes format "2330 台積電")
                                symbols = sub_df['股票'].astype(str).apply(lambda x: x.split()[0] if ' ' in x else x)
                                current_sector_symbols = symbols.tolist()
                                sector_symbols.update(current_sector_symbols)
                                
                                # Map symbol to sector
                                for sym in current_sector_symbols:
                                    if sym not in symbol_sector_map:
                                        symbol_sector_map[sym] = sector_name
                        
                        print(f"Extracted {len(sector_symbols)} unique symbols: {sorted(list(sector_symbols))}")
                        
                    except Exception as e:
                        print(f"Error extracting tables for {sector_name}: {e}")
                    
                    # --- Cleanup ---
                    if is_new_window:
                        driver.close()
                        driver.switch_to.window(original_window)
                    else:
                        # If we navigated in the same window, go back
                        if driver.current_url != url:
                            print("Navigating back to main list...")
                            driver.back()
                            # Wait for main table to reload
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "tb-out"))
                            )
                    
                    time.sleep(1) # Brief pause
                
                except Exception as e:
                    print(f"Error processing sector {sector_name}: {e}")
                    # Try to recover state
                    if driver.current_window_handle != original_window:
                         driver.close()
                         driver.switch_to.window(original_window)

            print("\n--- Final Consolidated Symbol List ---")
            sorted_symbols = sorted(list(symbol_sector_map.keys()))
            print(f"Total Unique Symbols: {len(sorted_symbols)}")
            print(sorted_symbols)
            
            # Save symbols to file
            with open("data/up_middle_symbols.txt", "w", encoding='utf-8') as f:
                for s in sorted_symbols:
                    f.write(f"{s}\n")
            print("Symbols saved to data/up_middle_symbols.txt")

            # --- Download Charts ---
            output_folder = "fig/cmoney_industry"
            print(f"\n--- Downloading Charts to {output_folder} ---")
            
            # Clean folder
            if os.path.exists(output_folder):
                print(f"Cleaning existing files in {output_folder}...")
                shutil.rmtree(output_folder)
            os.makedirs(output_folder, exist_ok=True)
            
            print(f"Downloading charts for {len(sorted_symbols)} symbols...")
            count = 0
            for symbol in sorted_symbols:
                sector = symbol_sector_map.get(symbol, "Unknown")
                # Clean sector name for filename
                safe_sector = "".join([c for c in sector if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
                prefix = f"{safe_sector}_"
                
                count += 1
                try:
                    # print(f"Processing {symbol} ({count}/{len(sorted_symbols)})...")
                    download_stock_charts(symbol, output_folder, prefix=prefix)
                except Exception as e:
                    print(f"Failed to download charts for {symbol}: {e}")
                
                if count % 10 == 0:
                    print(f"Downloaded {count}/{len(sorted_symbols)} symbols...")
            
            print("All downloads completed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_cmoney()
