# save_as: compute_returns_volatility.py

import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────
INPUT_PRICE_FILE  = "sp500_prices_with_esg.csv"
OUTPUT_PRICE_FILE = "sp500_prices_with_esg_plus_returns.csv"
# ─────────────────────────────────────────────────────────────

# 1) Load your normalized‐price+ESG time series
df = pd.read_csv(INPUT_PRICE_FILE, parse_dates=["date"])

# 2) Compute daily returns
df = df.sort_values(["symbol", "date"])
df["daily_return"] = df.groupby("symbol")["normalized_price"].pct_change()

# 3) Compute 30-day rolling volatility (std of daily_return)
df["volatility"] = (
    df
    .groupby("symbol")["daily_return"]
    .rolling(window=30, min_periods=15)
    .std()
    .reset_index(level=0, drop=True)
)

# 4) Compute cumulative return as the last normalized_price → cum_return
#    so that base (5/26/2020) = 1, and cum_return = normalized_price_last
cum = (
    df
    .groupby("symbol")["normalized_price"]
    .last()
    .rename("cum_return")
)

# 5) Merge those two series back onto every row (or just keep once per symbol)
df = (
    df
    .merge(cum, on="symbol", how="left")
)

# 6) Save the augmented file
df.to_csv(OUTPUT_PRICE_FILE, index=False)
print(f"✅ Written {OUTPUT_PRICE_FILE} with {len(df)} rows, including cum_return & volatility.")
