from openbb import obb
import os

# Define the filters exactly as they appear in the Finviz dropdowns
filters = {
    "Performance": "Today Up",
    "20-Day Simple Moving Average": "Price above SMA20",
    "50-Day Simple Moving Average": "Price above SMA50",
    "200-Day Simple Moving Average": "Price above SMA200",
    "50-Day High/Low": "New High",
}

# Run the screener
results = obb.equity.screener(
    provider="finviz",
    filters_dict=filters
)

# Convert to DataFrame
df = results.to_dataframe()

# Define output path
output_dir = "data/finviz"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "screener_results.csv")

# Save to CSV
df.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")