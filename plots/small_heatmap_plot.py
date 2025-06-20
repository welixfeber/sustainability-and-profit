import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── CONFIG ───────────────────────────────────────────────
PRICE_FILE  = "sp500_prices_with_esg.csv"      # normalized prices + ESG per day
MARGIN_FILE = "sp500_margins_with_esg.csv"     # profit margins + ESG per firm
# ─────────────────────────────────────────────────────────────

# 1) Load daily prices + compute cum_return & volatility
df_price = pd.read_csv(PRICE_FILE, parse_dates=["date"])
df_price = df_price.sort_values(["symbol", "date"])
df_price["return"] = df_price.groupby("symbol")["normalized_price"].pct_change()
df_price["volatility"] = (
    df_price
    .groupby("symbol")["return"]
    .rolling(30, min_periods=15)
    .std()
    .reset_index(0, drop=True)
)
cum_ret   = df_price.groupby("symbol")["normalized_price"].last().rename("cum_return")
vol       = df_price.groupby("symbol")["volatility"].last().rename("volatility")

# 2) Load margins + ESG
df_margin = pd.read_csv(MARGIN_FILE, parse_dates=["date"])
df_margin = df_margin.sort_values("date").groupby("symbol", as_index=False).last()
df_margin = df_margin.set_index("symbol")

# 3) Assemble cross‐section
esg_cols      = [
    "Total ESG Risk score",
    "Environment Risk Score",
    "Social Risk Score",
    "Governance Risk Score",
    "Controversy Score"
]
profit_cols   = ["netProfitMargin", "grossProfitMargin", "operatingProfitMargin"]
df_cs = pd.concat([
    df_margin[esg_cols],
    df_margin[profit_cols],
    cum_ret, vol
], axis=1).dropna()

# 4) Compute full correlation matrix
corr = df_cs.corr()

# 5) Extract only ESG‐vs‐profit/price correlations
corr_subset = corr.loc[esg_cols, profit_cols + ["cum_return", "volatility"]]

# 6) Plot heatmap
labels_x = corr_subset.columns
labels_y = corr_subset.index

plt.figure(figsize=(8, 4.5))
im = plt.imshow(corr_subset.values, cmap="coolwarm", vmin=-0.75, vmax=0.75, aspect="auto")

plt.xticks(np.arange(len(labels_x)), labels_x, rotation=45, ha="right")
plt.yticks(np.arange(len(labels_y)), labels_y)

cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
cbar.set_label("Pearson correlation")

plt.title("ESG Scores vs Profit & Stock Metrics Correlation")
plt.tight_layout()
plt.show()
