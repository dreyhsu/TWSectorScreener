from FinMind.data import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import os

class StockDataManager:
    def __init__(self, api_token=None):
        self.dl = DataLoader()
        if api_token:
            self.dl.login_by_token(api_token)
        
        # Create necessary directories
        Path("data").mkdir(exist_ok=True)
        Path("fig").mkdir(exist_ok=True)
    
    def get_vwap(self, df):
        """Calculate VWAP for the trading day/week"""
        df['vwap'] = (df['Trading_Volume'] * (df['max'] + df['min'] + df['close']) / 3).cumsum() / df['Trading_Volume'].cumsum()
        return df

    def resample_to_weekly(self, df):
        """Convert daily data to weekly data"""
        # Set date as index for resampling
        df = df.set_index('date')
        
        # Define aggregation rules
        agg_dict = {
            'open': 'first',
            'close': 'last',
            'max': 'max',
            'min': 'min',
            'Trading_Volume': 'sum',
            'Trading_money': 'sum',
            'Trading_turnover': 'sum'
        }
        
        # Resample to weekly (week ending on Friday)
        weekly_df = df.resample('W-FRI').agg(agg_dict)
        
        # Reset index to get date as column
        weekly_df = weekly_df.reset_index()
        
        return weekly_df
    
    def load_and_update_data(self, stock_id):
        """Load existing data or download new data for a stock"""
        today = datetime.now()
        two_years_ago = (today - timedelta(days=730)).strftime('%Y-%m-%d')
        file_path = f"data/{stock_id}_data.csv"
        
        if os.path.exists(file_path):
            # Load existing data
            existing_data = pd.read_csv(file_path)
            existing_data['date'] = pd.to_datetime(existing_data['date'])
            last_date = existing_data['date'].max()
            
            # Get new data if needed
            if last_date.date() < today.date():
                new_data = self.dl.taiwan_stock_daily(
                    stock_id=stock_id,
                    start_date=last_date.strftime('%Y-%m-%d'),
                    end_date=today.strftime('%Y-%m-%d')
                )
                
                if not new_data.empty:
                    new_data['date'] = pd.to_datetime(new_data['date'])
                    # Combine and remove duplicates
                    combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['date'])
                    combined_data = combined_data.sort_values('date')
                else:
                    combined_data = existing_data
            else:
                combined_data = existing_data
        else:
            # Download full history
            combined_data = self.dl.taiwan_stock_daily(
                stock_id=stock_id,
                start_date=two_years_ago,
                end_date=today.strftime('%Y-%m-%d')
            )
            combined_data['date'] = pd.to_datetime(combined_data['date'])
        
        # Save updated data
        combined_data.to_csv(file_path, index=False)
        return combined_data
    
    def plot_candlestick(self, ax, df, width=0.6):
        """Plot candlestick chart"""
        # Calculate position for candlesticks
        df['x_position'] = range(len(df))
        
        # Plot up and down candlesticks separately
        up = df[df['close'] >= df['open']]
        down = df[df['close'] < df['open']]
        
        # Plot up candlesticks
        ax.bar(up['x_position'], up['close'] - up['open'], width, bottom=up['open'], color='red', alpha=0.7)
        ax.vlines(up['x_position'], up['min'], up['max'], color='red', linewidth=1)
        
        # Plot down candlesticks
        ax.bar(down['x_position'], down['close'] - down['open'], width, bottom=down['open'], color='green', alpha=0.7)
        ax.vlines(down['x_position'], down['min'], down['max'], color='green', linewidth=1)
    
    def plot_stock_chart(self, df, stock_id, timeframe='D'):
        """Create and save stock chart with indicators"""
        # Calculate indicators
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA120'] = df['close'].rolling(window=120).mean()
        df = self.get_vwap(df)
        
        # Create figure and subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[3, 1], gridspec_kw={'hspace': 0.3})
        
        # Plot candlesticks
        self.plot_candlestick(ax1, df)
        
        # Plot moving averages and VWAP
        x_range = range(len(df))
        ax1.plot(x_range, df['MA20'], color='orange', label='MA20', linewidth=1)
        ax1.plot(x_range, df['MA120'], color='blue', label='MA120', linewidth=1)
        ax1.plot(x_range, df['vwap'], color='purple', label='VWAP', linewidth=1)
        
        # Plot volume
        colors = ['red' if c >= o else 'green' for c, o in zip(df['close'], df['open'])]
        ax2.bar(x_range, df['Trading_Volume'], color=colors, alpha=0.7)
        
        # Customize price subplot
        timeframe_text = 'Daily' if timeframe == 'D' else 'Weekly'
        ax1.set_title(f'Stock {stock_id} {timeframe_text} Technical Analysis', pad=20)
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend()
        
        # Customize volume subplot
        ax2.set_title('Volume')
        ax2.grid(True, linestyle=':', alpha=0.6)
        
        # Format y-axis for volume (millions)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        # Set x-axis labels
        date_ticks = np.linspace(0, len(df) - 1, 10, dtype=int)
        ax1.set_xticks(date_ticks)
        ax1.set_xticklabels([])  # Hide x-labels on price chart
        ax2.set_xticks(date_ticks)
        ax2.set_xticklabels([d.strftime('%Y-%m-%d') for d in df['date'].iloc[date_ticks]], rotation=45)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(f'fig/{stock_id}_{timeframe}_chart.png')
        plt.close()
    
    def process_stock_list(self, stock_list):
        """Process a list of stocks"""
        for stock_id in stock_list:
            try:
                print(f"Processing stock {stock_id}...")
                # Load and update data
                daily_df = self.load_and_update_data(stock_id)
                
                # Create weekly data
                weekly_df = self.resample_to_weekly(daily_df.copy())
                
                # Plot daily chart
                self.plot_stock_chart(daily_df, stock_id, timeframe='D')
                
                # Plot weekly chart
                self.plot_stock_chart(weekly_df, stock_id, timeframe='W')
                
                print(f"Successfully processed stock {stock_id}")
            except Exception as e:
                print(f"Error processing stock {stock_id}: {str(e)}")
                

def finmind_data_download(stock_list):
    # Initialize manager with your API token
    api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRlIjoiMjAyNC0wNi0wMSAxMjowNzoyOSIsInVzZXJfaWQiOiJkcmVfaHN1IiwiaXAiOiIzNS4yMzMuMTk5LjIyNyJ9.vdbfK7J1TixjHvBcrk4hZuFtc3oy_cpD6wNurTQuQ7o'
    manager = StockDataManager(api_token)
    
    # Process stock list
    manager.process_stock_list(stock_list)