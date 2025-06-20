import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

# 1) Load your merged dataset
df = pd.read_csv("sp500_margins_with_esg.csv", parse_dates=["date"])

# 2) Keep each company's most recent record
df_latest = df.sort_values("date").groupby("symbol", as_index=False).last()

# 3) Drop any rows missing the key columns
df_latest = df_latest.dropna(subset=["Total ESG Risk score", "netProfitMargin"])

# 4) Extract x (ESG) and y (Net Margin)
x = df_latest["Total ESG Risk score"].values
y = df_latest["netProfitMargin"].values

# 5) Compute LOWESS smooth curve
smoothed = lowess(y, x, frac=0.3, return_sorted=True)
xs, ys = smoothed[:, 0], smoothed[:, 1]

# 6) Plot
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.5, color="#4C72B0", label="Data points")
plt.plot(xs, ys, color="#DD8452", linewidth=3, label="LOWESS trend")

# 7) Set y-axis limits
plt.ylim(0.08, 0.25)

plt.xlabel("Total ESG Risk Score")
plt.ylabel("Net Profit Margin")
plt.title("Net Profit Margin vs Total ESG Risk Score\nwith LOWESS-Smoothed Trend")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
