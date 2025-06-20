import pandas as pd
import matplotlib.pyplot as plt

# ─── CONFIG ───────────────────────────────────────────────
INPUT_FILE = "sp500_prices_with_esg.csv"  # your merged normalized‐price + ESG file
# Define the order and colors for ESG Risk Levels
ESG_LEVELS = ["Negligible", "Low", "Medium", "High", "Severe"]
COLORS = {
    "Negligible": "#1f77b4",
    "Low": "#2ca02c",
    "Medium": "#ff7f0e",
    "High": "#d62728",
    "Severe": "#9467bd"
}


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load data
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    # 2) Keep only rows with an ESG Risk Level
    df = df[df["ESG Risk Level"].notna()]

    # 3) Compute daily average normalized_price by ESG Risk Level
    avg = (
        df
        .groupby(["date", "ESG Risk Level"])["normalized_price"]
        .mean()
        .reset_index()
    )

    # 4) Pivot so each ESG level is a column
    pivot = avg.pivot(index="date", columns="ESG Risk Level", values="normalized_price")
    # Reindex columns to enforce our desired order
    pivot = pivot.reindex(columns=ESG_LEVELS)

    # 5) Plot
    plt.figure(figsize=(12, 6))
    for level in ESG_LEVELS:
        if level in pivot:
            plt.plot(
                pivot.index,
                pivot[level],
                label=level,
                color=COLORS[level],
                linewidth=2
            )

    plt.xlabel("Date")
    plt.ylabel("Average Normalized Price")
    plt.title("Average Stock Price Development by ESG Risk Level")
    plt.legend(title="ESG Risk Level")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()