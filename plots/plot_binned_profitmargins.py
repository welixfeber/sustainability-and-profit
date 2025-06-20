import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# load & latest
df = pd.read_csv("sp500_margins_with_esg.csv", parse_dates=["date"])
df = df.sort_values("date").groupby("symbol", as_index=False).last()
df = df.dropna(subset=["Total ESG Risk score","netProfitMargin"])

# cut into 10 equal‐sized bins
df["esg_bin"] = pd.qcut(df["Total ESG Risk score"], q=25, duplicates="drop")

# compute mean ESG midpoint & mean margin per bin
b = (
    df.groupby("esg_bin")
      .agg(esg_mid=("Total ESG Risk score","mean"),
           net_mean=("netProfitMargin","mean"),
           count=("symbol","size"))
      .reset_index()
)

# optionally drop tiny bins
b = b[b["count"]>=2]

# plot
plt.figure(figsize=(10,6))
plt.scatter(df["Total ESG Risk score"], df["netProfitMargin"], alpha=0.2, color="#4C72B0")
plt.plot(b["esg_mid"], b["net_mean"], color="#DD8452", marker="o", lw=2, label="Binned average")
plt.ylim(0.08, 0.25)
plt.xlabel("Total ESG Risk Score")
plt.ylabel("Net Profit Margin")
plt.legend()
plt.show()
