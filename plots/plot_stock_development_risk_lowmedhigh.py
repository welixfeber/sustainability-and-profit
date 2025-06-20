import pandas as pd
import matplotlib.pyplot as plt

# ─── CONFIG ───────────────────────────────────────────────
INPUT_FILE = "sp500_prices_with_esg.csv"
# Only these ESG levels
ESG_LEVELS = ["Low", "Medium", "High"]
COLORS = {
    "Low": "#2ca02c",
    "Medium": "#ff7f0e",
    "High": "#d62728"
}


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load merged data
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    # 2) Keep only rows with the desired ESG Risk Levels
    df = df[df["ESG Risk Level"].isin(ESG_LEVELS)]

    # 3) Compute daily average normalized_price by ESG Risk Level
    avg = (
        df
        .groupby(["date", "ESG Risk Level"])["normalized_price"]
        .mean()
        .reset_index()
    )

    # 4) Pivot so each level is its own column
    pivot = avg.pivot(
        index="date",
        columns="ESG Risk Level",
        values="normalized_price"
    ).reindex(columns=ESG_LEVELS)

    # 5) Plot each series
    plt.figure(figsize=(12, 6))
    for level in ESG_LEVELS:
        plt.plot(
            pivot.index,
            pivot[level],
            label=level,
            color=COLORS[level],
            linewidth=2
        )

    plt.xlabel("Date")
    plt.ylabel("Average Normalized Price")
    plt.title("Average Stock Price Development by ESG Risk Level (Low/Med/High)")
    plt.legend(title="ESG Risk Level")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()