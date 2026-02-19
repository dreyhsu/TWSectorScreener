import os
import random
import pandas as pd
import json
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

# Paths
BASE_DIR = '/Users/chihjuihsu/Documents/python_script/TWSectorScreener/'
IMAGE_DIR = os.path.join(BASE_DIR, 'fig/today/')
DATA_DIR = os.path.join(BASE_DIR, 'data/')
HOLDINGS_FILE = os.path.join(BASE_DIR, 'holdings.json')
TRACKED_STOCKS_FILE = os.path.join(BASE_DIR, 'data/tracked_stocks.csv')

def get_stock_name(ticker):
    try:
        df = pd.read_csv(TRACKED_STOCKS_FILE)
        match = df[df['stock_id'].astype(str) == str(ticker)]
        if not match.empty:
            return match.iloc[0]['name']
    except Exception:
        pass
    return "Unknown"

def get_latest_price(ticker):
    try:
        csv_path = os.path.join(DATA_DIR, f"{ticker}_data.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if not df.empty:
                return float(df.iloc[-1]['close'])
    except Exception:
        pass
    return 0.0

def calculate_volume_shrinkage():
    results = []
    try:
        # Get all files and shuffle to get a variety
        all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('_data.csv') and not f.startswith('00')]
        random.shuffle(all_files)
        
        for file in all_files[:100]: 
            ticker = file.replace('_data.csv', '')
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            if len(df) > 25:
                # Compare last 5 days avg to preceding 20 days avg
                recent_vol = df['Trading_Volume'].tail(5).mean()
                prev_vol = df['Trading_Volume'].iloc[-25:-5].mean()
                if prev_vol > 0:
                    drop = (recent_vol - prev_vol) / prev_vol
                    results.append({
                        "ticker": ticker,
                        "name": get_stock_name(ticker),
                        "vol_drop": drop,
                        "vol_drop_pct": f"{round(drop * 100, 1)}%"
                    })
    except Exception as e:
        print(f"Error calculating volume shrinkage: {e}")
    
    # Sort by most negative drop and take top 10
    return sorted(results, key=lambda x: x['vol_drop'])[:10]

@app.route('/')
def dashboard():
    # Load Holdings
    holdings_data = []
    try:
        with open(HOLDINGS_FILE, 'r') as f:
            h_list = json.load(f).get('holdings', [])
            for ticker in h_list:
                price = get_latest_price(ticker)
                holdings_data.append({
                    "ticker": ticker,
                    "name": get_stock_name(ticker),
                    "shares": 1000, # Placeholder
                    "entry_price": round(price * 0.95, 2), # Mock entry
                    "current_price": price
                })
    except Exception:
        pass

    # Volume Shrinkage
    volume_shrinkage = calculate_volume_shrinkage()

    # Get Charts from fig/today
    # Group by ticker
    all_files = os.listdir(IMAGE_DIR)
    tickers = sorted(list(set([f.split('_')[0] for f in all_files if '_' in f and f.endswith('.png')])))
    
    # Just take the first few tickers for display or a specific one like 4925 if available
    display_tickers = [t for t in tickers if t != '00代號'][:3]
    if '4925' in tickers and '4925' not in display_tickers:
        display_tickers.insert(0, '4925')
    
    charts = []
    for t in display_tickers:
        t_charts = sorted([f for f in all_files if f.startswith(f"{t}_")])
        charts.extend(t_charts)

    return render_template('index.html', holdings=holdings_data, volume_shrinkage=volume_shrinkage, charts=charts)

@app.route('/fig/today/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route('/api/performance')
def get_performance():
    """Simulate a performance tracking tick based on available margin."""
    free_margin = random.choice([0, 50000, 120000, 200000])
    
    # Try to get real-ish 0050 return
    try:
        df_0050 = pd.read_csv(os.path.join(DATA_DIR, '0050_data.csv'))
        last_close = df_0050.iloc[-1]['close']
        prev_close = df_0050.iloc[-10]['close']
        base_0050 = round(((last_close - prev_close) / prev_close) * 100, 2)
    except:
        base_0050 = 2.5
    
    # Strategy performs slightly better or worse than benchmark
    strategy_perf = base_0050 + random.uniform(-0.5, 2.0)
        
    return jsonify({
        "0050_return": base_0050,
        "strategy_return": round(strategy_perf, 2),
        "free_margin": free_margin
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
