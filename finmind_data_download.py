from FinMind.data import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import os
import time
from dotenv import load_dotenv

load_dotenv()

class StockDataManager:
    def __init__(self, api_token=None):
        self.dl = DataLoader()
        if api_token:
            self.dl.login_by_token(api_token)
        
        Path("data").mkdir(exist_ok=True)
        Path("fig").mkdir(exist_ok=True)
        Path("fig/today").mkdir(parents=True, exist_ok=True) # Ensure subfolder exists
    
    def get_vwap(self, df):
        """Calculate VWAP"""
        cum_vol = df['Trading_Volume'].cumsum()
        cum_vol[cum_vol == 0] = 1 
        df['vwap'] = (df['Trading_Volume'] * (df['max'] + df['min'] + df['close']) / 3).cumsum() / cum_vol
        return df

    def load_and_update_data(self, stock_id):
        """Load or download stock data"""
        today = datetime.now()
        start_date_str = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        file_path = f"data/{stock_id}_data.csv"
        
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            existing_data['date'] = pd.to_datetime(existing_data['date'])
            last_date = existing_data['date'].max()
            
            if last_date.date() < today.date():
                try:
                    time.sleep(0.5) # Slight delay
                    new_data = self.dl.taiwan_stock_daily(
                        stock_id=stock_id,
                        start_date=(last_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                        end_date=today.strftime('%Y-%m-%d')
                    )
                    if not new_data.empty:
                        new_data['date'] = pd.to_datetime(new_data['date'])
                        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['date']).sort_values('date')
                    else:
                        combined_data = existing_data
                except Exception as e:
                    print(f"Warning: Failed to update {stock_id}: {e}")
                    combined_data = existing_data
            else:
                combined_data = existing_data
        else:
            print(f"Downloading history for {stock_id}...")
            combined_data = self.dl.taiwan_stock_daily(
                stock_id=stock_id,
                start_date=start_date_str,
                end_date=today.strftime('%Y-%m-%d')
            )
            combined_data['date'] = pd.to_datetime(combined_data['date'])
        
        combined_data.to_csv(file_path, index=False)
        return combined_data
    
    def plot_stock_chart(self, df, stock_id, stock_name, note="", subfolder=""):
        """Create and save stock chart, optionally in a subfolder"""
        df = df.copy()
        # Calculate indicators if they don't exist
        if 'MA20' not in df.columns:
            df['MA20'] = df['close'].rolling(window=20).mean()
        if 'MA60' not in df.columns:
            df['MA60'] = df['close'].rolling(window=60).mean()
        df = self.get_vwap(df)
        
        plot_df = df.tail(60).copy()
        if plot_df.empty or len(plot_df) < 10: return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[3, 1], gridspec_kw={'hspace': 0.3})
        
        # Candlestick
        plot_df['x_pos'] = range(len(plot_df))
        up = plot_df[plot_df['close'] >= plot_df['open']]
        down = plot_df[plot_df['close'] < plot_df['open']]
        
        ax1.bar(up['x_pos'], up['close'] - up['open'], 0.6, bottom=up['open'], color='red', alpha=0.7)
        ax1.vlines(up['x_pos'], up['min'], up['max'], color='red', linewidth=1)
        ax1.bar(down['x_pos'], down['close'] - down['open'], 0.6, bottom=down['open'], color='green', alpha=0.7)
        ax1.vlines(down['x_pos'], down['min'], down['max'], color='green', linewidth=1)
        
        # Indicators
        ax1.plot(plot_df['x_pos'], plot_df['MA20'], color='orange', label='MA20')
        ax1.plot(plot_df['x_pos'], plot_df['MA60'], color='blue', label='MA60')
        ax1.plot(plot_df['x_pos'], plot_df['vwap'], color='purple', label='VWAP', linestyle='--')
        
        # Volume
        colors = ['red' if c >= o else 'green' for c, o in zip(plot_df['close'], plot_df['open'])]
        ax2.bar(plot_df['x_pos'], plot_df['Trading_Volume'], color=colors, alpha=0.7)
        
        ax1.set_title(f'{stock_id} {stock_name} - {note}')
        ax1.legend()
        ax1.set_xticks([])
        
        date_ticks = np.linspace(0, len(plot_df) - 1, 8, dtype=int)
        ax2.set_xticks(date_ticks)
        ax2.set_xticklabels([d.strftime('%Y-%m-%d') for d in plot_df['date'].iloc[date_ticks]], rotation=45)
        
        plt.tight_layout()
        
        # Determine save path based on subfolder arg
        filename = f'{stock_id}_{stock_name}_{note.replace(" ", "_")}.png'
        save_path = os.path.join('fig', subfolder, filename)
        
        plt.savefig(save_path)
        plt.close()

    def plot_screener_results(self, screener_df):
        """Plots all stocks from today's screener results into fig/today"""
        print(f"Plotting {len(screener_df)} stocks from today's screen to fig/today/...")
        for _, row in screener_df.iterrows():
            stock_id = str(row['代號'])
            stock_name = row['名稱']
            try:
                df = self.load_and_update_data(stock_id)
                if df.empty or len(df) < 60: continue # Need enough data for MA60 plot

                # Plot specifically to the 'today' subfolder
                self.plot_stock_chart(df, stock_id, stock_name, note="TodayScreen", subfolder="today")
            except Exception as e:
                 print(f"Error plotting {stock_id} for today's list: {e}")

    def process_and_filter_tracked_stocks(self, tracked_df):
        """Processes the long-term tracked list for pullbacks and removal criteria"""
        valid_indices = []
        print(f"Analyzing {len(tracked_df)} tracked stocks for pullbacks (fig/)...")
        
        for index, row in tracked_df.iterrows():
            stock_id = str(row['stock_id'])
            stock_name = row['name']
            initial_open = row['initial_open']
            
            try:
                df = self.load_and_update_data(stock_id)
                if df.empty or len(df) < 25: continue
                
                # Calculate indicators for analysis
                df['MA20'] = df['close'].rolling(window=10).mean()
                df['Vol_MA5'] = df['Trading_Volume'].rolling(window=5).mean()
                
                latest = df.iloc[-1]
                
                # Fill initial open if missing
                if pd.isna(initial_open) or initial_open == 0:
                    initial_open = latest['open']
                    tracked_df.at[index, 'initial_open'] = initial_open

                # REMOVAL LOGIC
                if latest['close'] < initial_open:
                    # print(f"Removing {stock_id}: Close < Initial Open")
                    continue
                if latest['close'] < latest['MA20']:
                    # print(f"Removing {stock_id}: Close < MA20")
                    continue
                
                valid_indices.append(index)
                
                # PULLBACK DETECTION (Volume shrink + Price near MA20)
                vol_shrink = latest['Trading_Volume'] < latest['Vol_MA5']
                dist = abs(latest['close'] - latest['MA20']) / latest['MA20']
                
                # Define "close to MA20" as within 4%
                if vol_shrink and dist < 0.04:
                    print(f"*** Pullback Found: {stock_id} ***")
                    # Save pullback charts to main fig folder (empty subfolder arg)
                    self.plot_stock_chart(df, stock_id, stock_name, "PullbackSetup", subfolder="")
            
            except Exception as e:
                print(f"Error analyzing {stock_id}: {e}")
                valid_indices.append(index)
                
        return tracked_df.loc[valid_indices].copy()

def finmind_data_download(tracked_df, screener_df=None):
    # Initialize manager (add token if you have one: api_token='YOUR_TOKEN')
    manager = StockDataManager(api_token = os.getenv('FINMIND_TOKEN'))
    
    # 1. If today's screener data is provided, plot those first into fig/today
    if screener_df is not None and not screener_df.empty:
        manager.plot_screener_results(screener_df)
        
    # 2. Process the long-term tracked list for pullbacks and create filtered list
    cleaned_tracked_df = manager.process_and_filter_tracked_stocks(tracked_df)
    
    return cleaned_tracked_df