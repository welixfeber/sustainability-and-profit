import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load merged data
df = pd.read_csv("sp500_margins_with_esg.csv", parse_dates=["date"])

# Take most recent margin per company
df_latest = df.sort_values("date").groupby("symbol", as_index=False).last()

# Drop rows missing ESG Risk Level or margins
df_latest = df_latest.dropna(subset=[
    "ESG Risk Level",
    "netProfitMargin",
    "grossProfitMargin",
    "operatingProfitMargin"
])

# Compute average margins by ESG Risk Level
grouped = (
    df_latest
    .groupby("ESG Risk Level")[[
        "netProfitMargin",
        "grossProfitMargin",
        "operatingProfitMargin"
    ]]
    .mean()
)

# Order categories
order = ["Severe", "High", "Medium", "Low", "Negligible"]
grouped = grouped.reindex(order)

# Plot
x = np.arange(len(order))
width = 0.25

plt.figure(figsize=(10, 6))
plt.bar(x - width, grouped["netProfitMargin"], width, label="Net")
plt.bar(x,         grouped["grossProfitMargin"], width, label="Gross")
plt.bar(x + width, grouped["operatingProfitMargin"], width, label="Operating")

plt.xticks(x, order)
plt.xlabel("ESG Risk Level")
plt.ylabel("Average Profit Margin")
plt.title("Average Profit Margins by ESG Risk Level")
plt.legend()
plt.tight_layout()
plt.show()
