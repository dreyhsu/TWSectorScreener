import os
import re
from flask import Flask, render_template

app = Flask(__name__)

def get_stock_images():
    """
    Parse image filenames in the static folder and organize them by stock.
    Returns a dictionary with stock details and their chart paths.
    """
    stocks = {}
    static_folder = os.path.join(app.root_path, 'static')
    
    # Pattern to match: stock_id_chinese-name_D/W_chart.png
    pattern = re.compile(r'(\d+)_(.+)_(D|W)_chart\.png')
    
    for filename in os.listdir(static_folder):
        match = pattern.match(filename)
        if match:
            stock_id, chinese_name, chart_type = match.groups()
            
            # Create a unique key for each stock
            stock_key = f"{stock_id}_{chinese_name}"
            
            if stock_key not in stocks:
                stocks[stock_key] = {
                    'id': stock_id,
                    'name': chinese_name,
                    'daily_chart': None,
                    'weekly_chart': None
                }
            
            # Assign the appropriate chart path
            if chart_type == 'D':
                stocks[stock_key]['daily_chart'] = filename
            else:
                stocks[stock_key]['weekly_chart'] = filename
    
    # Convert to a list and sort by stock_id
    stock_list = list(stocks.values())
    stock_list.sort(key=lambda x: x['id'])
    
    return stock_list

@app.route('/')
def index():
    """Main page displaying all stock charts."""
    stocks = get_stock_images()
    return render_template('index.html', stocks=stocks)

if __name__ == '__main__':
    # Make the app accessible from other machines on the network
    app.run(host='0.0.0.0', port=5000, debug=True)