import pandas as pd
import matplotlib.pyplot as plt

# ─── Load and prepare data ─────────────────────────────────
df = pd.read_csv("sp500_margins_with_esg.csv", parse_dates=["date"])

# Take each company’s most recent margins
df_latest = df.sort_values("date") \
              .groupby("symbol", as_index=False) \
              .last()

# Drop rows missing percentile or margins
df_latest = df_latest.dropna(subset=[
    "ESG Risk Percentile",
    "netProfitMargin",
    "grossProfitMargin",
    "operatingProfitMargin"
])

# Convert "11th percentile" → 11, etc.
df_latest["ESG_Percentile"] = (
    df_latest["ESG Risk Percentile"]
      .str.replace(r"(\d+)(?:st|nd|rd|th) percentile", r"\1", regex=True)
      .astype(int)
)

# ─── Compute average margins by percentile ─────────────────
grouped = (
    df_latest
    .groupby("ESG_Percentile")[
        ["netProfitMargin", "grossProfitMargin", "operatingProfitMargin"]
    ]
    .mean()
    .sort_index()
)

# ─── Compute 3-point rolling trend lines ────────────────────
trend = grouped.rolling(window=5, min_periods=1).mean()

# ─── Plot raw averages and trend ────────────────────────────
plt.figure(figsize=(10, 6))

# Raw data with lower alpha
plt.plot(grouped.index, grouped["netProfitMargin"],
         marker='o', color='blue', alpha=0.2, label="Net PM (raw)", zorder=1)
plt.plot(grouped.index, grouped["grossProfitMargin"],
         marker='o', color='green', alpha=0.2, label="Gross PM (raw)", zorder=1)
plt.plot(grouped.index, grouped["operatingProfitMargin"],
         marker='o', color='red', alpha=0.2, label="Oper PM (raw)", zorder=1)

# Trend lines opaque and on top
plt.plot(trend.index, trend["netProfitMargin"],
         linestyle='--', color='blue', linewidth=2.5,
         label="Net PM (3-pt MA)", zorder=2)
plt.plot(trend.index, trend["grossProfitMargin"],
         linestyle='--', color='green', linewidth=2.5,
         label="Gross PM (3-pt MA)", zorder=2)
plt.plot(trend.index, trend["operatingProfitMargin"],
         linestyle='--', color='red', linewidth=2.5,
         label="Oper PM (3-pt MA)", zorder=2)

plt.xlabel("ESG Risk Percentile")
plt.ylabel("Average Profit Margin")
plt.title("Profit Margins by ESG Percentile with 3-Point Trend")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
