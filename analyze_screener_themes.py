import pandas as pd
import ast
import os
import shutil
import glob
from datetime import datetime

def calculate_trade_money(symbol):
    """
    Calculates trade money for a given symbol using 30-min data.
    Trade Money = (Avg of OHLC for the last date) * (Sum of Volume for the last date)
    Returns 0 if data not found or empty.
    """
    file_path = f'data/screener/{symbol}_30min.csv'
    if not os.path.exists(file_path):
        return 0.0
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return 0.0
        
        # Parse Datetime
        # Assuming format like '2026-01-26 01:00:00+00:00'
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        
        # Get the last date
        last_dt = df['Datetime'].max()
        last_date = last_dt.date()
        
        # Filter for the last date
        day_df = df[df['Datetime'].dt.date == last_date].copy()
        
        if day_df.empty:
            return 0.0
        
        # Calculate Average Price (OHLC average)
        # Using (Open + High + Low + Close) / 4
        # We take the mean of these averages for the day?
        # Or (Mean(Open) + Mean(High)...) / 4?
        # User said "average ohcl", usually implies the average price of the bar.
        # Let's calculate typical price per bar, then average it for the day.
        day_df['avg_price'] = (day_df['Open'] + day_df['High'] + day_df['Low'] + day_df['Close']) / 4.0
        daily_avg_price = day_df['avg_price'].mean()
        
        # Sum of Volume
        daily_volume = day_df['Volume'].sum()
        
        # Trade Money
        trade_money = daily_avg_price * daily_volume
        
        return trade_money
        
    except Exception as e:
        print(f"Error calculating trade money for {symbol}: {e}")
        return 0.0

def organize_images(df):
    """
    Organizes images in 'fig/today' into subdirectories based on industry counts and names.
    Copies images to new folders and renames them with rank based on trade money.
    """
    source_root = 'fig/today'
    if not os.path.exists(source_root):
        print(f"Directory {source_root} does not exist.")
        return

    # Get unique industries
    industries = df['detail_industry'].unique()
    
    print(f"Organizing and sorting images for {len(industries)} industries...")

    for industry in industries:
        # Get symbols for this industry
        industry_rows = df[df['detail_industry'] == industry]
        count = industry_rows.iloc[0]['counts'] # All rows for this industry have the same count
        
        # Calculate trade money for each symbol
        symbol_stats = []
        for _, row in industry_rows.iterrows():
            symbol = row['symbol']
            tm = calculate_trade_money(symbol)
            symbol_stats.append({'symbol': symbol, 'trade_money': tm})
        
        # Sort by trade money descending
        symbol_stats.sort(key=lambda x: x['trade_money'], reverse=True)
        
        # Prepare target directory
        safe_industry = str(industry).replace(':', '_').replace('/', '_')
        folder_name = f"{count}_{safe_industry}"
        target_dir = os.path.join(source_root, folder_name)
        
        os.makedirs(target_dir, exist_ok=True)
        
        # Process each symbol in ranked order
        for rank, stat in enumerate(symbol_stats, start=1):
            symbol = stat['symbol']
            
            # Find source files
            # Search recursively in fig/today because they might have been moved in a previous run
            # Pattern: {symbol}_*.png
            # We want to avoid matching files that already have a rank prefix (e.g., 1_2408_...)
            # But standard glob {symbol}_* matches {symbol} at the start.
            # 1_2408 does NOT start with 2408. So it is safe.
            
            search_pattern = os.path.join(source_root, '**', f"{symbol}_*.png")
            files = glob.glob(search_pattern, recursive=True)
            
            if not files:
                # print(f"No images found for {symbol}")
                continue
                
            for file_path in files:
                # Skip if the file is already in the target directory AND has the correct name?
                # Actually, we just want to copy to the target with the NEW name.
                
                filename = os.path.basename(file_path)
                new_filename = f"{rank}_{filename}"
                target_path = os.path.join(target_dir, new_filename)
                
                # Check if we are copying onto itself (e.g. source is target/filename, and we rename to target/new_filename)
                # Or if we are duplicating.
                
                try:
                    shutil.copy2(file_path, target_path)
                except shutil.SameFileError:
                    # If source and dest are same, we might need to rename?
                    # But the names are different ({rank}_...).
                    # So copy2 should work (it creates a new file).
                    pass
                except Exception as e:
                    print(f"Error copying {file_path} to {target_path}: {e}")

    print("Image organization and sorting complete.")

def main():
    # File paths
    screener_path = 'data/screener_data.csv'
    theme_path = 'data/themes.csv'

    try:
        # Load data
        screener_df = pd.read_csv(screener_path, dtype={'代號': str})
        theme_df = pd.read_csv(theme_path, dtype={'stock_id': str})
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file. {e}")
        return

    # Merge
    merged_df = pd.merge(screener_df, theme_df, left_on='代號', right_on='stock_id', how='left')
    merged_df = merged_df.dropna(subset=['category'])

    # Parse category column
    try:
        merged_df['category_list'] = merged_df['category'].apply(ast.literal_eval)
    except Exception as e:
        print(f"Error parsing category column: {e}")
        return

    # Explode
    exploded_df = merged_df.explode('category_list')
    exploded_df = exploded_df.rename(columns={'category_list': 'detail_industry', '代號': 'symbol'})

    # Counts
    industry_counts = exploded_df['detail_industry'].value_counts().reset_index()
    industry_counts.columns = ['detail_industry', 'counts']

    # Merge
    result_df = pd.merge(exploded_df, industry_counts, on='detail_industry', how='left')
    final_df = result_df[['symbol', 'detail_industry', 'counts']]

    # Sort
    final_df = final_df.sort_values(by=['counts', 'detail_industry'], ascending=[False, True])

    # Output
    print(final_df.to_string(index=False))
    
    # Organize images
    organize_images(final_df)

if __name__ == "__main__":
    main()