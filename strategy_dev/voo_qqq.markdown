import pandas as pd
import numpy as np
import vectorbt as vbt
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Parameters
initial_capital = 5000
num_portions = 10
portion_size = initial_capital / num_portions
voo_drawdown_threshold = 0.10  # 10% drawdown
voo_increase_threshold = 0.05  # 5% increase
tickers = ['VOO', 'QQQ']
start_date = '2010-01-01'  # Adjust as needed
end_date = datetime.now().strftime('%Y-%m-%d')

# Download data
print(f"Downloading data for {tickers} from {start_date} to {end_date}...")
data = yf.download(tickers, start=start_date, end=end_date)
close_prices = data['Adj Close']
print("Data downloaded successfully.")

# Calculate 250-day rolling highest and lowest close for VOO
voo_prices = close_prices['VOO']
voo_250d_high = voo_prices.rolling(window=250).max()
voo_250d_low = voo_prices.rolling(window=250).min()

# Initialize position tracking
voo_portions = num_portions
qqq_portions = 0
positions = pd.DataFrame(index=close_prices.index, columns=['VOO_portions', 'QQQ_portions', 'VOO_value', 'QQQ_value', 'Total_value'])

# Strategy implementation
for i in range(250, len(close_prices)):
    current_date = close_prices.index[i]
    prev_date = close_prices.index[i-1]
    
    # Check conditions only if we have at least one day of previous data
    if i > 250:
        # Check for VOO 10% drawdown from 250d high
        if voo_prices[current_date] <= voo_250d_high[prev_date] * (1 - voo_drawdown_threshold) and voo_portions >= 2:
            # Sell 2 portions of VOO and buy QQQ
            voo_portions -= 2
            qqq_portions += 2
            print(f"{current_date}: VOO 10% drawdown detected. Selling 2 VOO portions, buying 2 QQQ portions.")
        
        # Check for VOO 5% increase from 250d low
        elif voo_prices[current_date] >= voo_250d_low[prev_date] * (1 + voo_increase_threshold) and qqq_portions >= 1:
            # Sell 1 portion of QQQ and buy VOO
            qqq_portions -= 1
            voo_portions += 1
            print(f"{current_date}: VOO 5% increase detected. Selling 1 QQQ portion, buying 1 VOO portion.")
    
    # Calculate current values
    voo_value = voo_portions * portion_size * (voo_prices[current_date] / voo_prices[close_prices.index[250]])
    qqq_value = qqq_portions * portion_size * (close_prices['QQQ'][current_date] / close_prices['QQQ'][close_prices.index[250]]) if qqq_portions > 0 else 0
    total_value = voo_value + qqq_value
    
    # Store positions
    positions.loc[current_date] = [voo_portions, qqq_portions, voo_value, qqq_value, total_value]

# Fill NaN values with 0
positions = positions.fillna(0)

# Calculate strategy returns
strategy_returns = positions['Total_value'].pct_change().fillna(0)

# Create benchmark (100% VOO)
benchmark_value = initial_capital * (voo_prices / voo_prices[close_prices.index[250]])
benchmark_returns = benchmark_value.pct_change().fillna(0)

# Trim data to start from day 250 (when we have enough data for the strategy)
start_idx = 250
strategy_returns = strategy_returns[start_idx:]
benchmark_returns = benchmark_returns[start_idx:]

# Convert to vectorbt PortfolioStats
strategy_rets = vbt.returns.Returns(strategy_returns)
benchmark_rets = vbt.returns.Returns(benchmark_returns)
strategy_stats = strategy_rets.stats()
benchmark_stats = benchmark_rets.stats()

# Display results
print("\n--- Strategy Performance ---")
print(f"Final Portfolio Value: ${positions['Total_value'][-1]:.2f}")
print(f"Total Return: {(positions['Total_value'][-1] / initial_capital - 1) * 100:.2f}%")
print(f"VOO Portions: {positions['VOO_portions'][-1]}")
print(f"QQQ Portions: {positions['QQQ_portions'][-1]}")

print("\n--- Comparison with Benchmark ---")
print(f"Strategy Sharpe Ratio: {strategy_stats['sharpe_ratio']:.2f}")
print(f"Benchmark Sharpe Ratio: {benchmark_stats['sharpe_ratio']:.2f}")
print(f"Strategy Max Drawdown: {strategy_stats['max_drawdown'] * 100:.2f}%")
print(f"Benchmark Max Drawdown: {benchmark_stats['max_drawdown'] * 100:.2f}%")
print(f"Strategy CAGR: {strategy_stats['yearly_return'] * 100:.2f}%")
print(f"Benchmark CAGR: {benchmark_stats['yearly_return'] * 100:.2f}%")

# Plot performance
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
plt.plot(positions['Total_value'], label='Strategy')
plt.plot(benchmark_value[benchmark_value.index >= positions.index[0]], label='Benchmark (VOO)')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Value ($)')
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(positions['VOO_portions'], label='VOO Portions', color='blue')
plt.plot(positions['QQQ_portions'], label='QQQ Portions', color='green')
plt.title('Asset Allocation Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Portions')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('voo_qqq_strategy_results.png')
plt.show()

# Create a more detailed performance report
print("\n--- Detailed Performance Report ---")
report_df = pd.DataFrame({
    'Metric': ['Total Return', 'CAGR', 'Sharpe Ratio', 'Max Drawdown', 'Volatility'],
    'Strategy': [
        f"{(positions['Total_value'][-1] / initial_capital - 1) * 100:.2f}%",
        f"{strategy_stats['yearly_return'] * 100:.2f}%",
        f"{strategy_stats['sharpe_ratio']:.2f}",
        f"{strategy_stats['max_drawdown'] * 100:.2f}%",
        f"{strategy_stats['yearly_vol'] * 100:.2f}%"
    ],
    'Benchmark (VOO)': [
        f"{(benchmark_value[-1] / initial_capital - 1) * 100:.2f}%",
        f"{benchmark_stats['yearly_return'] * 100:.2f}%",
        f"{benchmark_stats['sharpe_ratio']:.2f}",
        f"{benchmark_stats['max_drawdown'] * 100:.2f}%",
        f"{benchmark_stats['yearly_vol'] * 100:.2f}%"
    ]
})

print(report_df.to_string(index=False))

# Save results to CSV
positions.to_csv('voo_qqq_strategy_positions.csv')
report_df.to_csv('voo_qqq_strategy_report.csv', index=False)
print("\nResults saved to CSV files and plot saved as 'voo_qqq_strategy_results.png'")
