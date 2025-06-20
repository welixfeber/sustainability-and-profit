import pandas as pd
import matplotlib.pyplot as plt

# ─── Load & prepare ─────────────────────────────────────────
df = pd.read_csv("sp500_margins_with_esg.csv", parse_dates=["date"])
df_latest = (
    df.sort_values("date")
      .groupby("symbol", as_index=False).last()
      .dropna(subset=["ESG Risk Percentile",
                      "netProfitMargin",
                      "grossProfitMargin",
                      "operatingProfitMargin"])
)
df_latest["ESG_Percentile"] = (
    df_latest["ESG Risk Percentile"]
      .str.replace(r"(\d+)(?:st|nd|rd|th) percentile", r"\1", regex=True)
      .astype(int)
)

# ─── Compute per-percentile averages ─────────────────────────
grouped = (
    df_latest
      .groupby("ESG_Percentile")[["netProfitMargin",
                                 "grossProfitMargin",
                                 "operatingProfitMargin"]]
      .mean()
      .sort_index()
)

# ─── 5-pt rolling for each margin ────────────────────────────
trend5 = grouped.rolling(window=5, min_periods=1).mean()

# ─── NEW: combined average & 11-pt rolling ───────────────────
grouped["avgMargin"] = grouped.mean(axis=1)
big_trend = grouped["avgMargin"].rolling(window=11, min_periods=1, center=True).mean()

# ─── Plot everything ──────────────────────────────────────────
plt.figure(figsize=(12, 7))

# raw scatter
plt.scatter(grouped.index, grouped["netProfitMargin"],
            alpha=0.3, color="C0", label="Net PM (raw)")
plt.scatter(grouped.index, grouped["grossProfitMargin"],
            alpha=0.3, color="C1", label="Gross PM (raw)")
plt.scatter(grouped.index, grouped["operatingProfitMargin"],
            alpha=0.3, color="C2", label="Oper PM (raw)")

# 5-pt trends
plt.plot(trend5.index, trend5["netProfitMargin"],
         color="C0", linestyle="--", lw=2, label="Net PM (5-pt MA)")
plt.plot(trend5.index, trend5["grossProfitMargin"],
         color="C1", linestyle="--", lw=2, label="Gross PM (5-pt MA)")
plt.plot(trend5.index, trend5["operatingProfitMargin"],
         color="C2", linestyle="--", lw=2, label="Oper PM (5-pt MA)")

# BIG single trend
plt.plot(big_trend.index, big_trend,
         color="k", linewidth=3.5, label="Avg PM (11-pt MA)")

plt.xlabel("ESG Risk Percentile")
plt.ylabel("Profit Margin")
plt.title("Profit Margins by ESG Percentile with One Big Smooth Trend")
plt.legend()
plt.grid(alpha=0.4, linestyle=":")
plt.tight_layout()
plt.show()
