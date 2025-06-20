import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

# ─── CONFIG ───────────────────────────────────────────────
INPUT_FILE = "sp500_margins_with_esg.csv"  # the merged CSV in your working directory
# ─────────────────────────────────────────────────────────────

# 1) Load merged data
df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# 2) For each symbol, keep the most recent profit margin record
df_latest = df.sort_values("date").groupby("symbol", as_index=False).last()

# 3) Drop rows missing percentile or net margin
df_latest = df_latest.dropna(subset=["ESG Risk Percentile", "netProfitMargin"])

# 4) Extract numeric ESG percentile (e.g. "62nd percentile" → 62.0)
df_latest["esg_pct"] = (
    df_latest["ESG Risk Percentile"]
      .str.extract(r"(\d+)")
      .astype(float)
)

# 5) Prepare data for plotting
x = df_latest["esg_pct"].values
y = df_latest["netProfitMargin"].values

# 6) Compute LOWESS smoothing curve
#    frac controls the span: lower = more sensitive, higher = smoother
smoothed = lowess(endog=y, exog=x, frac=0.3, return_sorted=True)
xs, ys = smoothed[:, 0], smoothed[:, 1]

# 7) Plot scatter + smooth trend
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.5, color="#4C72B0", label="Data points")
plt.plot(xs, ys, color="#DD8452", linewidth=3, label="LOWESS Trend")

plt.ylim(0.08, 0.2)
plt.xlabel("ESG Risk Percentile")
plt.ylabel("Net Profit Margin")
plt.title("Net Profit Margin vs ESG Risk Percentile\nwith LOWESS-Smoothed Trend")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
