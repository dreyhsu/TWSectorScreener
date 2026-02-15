from openbb import obb
import pandas as pd

# 1. Fetch Sector Performance Data
# We use the 'finviz' provider as it is standard for group/sector performance
# valid 'group' options: 'sector', 'industry', 'country'
df_groups = obb.equity.compare.groups(
    group="sector", 
    metric="performance", 
    provider="finviz"
).to_df()

# 2. Pre-process Data
# Finviz data often comes as strings with '%' signs (e.g., "5.23%"). 
# We need to convert them to floats for calculation.
cols_to_clean = ['performance_1m', 'performance_3m']

for col in cols_to_clean:
    # Remove %, convert to float, handle errors
    if col in df_groups.columns:
        df_groups[col] = df_groups[col].astype(str).str.rstrip('%').astype(float)

# 3. Apply Filters
# Condition A: 3-Month Performance (Quarter) must be Positive
# Condition B: 1-Month Performance (Month) must be Positive
positive_groups = df_groups[
    (df_groups['performance_3m'] > 0) & 
    (df_groups['performance_1m'] > 0)
].copy()

# 4. Rank and Extract "Up Middle"
# Sort by 3-Month Performance (descending: best at top)
ranked_groups = positive_groups.sort_values(by='performance_3m', ascending=False)

# Calculate indices for the "Up Middle" (e.g., the middle 33% or just the median)
n = len(ranked_groups)
if n > 0:
    # Defining "Up Middle" as the middle third of the qualified list
    start_idx = int(n * 0.33)
    end_idx = int(n * 0.66)
    
    # Handle edge case where list is small
    if start_idx == end_idx: 
        up_middle = ranked_groups.iloc[start_idx:start_idx+1] # Pick the median
    else:
        up_middle = ranked_groups.iloc[start_idx:end_idx]

    print(f"--- All Qualified Groups (Positive 1M & 3M) [{n} found] ---")
    print(ranked_groups[['name', 'performance_1m', 'performance_3m']])
    
    print("\n--- 'Up Middle' Groups (Target Selection) ---")
    print(up_middle[['name', 'performance_1m', 'performance_3m']])
else:
    print("No groups met the positive performance criteria.")